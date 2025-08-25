using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.EventSystems;
using UnityEngine.UI;

[DisallowMultipleComponent]
[DefaultExecutionOrder(100)]
public class MinimapSystem : MonoBehaviour
{
    // =============================
    // Inspector configuration
    // =============================

    [Header("Player Arrow")]
    [Tooltip("Player transform to follow and/or orient the minimap.")]
    public Transform player;
    [Tooltip("Sprite used for the player's arrow/icon (optional). If null, a default triangle will be generated.")]
    public Sprite playerArrowSprite;
    [Tooltip("Color of the player's arrow/icon.")]
    public Color playerArrowColor = Color.white;
    [Tooltip("Size of the player's arrow/icon in UI pixels.")]
    public float playerArrowSize = 18f;
    [Tooltip("Rotate the map to match the player's yaw. If enabled, the arrow points up.")]
    public bool rotateMapWithPlayer = true;
    [Tooltip("Force North-Up (map fixed). If enabled, the map does not rotate, and the arrow rotates with player.")]
    public bool northUp = false;

    [Header("Tracked Objects")]
    public List<TrackedObject> trackedObjects = new List<TrackedObject>();

    [Header("Waypoints")]
    public List<Waypoint> waypoints = new List<Waypoint>();
    [Tooltip("Show an edge arrow for off-screen waypoints.")]
    public bool waypointEdgeArrows = true;

    [Header("Click-To-Create Waypoints")]
    [Tooltip("Enable clicking inside the minimap to create waypoints at the clicked world position.")]
    public bool clickToCreateWaypoints = false;
    public Color defaultWaypointColor = Color.yellow;
    public string defaultWaypointLabel = "Waypoint";
    public float defaultWaypointRadius = 2f;

    [Header("Map Style")]
    public MapShape mapShape = MapShape.Circle;
    [Tooltip("Custom sprite to use as mask when Map Shape is Custom.")]
    public Sprite customMaskSprite;
    public Color borderColor = Color.white;
    public float borderThickness = 6f;
    public Color backgroundColor = new Color(0f, 0f, 0f, 0.4f);

    [Header("UI Placement")]
    public Corner corner = Corner.TopRight;
    public Vector2 anchoredOffset = new Vector2(-16f, -16f);
    [Tooltip("Square size of the minimap in UI pixels (outer frame).")]
    public float mapUISize = 256f;
    [Tooltip("Scale multiplier applied to the whole minimap Canvas.")]
    public float uiScale = 1f;
    [Tooltip("Fine multiplier to adjust UI scale precisely without changing logical size.")]
    public float uiScaleFine = 1f;

    [Header("Camera & Alignment")]
    [Tooltip("World area covered by the minimap width (in world units). Height adjusts by aspect.")]
    public float coverageWorldSize = 100f;
    [Tooltip("Orthographic camera height above ground.")]
    public float cameraHeight = 200f;
    [Tooltip("World-space XZ offset applied to the minimap center.")]
    public Vector2 worldOffset = Vector2.zero;
    [Tooltip("Auto-fit coverage to the active Terrain bounds.")]
    public bool autoFitToTerrain = false;
    public Terrain terrainOverride;
    [Tooltip("Culling mask for the minimap camera.")]
    public LayerMask minimapCullingMask = ~0;
    public Vector2Int renderTextureSize = new Vector2Int(512, 512);

    [Header("Performance & UX")]
    [Tooltip("Lerp speed in units/sec for smoothing UI marker movement.")]
    public float markerSmoothing = 12f;
    [Tooltip("Initial pool size for marker UI elements.")]
    public int initialPoolSize = 32;

    [Header("Popups (Optional)")]
    [Tooltip("Show a simple popup when waypoints are reached. Optionally use a custom prefab.")]
    public bool enablePopups = false;
    public GameObject customPopupPrefab;
    public float popupDuration = 3f;

    // =============================
    // Private/runtime state
    // =============================
    private Camera minimapCamera;
    private RenderTexture minimapRenderTexture;

    private Canvas minimapCanvas;
    private CanvasScaler minimapCanvasScaler;
    private RectTransform minimapRoot;         // The framed square
    private RectTransform clipRect;            // The inner masked rect
    private RawImage mapImage;                 // Displays the RenderTexture
    private Image frameImage;                  // Outer border frame
    private Image clipMaskImage;               // Image with Mask component for shape clipping
    private RectTransform markerContainer;     // Overlay container for markers
    private RectTransform playerArrowRect;
    private Image playerArrowImage;
    private MinimapClickCatcher clickCatcher;

    // Popup UI
    private RectTransform popupRoot;
    private Text popupText;
    private float popupHideTime;

    // Pools and bookkeeping
    private readonly List<MarkerUI> markerPool = new List<MarkerUI>();
    private readonly Dictionary<TrackedObject, MarkerUI> trackedToMarker = new Dictionary<TrackedObject, MarkerUI>();
    private readonly Dictionary<Waypoint, MarkerUI> waypointToMarker = new Dictionary<Waypoint, MarkerUI>();
    private readonly Dictionary<Waypoint, MarkerUI> waypointToArrow = new Dictionary<Waypoint, MarkerUI>();

    // Generated sprites cache
    private Sprite cachedSquareSprite;
    private Sprite cachedCircleSprite;
    private Sprite cachedDiamondSprite;
    private Sprite cachedStarSprite;
    private Sprite cachedArrowSprite;

    private const string CanvasName = "Minimap_Canvas";
    private const string CameraName = "Minimap_Camera";
    private const string RootName = "Minimap";
    private const string FrameName = "Frame";
    private const string ClipName = "Clip";
    private const string RenderName = "Render";
    private const string MarkersName = "Markers";
    private const string ClickName = "ClickCatcher";
    private const string PopupName = "Popup";

    // =============================
    // Unity lifecycle
    // =============================
    private void Reset()
    {
        // Reasonable defaults
        borderThickness = 6f;
        mapUISize = 256f;
        coverageWorldSize = 100f;
        cameraHeight = 200f;
        renderTextureSize = new Vector2Int(512, 512);
        markerSmoothing = 12f;
        initialPoolSize = 32;
        playerArrowColor = Color.white;
        defaultWaypointColor = Color.yellow;
        popupDuration = 3f;
    }

    private void Awake()
    {
        EnsureEventSystem();
        EnsureSprites();
        EnsureCamera();
        EnsureCanvasAndUI();
        PrewarmPool(initialPoolSize);
    }

    private void Start()
    {
        if (autoFitToTerrain)
        {
            AutoFitCoverageToTerrain();
        }

        RebuildAllMarkers();
        UpdateCameraImmediate();
        UpdateAllMarkersImmediate();
    }

    private void OnValidate()
    {
        // Keep incompatible toggles sane
        if (northUp) rotateMapWithPlayer = false;
        if (rotateMapWithPlayer) northUp = false;

        if (borderThickness < 0f) borderThickness = 0f;
        if (mapUISize < 64f) mapUISize = 64f;
        if (coverageWorldSize < 1f) coverageWorldSize = 1f;
        if (cameraHeight < 1f) cameraHeight = 1f;
        if (renderTextureSize.x < 64) renderTextureSize.x = 64;
        if (renderTextureSize.y < 64) renderTextureSize.y = 64;

        if (Application.isPlaying == false)
        {
            EnsureSprites();
            EnsureCanvasAndUI();
            EnsureCamera();
            ApplyStyleRuntime();
            RebuildAllMarkers();
            UpdateCameraImmediate();
            UpdateAllMarkersImmediate();
        }
    }

    private void LateUpdate()
    {
        UpdateCameraRuntime();
        UpdateMarkersRuntime(Time.deltaTime);
        UpdatePopupRuntime();
    }

    private void OnDestroy()
    {
        if (minimapCamera != null)
        {
            minimapCamera.targetTexture = null;
        }
        if (minimapRenderTexture != null)
        {
            if (minimapRenderTexture.IsCreated()) minimapRenderTexture.Release();
            if (Application.isPlaying)
                Destroy(minimapRenderTexture);
            else
                DestroyImmediate(minimapRenderTexture);
            minimapRenderTexture = null;
        }
    }

    // =============================
    // Public API
    // =============================

    public Waypoint CreateWaypoint(Vector3 worldPosition, string label = null, Color? color = null)
    {
        var wp = new Waypoint
        {
            useTransform = false,
            worldPosition = worldPosition,
            label = string.IsNullOrEmpty(label) ? defaultWaypointLabel : label,
            color = color ?? defaultWaypointColor,
            radius = defaultWaypointRadius,
            showEdgeArrow = true,
            reached = false,
            onReach = new UnityEvent()
        };
        waypoints.Add(wp);
        EnsureWaypointMarker(wp);
        return wp;
    }

    public void HandleMinimapPointer(Vector2 localPoint, PointerEventData eventData)
    {
        if (!clickToCreateWaypoints) return;
        if (clipRect == null) return;

        // Reject clicks outside of mask shape
        if (!IsInsideMask(localPoint, out _)) return;

        Vector3 world = LocalToWorld(localPoint);
        CreateWaypoint(world, null, null);
    }

    // =============================
    // UI / Camera setup
    // =============================
    private void EnsureEventSystem()
    {
        if (FindObjectOfType<EventSystem>() == null)
        {
            var go = new GameObject("EventSystem", typeof(EventSystem), typeof(StandaloneInputModule));
            go.hideFlags = HideFlags.DontSave;
        }
    }

    private void EnsureSprites()
    {
        if (cachedSquareSprite == null) cachedSquareSprite = CreateSolidSprite(64, 64, Color.white);
        if (cachedCircleSprite == null) cachedCircleSprite = CreateCircleSprite(64);
        if (cachedDiamondSprite == null) cachedDiamondSprite = CreateDiamondSprite(64);
        if (cachedStarSprite == null) cachedStarSprite = CreateStarSprite(64);
        if (cachedArrowSprite == null) cachedArrowSprite = CreateArrowSprite(64, 64);
        if (playerArrowSprite == null) playerArrowSprite = cachedArrowSprite;
    }

    private void EnsureCamera()
    {
        if (minimapCamera == null)
        {
            Transform child = transform.Find(CameraName);
            GameObject camGo = child != null ? child.gameObject : new GameObject(CameraName);
            if (camGo.transform.parent != transform) camGo.transform.SetParent(transform, false);
            minimapCamera = camGo.GetComponent<Camera>();
            if (minimapCamera == null) minimapCamera = camGo.AddComponent<Camera>();
        }

        minimapCamera.orthographic = true;
        minimapCamera.nearClipPlane = 0.1f;
        minimapCamera.farClipPlane = 2000f;
        minimapCamera.clearFlags = CameraClearFlags.SolidColor;
        minimapCamera.backgroundColor = new Color(0, 0, 0, 0);
        minimapCamera.cullingMask = minimapCullingMask;
        minimapCamera.allowHDR = false;
        minimapCamera.allowMSAA = false;
        minimapCamera.useOcclusionCulling = false;

        // Place above the world, looking straight down
        minimapCamera.transform.position = new Vector3(0, cameraHeight, 0);
        minimapCamera.transform.rotation = Quaternion.Euler(90f, 0f, 0f);

        EnsureRenderTexture();
        minimapCamera.targetTexture = minimapRenderTexture;
    }

