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
    [Header("Player Arrow")]
    public Transform player;
    public Sprite playerArrowSprite;
    public Color playerArrowColor = Color.white;
    public float playerArrowSize = 18f;
    public bool rotateMapWithPlayer = true;
    public bool northUp = false;

    [Header("Map Objects (static markers)")]
    public List<TrackedObject> trackedObjects = new List<TrackedObject>();
    [Tooltip("If true, static markers outside the minimap are hidden. If false and clamp enabled, they clamp to edge.")]
    public bool hideStaticMarkersOffscreen = true;
    [Tooltip("Clamp static markers to edge when off-screen (if not hidden).")]
    public bool clampStaticMarkersToEdge = false;

    [Header("Waypoints")]
    public List<Waypoint> waypoints = new List<Waypoint>();
    public bool waypointEdgeArrows = true;

    [Header("Click-To-Create Waypoints")]
    public bool clickToCreateWaypoints = false;
    public Color defaultWaypointColor = Color.yellow;
    public string defaultWaypointLabel = "Waypoint";
    public float defaultWaypointRadius = 2f;

    [Header("Map Style")]
    public MapShape mapShape = MapShape.Circle;
    public Sprite customMaskSprite;
    public Color borderColor = Color.white;
    public float borderThickness = 6f;
    public Color backgroundColor = new Color(0f, 0f, 0f, 0.4f);

    [Header("UI Placement")]
    public Corner corner = Corner.TopRight;
    public Vector2 anchoredOffset = new Vector2(-16f, -16f);
    public float mapUISize = 256f;
    public float uiScale = 1f;
    public float uiScaleFine = 1f;
    [Tooltip("Use fully custom anchors/pivot/position instead of corner presets.")]
    public bool useCustomPosition = false;
    public Vector2 customAnchorMin = new Vector2(1f, 1f);
    public Vector2 customAnchorMax = new Vector2(1f, 1f);
    public Vector2 customPivot = new Vector2(1f, 1f);
    public Vector2 customAnchoredPosition = new Vector2(-20f, -20f);

    [Header("Camera & Alignment")]
    public float coverageWorldSize = 100f;
    public float cameraHeight = 200f;
    public Vector2 worldOffset = Vector2.zero;
    public bool autoFitToTerrain = false;
    public Terrain terrainOverride;
    public LayerMask minimapCullingMask = ~0;
    public Vector2Int renderTextureSize = new Vector2Int(512, 512);

    [Header("Expanded Map")]
    [Tooltip("Enable a larger overlay map that can be toggled.")]
    public bool enableExpandedMap = true;
    [Tooltip("Key to toggle the expanded map overlay.")]
    public KeyCode expandedToggleKey = KeyCode.M;
    [Tooltip("Expanded map size in UI pixels.")]
    public float expandedMapSize = 512f;
    [Tooltip("Allow waypoint creation by clicking on the expanded map.")]
    public bool clickToCreateOnExpanded = true;
    [Tooltip("Allow waypoint creation by clicking on the small minimap.")]
    public bool clickToCreateOnMinimap = false;

    [Header("Performance & UX")]
    public float markerSmoothing = 12f;
    public int initialPoolSize = 32;

    [Header("Popups (Optional)")]
    public bool enablePopups = false;
    public GameObject customPopupPrefab;
    public float popupDuration = 3f;

    [Header("Fonts")]
    [Tooltip("Default UI Font for labels and popups. Assign a project font asset here.")]
    public Font defaultUIFont;

    // Runtime
    private Camera minimapCamera;
    private RenderTexture minimapRenderTexture;
    private Canvas minimapCanvas;
    private CanvasScaler minimapCanvasScaler;
    private RectTransform minimapRoot;
    private RectTransform clipRect;
    private RawImage mapImage;
    private Image frameImage;
    private Image clipMaskImage;
    private RectTransform markerContainer;
    private RectTransform playerArrowRect;
    private Image playerArrowImage;
    private MinimapClickCatcher clickCatcher;

    // Expanded overlay
    private RectTransform expandedRoot;
    private Image expandedFrameImage;
    private RectTransform expandedClipRect;
    private Image expandedClipMaskImage;
    private RawImage expandedMapImage;
    private MinimapClickCatcher expandedClickCatcher;
    private bool expandedVisible;
    private RectTransform expandedMarkersContainer;

    private RectTransform popupRoot;
    private Text popupText;
    private float popupHideTime;

    private readonly List<MarkerUI> markerPool = new List<MarkerUI>();
    private readonly Dictionary<TrackedObject, MarkerUI> trackedToMarker = new Dictionary<TrackedObject, MarkerUI>();
    private readonly Dictionary<Waypoint, MarkerUI> waypointToMarker = new Dictionary<Waypoint, MarkerUI>();
    private readonly Dictionary<Waypoint, MarkerUI> waypointToArrow = new Dictionary<Waypoint, MarkerUI>();

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

    private void Reset()
    {
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
        if (northUp) rotateMapWithPlayer = false;
        if (rotateMapWithPlayer) northUp = false;
        borderThickness = Mathf.Max(0f, borderThickness);
        mapUISize = Mathf.Max(64f, mapUISize);
        coverageWorldSize = Mathf.Max(1f, coverageWorldSize);
        cameraHeight = Mathf.Max(1f, cameraHeight);
        renderTextureSize.x = Mathf.Max(64, renderTextureSize.x);
        renderTextureSize.y = Mathf.Max(64, renderTextureSize.y);

        if (!Application.isPlaying)
        {
            EnsureSprites();
            // Only update style if UI already exists to avoid editor SendMessage warnings
            if (minimapCanvas != null || minimapRoot != null)
            {
                ApplyStyleRuntime();
                UpdateCameraImmediate();
                UpdateAllMarkersImmediate();
            }
        }
    }

    private void LateUpdate()
    {
        // Toggle expanded map
        if (enableExpandedMap && Input.GetKeyDown(expandedToggleKey))
        {
            SetExpandedVisible(!expandedVisible);
        }
        UpdateCameraRuntime();
        UpdateMarkersRuntime(Time.deltaTime);
        UpdatePopupRuntime();
    }

    private void OnDestroy()
    {
        if (minimapCamera != null) minimapCamera.targetTexture = null;
        if (minimapRenderTexture != null)
        {
            if (minimapRenderTexture.IsCreated()) minimapRenderTexture.Release();
            if (Application.isPlaying) Destroy(minimapRenderTexture); else DestroyImmediate(minimapRenderTexture);
            minimapRenderTexture = null;
        }
    }

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
        // Use separate toggles for minimap vs expanded
        bool isFromExpanded = eventData != null && eventData.pointerPressRaycast.module != null && expandedVisible;
        bool allow = (isFromExpanded && clickToCreateOnExpanded) || (!isFromExpanded && clickToCreateOnMinimap);
        if (!allow) return;

        // Choose which clip to test against
        RectTransform clip = isFromExpanded && expandedVisible ? expandedClipRect : clipRect;
        if (clip == null) return;
        if (!IsInsideMask(localPoint, out _)) return;
        Vector3 world = LocalToWorld(localPoint);
        CreateWaypoint(world, null, null);
    }

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

        minimapCamera.transform.position = new Vector3(0, cameraHeight, 0);
        minimapCamera.transform.rotation = Quaternion.Euler(90f, 0f, 0f);

        EnsureRenderTexture();
        minimapCamera.targetTexture = minimapRenderTexture;
    }

    private void EnsureRenderTexture()
    {
        if (minimapRenderTexture != null)
        {
            if (minimapRenderTexture.width == renderTextureSize.x && minimapRenderTexture.height == renderTextureSize.y) return;
            if (minimapRenderTexture.IsCreated()) minimapRenderTexture.Release();
            if (Application.isPlaying) Destroy(minimapRenderTexture); else DestroyImmediate(minimapRenderTexture);
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

    private void AutoFitCoverageToTerrain()
    {
        var t = terrainOverride != null ? terrainOverride : Terrain.activeTerrain;
        if (t == null || t.terrainData == null) return;
        var size = t.terrainData.size;
        coverageWorldSize = Mathf.Max(1f, Mathf.Max(size.x, size.z));
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

        if (minimapRoot == null)
        {
            var rootTf = transform.Find(RootName);
            var rootGo = rootTf != null ? rootTf.gameObject : new GameObject(RootName, typeof(RectTransform));
            if (rootGo.transform.parent != minimapCanvas.transform) rootGo.transform.SetParent(minimapCanvas.transform, false);
            minimapRoot = rootGo.GetComponent<RectTransform>();
        }
        ApplyRootPositioning(minimapRoot, mapUISize);

        if (frameImage == null)
        {
            var frameGo = FindOrCreateChild(minimapRoot, FrameName);
            frameImage = GetOrAdd<Image>(frameGo);
        }
        frameImage.color = borderColor;
        frameImage.sprite = GetFrameSpriteForShape();
        frameImage.type = Image.Type.Simple;
        frameImage.raycastTarget = false;
        frameImage.rectTransform.sizeDelta = new Vector2(mapUISize, mapUISize);

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
        ApplyMaskSprite(clipMaskImage);

        var bgGo = FindOrCreateChild(clipRect, "BackgroundFill");
        var bgImg = GetOrAdd<Image>(bgGo);
        StretchToFill(bgImg.rectTransform);
        bgImg.color = backgroundColor;
        bgImg.sprite = cachedSquareSprite;
        bgImg.type = Image.Type.Sliced;
        bgImg.raycastTarget = false;

        if (mapImage == null)
        {
            var renderGo = FindOrCreateChild(clipRect, RenderName);
            mapImage = GetOrAdd<RawImage>(renderGo);
            StretchToFill(mapImage.rectTransform);
        }
        mapImage.texture = minimapRenderTexture;

        if (markerContainer == null)
        {
            var markersGo = FindOrCreateChild(clipRect, MarkersName);
            markerContainer = markersGo.GetComponent<RectTransform>();
            StretchToFill(markerContainer);
        }

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

        if (clickCatcher == null)
        {
            var clickGo = FindOrCreateChild(clipRect, ClickName);
            clickCatcher = GetOrAdd<MinimapClickCatcher>(clickGo);
            var rt = clickCatcher.GetComponent<RectTransform>();
            StretchToFill(rt);
            clickCatcher.minimapSystem = this;
        }

        EnsurePopupUI();
        if (enableExpandedMap)
        {
            EnsureExpandedUI();
        }
    }

    private void ApplyStyleRuntime()
    {
        if (minimapCanvasScaler != null) minimapCanvasScaler.scaleFactor = Mathf.Max(0.1f, uiScale * uiScaleFine);
        if (minimapRoot != null) ApplyRootPositioning(minimapRoot, mapUISize);
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
        ApplyMaskSprite(clipMaskImage);
        if (mapImage != null) mapImage.texture = minimapRenderTexture;
        if (playerArrowImage != null)
        {
            playerArrowImage.sprite = playerArrowSprite ?? cachedArrowSprite;
            playerArrowImage.color = playerArrowColor;
            if (playerArrowRect != null) playerArrowRect.sizeDelta = new Vector2(playerArrowSize, playerArrowSize);
        }
    }

    private void ApplyMaskSprite(Image targetMaskImage)
    {
        if (targetMaskImage == null) return;
        switch (mapShape)
        {
            case MapShape.Circle:
                targetMaskImage.sprite = cachedCircleSprite;
                targetMaskImage.type = Image.Type.Simple;
                break;
            case MapShape.Square:
                targetMaskImage.sprite = cachedSquareSprite;
                targetMaskImage.type = Image.Type.Sliced;
                break;
            case MapShape.Star:
                targetMaskImage.sprite = cachedStarSprite;
                targetMaskImage.type = Image.Type.Simple;
                break;
            case MapShape.Custom:
                targetMaskImage.sprite = customMaskSprite != null ? customMaskSprite : cachedSquareSprite;
                targetMaskImage.type = Image.Type.Simple;
                break;
        }
    }

    private Sprite GetFrameSpriteForShape()
    {
        switch (mapShape)
        {
            case MapShape.Circle: return cachedCircleSprite;
            case MapShape.Square: return cachedSquareSprite;
            case MapShape.Star: return cachedStarSprite;
            case MapShape.Custom: return customMaskSprite != null ? customMaskSprite : cachedSquareSprite;
        }
        return cachedSquareSprite;
    }

    private void ApplyRootPositioning(RectTransform root, float size)
    {
        if (root == null) return;
        if (useCustomPosition)
        {
            root.anchorMin = customAnchorMin;
            root.anchorMax = customAnchorMax;
            root.pivot = customPivot;
            root.anchoredPosition = customAnchoredPosition;
            root.sizeDelta = new Vector2(size, size);
        }
        else
        {
            ConfigureAnchors(root, corner, anchoredOffset, size);
        }
    }

    private void EnsureExpandedUI()
    {
        if (expandedRoot == null)
        {
            var rootGo = new GameObject("Minimap_Expanded", typeof(RectTransform));
            rootGo.transform.SetParent(minimapCanvas.transform, false);
            expandedRoot = rootGo.GetComponent<RectTransform>();
            expandedRoot.anchorMin = new Vector2(0.5f, 0.5f);
            expandedRoot.anchorMax = new Vector2(0.5f, 0.5f);
            expandedRoot.pivot = new Vector2(0.5f, 0.5f);
            expandedRoot.sizeDelta = new Vector2(expandedMapSize, expandedMapSize);
            expandedRoot.anchoredPosition = Vector2.zero;

            var frameGo = FindOrCreateChild(expandedRoot, FrameName);
            expandedFrameImage = GetOrAdd<Image>(frameGo);
            expandedFrameImage.color = borderColor;
            expandedFrameImage.sprite = GetFrameSpriteForShape();
            expandedFrameImage.type = Image.Type.Simple;
            expandedFrameImage.rectTransform.sizeDelta = new Vector2(expandedMapSize, expandedMapSize);

            var clipGo = FindOrCreateChild(expandedFrameImage.rectTransform, ClipName);
            expandedClipRect = clipGo.GetComponent<RectTransform>();
            expandedClipMaskImage = GetOrAdd<Image>(clipGo);
            var mask = clipGo.GetComponent<Mask>();
            if (mask == null) mask = clipGo.AddComponent<Mask>();
            mask.showMaskGraphic = false;
            float innerSize = Mathf.Max(0f, expandedMapSize - 2f * borderThickness);
            expandedClipRect.sizeDelta = new Vector2(innerSize, innerSize);
            expandedClipRect.anchoredPosition = Vector2.zero;
            ApplyMaskSprite(expandedClipMaskImage);

            var bgGo = FindOrCreateChild(expandedClipRect, "BackgroundFill");
            var bgImg = GetOrAdd<Image>(bgGo);
            StretchToFill(bgImg.rectTransform);
            bgImg.color = backgroundColor;
            bgImg.sprite = cachedSquareSprite;
            bgImg.type = Image.Type.Sliced;
            bgImg.raycastTarget = false;

            var renderGo = FindOrCreateChild(expandedClipRect, RenderName);
            expandedMapImage = GetOrAdd<RawImage>(renderGo);
            StretchToFill(expandedMapImage.rectTransform);
            expandedMapImage.texture = minimapRenderTexture;

            var markersGo = FindOrCreateChild(expandedClipRect, MarkersName);
            expandedMarkersContainer = markersGo.GetComponent<RectTransform>();
            StretchToFill(expandedMarkersContainer);

            var clickGo = FindOrCreateChild(expandedClipRect, ClickName);
            expandedClickCatcher = GetOrAdd<MinimapClickCatcher>(clickGo);
            var rt = expandedClickCatcher.GetComponent<RectTransform>();
            StretchToFill(rt);
            expandedClickCatcher.minimapSystem = this;
            expandedClickCatcher.forExpanded = true;

            rootGo.SetActive(false);
        }
    }

    private void SetExpandedVisible(bool visible)
    {
        if (!enableExpandedMap) return;
        EnsureExpandedUI();
        expandedVisible = visible;
        expandedRoot.gameObject.SetActive(visible);

        // Reparent arrow and markers to active container
        var targetContainer = visible ? expandedMarkersContainer : markerContainer;
        if (playerArrowRect != null)
        {
            playerArrowRect.SetParent(visible ? expandedClipRect : clipRect, false);
        }
        foreach (var kv in trackedToMarker)
        {
            if (kv.Value != null) kv.Value.rect.SetParent(targetContainer, false);
        }
        foreach (var kv in waypointToMarker)
        {
            if (kv.Value != null) kv.Value.rect.SetParent(targetContainer, false);
        }
        foreach (var kv in waypointToArrow)
        {
            if (kv.Value != null) kv.Value.rect.SetParent(targetContainer, false);
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
                if (defaultUIFont != null) popupText.font = defaultUIFont;
                popupText.resizeTextForBestFit = true;
                popupText.resizeTextMinSize = 12;
                popupText.resizeTextMaxSize = 32;
            }
        }
        popupRoot.gameObject.SetActive(false);
    }

    private void UpdateCameraImmediate()
    {
        UpdateCameraRuntimeInternal(Time.deltaTime, true);
    }

    private void UpdateCameraRuntime()
    {
        UpdateCameraRuntimeInternal(Time.deltaTime, false);
    }

    private void UpdateCameraRuntimeInternal(float dt, bool immediate)
    {
        if (minimapCamera == null || clipRect == null) return;
        float innerSize = Mathf.Max(0f, mapUISize - 2f * borderThickness);
        minimapCamera.aspect = 1f;
        minimapCamera.orthographicSize = Mathf.Max(1f, coverageWorldSize * 0.5f);
        Vector3 targetPos = Vector3.zero;
        float yaw = 0f;
        if (player != null) { targetPos = player.position; yaw = player.eulerAngles.y; }
        if (northUp) yaw = 0f;
        targetPos += new Vector3(worldOffset.x, 0f, worldOffset.y);
        minimapCamera.transform.position = new Vector3(targetPos.x, cameraHeight, targetPos.z);
        minimapCamera.transform.rotation = Quaternion.Euler(90f, rotateMapWithPlayer ? yaw : 0f, 0f);
        if (playerArrowRect != null)
        {
            if (rotateMapWithPlayer) playerArrowRect.localEulerAngles = Vector3.zero;
            else playerArrowRect.localEulerAngles = new Vector3(0, 0, -(player != null ? player.eulerAngles.y : 0f));
        }
    }

    private Vector2 WorldToLocalUI(Vector3 worldPosition)
    {
        if (minimapCamera == null || clipRect == null) return Vector2.zero;
        Vector3 camCenter = minimapCamera.transform.position;
        float yaw = minimapCamera.transform.eulerAngles.y * Mathf.Deg2Rad;
        float cos = Mathf.Cos(-yaw);
        float sin = Mathf.Sin(-yaw);
        Vector2 deltaXZ = new Vector2(worldPosition.x - camCenter.x, worldPosition.z - camCenter.z);
        float localX = deltaXZ.x * cos - deltaXZ.y * sin;
        float localY = deltaXZ.x * sin + deltaXZ.y * cos;
        float halfWorldW = minimapCamera.orthographicSize * minimapCamera.aspect;
        float halfWorldH = minimapCamera.orthographicSize;
        float innerSize = Mathf.Max(0f, mapUISize - 2f * borderThickness);
        float halfUI = innerSize * 0.5f;
        float uiX = (localX / halfWorldW) * halfUI;
        float uiY = (localY / halfWorldH) * halfUI;
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
        foreach (var kv in trackedToMarker) { ReturnMarkerToPool(kv.Value); }
        trackedToMarker.Clear();
        foreach (var kv in waypointToMarker) { ReturnMarkerToPool(kv.Value); }
        waypointToMarker.Clear();
        foreach (var kv in waypointToArrow) { ReturnMarkerToPool(kv.Value); }
        waypointToArrow.Clear();
        foreach (var to in trackedObjects)
        {
            if (to != null && to.target != null) trackedToMarker[to] = CreateOrReuseMarkerForTracked(to);
        }
        foreach (var wp in waypoints) EnsureWaypointMarker(wp);
    }

    private void UpdateAllMarkersImmediate()
    {
        UpdateMarkersRuntimeInternal(Time.deltaTime, true);
    }

    private void UpdateMarkersRuntime(float deltaTime)
    {
        UpdateMarkersRuntimeInternal(deltaTime, false);
    }

    private void UpdateMarkersRuntimeInternal(float deltaTime, bool immediate)
    {
        if (markerContainer == null) return;

        foreach (var kv in trackedToMarker)
        {
            var tracked = kv.Key;
            var marker = kv.Value;
            if (tracked.target == null) { marker.gameObject.SetActive(false); continue; }
            Vector2 local = WorldToLocalUI(tracked.target.position);
            bool inside = IsInsideMask(local, out var limit);
            if (!inside)
            {
                if (hideStaticMarkersOffscreen)
                {
                    marker.gameObject.SetActive(false);
                    continue;
                }
                if (clampStaticMarkersToEdge) local = ClampToEdge(local, limit);
            }
            marker.gameObject.SetActive(true);
            MoveMarker(marker, local, deltaTime, immediate);
        }

        foreach (var wp in waypoints)
        {
            EnsureWaypointMarker(wp);
            var marker = waypointToMarker[wp];
            Vector3 worldPos = wp.useTransform && wp.targetTransform != null ? wp.targetTransform.position : wp.worldPosition;
            Vector2 local = WorldToLocalUI(worldPos);
            bool inside = IsInsideMask(local, out var limit);
            if (!wp.reached && player != null)
            {
                var flatPlayer = player.position; flatPlayer.y = 0f;
                var flatWP = worldPos; flatWP.y = 0f;
                float dist = Vector3.Distance(flatPlayer, flatWP);
                if (dist <= wp.radius)
                {
                    wp.reached = true;
                    try { wp.onReach?.Invoke(); } catch {}
                    if (enablePopups) ShowPopup(!string.IsNullOrEmpty(wp.label) ? $"Reached {wp.label}" : "Waypoint reached");
                }
            }

            if (inside)
            {
                MoveMarker(marker, local, deltaTime, immediate);
                marker.gameObject.SetActive(true);
                if (waypointToArrow.TryGetValue(wp, out var arrow)) arrow.gameObject.SetActive(false);
            }
            else
            {
                marker.gameObject.SetActive(false);
                if (waypointEdgeArrows && wp.showEdgeArrow)
                {
                    var arrow = EnsureWaypointArrow(wp);
                    Vector2 edgePos = ClampToEdge(local, limit);
                    MoveMarker(arrow, edgePos, deltaTime, immediate);
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
                float half = radius;
                Vector2 clamped = local;
                float mx = half - 8f;
                float my = half - 8f;
                if (Mathf.Abs(clamped.x) * my > Mathf.Abs(clamped.y) * mx)
                {
                    clamped.x = Mathf.Clamp(clamped.x, -mx, mx);
                    clamped.y = Mathf.Sign(local.y) * (Mathf.Abs(clamped.x) * my / mx);
                }
                else
                {
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
        if (immediate || markerSmoothing <= 0f) { marker.rect.anchoredPosition = targetLocal; return; }
        var current = marker.rect.anchoredPosition;
        var next = Vector2.Lerp(current, targetLocal, 1f - Mathf.Exp(-markerSmoothing * deltaTime));
        marker.rect.anchoredPosition = next;
    }

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
        if (defaultUIFont != null) text.font = defaultUIFont;
        text.color = Color.white;
        text.alignment = TextAnchor.UpperCenter;
        text.raycastTarget = false;
        text.fontSize = 12;
        text.horizontalOverflow = HorizontalWrapMode.Overflow;
        text.verticalOverflow = VerticalWrapMode.Overflow;
        return new MarkerUI { gameObject = go, rect = rect, image = img, label = text };
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

    private static Sprite CreateSolidSprite(int width, int height, Color color)
    {
        var tex = new Texture2D(width, height, TextureFormat.ARGB32, false);
        var fill = new Color32[width * height];
        var c32 = (Color32)color;
        for (int i = 0; i < fill.Length; i++) fill[i] = c32;
        tex.SetPixels32(fill);
        tex.Apply(false);
        return Sprite.Create(tex, new Rect(0, 0, width, height), new Vector2(0.5f, 0.5f), 100f);
    }

    private static Sprite CreateCircleSprite(int size)
    {
        var tex = new Texture2D(size, size, TextureFormat.ARGB32, false);
        int r = size / 2; int cx = r, cy = r;
        var white = new Color32(255, 255, 255, 255); var clear = new Color32(0, 0, 0, 0);
        for (int y = 0; y < size; y++)
            for (int x = 0; x < size; x++)
            {
                int dx = x - cx; int dy = y - cy;
                tex.SetPixel(x, y, (dx * dx + dy * dy <= r * r) ? (Color)white : (Color)clear);
            }
        tex.Apply(false);
        return Sprite.Create(tex, new Rect(0, 0, size, size), new Vector2(0.5f, 0.5f), 100f);
    }

    private static Sprite CreateDiamondSprite(int size)
    {
        var tex = new Texture2D(size, size, TextureFormat.ARGB32, false);
        int r = size / 2; int cx = r, cy = r;
        var white = new Color32(255, 255, 255, 255); var clear = new Color32(0, 0, 0, 0);
        for (int y = 0; y < size; y++)
            for (int x = 0; x < size; x++)
            {
                int dx = Mathf.Abs(x - cx); int dy = Mathf.Abs(y - cy);
                tex.SetPixel(x, y, (dx + dy <= r) ? (Color)white : (Color)clear);
            }
        tex.Apply(false);
        return Sprite.Create(tex, new Rect(0, 0, size, size), new Vector2(0.5f, 0.5f), 100f);
    }

    private static Sprite CreateStarSprite(int size)
    {
        var tex = new Texture2D(size, size, TextureFormat.ARGB32, false);
        var white = new Color32(255, 255, 255, 255); var clear = new Color32(0, 0, 0, 0);
        float cx = (size - 1) * 0.5f, cy = (size - 1) * 0.5f; float outer = size * 0.48f; float inner = outer * 0.5f;
        var verts = new List<Vector2>();
        for (int i = 0; i < 10; i++) { float ang = (Mathf.PI / 2f) + i * (Mathf.PI * 2f / 10f); float r = (i % 2 == 0) ? outer : inner; verts.Add(new Vector2(cx + Mathf.Cos(ang) * r, cy + Mathf.Sin(ang) * r)); }
        for (int y = 0; y < size; y++)
            for (int x = 0; x < size; x++)
            {
                bool inside = PointInPolygon(new Vector2(x + 0.5f, y + 0.5f), verts);
                tex.SetPixel(x, y, inside ? (Color)white : (Color)clear);
            }
        tex.Apply(false);
        return Sprite.Create(tex, new Rect(0, 0, size, size), new Vector2(0.5f, 0.5f), 100f);
    }

    private static bool PointInPolygon(Vector2 p, List<Vector2> verts)
    {
        bool inside = false; for (int i = 0, j = verts.Count - 1; i < verts.Count; j = i++) { var vi = verts[i]; var vj = verts[j]; bool intersect = ((vi.y > p.y) != (vj.y > p.y)) && (p.x < (vj.x - vi.x) * (p.y - vi.y) / (vj.y - vi.y + 1e-6f) + vi.x); if (intersect) inside = !inside; } return inside;
    }

    private static Sprite CreateArrowSprite(int width, int height)
    {
        var tex = new Texture2D(width, height, TextureFormat.ARGB32, false);
        var white = new Color32(255, 255, 255, 255); var clear = new Color32(0, 0, 0, 0);
        Vector2 p0 = new Vector2(width * 0.5f, height * 0.95f); Vector2 p1 = new Vector2(width * 0.1f, height * 0.05f); Vector2 p2 = new Vector2(width * 0.9f, height * 0.05f);
        for (int y = 0; y < height; y++) for (int x = 0; x < width; x++) { bool inside = PointInTriangle(new Vector2(x + 0.5f, y + 0.5f), p0, p1, p2); tex.SetPixel(x, y, inside ? (Color)white : (Color)clear); }
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
        Transform child = null; for (int i = 0; i < parent.childCount; i++) { if (parent.GetChild(i).name == name) { child = parent.GetChild(i); break; } }
        GameObject go; if (child == null) { go = new GameObject(name, typeof(RectTransform)); go.transform.SetParent(parent, false); } else { go = child.gameObject; }
        return go;
    }

    private static void StretchToFill(RectTransform rect)
    {
        rect.anchorMin = Vector2.zero; rect.anchorMax = Vector2.one; rect.pivot = new Vector2(0.5f, 0.5f); rect.anchoredPosition = Vector2.zero; rect.sizeDelta = Vector2.zero;
    }
}