    private void EnsureRenderTexture()
    {
        if (minimapRenderTexture != null)
        {
            if (minimapRenderTexture.width == renderTextureSize.x && minimapRenderTexture.height == renderTextureSize.y)
            {
                return;
            }
            minimapRenderTexture.Release();
            DestroyImmediate(minimapRenderTexture);
            minimapRenderTexture = null;
        }

        minimapRenderTexture = new RenderTexture(renderTextureSize.x, renderTextureSize.y, 16, RenderTextureFormat.ARGB32)
        {
            name = "Minimap_RTex",
            antiAliasing = 1,
            useMipMap = false,
            autoGenerateMips = false
        };
        minimapRenderTexture.Create();
    }

    private void EnsureCanvasAndUI()
    {
        if (minimapCanvas == null)
        {
            Transform canvasChild = transform.Find(CanvasName);
            GameObject canvasGo = canvasChild != null ? canvasChild.gameObject : new GameObject(CanvasName);
            if (canvasGo.transform.parent != transform) canvasGo.transform.SetParent(transform, false);
            minimapCanvas = canvasGo.GetComponent<Canvas>();
            if (minimapCanvas == null) minimapCanvas = canvasGo.AddComponent<Canvas>();
            minimapCanvas.renderMode = RenderMode.ScreenSpaceOverlay;

            minimapCanvasScaler = canvasGo.GetComponent<CanvasScaler>();
            if (minimapCanvasScaler == null) minimapCanvasScaler = canvasGo.AddComponent<CanvasScaler>();
            minimapCanvasScaler.uiScaleMode = CanvasScaler.ScaleMode.ConstantPixelSize;
            minimapCanvasScaler.scaleFactor = Mathf.Max(0.1f, uiScale * uiScaleFine);
        }

        // Root container
        if (minimapRoot == null)
        {
            var rootGo = GameObject.Find(RootName);
            if (rootGo == null)
            {
                rootGo = new GameObject(RootName, typeof(RectTransform));
                rootGo.transform.SetParent(minimapCanvas.transform, false);
            }
            minimapRoot = rootGo.GetComponent<RectTransform>();
            ConfigureAnchors(minimapRoot, corner, anchoredOffset, mapUISize);
        }

        // Frame image
        if (frameImage == null)
        {
            var frameGo = FindOrCreateChild(minimapRoot, FrameName);
            frameImage = GetOrAdd<Image>(frameGo);
        }
        frameImage.color = borderColor;
        frameImage.sprite = cachedSquareSprite;
        frameImage.type = Image.Type.Sliced;
        frameImage.raycastTarget = false;
        frameImage.rectTransform.sizeDelta = new Vector2(mapUISize, mapUISize);

        // Clip area (masked)
        if (clipRect == null)
        {
            var clipGo = FindOrCreateChild(frameImage.rectTransform, ClipName);
            clipRect = clipGo.GetComponent<RectTransform>();
            clipMaskImage = GetOrAdd<Image>(clipGo);
            var mask = clipGo.GetComponent<Mask>();
            if (mask == null) mask = clipGo.AddComponent<Mask>();
            mask.showMaskGraphic = false;
        }

        float innerSize = Mathf.Max(0f, mapUISize - 2f * borderThickness);
        clipRect.sizeDelta = new Vector2(innerSize, innerSize);
        clipRect.anchoredPosition = Vector2.zero;
        ApplyMaskSprite();

        // Background fill under the map RenderImage (within mask)
        var bgGo = FindOrCreateChild(clipRect, "BackgroundFill");
        var bgImg = GetOrAdd<Image>(bgGo);
        StretchToFill(bgImg.rectTransform);
        bgImg.color = backgroundColor;
        bgImg.sprite = cachedSquareSprite;
        bgImg.type = Image.Type.Sliced;
        bgImg.raycastTarget = false;

        // Map render RawImage
        if (mapImage == null)
        {
            var renderGo = FindOrCreateChild(clipRect, RenderName);
            mapImage = GetOrAdd<RawImage>(renderGo);
            StretchToFill(mapImage.rectTransform);
        }
        mapImage.texture = minimapRenderTexture;

        // Markers container
        if (markerContainer == null)
        {
            var markersGo = FindOrCreateChild(clipRect, MarkersName);
            markerContainer = markersGo.GetComponent<RectTransform>();
            StretchToFill(markerContainer);
        }

        // Player arrow
        if (playerArrowImage == null)
        {
            var playerGo = FindOrCreateChild(clipRect, "PlayerArrow");
            playerArrowRect = playerGo.GetComponent<RectTransform>();
            playerArrowImage = GetOrAdd<Image>(playerGo);
            playerArrowImage.raycastTarget = false;
        }
        playerArrowImage.sprite = playerArrowSprite ?? cachedArrowSprite;
        playerArrowImage.color = playerArrowColor;
        playerArrowRect.sizeDelta = new Vector2(playerArrowSize, playerArrowSize);
        playerArrowRect.anchoredPosition = Vector2.zero;

        // Click catcher
        if (clickCatcher == null)
        {
            var clickGo = FindOrCreateChild(clipRect, ClickName);
            clickCatcher = GetOrAdd<MinimapClickCatcher>(clickGo);
            var rt = clickCatcher.GetComponent<RectTransform>();
            StretchToFill(rt);
            clickCatcher.minimapSystem = this;
        }

        // Popups
        EnsurePopupUI();
    }

    private void ApplyStyleRuntime()
    {
        if (minimapCanvasScaler != null)
        {
            minimapCanvasScaler.scaleFactor = Mathf.Max(0.1f, uiScale * uiScaleFine);
        }
        if (frameImage != null)
        {
            frameImage.color = borderColor;
            frameImage.rectTransform.sizeDelta = new Vector2(mapUISize, mapUISize);
        }
        if (clipRect != null)
        {
            float innerSize = Mathf.Max(0f, mapUISize - 2f * borderThickness);
            clipRect.sizeDelta = new Vector2(innerSize, innerSize);
            clipRect.anchoredPosition = Vector2.zero;
        }
        if (minimapRoot != null)
        {
            ConfigureAnchors(minimapRoot, corner, anchoredOffset, mapUISize);
        }
        ApplyMaskSprite();
        if (mapImage != null) mapImage.texture = minimapRenderTexture;
        if (playerArrowImage != null)
        {
            playerArrowImage.sprite = playerArrowSprite ?? cachedArrowSprite;
            playerArrowImage.color = playerArrowColor;
            if (playerArrowRect != null)
                playerArrowRect.sizeDelta = new Vector2(playerArrowSize, playerArrowSize);
        }
    }

    private void ApplyMaskSprite()
    {
        if (clipMaskImage == null) return;
        switch (mapShape)
        {
            case MapShape.Circle:
                clipMaskImage.sprite = cachedCircleSprite;
                clipMaskImage.type = Image.Type.Simple;
                break;
            case MapShape.Square:
                clipMaskImage.sprite = cachedSquareSprite;
                clipMaskImage.type = Image.Type.Sliced;
                break;
            case MapShape.Star:
                clipMaskImage.sprite = cachedStarSprite;
                clipMaskImage.type = Image.Type.Simple;
                break;
            case MapShape.Custom:
                clipMaskImage.sprite = customMaskSprite != null ? customMaskSprite : cachedSquareSprite;
                clipMaskImage.type = Image.Type.Simple;
                break;
        }
    }

    private void EnsurePopupUI()
    {
        if (!enablePopups)
        {
            if (popupRoot != null) popupRoot.gameObject.SetActive(false);
            return;
        }

        if (popupRoot == null)
        {
            if (customPopupPrefab != null)
            {
                var inst = Instantiate(customPopupPrefab, minimapCanvas.transform);
                popupRoot = inst.GetComponent<RectTransform>();
                popupText = inst.GetComponentInChildren<Text>();
            }
            else
            {
                var popupGo = new GameObject(PopupName, typeof(RectTransform));
                popupGo.transform.SetParent(minimapCanvas.transform, false);
                popupRoot = popupGo.GetComponent<RectTransform>();
                popupRoot.anchorMin = new Vector2(0.5f, 0.5f);
                popupRoot.anchorMax = new Vector2(0.5f, 0.5f);
                popupRoot.pivot = new Vector2(0.5f, 0.5f);
                popupRoot.anchoredPosition = new Vector2(0, -mapUISize * 0.6f);
                popupRoot.sizeDelta = new Vector2(mapUISize * 1.2f, 40f);

                var bg = popupGo.AddComponent<Image>();
                bg.color = new Color(0f, 0f, 0f, 0.7f);

                var textGo = new GameObject("Text", typeof(RectTransform));
                textGo.transform.SetParent(popupRoot, false);
                var textRect = textGo.GetComponent<RectTransform>();
                StretchToFill(textRect);
                popupText = textGo.AddComponent<Text>();
                popupText.text = "";
                popupText.alignment = TextAnchor.MiddleCenter;
                popupText.color = Color.white;
                popupText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
                popupText.resizeTextForBestFit = true;
                popupText.resizeTextMinSize = 12;
                popupText.resizeTextMaxSize = 32;
            }
        }
        popupRoot.gameObject.SetActive(false);
    }

    private static void ConfigureAnchors(RectTransform rect, Corner corner, Vector2 offset, float size)
    {
        rect.pivot = new Vector2(0.5f, 0.5f);
        switch (corner)
        {
            case Corner.TopLeft:
                rect.anchorMin = new Vector2(0f, 1f);
                rect.anchorMax = new Vector2(0f, 1f);
                rect.anchoredPosition = new Vector2(offset.x + size * 0.5f, offset.y - size * 0.5f);
                break;
            case Corner.TopRight:
                rect.anchorMin = new Vector2(1f, 1f);
                rect.anchorMax = new Vector2(1f, 1f);
                rect.anchoredPosition = new Vector2(offset.x - size * 0.5f, offset.y - size * 0.5f);
                break;
            case Corner.BottomLeft:
                rect.anchorMin = new Vector2(0f, 0f);
                rect.anchorMax = new Vector2(0f, 0f);
                rect.anchoredPosition = new Vector2(offset.x + size * 0.5f, offset.y + size * 0.5f);
                break;
            case Corner.BottomRight:
                rect.anchorMin = new Vector2(1f, 0f);
                rect.anchorMax = new Vector2(1f, 0f);
                rect.anchoredPosition = new Vector2(offset.x - size * 0.5f, offset.y + size * 0.5f);
                break;
        }
        rect.sizeDelta = new Vector2(size, size);
    }

    private static T GetOrAdd<T>(GameObject go) where T : Component
    {
        var t = go.GetComponent<T>();
        if (t == null) t = go.AddComponent<T>();
        return t;
    }

    private static GameObject FindOrCreateChild(Transform parent, string name)
    {
        Transform child = null;
        for (int i = 0; i < parent.childCount; i++)
        {
            if (parent.GetChild(i).name == name) { child = parent.GetChild(i); break; }
        }
        GameObject go;
        if (child == null)
        {
            go = new GameObject(name, typeof(RectTransform));
            go.transform.SetParent(parent, false);
        }
        else
        {
            go = child.gameObject;
        }
        return go;
    }

    private static void StretchToFill(RectTransform rect)
    {
        rect.anchorMin = Vector2.zero;
        rect.anchorMax = Vector2.one;
        rect.pivot = new Vector2(0.5f, 0.5f);
        rect.anchoredPosition = Vector2.zero;
        rect.sizeDelta = Vector2.zero;
    }

    private void AutoFitCoverageToTerrain()
    {
        var t = terrainOverride != null ? terrainOverride : Terrain.activeTerrain;
        if (t == null) return;
        var size = t.terrainData != null ? t.terrainData.size : new Vector3(coverageWorldSize, 0, coverageWorldSize);
        coverageWorldSize = Mathf.Max(size.x, size.z);
    }

    // =============================
    // Camera & mapping
    // =============================
    private void UpdateCameraImmediate()
    {
        UpdateCameraRuntimeInternal(Time.deltaTime, immediate: true);
    }

    private void UpdateCameraRuntime()
    {
        UpdateCameraRuntimeInternal(Time.deltaTime, immediate: false);
    }

    private void UpdateCameraRuntimeInternal(float deltaTime, bool immediate)
    {
        if (minimapCamera == null) return;
        if (clipRect == null) return;

        // Aspect based on UI inner clip rect
        float innerSize = Mathf.Max(0f, mapUISize - 2f * borderThickness);
        float aspect = innerSize / innerSize; // square by design
        minimapCamera.aspect = aspect;
        minimapCamera.orthographicSize = Mathf.Max(1f, coverageWorldSize * 0.5f);

        // Follow player or origin
        Vector3 targetPos = Vector3.zero;
        float yaw = 0f;
        if (player != null)
        {
            targetPos = player.position;
            yaw = player.eulerAngles.y;
        }

        if (northUp)
        {
            yaw = 0f;
        }

        // Apply world-space offset in XZ
        targetPos += new Vector3(worldOffset.x, 0f, worldOffset.y);
        var camPos = new Vector3(targetPos.x, cameraHeight, targetPos.z);
        minimapCamera.transform.position = camPos;
        minimapCamera.transform.rotation = Quaternion.Euler(90f, rotateMapWithPlayer ? yaw : 0f, 0f);

        // Player arrow orientation
        if (playerArrowRect != null)
        {
            if (rotateMapWithPlayer)
            {
                // Map rotates with player; keep arrow pointing up
                playerArrowRect.localEulerAngles = Vector3.zero;
            }
            else
            {
                // Map fixed; arrow rotates to match player yaw
                float arrowYaw = player != null ? player.eulerAngles.y : 0f;
                playerArrowRect.localEulerAngles = new Vector3(0, 0, -arrowYaw);
            }
        }
    }

    private Vector2 WorldToLocalUI(Vector3 worldPosition)
    {
        if (minimapCamera == null || clipRect == null) return Vector2.zero;

        // Compute vector in world space relative to camera center
        Vector3 camCenter = minimapCamera.transform.position;
        float yaw = minimapCamera.transform.eulerAngles.y * Mathf.Deg2Rad;
        float cos = Mathf.Cos(-yaw);
        float sin = Mathf.Sin(-yaw);

        Vector2 deltaXZ = new Vector2(worldPosition.x - camCenter.x, worldPosition.z - camCenter.z);
        // Rotate by -yaw to align with camera orientation
        float localX = deltaXZ.x * cos - deltaXZ.y * sin;
        float localY = deltaXZ.x * sin + deltaXZ.y * cos;

        float halfWorldW = minimapCamera.orthographicSize * minimapCamera.aspect;
        float halfWorldH = minimapCamera.orthographicSize;

        float innerSize = Mathf.Max(0f, mapUISize - 2f * borderThickness);
        float halfUIW = innerSize * 0.5f;
        float halfUIH = innerSize * 0.5f;

        float uiX = (localX / halfWorldW) * halfUIW;
        float uiY = (localY / halfWorldH) * halfUIH;
        return new Vector2(uiX, uiY);
    }

    private Vector3 LocalToWorld(Vector2 local)
    {
        if (minimapCamera == null) return Vector3.zero;
        float innerSize = Mathf.Max(0f, mapUISize - 2f * borderThickness);
        float halfUI = innerSize * 0.5f;

        float yaw = minimapCamera.transform.eulerAngles.y * Mathf.Deg2Rad;
        float cos = Mathf.Cos(yaw);
        float sin = Mathf.Sin(yaw);

        float halfWorldW = minimapCamera.orthographicSize * minimapCamera.aspect;
        float halfWorldH = minimapCamera.orthographicSize;

        float localX = (local.x / halfUI) * halfWorldW;
        float localY = (local.y / halfUI) * halfWorldH;

        // Rotate back to world axes
        float worldX = localX * cos - localY * sin;
        float worldZ = localX * sin + localY * cos;

        Vector3 center = minimapCamera.transform.position;
        return new Vector3(center.x + worldX, 0f, center.z + worldZ);
    }

    private bool IsInsideMask(Vector2 local, out float limitRadius)
    {
        float innerSize = Mathf.Max(0f, mapUISize - 2f * borderThickness);
        float half = innerSize * 0.5f;
        switch (mapShape)
        {
            case MapShape.Square:
            case MapShape.Custom:
                limitRadius = half;
                return (Mathf.Abs(local.x) <= half && Mathf.Abs(local.y) <= half);
            case MapShape.Circle:
            case MapShape.Star:
                limitRadius = half;
                return (local.sqrMagnitude <= (half * half));
            default:
                limitRadius = half;
                return true;
        }
    }

    // =============================
    // Markers & waypoints
    // =============================
    private void PrewarmPool(int count)
    {
        for (int i = 0; i < count; i++)
        {
            var marker = CreateMarkerUI();
            ReturnMarkerToPool(marker);
        }
    }

    private void RebuildAllMarkers()
    {
        // Clear existing
        foreach (var kv in trackedToMarker) { ReturnMarkerToPool(kv.Value); }
        trackedToMarker.Clear();
        foreach (var kv in waypointToMarker) { ReturnMarkerToPool(kv.Value); }
        waypointToMarker.Clear();
        foreach (var kv in waypointToArrow) { ReturnMarkerToPool(kv.Value); }
        waypointToArrow.Clear();

        // Recreate
        foreach (var to in trackedObjects)
        {
            if (to != null && to.target != null)
            {
                trackedToMarker[to] = CreateOrReuseMarkerForTracked(to);
            }
        }
        foreach (var wp in waypoints)
        {
            EnsureWaypointMarker(wp);
        }
    }

    private void UpdateAllMarkersImmediate()
    {
        UpdateMarkersRuntimeInternal(Time.deltaTime, immediate: true);
    }

    private void UpdateMarkersRuntime(float deltaTime)
    {
        UpdateMarkersRuntimeInternal(deltaTime, immediate: false);
    }

    private void UpdateMarkersRuntimeInternal(float deltaTime, bool immediate)
    {
        if (markerContainer == null) return;

        // Tracked objects markers
        foreach (var kv in trackedToMarker)
        {
            var tracked = kv.Key;
            var marker = kv.Value;
            if (tracked.target == null)
            {
                marker.gameObject.SetActive(false);
                continue;
            }

            Vector2 local = WorldToLocalUI(tracked.target.position);
            bool inside = IsInsideMask(local, out var limit);
            if (!inside)
            {
                // Tracked objects: clamp to edge rather than hide
                local = ClampToEdge(local, limit);
            }
            MoveMarker(marker, local, deltaTime, immediate);
        }

        // Waypoints markers + edge arrows
        foreach (var wp in waypoints)
        {
            // Lazy create in case added during play
            EnsureWaypointMarker(wp);
            var marker = waypointToMarker[wp];

            Vector3 worldPos = wp.useTransform && wp.targetTransform != null ? wp.targetTransform.position : wp.worldPosition;
            Vector2 local = WorldToLocalUI(worldPos);
            bool inside = IsInsideMask(local, out var limit);

            // Trigger reach logic
            if (!wp.reached && player != null)
            {
                var flatPlayer = player.position; flatPlayer.y = 0f;
                var flatWP = worldPos; flatWP.y = 0f;
                float dist = Vector3.Distance(flatPlayer, flatWP);
                if (dist <= wp.radius)
                {
                    wp.reached = true;
                    try { wp.onReach?.Invoke(); } catch (Exception) { }
                    if (enablePopups) ShowPopup(!string.IsNullOrEmpty(wp.label) ? $"Reached {wp.label}" : "Waypoint reached");
                }
            }

            if (inside)
            {
                // Show marker at local, hide edge arrow if any
                MoveMarker(marker, local, deltaTime, immediate);
                marker.gameObject.SetActive(true);
                if (waypointToArrow.TryGetValue(wp, out var arrow))
                {
                    arrow.gameObject.SetActive(false);
                }
            }
            else
            {
                // Hide center marker, show edge arrow if enabled
                marker.gameObject.SetActive(false);
                if (waypointEdgeArrows && wp.showEdgeArrow)
                {
                    var arrow = EnsureWaypointArrow(wp);
                    Vector2 edgePos = ClampToEdge(local, limit);
                    MoveMarker(arrow, edgePos, deltaTime, immediate);
                    // Our arrow sprite points UP by default; rotate so it faces the waypoint
                    float angle = Mathf.Atan2(local.y, local.x) * Mathf.Rad2Deg - 90f;
                    arrow.rect.localEulerAngles = new Vector3(0, 0, angle);
                    arrow.gameObject.SetActive(true);
                }
            }
        }
    }

    private Vector2 ClampToEdge(Vector2 local, float radius)
    {
        switch (mapShape)
        {
            case MapShape.Square:
            case MapShape.Custom:
            case MapShape.Star:
                // Treat Star/Custom as square bounds for clamping
                float half = radius;
                Vector2 clamped = local;
                float mx = half - 8f;
                float my = half - 8f;
                if (Mathf.Abs(clamped.x) * my > Mathf.Abs(clamped.y) * mx)
                {
                    // Hit left/right
                    clamped.x = Mathf.Clamp(clamped.x, -mx, mx);
                    clamped.y = Mathf.Sign(local.y) * (Mathf.Abs(clamped.x) * my / mx);
                }
                else
                {
                    // Hit top/bottom
                    clamped.y = Mathf.Clamp(clamped.y, -my, my);
                    clamped.x = Mathf.Sign(local.x) * (Mathf.Abs(clamped.y) * mx / my);
                }
                return clamped;
            case MapShape.Circle:
                float mag = local.magnitude;
                if (mag > 0.001f)
                {
                    float r = radius - 8f;
                    return local * (r / mag);
                }
                return new Vector2(radius - 8f, 0f);
            default:
                return local;
        }
    }

    private MarkerUI CreateOrReuseMarkerForTracked(TrackedObject tracked)
    {
        var marker = GetMarkerFromPool();
        marker.image.sprite = GetSpriteForShape(tracked.shape, tracked.customSprite);
        marker.image.color = tracked.color;
        marker.rect.sizeDelta = Vector2.one * Mathf.Max(2f, tracked.size);
        marker.label.text = string.Empty;
        marker.gameObject.name = tracked.target != null ? $"Tracked_{tracked.target.name}" : "Tracked";
        marker.gameObject.SetActive(true);
        return marker;
    }

    private void EnsureWaypointMarker(Waypoint wp)
    {
        if (!waypointToMarker.TryGetValue(wp, out var marker))
        {
            marker = GetMarkerFromPool();
            waypointToMarker[wp] = marker;
        }
        marker.image.sprite = GetSpriteForShape(MarkerShape.Circle, null);
        marker.image.color = wp.color;
        marker.rect.sizeDelta = Vector2.one * 10f;
        marker.label.text = string.IsNullOrEmpty(wp.label) ? string.Empty : wp.label;
        marker.gameObject.name = string.IsNullOrEmpty(wp.label) ? "Waypoint" : $"WP_{wp.label}";
        marker.gameObject.SetActive(true);
    }

    private MarkerUI EnsureWaypointArrow(Waypoint wp)
    {
        if (!waypointToArrow.TryGetValue(wp, out var arrow))
        {
            arrow = GetMarkerFromPool();
            waypointToArrow[wp] = arrow;
            arrow.image.sprite = cachedArrowSprite;
            arrow.image.color = wp.color;
            arrow.rect.sizeDelta = new Vector2(14f, 14f);
            arrow.label.text = string.Empty;
            arrow.gameObject.name = "WP_Arrow";
        }
        return arrow;
    }

    private void MoveMarker(MarkerUI marker, Vector2 targetLocal, float deltaTime, bool immediate)
    {
        if (immediate || markerSmoothing <= 0f)
        {
            marker.rect.anchoredPosition = targetLocal;
            return;
        }
        var current = marker.rect.anchoredPosition;
        var next = Vector2.Lerp(current, targetLocal, 1f - Mathf.Exp(-markerSmoothing * deltaTime));
        marker.rect.anchoredPosition = next;
    }

    // =============================
    // Popup
    // =============================
    private void ShowPopup(string message)
    {
        if (!enablePopups || popupRoot == null || popupText == null) return;
        popupText.text = message;
        popupRoot.gameObject.SetActive(true);
        popupHideTime = Time.unscaledTime + Mathf.Max(0.25f, popupDuration);
    }

    private void UpdatePopupRuntime()
    {
        if (!enablePopups || popupRoot == null) return;
        if (popupRoot.gameObject.activeSelf && Time.unscaledTime >= popupHideTime)
        {
            popupRoot.gameObject.SetActive(false);
        }
    }

    // =============================
    // Marker UI pool
    // =============================
    private MarkerUI CreateMarkerUI()
    {
        var go = new GameObject("Marker", typeof(RectTransform));
        go.transform.SetParent(markerContainer != null ? markerContainer : transform, false);
        var rect = go.GetComponent<RectTransform>();
        rect.anchorMin = rect.anchorMax = new Vector2(0.5f, 0.5f);
        rect.pivot = new Vector2(0.5f, 0.5f);
        rect.anchoredPosition = Vector2.zero;

        var img = go.AddComponent<Image>();
        img.raycastTarget = false;
        img.sprite = cachedCircleSprite;
        img.color = Color.white;

        var labelGo = new GameObject("Label", typeof(RectTransform));
        labelGo.transform.SetParent(go.transform, false);
        var labelRect = labelGo.GetComponent<RectTransform>();
        labelRect.anchorMin = new Vector2(0.5f, 0f);
        labelRect.anchorMax = new Vector2(0.5f, 0f);
        labelRect.pivot = new Vector2(0.5f, 1f);
        labelRect.anchoredPosition = new Vector2(0, -2f);
        labelRect.sizeDelta = new Vector2(80f, 18f);
        var text = labelGo.AddComponent<Text>();
        text.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
        text.color = Color.white;
        text.alignment = TextAnchor.UpperCenter;
        text.raycastTarget = false;
        text.fontSize = 12;
        text.horizontalOverflow = HorizontalWrapMode.Overflow;
        text.verticalOverflow = VerticalWrapMode.Overflow;

        return new MarkerUI
        {
            gameObject = go,
            rect = rect,
            image = img,
            label = text
        };
    }

    private MarkerUI GetMarkerFromPool()
    {
        for (int i = 0; i < markerPool.Count; i++)
        {
            if (!markerPool[i].gameObject.activeSelf)
            {
                var m = markerPool[i];
                m.gameObject.transform.SetParent(markerContainer, false);
                m.gameObject.SetActive(true);
                return m;
            }
        }
        var created = CreateMarkerUI();
        markerPool.Add(created);
        created.gameObject.transform.SetParent(markerContainer, false);
        created.gameObject.SetActive(true);
        return created;
    }

    private void ReturnMarkerToPool(MarkerUI marker)
    {
        if (marker == null) return;
        marker.gameObject.SetActive(false);
        marker.gameObject.transform.SetParent(minimapRoot, false);
    }

    private Sprite GetSpriteForShape(MarkerShape shape, Sprite custom)
    {
        switch (shape)
        {
            case MarkerShape.Square: return cachedSquareSprite;
            case MarkerShape.Circle: return cachedCircleSprite;
            case MarkerShape.Diamond: return cachedDiamondSprite;
            case MarkerShape.Star: return cachedStarSprite;
            case MarkerShape.Custom: return custom != null ? custom : cachedCircleSprite;
            default: return cachedCircleSprite;
        }
    }

    // =============================
    // Sprite generation helpers
    // =============================
    private static Sprite CreateSolidSprite(int width, int height, Color color)
    {
        var tex = new Texture2D(width, height, TextureFormat.ARGB32, false);
        var fill = new Color32[(int)(width * height)];
        var c32 = (Color32)color;
        for (int i = 0; i < fill.Length; i++) fill[i] = c32;
        tex.SetPixels32(fill);
        tex.Apply(false);
        return Sprite.Create(tex, new Rect(0, 0, width, height), new Vector2(0.5f, 0.5f), 100f);
    }

    private static Sprite CreateCircleSprite(int size)
    {
        var tex = new Texture2D(size, size, TextureFormat.ARGB32, false);
        int r = size / 2;
        int cx = r, cy = r;
        var white = new Color32(255, 255, 255, 255);
        var clear = new Color32(0, 0, 0, 0);
        for (int y = 0; y < size; y++)
        {
            for (int x = 0; x < size; x++)
            {
                int dx = x - cx;
                int dy = y - cy;
                tex.SetPixel(x, y, (dx * dx + dy * dy <= r * r) ? (Color)white : (Color)clear);
            }
        }
        tex.Apply(false);
        return Sprite.Create(tex, new Rect(0, 0, size, size), new Vector2(0.5f, 0.5f), 100f);
    }

    private static Sprite CreateDiamondSprite(int size)
    {
        var tex = new Texture2D(size, size, TextureFormat.ARGB32, false);
        int r = size / 2;
        int cx = r, cy = r;
        var white = new Color32(255, 255, 255, 255);
        var clear = new Color32(0, 0, 0, 0);
        for (int y = 0; y < size; y++)
        {
            for (int x = 0; x < size; x++)
            {
                int dx = Mathf.Abs(x - cx);
                int dy = Mathf.Abs(y - cy);
                tex.SetPixel(x, y, (dx + dy <= r) ? (Color)white : (Color)clear);
            }
        }
        tex.Apply(false);
        return Sprite.Create(tex, new Rect(0, 0, size, size), new Vector2(0.5f, 0.5f), 100f);
    }

    private static Sprite CreateStarSprite(int size)
    {
        // 5-point star via polygon fill
        var tex = new Texture2D(size, size, TextureFormat.ARGB32, false);
        var white = new Color32(255, 255, 255, 255);
        var clear = new Color32(0, 0, 0, 0);
        float cx = (size - 1) * 0.5f;
        float cy = (size - 1) * 0.5f;
        float outer = size * 0.48f;
        float inner = outer * 0.5f;
        var verts = new List<Vector2>();
        for (int i = 0; i < 10; i++)
        {
            float ang = (Mathf.PI / 2f) + i * (Mathf.PI * 2f / 10f);
            float r = (i % 2 == 0) ? outer : inner;
            verts.Add(new Vector2(cx + Mathf.Cos(ang) * r, cy + Mathf.Sin(ang) * r));
        }
        for (int y = 0; y < size; y++)
        {
            for (int x = 0; x < size; x++)
            {
                bool inside = PointInPolygon(new Vector2(x + 0.5f, y + 0.5f), verts);
                tex.SetPixel(x, y, inside ? (Color)white : (Color)clear);
            }
        }
        tex.Apply(false);
        return Sprite.Create(tex, new Rect(0, 0, size, size), new Vector2(0.5f, 0.5f), 100f);
    }

    private static bool PointInPolygon(Vector2 p, List<Vector2> verts)
    {
        // Ray casting
        bool inside = false;
        for (int i = 0, j = verts.Count - 1; i < verts.Count; j = i++)
        {
            var vi = verts[i];
            var vj = verts[j];
            bool intersect = ((vi.y > p.y) != (vj.y > p.y)) &&
                             (p.x < (vj.x - vi.x) * (p.y - vi.y) / (vj.y - vi.y + 1e-6f) + vi.x);
            if (intersect) inside = !inside;
        }
        return inside;
    }

    private static Sprite CreateArrowSprite(int width, int height)
    {
        var tex = new Texture2D(width, height, TextureFormat.ARGB32, false);
        var white = new Color32(255, 255, 255, 255);
        var clear = new Color32(0, 0, 0, 0);
        // Simple isosceles triangle pointing up
        Vector2 p0 = new Vector2(width * 0.5f, height * 0.95f);
        Vector2 p1 = new Vector2(width * 0.1f, height * 0.05f);
        Vector2 p2 = new Vector2(width * 0.9f, height * 0.05f);
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                bool inside = PointInTriangle(new Vector2(x + 0.5f, y + 0.5f), p0, p1, p2);
                tex.SetPixel(x, y, inside ? (Color)white : (Color)clear);
            }
        }
        tex.Apply(false);
        return Sprite.Create(tex, new Rect(0, 0, width, height), new Vector2(0.5f, 0.25f), 100f);
    }

    private static bool PointInTriangle(Vector2 p, Vector2 a, Vector2 b, Vector2 c)
    {
        float area = 0.5f * (-b.y * c.x + a.y * (-b.x + c.x) + a.x * (b.y - c.y) + b.x * c.y);
        float s = 1f / (2f * area) * (a.y * c.x - a.x * c.y + (c.y - a.y) * p.x + (a.x - c.x) * p.y);
        float t = 1f / (2f * area) * (a.x * b.y - a.y * b.x + (a.y - b.y) * p.x + (b.x - a.x) * p.y);
        float u = 1f - s - t;
        return s >= 0 && t >= 0 && u >= 0;
    }

    // =============================
    // Data types
    // =============================
    [Serializable]
    public class TrackedObject
    {
        public Transform target;
        public MarkerShape shape = MarkerShape.Circle;
        public Sprite customSprite;
        public Color color = Color.white;
        public float size = 8f;
    }

    [Serializable]
    public class Waypoint
    {
        public Transform targetTransform;
        public bool useTransform = false;
        public Vector3 worldPosition;
        public string label;
        public Color color = Color.yellow;
        public float radius = 2f;
        public bool showEdgeArrow = true;
        public bool reached = false;
        public UnityEvent onReach = new UnityEvent();
    }

    private class MarkerUI
    {
        public GameObject gameObject;
        public RectTransform rect;
        public Image image;
        public Text label;
    }

    public enum MapShape { Circle, Square, Star, Custom }
    public enum MarkerShape { Circle, Square, Diamond, Star, Custom }
    public enum Corner { TopLeft, TopRight, BottomLeft, BottomRight }
}

using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace Minimap
{
	/// <summary>
	/// Attach this single component to any GameObject to create a fully self-contained
	/// minimap system. It auto-creates its own Camera, Canvas, RenderTexture, UI, pooling,
	/// and exposes Inspector-first controls for player arrow, tracked objects, waypoints,
	/// map shapes/styles, alignment, and mission/tutorial popups.
	/// </summary>
	[DefaultExecutionOrder(-50)]
	public class MinimapSystem : MonoBehaviour
	{
		#region Types
		[Serializable]
		public enum MapShape
		{
			Circle,
			Square,
			Star,
			Custom
		}

		[Serializable]
		public enum MarkerShape
		{
			Circle,
			Square,
			Star,
			Arrow,
			Diamond,
			Triangle
		}

		[Serializable]
		public class PlayerArrowSettings
		{
			[Tooltip("Player transform whose orientation drives the arrow rotation and camera follow.")]
			public Transform player;

			[Tooltip("Arrow sprite for the player. If unset, a procedural arrow sprite is generated.")]
			public Sprite arrowSprite;

			[Tooltip("Arrow color.")]
			public Color color = new Color(1f, 1f, 1f, 1f);

			[Tooltip("Arrow size (UI units).")]
			public Vector2 size = new Vector2(28, 28);

			[Tooltip("If true, player arrow rotates with player's Y orientation (yaw). If false, stays north-up.")]
			public bool rotateWithPlayer = true;

			[Tooltip("Additional rotation offset in degrees applied to the arrow UI.")]
			public float rotationOffsetDegrees = 0f;
		}

		[Serializable]
		public class TrackedObjectEntry
		{
			[Tooltip("Name for Inspector clarity only.")]
			public string name;

			[Tooltip("World object to track on the minimap.")]
			public Transform target;

			[Tooltip("Marker shape (ignored if Custom Icon is provided).")]
			public MarkerShape shape = MarkerShape.Square;

			[Tooltip("Override with a custom sprite/icon. If set, Shape is ignored.")]
			public Sprite customIcon;

			[Tooltip("Marker color (tint applied to icon/sprite).")]
			public Color color = Color.yellow;

			[Tooltip("UI size for the marker.")]
			public Vector2 size = new Vector2(18, 18);

			[NonSerialized] public MarkerUI runtimeUI;
		}

		[Serializable]
		public class WaypointEntry
		{
			[Tooltip("Optional label shown next to the waypoint marker.")]
			public string label = "";

			[Tooltip("Assign a transform to follow (alternatively leave null and set World Position).")]
			public Transform target;

			[Tooltip("If true, uses Transform's position; otherwise uses World Position.")]
			public bool useTransform = true;

			[Tooltip("Static world position if Use Transform is false.")]
			public Vector3 worldPosition;

			[Tooltip("Marker shape (ignored if Custom Icon is provided).")]
			public MarkerShape shape = MarkerShape.Star;

			[Tooltip("Override with a custom sprite/icon. If set, Shape is ignored.")]
			public Sprite customIcon;

			[Tooltip("Marker color (tint applied to icon/sprite).")]
			public Color color = Color.cyan;

			[Tooltip("UI size for the waypoint.")]
			public Vector2 size = new Vector2(20, 20);

			[Tooltip("Radius in world units that triggers the waypoint event when the player enters.")]
			public float triggerRadius = 3f;

			[Tooltip("Invoke when waypoint is reached (player enters radius).")]
			public UnityEvent onReached;

			[Tooltip("If true, remove/hide the waypoint after it's reached.")]
			public bool removeOnReached = false;

			[NonSerialized] public bool hasFired;
			[NonSerialized] public MarkerUI runtimeUI;
			[NonSerialized] public MarkerUI runtimeEdgeArrowUI;
		}

		[Serializable]
		public class PopupSettings
		{
			[Tooltip("Enable built-in simple mission/tutorial popups.")]
			public bool enableBuiltInPopups = true;

			[Tooltip("Optional custom popup prefab with a Text and close Button; otherwise a default is created.")]
			public GameObject popupPrefab;

			[Tooltip("Default popup title text.")]
			public string defaultTitle = "Waypoint Reached";

			[Tooltip("Background color for the default popup.")]
			public Color backgroundColor = new Color(0, 0, 0, 0.85f);

			[Tooltip("Text color for the default popup.")]
			public Color textColor = Color.white;
		}

		private class MarkerUI
		{
			public GameObject gameObject;
			public RectTransform rectTransform;
			public Image image;
			public Text label;
			public Vector2 currentAnchoredPos;
			public Vector2 velocity;
		}
		#endregion

		#region Inspector
		[Header("Player Arrow")]
		public PlayerArrowSettings playerArrow = new PlayerArrowSettings();

		[Header("Tracked Objects")]
		[Tooltip("Add scene objects to display as static markers on the minimap.")]
		public List<TrackedObjectEntry> trackedObjects = new List<TrackedObjectEntry>();

		[Header("Waypoints")]
		[Tooltip("Add waypoints; can be transform-following or static world positions.")]
		public List<WaypointEntry> waypoints = new List<WaypointEntry>();

		[Header("Minimap Map & Style")]
		[Tooltip("Camera culling mask for the minimap render camera.")]
		public LayerMask minimapCullingMask = ~0;

		[Tooltip("Minimap camera orthographic size (half height in world units). Smaller = more zoomed in.")]
		[Min(1f)] public float cameraOrthographicSize = 75f;

		[Tooltip("If true, the minimap camera follows the player horizontally (XZ).")]
		public bool cameraFollowPlayer = true;

		[Tooltip("If true, the minimap UI rotates with player yaw (map rotates, arrow can be locked).")]
		public bool rotateMapWithPlayer = false;

		[Tooltip("Minimap shape for mask and border.")]
		public MapShape mapShape = MapShape.Circle;

		[Tooltip("Custom mask sprite when Map Shape is Custom.")]
		public Sprite customMapMaskSprite;

		[Tooltip("Minimap size in UI units (width x height).")]
		public Vector2 minimapSize = new Vector2(256, 256);

		[Tooltip("Minimap anchored position in the Canvas. Top-right default (-20, -20) means 20px from top-right.")]
		public Vector2 minimapAnchoredPosition = new Vector2(-20, -20);

		[Tooltip("Background color and opacity behind the minimap render.")]
		public Color backgroundColor = new Color(0, 0, 0, 0.35f);

		[Tooltip("Border color.")]
		public Color borderColor = new Color(1, 1, 1, 0.9f);

		[Tooltip("Border thickness in UI units.")]
		[Min(0f)] public float borderThickness = 4f;

		[Header("Alignment & World Mapping")]
		[Tooltip("Additional world offset applied to all world->minimap projections.")]
		public Vector3 worldOffset;

		[Tooltip("Fine-tune UI alignment scaling multiplier (1 = camera exact).")]
		public float uiScaleFine = 1f;

		[Tooltip("Auto-fit the minimap camera to active terrain bounds (if any) on Start.")]
		public bool autoFitToTerrain = false;

		[Header("Runtime Interaction")]
		[Tooltip("Enable clicking on the minimap to create waypoints at clicked world positions.")]
		public bool clickToCreateWaypoint = true;

		[Tooltip("Default label for click-created waypoints.")]
		public string clickWaypointLabel = "Waypoint";

		[Tooltip("Smoothing time for marker UI movement (seconds). 0 = no smoothing.")]
		[Min(0f)] public float markerSmoothTime = 0.07f;

		[Tooltip("Maximum pool size for marker UI elements.")]
		[Min(8)] public int markerPoolCapacity = 64;

		[Header("Popups (Built-In)")]
		public PopupSettings popups = new PopupSettings();
		#endregion

		#region Private State
		// Core objects
		private Camera _minimapCamera;
		private RenderTexture _renderTexture;
		private Canvas _canvas;
		private RectTransform _minimapRoot;
		private RawImage _minimapImage;
		private RectTransform _maskContainer;
		private Image _maskImage;
		private RectTransform _markersContainer;
		private MarkerUI _playerArrowUI;

		// Pools
		private readonly Queue<MarkerUI> _markerPool = new Queue<MarkerUI>();
		private readonly List<MarkerUI> _activeMarkers = new List<MarkerUI>();

		// Generated sprites cache
		private Sprite _generatedArrowSprite;
		private Sprite _generatedCircleSprite;
		private Sprite _generatedSquareSprite;
		private Sprite _generatedStarSprite;
		private Sprite _generatedDiamondSprite;
		private Sprite _generatedTriangleSprite;

		// Popup UI
		private RectTransform _popupRoot;
		private GameObject _popupInstance;
		private Text _popupText;

		// Reusable buffers
		private readonly List<TrackedObjectEntry> _trackedBuffer = new List<TrackedObjectEntry>();
		private readonly List<WaypointEntry> _waypointsBuffer = new List<WaypointEntry>();
		#endregion

		#region Unity Lifecycle
		private void Awake()
		{
			EnsureEventSystemExists();
			BuildGeneratedSprites();
			EnsureCanvasAndUI();
			EnsureMinimapCamera();
			EnsurePlayerArrow();
			EnsurePopupUI();
		}

		private void Start()
		{
			if (autoFitToTerrain)
			{
				AutoFitCameraToTerrain();
			}
		}

		private void OnDestroy()
		{
			if (_renderTexture != null)
			{
				if (_minimapImage != null)
				{
					_minimapImage.texture = null;
				}
				_renderTexture.Release();
				Destroy(_renderTexture);
			}
		}

		private void Update()
		{
			UpdateCameraFollowAndRotation();
			UpdatePlayerArrow();
			UpdateTrackedObjects();
			UpdateWaypoints();
			HandleRuntimeClick();
		}
		#endregion

		#region Public API
		/// <summary>
		/// Creates a waypoint at the world position or transform with the provided settings.
		/// </summary>
		public WaypointEntry CreateWaypoint(Vector3 worldPosition, string label = null, Color? color = null)
		{
			var wp = new WaypointEntry
			{
				useTransform = false,
				worldPosition = worldPosition,
				label = string.IsNullOrEmpty(label) ? clickWaypointLabel : label,
				color = color ?? Color.cyan,
				shape = MarkerShape.Star,
				size = new Vector2(20, 20),
				triggerRadius = 3f
			};
			waypoints.Add(wp);
			return wp;
		}

		/// <summary>
		/// Removes a waypoint instance from the list and despawns its UI.
		/// </summary>
		public void RemoveWaypoint(WaypointEntry waypoint)
		{
			if (waypoints.Remove(waypoint))
			{
				DespawnMarkerUI(waypoint.runtimeUI);
				DespawnMarkerUI(waypoint.runtimeEdgeArrowUI);
			}
		}
		#endregion

		#region Build & Ensure
		private void EnsureEventSystemExists()
		{
			if (FindObjectOfType<EventSystem>() == null)
			{
				var es = new GameObject("EventSystem", typeof(EventSystem));
				es.AddComponent<StandaloneInputModule>();
			}
		}

		private void BuildGeneratedSprites()
		{
			_generatedArrowSprite = ProceduralSpriteFactory.GenerateArrowSprite(64, 64, Color.white);
			_generatedCircleSprite = ProceduralSpriteFactory.GenerateCircleSprite(64, 64, Color.white);
			_generatedSquareSprite = ProceduralSpriteFactory.GenerateSquareSprite(64, 64, Color.white);
			_generatedStarSprite = ProceduralSpriteFactory.GenerateStarSprite(64, 64, 5, 0.5f, Color.white);
			_generatedDiamondSprite = ProceduralSpriteFactory.GenerateDiamondSprite(64, 64, Color.white);
			_generatedTriangleSprite = ProceduralSpriteFactory.GenerateTriangleSprite(64, 64, Color.white);
		}

		private void EnsureCanvasAndUI()
		{
			var canvasGO = new GameObject("MinimapCanvas", typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
			_canvas = canvasGO.GetComponent<Canvas>();
			_canvas.renderMode = RenderMode.ScreenSpaceOverlay;
			var scaler = canvasGO.GetComponent<CanvasScaler>();
			scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
			scaler.referenceResolution = new Vector2(1920, 1080);

			// Root container
			var rootGO = new GameObject("Minimap_Root", typeof(RectTransform));
			rootGO.transform.SetParent(_canvas.transform, false);
			_minimapRoot = rootGO.GetComponent<RectTransform>();
			_minimapRoot.sizeDelta = minimapSize;
			AnchorTopRight(_minimapRoot, minimapAnchoredPosition);

			// Background panel (acts as border fill color)
			var bgGO = new GameObject("Minimap_Background", typeof(RectTransform), typeof(Image));
			bgGO.transform.SetParent(_minimapRoot, false);
			var bgRT = bgGO.GetComponent<RectTransform>();
			bgRT.anchorMin = new Vector2(0, 0);
			bgRT.anchorMax = new Vector2(1, 1);
			bgRT.offsetMin = Vector2.zero;
			bgRT.offsetMax = Vector2.zero;
			var bgImage = bgGO.GetComponent<Image>();
			bgImage.color = borderColor;

			// Inner panel (actual map background), inset by border thickness
			var innerGO = new GameObject("Minimap_Inner", typeof(RectTransform), typeof(Image));
			innerGO.transform.SetParent(_minimapRoot, false);
			var innerRT = innerGO.GetComponent<RectTransform>();
			innerRT.anchorMin = new Vector2(0, 0);
			innerRT.anchorMax = new Vector2(1, 1);
			innerRT.offsetMin = new Vector2(borderThickness, borderThickness);
			innerRT.offsetMax = new Vector2(-borderThickness, -borderThickness);
			var innerImage = innerGO.GetComponent<Image>();
			innerImage.color = backgroundColor;

			// Mask container + mask image
			var maskGO = new GameObject("Minimap_Mask", typeof(RectTransform), typeof(Image));
			maskGO.transform.SetParent(innerRT, false);
			_maskContainer = maskGO.GetComponent<RectTransform>();
			_maskContainer.anchorMin = new Vector2(0, 0);
			_maskContainer.anchorMax = new Vector2(1, 1);
			_maskContainer.offsetMin = Vector2.zero;
			_maskContainer.offsetMax = Vector2.zero;
			_maskImage = maskGO.GetComponent<Image>();
			_maskImage.raycastTarget = true; // captures clicks
			ApplyMaskShape();

			// RawImage to display the minimap RenderTexture
			var mapGO = new GameObject("Minimap_Image", typeof(RectTransform), typeof(RawImage));
			mapGO.transform.SetParent(_maskContainer, false);
			var mapRT = mapGO.GetComponent<RectTransform>();
			mapRT.anchorMin = new Vector2(0, 0);
			mapRT.anchorMax = new Vector2(1, 1);
			mapRT.offsetMin = Vector2.zero;
			mapRT.offsetMax = Vector2.zero;
			_minimapImage = mapGO.GetComponent<RawImage>();
			_minimapImage.raycastTarget = false; // clicks captured by mask

			// Markers container (clipped by mask)
			var markersGO = new GameObject("Minimap_Markers", typeof(RectTransform));
			markersGO.transform.SetParent(_maskContainer, false);
			_markersContainer = markersGO.GetComponent<RectTransform>();
			_markersContainer.anchorMin = new Vector2(0, 0);
			_markersContainer.anchorMax = new Vector2(1, 1);
			_markersContainer.offsetMin = Vector2.zero;
			_markersContainer.offsetMax = Vector2.zero;
		}

		private void EnsureMinimapCamera()
		{
			var camGO = new GameObject("Minimap_Camera", typeof(Camera));
			camGO.transform.SetParent(transform, false);
			_minimapCamera = camGO.GetComponent<Camera>();
			_minimapCamera.orthographic = true;
			_minimapCamera.orthographicSize = cameraOrthographicSize;
			_minimapCamera.clearFlags = CameraClearFlags.SolidColor;
			_minimapCamera.backgroundColor = new Color(0, 0, 0, 0);
			_minimapCamera.cullingMask = minimapCullingMask;
			_minimapCamera.allowMSAA = false;
			_minimapCamera.allowHDR = false;
			_minimapCamera.useOcclusionCulling = false;
			_minimapCamera.depth = -100;
			_minimapCamera.transform.rotation = Quaternion.Euler(90f, 0f, 0f);
			_minimapCamera.nearClipPlane = 0.1f;
			_minimapCamera.farClipPlane = 5000f;
			_minimapCamera.transform.position = new Vector3(0f, 500f, 0f);

			int texSize = Mathf.NextPowerOfTwo(Mathf.RoundToInt(Mathf.Max(minimapSize.x, minimapSize.y)));
			texSize = Mathf.Clamp(texSize, 256, 2048);
			_renderTexture = new RenderTexture(texSize, texSize, 16, RenderTextureFormat.ARGB32);
			_renderTexture.name = "Minimap_RT";
			_renderTexture.Create();
			_minimapCamera.targetTexture = _renderTexture;
			_minimapImage.texture = _renderTexture;
		}

		private void EnsurePlayerArrow()
		{
			_playerArrowUI = SpawnMarkerUI(_markersContainer, "PlayerArrow", playerArrow.arrowSprite != null ? playerArrow.arrowSprite : _generatedArrowSprite, playerArrow.color, playerArrow.size, hasLabel: false);
		}

		private void EnsurePopupUI()
		{
			var popupRootGO = new GameObject("Minimap_PopupRoot", typeof(RectTransform));
			popupRootGO.transform.SetParent(_canvas.transform, false);
			_popupRoot = popupRootGO.GetComponent<RectTransform>();
			_popupRoot.anchorMin = new Vector2(0.5f, 0.5f);
			_popupRoot.anchorMax = new Vector2(0.5f, 0.5f);
			_popupRoot.sizeDelta = new Vector2(480, 160);
			_popupRoot.anchoredPosition = Vector2.zero;
		}
		#endregion

		#region Updates
		private void UpdateCameraFollowAndRotation()
		{
			if (_minimapCamera == null)
				return;

			Vector3 center = _minimapCamera.transform.position;
			if (cameraFollowPlayer && playerArrow.player != null)
			{
				center.x = playerArrow.player.position.x + worldOffset.x;
				center.z = playerArrow.player.position.z + worldOffset.z;
			}
			_minimapCamera.transform.position = center;

			if (rotateMapWithPlayer && playerArrow.player != null)
			{
				float yaw = GetYawDegrees(playerArrow.player);
				_minimapCamera.transform.rotation = Quaternion.Euler(90f, yaw, 0f);
			}
			else
			{
				_minimapCamera.transform.rotation = Quaternion.Euler(90f, 0f, 0f);
			}
		}

		private void UpdatePlayerArrow()
		{
			if (_playerArrowUI == null)
				return;

			_playerArrowUI.rectTransform.anchoredPosition = Vector2.zero;
			_playerArrowUI.rectTransform.sizeDelta = playerArrow.size;
			_playerArrowUI.image.color = playerArrow.color;

			if (playerArrow.arrowSprite != null)
			{
				_playerArrowUI.image.sprite = playerArrow.arrowSprite;
			}

			float targetRotation = 0f;
			if (playerArrow.rotateWithPlayer && playerArrow.player != null)
			{
				// Arrow rotates with player's yaw; if map also rotates with player, arrow can stay north-up by subtracting yaw
				float yaw = GetYawDegrees(playerArrow.player);
				targetRotation = rotateMapWithPlayer ? 0f : yaw;
			}
			_playerArrowUI.rectTransform.localRotation = Quaternion.Euler(0, 0, -targetRotation + playerArrow.rotationOffsetDegrees);
		}

		private void UpdateTrackedObjects()
		{
			_trackedBuffer.Clear();
			_trackedBuffer.AddRange(trackedObjects);

			foreach (var entry in _trackedBuffer)
			{
				if (entry == null || entry.target == null)
				{
					DespawnMarkerUI(entry?.runtimeUI);
					continue;
				}

				var sprite = entry.customIcon != null ? entry.customIcon : GetShapeSprite(entry.shape);
				if (entry.runtimeUI == null)
				{
					entry.runtimeUI = SpawnMarkerUI(_markersContainer, $"Tracked_{entry.name}", sprite, entry.color, entry.size, hasLabel: false);
				}
				else
				{
					entry.runtimeUI.image.sprite = sprite;
				}
				entry.runtimeUI.image.color = entry.color;
				entry.runtimeUI.rectTransform.sizeDelta = entry.size;

				Vector2 targetPos = WorldToMinimapAnchoredPosition(entry.target.position);
				MoveMarkerSmooth(entry.runtimeUI, targetPos, markerSmoothTime);
			}
		}

		private void UpdateWaypoints()
		{
			_waypointsBuffer.Clear();
			_waypointsBuffer.AddRange(waypoints);

			for (int i = 0; i < _waypointsBuffer.Count; i++)
			{
				var wp = _waypointsBuffer[i];
				if (wp == null)
					continue;

				Vector3 worldPos = wp.useTransform && wp.target != null ? wp.target.position : wp.worldPosition;
				var sprite = wp.customIcon != null ? wp.customIcon : GetShapeSprite(wp.shape);
				bool newUI = false;
				if (wp.runtimeUI == null)
				{
					wp.runtimeUI = SpawnMarkerUI(_markersContainer, $"Waypoint_{wp.label}", sprite, wp.color, wp.size, hasLabel: !string.IsNullOrWhiteSpace(wp.label));
					newUI = true;
				}
				else
				{
					wp.runtimeUI.image.sprite = sprite;
				}
				wp.runtimeUI.image.color = wp.color;
				wp.runtimeUI.rectTransform.sizeDelta = wp.size;
				if (wp.runtimeUI.label != null)
				{
					wp.runtimeUI.label.text = wp.label;
				}

				Vector2 targetPos = WorldToMinimapAnchoredPosition(worldPos);
				MoveMarkerSmooth(wp.runtimeUI, targetPos, newUI ? 0f : markerSmoothTime);

				UpdateWaypointEdgeArrow(wp, targetPos);
				CheckWaypointTrigger(wp, worldPos);
			}
		}
		#endregion

		#region Helpers - UI Creation
		private void AnchorTopRight(RectTransform rt, Vector2 anchored)
		{
			rt.anchorMin = new Vector2(1, 1);
			rt.anchorMax = new Vector2(1, 1);
			rt.pivot = new Vector2(1, 1);
			rt.anchoredPosition = anchored;
		}

		private void ApplyMaskShape()
		{
			// Remove existing mask components
			var existingMask = _maskContainer.GetComponent<Mask>();
			if (existingMask != null) Destroy(existingMask);
			var rectMask = _maskContainer.GetComponent<RectMask2D>();
			if (rectMask != null) Destroy(rectMask);

			switch (mapShape)
			{
				case MapShape.Circle:
					_maskImage.sprite = _generatedCircleSprite;
					_maskContainer.gameObject.AddComponent<Mask>().showMaskGraphic = false;
					break;
				case MapShape.Square:
					_maskImage.sprite = _generatedSquareSprite;
					_maskContainer.gameObject.AddComponent<RectMask2D>();
					break;
				case MapShape.Star:
					_maskImage.sprite = _generatedStarSprite;
					_maskContainer.gameObject.AddComponent<Mask>().showMaskGraphic = false;
					break;
				case MapShape.Custom:
					_maskImage.sprite = customMapMaskSprite != null ? customMapMaskSprite : _generatedSquareSprite;
					_maskContainer.gameObject.AddComponent<Mask>().showMaskGraphic = false;
					break;
			}
			_maskImage.type = Image.Type.Simple;
			_maskImage.color = Color.white;
		}

		private void ApplyBorderMaterial(Image borderImage)
		{
			// Border image uses the same sprite as mask for visual coherence
			borderImage.sprite = GetMaskSpriteForBorder();
			borderImage.type = Image.Type.Simple;
			borderImage.pixelsPerUnitMultiplier = 1f;
		}

		private Sprite GetMaskSpriteForBorder()
		{
			switch (mapShape)
			{
				case MapShape.Circle: return _generatedCircleSprite;
				case MapShape.Square: return _generatedSquareSprite;
				case MapShape.Star: return _generatedStarSprite;
				case MapShape.Custom: return customMapMaskSprite != null ? customMapMaskSprite : _generatedSquareSprite;
			}
			return _generatedSquareSprite;
		}

		private MarkerUI SpawnMarkerUI(RectTransform parent, string name, Sprite sprite, Color color, Vector2 size, bool hasLabel)
		{
			MarkerUI ui = (_markerPool.Count > 0) ? _markerPool.Dequeue() : CreateMarkerUIGameObject(parent);
			_activeMarkers.Add(ui);
			ui.gameObject.name = name;
			ui.image.sprite = sprite;
			ui.image.color = color;
			ui.rectTransform.sizeDelta = size;
			ui.rectTransform.anchoredPosition = Vector2.zero;
			ui.currentAnchoredPos = Vector2.zero;
			ui.velocity = Vector2.zero;
			ui.gameObject.SetActive(true);

			if (ui.label != null)
			{
				ui.label.gameObject.SetActive(hasLabel);
			}

			return ui;
		}

		private MarkerUI CreateMarkerUIGameObject(Transform parent)
		{
			var go = new GameObject("Marker", typeof(RectTransform), typeof(Image));
			go.transform.SetParent(parent, false);
			var rt = go.GetComponent<RectTransform>();
			rt.anchorMin = new Vector2(0.5f, 0.5f);
			rt.anchorMax = new Vector2(0.5f, 0.5f);
			rt.pivot = new Vector2(0.5f, 0.5f);
			var img = go.GetComponent<Image>();
			img.raycastTarget = false;

			// Optional label as a child
			var labelGO = new GameObject("Label", typeof(RectTransform), typeof(Text));
			labelGO.transform.SetParent(go.transform, false);
			var lrt = labelGO.GetComponent<RectTransform>();
			lrt.anchorMin = new Vector2(0.5f, 0);
			lrt.anchorMax = new Vector2(0.5f, 0);
			lrt.pivot = new Vector2(0.5f, 1f);
			lrt.anchoredPosition = new Vector2(0, -14);
			var text = labelGO.GetComponent<Text>();
			text.text = "";
			text.alignment = TextAnchor.UpperCenter;
			text.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
			text.color = Color.white;
			text.fontSize = 14;
			text.raycastTarget = false;
			labelGO.SetActive(false);

			return new MarkerUI
			{
				gameObject = go,
				rectTransform = rt,
				image = img,
				label = text
			};
		}

		private void DespawnMarkerUI(MarkerUI ui)
		{
			if (ui == null)
				return;
			if (_activeMarkers.Contains(ui))
				_activeMarkers.Remove(ui);
			if (_markerPool.Count < markerPoolCapacity)
			{
				ui.gameObject.SetActive(false);
				_markerPool.Enqueue(ui);
			}
			else
			{
				Destroy(ui.gameObject);
			}
		}
		#endregion

		#region Helpers - Math & Movement
		private float GetYawDegrees(Transform t)
		{
			Vector3 forward = t.forward;
			forward.y = 0f;
			forward.Normalize();
			if (forward.sqrMagnitude <= 0.0001f)
				return 0f;
			float yaw = Mathf.Atan2(forward.x, forward.z) * Mathf.Rad2Deg;
			return yaw;
		}

		private Vector2 WorldToMinimapAnchoredPosition(Vector3 world)
		{
			if (_minimapCamera == null || _minimapRoot == null)
				return Vector2.zero;

			Vector3 center = _minimapCamera.transform.position;
			Vector3 delta = world + worldOffset - new Vector3(center.x, 0, center.z);

			float halfHeightWorld = _minimapCamera.orthographicSize;
			float halfWidthWorld = halfHeightWorld * _minimapCamera.aspect;

			Rect rect = _maskContainer.rect;
			float halfHeightUI = rect.height * 0.5f;
			float halfWidthUI = rect.width * 0.5f;

			float uiPerWorldX = (halfWidthUI / Mathf.Max(halfWidthWorld, 0.0001f)) * uiScaleFine;
			float uiPerWorldY = (halfHeightUI / Mathf.Max(halfHeightWorld, 0.0001f)) * uiScaleFine;

			Vector2 ui = new Vector2(delta.x * uiPerWorldX, delta.z * uiPerWorldY);
			if (rotateMapWithPlayer && playerArrow.player != null)
			{
				float yaw = GetYawDegrees(playerArrow.player);
				float rad = -yaw * Mathf.Deg2Rad;
				float cos = Mathf.Cos(rad);
				float sin = Mathf.Sin(rad);
				ui = new Vector2(ui.x * cos - ui.y * sin, ui.x * sin + ui.y * cos);
			}
			return ui;
		}

		private Vector3 MinimapLocalToWorld(Vector2 local)
		{
			// Inverse of WorldToMinimapAnchoredPosition
			if (_minimapCamera == null)
				return Vector3.zero;

			float halfHeightWorld = _minimapCamera.orthographicSize;
			float halfWidthWorld = halfHeightWorld * _minimapCamera.aspect;
			Rect rect = _maskContainer.rect;
			float halfHeightUI = rect.height * 0.5f;
			float halfWidthUI = rect.width * 0.5f;

			float worldPerUIX = (halfWidthWorld / Mathf.Max(halfWidthUI, 0.0001f)) / Mathf.Max(uiScaleFine, 0.0001f);
			float worldPerUIY = (halfHeightWorld / Mathf.Max(halfHeightUI, 0.0001f)) / Mathf.Max(uiScaleFine, 0.0001f);

			Vector2 ui = local;
			if (rotateMapWithPlayer && playerArrow.player != null)
			{
				float yaw = GetYawDegrees(playerArrow.player);
				float rad = yaw * Mathf.Deg2Rad; // inverse rotation
				float cos = Mathf.Cos(rad);
				float sin = Mathf.Sin(rad);
				ui = new Vector2(ui.x * cos - ui.y * sin, ui.x * sin + ui.y * cos);
			}

			Vector3 center = _minimapCamera.transform.position;
			Vector3 world = new Vector3(
				center.x + ui.x * worldPerUIX - worldOffset.x,
				0f,
				center.z + ui.y * worldPerUIY - worldOffset.z
			);
			return world;
		}

		private void MoveMarkerSmooth(MarkerUI ui, Vector2 targetAnchored, float smoothTime)
		{
			if (smoothTime <= 0f)
			{
				ui.currentAnchoredPos = targetAnchored;
			}
			else
			{
				ui.currentAnchoredPos = Vector2.SmoothDamp(ui.currentAnchoredPos, targetAnchored, ref ui.velocity, smoothTime, Mathf.Infinity, Time.unscaledDeltaTime);
			}
			ui.rectTransform.anchoredPosition = ui.currentAnchoredPos;
		}
		#endregion

		#region Waypoint Logic
		private void UpdateWaypointEdgeArrow(WaypointEntry wp, Vector2 anchoredPos)
		{
			bool isInside = IsInsideMask(anchoredPos);
			if (isInside)
			{
				DespawnMarkerUI(wp.runtimeEdgeArrowUI);
				wp.runtimeEdgeArrowUI = null;
				return;
			}

			if (wp.runtimeEdgeArrowUI == null)
			{
				wp.runtimeEdgeArrowUI = SpawnMarkerUI(_markersContainer, $"WaypointArrow_{wp.label}", _generatedArrowSprite, wp.color, new Vector2(18, 18), hasLabel: false);
			}

			Vector2 edgePos;
			float angleDeg;
			ComputeEdgePositionAndAngle(anchoredPos, out edgePos, out angleDeg);
			wp.runtimeEdgeArrowUI.rectTransform.anchoredPosition = edgePos;
			wp.runtimeEdgeArrowUI.rectTransform.localRotation = Quaternion.Euler(0, 0, -angleDeg);
			wp.runtimeEdgeArrowUI.image.color = wp.color;
		}

		private bool IsInsideMask(Vector2 anchored)
		{
			Rect rect = _maskContainer.rect;
			float halfW = rect.width * 0.5f;
			float halfH = rect.height * 0.5f;

			switch (mapShape)
			{
				case MapShape.Square:
					return Mathf.Abs(anchored.x) <= halfW && Mathf.Abs(anchored.y) <= halfH;
				case MapShape.Circle:
					float radius = Mathf.Min(halfW, halfH);
					return anchored.sqrMagnitude <= radius * radius;
				case MapShape.Star:
					// Approximate: use inscribed circle for inside test
					float r = Mathf.Min(halfW, halfH) * 0.9f;
					return anchored.sqrMagnitude <= r * r;
				case MapShape.Custom:
					// Fallback square bounds
					return Mathf.Abs(anchored.x) <= halfW && Mathf.Abs(anchored.y) <= halfH;
			}
			return true;
		}

		private void ComputeEdgePositionAndAngle(Vector2 anchored, out Vector2 edgePos, out float angleDeg)
		{
			Rect rect = _maskContainer.rect;
			float halfW = rect.width * 0.5f;
			float halfH = rect.height * 0.5f;

			Vector2 dir = anchored.normalized;
			angleDeg = Mathf.Atan2(dir.y, dir.x) * Mathf.Rad2Deg - 90f; // arrow points up by default

			switch (mapShape)
			{
				case MapShape.Square:
					// Clamp to rectangle edge
					float tX = halfW / Mathf.Max(Mathf.Abs(dir.x), 0.0001f);
					float tY = halfH / Mathf.Max(Mathf.Abs(dir.y), 0.0001f);
					float t = Mathf.Min(tX, tY);
					edgePos = dir * t;
					break;
				case MapShape.Circle:
					float radius = Mathf.Min(halfW, halfH);
					edgePos = dir * radius;
					break;
				case MapShape.Star:
					float r = Mathf.Min(halfW, halfH) * 0.92f;
					edgePos = dir * r;
					break;
				case MapShape.Custom:
					// Approximate with rectangle bounds
					float tx = halfW / Mathf.Max(Mathf.Abs(dir.x), 0.0001f);
					float ty = halfH / Mathf.Max(Mathf.Abs(dir.y), 0.0001f);
					float tt = Mathf.Min(tx, ty);
					edgePos = dir * tt;
					break;
				default:
					edgePos = dir * halfW;
					break;
			}
		}

		private void CheckWaypointTrigger(WaypointEntry wp, Vector3 worldPos)
		{
			if (wp.hasFired || playerArrow.player == null)
				return;

			Vector3 playerPos = playerArrow.player.position;
			playerPos.y = 0f;
			worldPos.y = 0f;
			float dist = Vector3.Distance(playerPos, worldPos);
			if (dist <= wp.triggerRadius)
			{
				wp.hasFired = true;
				wp.onReached?.Invoke();
				if (popups.enableBuiltInPopups)
				{
					ShowPopup(string.IsNullOrEmpty(wp.label) ? popups.defaultTitle : wp.label);
				}
				if (wp.removeOnReached)
				{
					RemoveWaypoint(wp);
				}
			}
		}
		#endregion

		#region Popups
		private void ShowPopup(string message)
		{
			if (!popups.enableBuiltInPopups)
				return;

			if (_popupInstance == null)
			{
				if (popups.popupPrefab != null)
				{
					_popupInstance = Instantiate(popups.popupPrefab, _popupRoot);
					_popupInstance.name = "Minimap_PopupInstance";
					_popupText = _popupInstance.GetComponentInChildren<Text>();
				}
				else
				{
					// Build a simple popup
					var panel = new GameObject("PopupPanel", typeof(RectTransform), typeof(Image));
					panel.transform.SetParent(_popupRoot, false);
					var prt = panel.GetComponent<RectTransform>();
					prt.anchorMin = new Vector2(0, 0);
					prt.anchorMax = new Vector2(1, 1);
					prt.offsetMin = Vector2.zero;
					prt.offsetMax = Vector2.zero;
					var pimg = panel.GetComponent<Image>();
					pimg.color = popups.backgroundColor;

					var textGO = new GameObject("Text", typeof(RectTransform), typeof(Text));
					textGO.transform.SetParent(panel.transform, false);
					var trt = textGO.GetComponent<RectTransform>();
					trt.anchorMin = new Vector2(0.08f, 0.2f);
					trt.anchorMax = new Vector2(0.92f, 0.8f);
					trt.offsetMin = Vector2.zero;
					trt.offsetMax = Vector2.zero;
					_popupText = textGO.GetComponent<Text>();
					_popupText.text = "";
					_popupText.alignment = TextAnchor.MiddleCenter;
					_popupText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
					_popupText.color = popups.textColor;
					_popupText.fontSize = 24;

					var closeGO = new GameObject("CloseButton", typeof(RectTransform), typeof(Image), typeof(Button));
					closeGO.transform.SetParent(panel.transform, false);
					var crt = closeGO.GetComponent<RectTransform>();
					crt.anchorMin = new Vector2(0.5f, 0f);
					crt.anchorMax = new Vector2(0.5f, 0f);
					crt.sizeDelta = new Vector2(120, 36);
					crt.anchoredPosition = new Vector2(0, 18);
					var cimg = closeGO.GetComponent<Image>();
					cimg.color = new Color(1, 1, 1, 0.2f);
					var cbtn = closeGO.GetComponent<Button>();
					cbtn.onClick.AddListener(() => { _popupInstance.SetActive(false); });

					var ctextGO = new GameObject("Text", typeof(RectTransform), typeof(Text));
					ctextGO.transform.SetParent(closeGO.transform, false);
					var ctrt = ctextGO.GetComponent<RectTransform>();
					ctrt.anchorMin = new Vector2(0, 0);
					ctrt.anchorMax = new Vector2(1, 1);
					ctrt.offsetMin = Vector2.zero;
					ctrt.offsetMax = Vector2.zero;
					var ctext = ctextGO.GetComponent<Text>();
					ctext.text = "Close";
					ctext.alignment = TextAnchor.MiddleCenter;
					ctext.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
					ctext.color = Color.white;
					ctext.fontSize = 18;

					_popupInstance = panel;
				}
			}

			_popupText.text = message;
			_popupInstance.SetActive(true);
		}
		#endregion

		#region Click Handling
		public void HandleMinimapClick(Vector2 screenPosition, Camera eventCamera)
		{
			if (!clickToCreateWaypoint)
				return;

			if (!RectTransformUtility.ScreenPointToLocalPointInRectangle(_maskContainer, screenPosition, eventCamera, out var local))
				return;

			if (!IsInsideMask(local))
				return;

			Vector3 world = MinimapLocalToWorld(local);
			CreateWaypoint(world, clickWaypointLabel, Color.cyan);
		}

		private void HandleRuntimeClick()
		{
			if (!clickToCreateWaypoint)
				return;
			if (!Input.GetMouseButtonDown(0))
				return;
			var screen = (Vector2)Input.mousePosition;
			if (!RectTransformUtility.RectangleContainsScreenPoint(_maskContainer, screen))
				return;
			HandleMinimapClick(screen, null);
		}
		#endregion

		#region Terrain Auto-Fit
		[ContextMenu("Auto-Fit Minimap Camera To Terrain")]
		public void AutoFitCameraToTerrain()
		{
			Terrain t = Terrain.activeTerrain;
			if (t == null)
				return;

			Vector3 size = t.terrainData.size;
			Vector3 center = t.transform.position + size * 0.5f;
			_minimapCamera.transform.position = new Vector3(center.x, _minimapCamera.transform.position.y, center.z);

			// Fit the longer side to orthographic size
			float aspect = _minimapCamera.aspect;
			float halfHeight = Mathf.Max(size.x / (2f * aspect), size.z / 2f);
			_minimapCamera.orthographicSize = halfHeight;
		}
		#endregion

		#region Sprites Factory
		private Sprite GetShapeSprite(MarkerShape shape)
		{
			switch (shape)
			{
				case MarkerShape.Circle: return _generatedCircleSprite;
				case MarkerShape.Square: return _generatedSquareSprite;
				case MarkerShape.Star: return _generatedStarSprite;
				case MarkerShape.Arrow: return _generatedArrowSprite;
				case MarkerShape.Diamond: return _generatedDiamondSprite;
				case MarkerShape.Triangle: return _generatedTriangleSprite;
			}
			return _generatedSquareSprite;
		}

		private static class ProceduralSpriteFactory
		{
			public static Sprite GenerateCircleSprite(int width, int height, Color color)
			{
				Texture2D tex = new Texture2D(width, height, TextureFormat.ARGB32, false);
				tex.name = "CircleTex";
				tex.filterMode = FilterMode.Bilinear;
				tex.wrapMode = TextureWrapMode.Clamp;
				float cx = (width - 1) * 0.5f;
				float cy = (height - 1) * 0.5f;
				float r = Mathf.Min(cx, cy) - 1f;
				float r2 = r * r;
				Color32 clear = new Color(0, 0, 0, 0);
				for (int y = 0; y < height; y++)
				{
					for (int x = 0; x < width; x++)
					{
						float dx = x - cx;
						float dy = y - cy;
						float d2 = dx * dx + dy * dy;
						tex.SetPixel(x, y, d2 <= r2 ? color : clear);
					}
				}
				tex.Apply();
				return Sprite.Create(tex, new Rect(0, 0, width, height), new Vector2(0.5f, 0.5f), 100f);
			}

			public static Sprite GenerateSquareSprite(int width, int height, Color color)
			{
				Texture2D tex = new Texture2D(width, height, TextureFormat.ARGB32, false);
				tex.name = "SquareTex";
				tex.filterMode = FilterMode.Point;
				tex.wrapMode = TextureWrapMode.Clamp;
				Color32 clear = new Color(0, 0, 0, 0);
				for (int y = 0; y < height; y++)
				{
					for (int x = 0; x < width; x++)
					{
						bool inside = x > 0 && y > 0 && x < width - 1 && y < height - 1;
						tex.SetPixel(x, y, inside ? color : clear);
					}
				}
				tex.Apply();
				return Sprite.Create(tex, new Rect(0, 0, width, height), new Vector2(0.5f, 0.5f), 100f);
			}

			public static Sprite GenerateStarSprite(int width, int height, int points, float innerRadiusRatio, Color color)
			{
				Texture2D tex = new Texture2D(width, height, TextureFormat.ARGB32, false);
				tex.name = "StarTex";
				tex.filterMode = FilterMode.Bilinear;
				tex.wrapMode = TextureWrapMode.Clamp;
				Color32 clear = new Color(0, 0, 0, 0);
				float cx = (width - 1) * 0.5f;
				float cy = (height - 1) * 0.5f;
				float rOuter = Mathf.Min(cx, cy) - 1f;
				float rInner = rOuter * Mathf.Clamp01(innerRadiusRatio);
				for (int y = 0; y < height; y++)
				{
					for (int x = 0; x < width; x++)
					{
						Vector2 p = new Vector2(x - cx, y - cy);
						float ang = Mathf.Atan2(p.y, p.x);
						float k = Mathf.PI / points;
						float m = Mathf.Cos(points * ang) * 0.5f + 0.5f;
						float r = Mathf.Lerp(rOuter, rInner, m);
						bool inside = p.sqrMagnitude <= r * r;
						tex.SetPixel(x, y, inside ? color : clear);
					}
				}
				tex.Apply();
				return Sprite.Create(tex, new Rect(0, 0, width, height), new Vector2(0.5f, 0.5f), 100f);
			}

			public static Sprite GenerateArrowSprite(int width, int height, Color color)
			{
				Texture2D tex = new Texture2D(width, height, TextureFormat.ARGB32, false);
				tex.name = "ArrowTex";
				tex.filterMode = FilterMode.Bilinear;
				tex.wrapMode = TextureWrapMode.Clamp;
				Color32 clear = new Color(0, 0, 0, 0);
				float cx = (width - 1) * 0.5f;
				float cy = (height - 1) * 0.5f;
				for (int y = 0; y < height; y++)
				{
					for (int x = 0; x < width; x++)
					{
						// Up-pointing arrow shape
						float nx = (x - cx) / (width * 0.5f);
						float ny = (y - cy) / (height * 0.5f);
						bool head = ny > -0.1f && ny <= 1.0f && Mathf.Abs(nx) < Mathf.Lerp(0.05f, 0.6f, Mathf.InverseLerp(0.2f, 1f, ny));
						bool body = ny <= 0.2f && ny > -1f && Mathf.Abs(nx) < 0.1f;
						tex.SetPixel(x, y, (head || body) ? color : clear);
					}
				}
				tex.Apply();
				return Sprite.Create(tex, new Rect(0, 0, width, height), new Vector2(0.5f, 0.2f), 100f);
			}

			public static Sprite GenerateDiamondSprite(int width, int height, Color color)
			{
				Texture2D tex = new Texture2D(width, height, TextureFormat.ARGB32, false);
				tex.name = "DiamondTex";
				tex.filterMode = FilterMode.Bilinear;
				tex.wrapMode = TextureWrapMode.Clamp;
				Color32 clear = new Color(0, 0, 0, 0);
				float cx = (width - 1) * 0.5f;
				float cy = (height - 1) * 0.5f;
				for (int y = 0; y < height; y++)
				{
					for (int x = 0; x < width; x++)
					{
						float dx = Mathf.Abs(x - cx);
						float dy = Mathf.Abs(y - cy);
						bool inside = dx + dy <= Mathf.Min(cx, cy) - 1f;
						tex.SetPixel(x, y, inside ? color : clear);
					}
				}
				tex.Apply();
				return Sprite.Create(tex, new Rect(0, 0, width, height), new Vector2(0.5f, 0.5f), 100f);
			}

			public static Sprite GenerateTriangleSprite(int width, int height, Color color)
			{
				Texture2D tex = new Texture2D(width, height, TextureFormat.ARGB32, false);
				tex.name = "TriangleTex";
				tex.filterMode = FilterMode.Bilinear;
				tex.wrapMode = TextureWrapMode.Clamp;
				Color32 clear = new Color(0, 0, 0, 0);
				float cx = (width - 1) * 0.5f;
				float cy = (height - 1) * 0.5f;
				for (int y = 0; y < height; y++)
				{
					for (int x = 0; x < width; x++)
					{
						float nx = Mathf.Abs((x - cx) / (width * 0.5f));
						float ny = (y - (cy - 2f)) / (height * 0.5f);
						bool inside = ny >= -1f && ny <= 1f && nx < Mathf.Lerp(0.02f, 1f, Mathf.InverseLerp(-1f, 1f, ny));
						tex.SetPixel(x, y, inside ? color : clear);
					}
				}
				tex.Apply();
				return Sprite.Create(tex, new Rect(0, 0, width, height), new Vector2(0.5f, 0.1f), 100f);
			}
		}
		#endregion
	}
}

