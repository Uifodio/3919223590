using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.EventSystems;
using UnityEngine.UI;

/// <summary>
/// AAAMinimap: A single-script, self-contained minimap system with auto-created camera, canvas, UI, markers,
/// waypoints, pooling, shape/border styling, and rich inspector controls. AAA-grade UX features include
/// click-to-create waypoints, mission/tutorial styles, off-screen indicators, popups, zoom/toggle controls,
/// north arrow, optional grid overlay, distance-based scaling/culling, and performance-friendly updates.
/// </summary>
[DefaultExecutionOrder(-50)]
[DisallowMultipleComponent]
[ExecuteAlways]
public class AAAMinimap : MonoBehaviour
{
	#region Enums
	public enum MapShape { Circle, Square, Star, CustomSprite }
	public enum WaypointType { Generic, Mission, Tutorial }
	public enum MarkerKind { Player, Static, Waypoint }
	public enum OffscreenIndicatorStyle { None, Arrow, Dot }
	#endregion

	#region Serializable Data Containers
	[Serializable]
	public class MarkerVisual
	{
		[Tooltip("Shape used when 'useCustomIcon' is false")] public MapShape shape = MapShape.Circle;
		[Tooltip("Optional custom sprite used when shape is CustomSprite OR when 'useCustomIcon' is true")] public Sprite customSprite;
		[Tooltip("Use the customSprite as the icon instead of generated shape")] public bool useCustomIcon = false;
		[Tooltip("Primary color of the marker")] public Color color = Color.white;
		[Tooltip("Outline/border color around marker (if supported)")] public Color borderColor = new Color(0, 0, 0, 0.75f);
		[Range(4f, 128f)] [Tooltip("Size of the marker in pixels")] public float size = 18f;
		[Range(0f, 10f)] [Tooltip("Optional border thickness (pixels)")] public float borderThickness = 2f;
		[Tooltip("Optional label under/near the marker")] public string label;
		[Tooltip("Label color")] public Color labelColor = Color.white;
		[Range(8, 28)] [Tooltip("Label font size")] public int labelFontSize = 12;
	}

	[Serializable]
	public class PlayerSettings
	{
		[Tooltip("Player Transform to follow and/or rotate the map around")] public Transform playerTransform;
		[Tooltip("Rotate the map so player 'up' is screen up")] public bool rotateMapWithPlayer = true;
		[Tooltip("Rotate the player arrow with the player's forward if map is north-up")] public bool rotateArrowWithPlayer = true;
		[Tooltip("Visual for the player arrow marker")] public MarkerVisual visual = new MarkerVisual
		{
			shape = MapShape.Star,
			color = new Color(1f, 0.85f, 0.2f, 1f),
			borderColor = new Color(0f, 0f, 0f, 0.9f),
			size = 26f,
			borderThickness = 2f,
			label = "",
			labelColor = Color.white,
			labelFontSize = 12
		};
	}

	[Serializable]
	public class StaticMarkerDefinition
	{
		[Tooltip("Name of the static marker (for reference only)")] public string name = "Static Marker";
		[Tooltip("If true, uses 'target' Transform position. If false, uses 'worldPosition'.")] public bool useTransform = true;
		[Tooltip("World Transform to track, if useTransform is true")] public Transform target;
		[Tooltip("Fixed world position used when useTransform is false")] public Vector3 worldPosition;
		[Tooltip("Whether to show an offscreen indicator for this marker")] public OffscreenIndicatorStyle offscreenIndicator = OffscreenIndicatorStyle.Arrow;
		[Tooltip("Visual appearance of the marker")] public MarkerVisual visual = new MarkerVisual();
	}

	[Serializable]
	public class WaypointDefinition
	{
		[Tooltip("Optional ID or label for programmatic access")] public string id;
		[Tooltip("World Transform to follow (overrides 'worldPosition' if set)")] public Transform target;
		[Tooltip("Fixed world position if 'target' is not set")] public Vector3 worldPosition;
		[Tooltip("Meters from player to trigger")] public float triggerRadius = 2.5f;
		[Tooltip("Show an offscreen indicator for this waypoint")] public OffscreenIndicatorStyle offscreenIndicator = OffscreenIndicatorStyle.Arrow;
		[Tooltip("Destroy the waypoint when reached")] public bool destroyOnReach = true;
		[Tooltip("If false and destroyOnReach=false, can trigger events multiple times")] public bool triggerOnce = true;
		[Tooltip("Type hint for default styles")] public WaypointType type = WaypointType.Generic;
		[Tooltip("Popup text to display when reached (optional)")] [TextArea(1, 3)] public string popupText;
		[Tooltip("Events invoked when waypoint is reached")] public UnityEvent onReached;
		[Tooltip("Visual appearance of the waypoint marker")] public MarkerVisual visual = new MarkerVisual
		{
			shape = MapShape.Circle,
			color = new Color(0.2f, 0.9f, 0.2f, 1f),
			borderColor = new Color(0f, 0.3f, 0f, 1f),
			size = 20f,
			borderThickness = 2f,
			label = "",
			labelColor = Color.white,
			labelFontSize = 12
		};
	}
	#endregion

	#region Inspector - Global UI & Map Controls
	[Header("Minimap Root & Placement")]
	[Tooltip("Parent canvas will be created if none exists")] public Canvas existingCanvas;
	[Tooltip("Sorting order for the auto-created canvas")] public int canvasSortingOrder = 5000;
	[Tooltip("Anchor position for minimap root in screen space")] public Vector2 anchoredPosition = new Vector2(-20f, -20f);
	[Tooltip("Pivot for minimap root")] public Vector2 pivot = new Vector2(1f, 0f);
	[Tooltip("Size of the minimap (pixels)")] [Range(64f, 1024f)] public float sizePixels = 256f;
	[Tooltip("Overall opacity of the minimap")] [Range(0.05f, 1f)] public float opacity = 0.95f;

	[Header("Map Shape & Style")]
	[Tooltip("Mask shape used for the minimap viewport")] public MapShape mapShape = MapShape.Circle;
	[Tooltip("Optional custom sprite for the map shape when using CustomSprite")] public Sprite mapCustomSprite;
	[Tooltip("Fill color of the map area")] public Color mapFillColor = new Color(0.07f, 0.07f, 0.07f, 0.95f);
	[Tooltip("Color of the map border")] public Color mapBorderColor = new Color(0f, 0f, 0f, 1f);
	[Tooltip("Thickness of the border (pixels)")] [Range(0f, 24f)] public float mapBorderThickness = 6f;

	[Header("Camera & World Alignment")]
	[Tooltip("Orthographic size scaling multiplier for the camera auto-fit")] [Range(0.25f, 4f)] public float cameraSizeScale = 1f;
	[Tooltip("RenderTexture resolution (width=height). Higher = sharper but slower")] [Range(128, 2048)] public int renderTextureSize = 512;
	[Tooltip("If true, the camera will follow the player in XZ")] public bool cameraFollowsPlayer = true;
	[Tooltip("If true, the camera will auto-fit to the detected terrain or scene bounds")] public bool autoFitWorldBounds = true;
	[Tooltip("Optional offset applied to world mapping (meters)")] public Vector2 worldOffsetXZ = Vector2.zero;
	[Tooltip("Manual world scale (meters to minimap units). Used when autoFitWorldBounds is false")] public float manualWorldSizeX = 200f;
	[Tooltip("Manual world scale (meters to minimap units). Used when autoFitWorldBounds is false")] public float manualWorldSizeZ = 200f;
	[Tooltip("Height of the minimap camera above world center")] public float cameraHeight = 200f;
	[Tooltip("Camera background color")] public Color cameraBackgroundColor = Color.black;

	[Header("Interaction & Updates")]
	[Tooltip("Allow user to click on minimap to create a waypoint")] public bool clickToCreateWaypoints = true;
	[Tooltip("Default waypoint settings for click-created waypoints")] public WaypointDefinition defaultClickWaypoint = new WaypointDefinition
	{
		triggerRadius = 2f,
		destroyOnReach = true,
		triggerOnce = true,
		popupText = "Waypoint reached",
		visual = new MarkerVisual
		{
			shape = MapShape.Star,
			color = new Color(0.2f, 0.6f, 1f, 1f),
			borderColor = new Color(0f, 0.2f, 0.5f, 1f),
			size = 18f,
			borderThickness = 2f,
			label = "",
			labelColor = Color.white,
			labelFontSize = 12
		}
	};
	[Tooltip("How many times per second to update marker positions")] [Range(1, 120)] public int updatesPerSecond = 30;
	[Tooltip("Clamp and hide offscreen markers or show indicators")] public bool clampMarkersToEdge = true;
	#endregion

	#region Inspector - Content: Player, Static Markers, Waypoints
	[Header("Player")] public PlayerSettings player = new PlayerSettings();
	[Header("Static Tracked Objects")] [Tooltip("Add any static objects or world positions to show on the minimap")] public List<StaticMarkerDefinition> staticMarkers = new List<StaticMarkerDefinition>();
	[Header("Waypoints")] [Tooltip("Define mission/tutorial/generic waypoints here")] public List<WaypointDefinition> waypoints = new List<WaypointDefinition>();
	#endregion

	#region Inspector - UX & Controls
	[Header("UX & Controls")]
	[Tooltip("Allow toggling minimap visibility via key")] public bool allowToggleKey = true;
	[Tooltip("Key to toggle minimap visibility")] public KeyCode toggleKey = KeyCode.M;
	[Tooltip("Enable zoom controls")] public bool enableZoomControls = true;
	[Tooltip("Scroll wheel zoom when cursor over minimap")] public bool scrollZoom = true;
	[Tooltip("Minimum zoom (camera size scale)")] [Range(0.25f, 4f)] public float minZoom = 0.5f;
	[Tooltip("Maximum zoom (camera size scale)")] [Range(0.25f, 4f)] public float maxZoom = 2.5f;
	[Tooltip("Zoom step when using keys")] [Range(0.01f, 1f)] public float zoomStep = 0.1f;
	[Tooltip("Optional key to zoom in")] public KeyCode zoomInKey = KeyCode.Equals;
	[Tooltip("Optional key to zoom out")] public KeyCode zoomOutKey = KeyCode.Minus;
	[Tooltip("Show north indicator arrow")]
	public bool showNorthIndicator = true;
	[Tooltip("North indicator color")] public Color northIndicatorColor = new Color(1f, 1f, 1f, 0.9f);
	[Tooltip("Show a subtle grid overlay in the map")] public bool showGridOverlay = false;
	[Tooltip("Grid line color")] public Color gridColor = new Color(1f, 1f, 1f, 0.1f);
	[Tooltip("Grid spacing in world meters (auto-fit mode)")] public float gridWorldSpacing = 50f;
	[Tooltip("Cull markers beyond this distance from player (0 = no cull)")] public float markerMaxDistance = 0f;
	[Tooltip("Scale markers down with distance")] public bool scaleMarkersWithDistance = true;
	[Tooltip("Marker scale factor at max distance")] [Range(0.1f, 1f)] public float markerMinScaleAtMaxDistance = 0.6f;
	#endregion

	#region Runtime Fields
	private Canvas _canvas;
	private RectTransform _minimapRoot;
	private Image _maskImage;
	private Mask _mask;
	private RawImage _mapRawImage;
	private Image _borderImage;
	private RectTransform _markerContainer;
	private RectTransform _contentRoot;
	private CanvasGroup _canvasGroup;
	private EventTrigger _eventTrigger;
	private bool _isPointerOver;

	private Camera _minimapCamera;
	private RenderTexture _renderTexture;
	private Bounds _worldBounds;

	private float _updateInterval;
	private float _timeSinceUpdate;

	// Pools
	private readonly Queue<MarkerUI> _markerPool = new Queue<MarkerUI>();
	private readonly List<MarkerUI> _activeMarkers = new List<MarkerUI>();
	private readonly Queue<PopupUI> _popupPool = new Queue<PopupUI>();
	private readonly List<PopupUI> _activePopups = new List<PopupUI>();

	// Registries
	private readonly List<RuntimeStaticMarker> _runtimeStaticMarkers = new List<RuntimeStaticMarker>();
	private readonly List<RuntimeWaypoint> _runtimeWaypoints = new List<RuntimeWaypoint>();
	private MarkerUI _playerMarkerUI;

	// Generated sprites
	private Sprite _generatedMaskSprite;
	private Sprite _generatedBorderSprite;
	private Texture2D _generatedMaskTexture;
	private Texture2D _generatedBorderTexture;

	// Overlays
	private Image _northArrowImage;
	private RawImage _gridOverlay;
	private Texture2D _gridTexture;
	#endregion

	#region Nested Runtime Classes
	private class MarkerUI
	{
		public GameObject root;
		public RectTransform rectTransform;
		public Image image;
		public Text labelText;
		public GameObject offscreenRoot;
		public RectTransform offscreenRect;
		public Image offscreenImage;
		public MarkerKind kind;
		public object backingData; // RuntimeStaticMarker or RuntimeWaypoint or Player
	}

	private class RuntimeStaticMarker
	{
		public StaticMarkerDefinition def;
		public MarkerUI ui;
	}

	private class RuntimeWaypoint
	{
		public WaypointDefinition def;
		public MarkerUI ui;
		public bool triggered;
	}

	private class PopupUI
	{
		public GameObject root;
		public RectTransform rectTransform;
		public Image background;
		public Text text;
		public float timeRemaining;
	}
	#endregion

	#region Unity Lifecycle
	private void OnEnable()
	{
		InitializeIfNeeded();
		RebuildAllMarkers();
	}

	private void OnDisable()
	{
		CleanupRenderTexture();
	}

	private void OnDestroy()
	{
		CleanupGeneratedSprites();
		CleanupRenderTexture();
		if (_gridTexture != null) { DestroyImmediate(_gridTexture); _gridTexture = null; }
	}

	private void OnValidate()
	{
		updatesPerSecond = Mathf.Clamp(updatesPerSecond, 1, 120);
		renderTextureSize = Mathf.Clamp(renderTextureSize, 128, 4096);
		sizePixels = Mathf.Clamp(sizePixels, 64f, 4096f);
		mapBorderThickness = Mathf.Max(0f, mapBorderThickness);
		cameraHeight = Mathf.Max(10f, cameraHeight);
		cameraSizeScale = Mathf.Clamp(cameraSizeScale, minZoom, maxZoom);
		if (!Application.isPlaying && _minimapRoot != null)
		{
			ApplyLayout();
			RebuildMapSprites();
			EnsureOverlays();
			UpdateNorthArrow();
		}
	}

	private void Update()
	{
		if (!Application.isPlaying)
		{
			// Keep visuals synced in edit mode
			InitializeIfNeeded();
			ApplyLayout();
			RebuildMapSprites();
			EnsureOverlays();
			UpdateCameraAlignmentImmediate();
			UpdateAllMarkerVisualsImmediate();
			UpdateMapRotation();
			UpdateNorthArrow();
			return;
		}

		if (_minimapCamera == null || _minimapRoot == null) InitializeIfNeeded();

		HandleInput();

		_updateInterval = 1f / Mathf.Max(1, updatesPerSecond);
		_timeSinceUpdate += Time.unscaledDeltaTime;
		if (_timeSinceUpdate >= _updateInterval)
		{
			_timeSinceUpdate = 0f;
			UpdateCameraFollow();
			UpdateMarkers();
			UpdateMapRotation();
			UpdateWaypoints();
			UpdateNorthArrow();
		}

		UpdatePopups(Time.unscaledDeltaTime);
	}
	#endregion

	#region Initialization
	private void InitializeIfNeeded()
	{
		EnsureCanvasAndRoot();
		EnsureEventSystem();
		EnsureCameraAndRenderTexture();
		ApplyLayout();
		RebuildMapSprites();
		EnsureOverlays();
	}

	private void EnsureCanvasAndRoot()
	{
		if (_canvas == null)
		{
			_canvas = existingCanvas != null ? existingCanvas : FindObjectOfType<Canvas>();
			if (_canvas == null)
			{
				var canvasGo = new GameObject("AAAMinimap_Canvas", typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
				_canvas = canvasGo.GetComponent<Canvas>();
				_canvas.renderMode = RenderMode.ScreenSpaceOverlay;
				_canvas.sortingOrder = canvasSortingOrder;
				var scaler = canvasGo.GetComponent<CanvasScaler>();
				scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
				scaler.referenceResolution = new Vector2(1920, 1080);
				scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.MatchWidthOrHeight;
				scaler.matchWidthOrHeight = 1f;
			}
		}

		if (_minimapRoot == null)
		{
			var rootGo = GameObject.Find("AAAMinimap_Root");
			if (rootGo == null || rootGo.transform.parent != _canvas.transform)
			{
				rootGo = new GameObject("AAAMinimap_Root", typeof(RectTransform), typeof(CanvasGroup));
				rootGo.transform.SetParent(_canvas.transform, false);
			}
			_minimapRoot = rootGo.GetComponent<RectTransform>();
			_canvasGroup = rootGo.GetComponent<CanvasGroup>();

			// Mask object
			var maskGo = GameObject.Find("AAAMinimap_Mask");
			if (maskGo == null || maskGo.transform.parent != _minimapRoot)
			{
				maskGo = new GameObject("AAAMinimap_Mask", typeof(RectTransform), typeof(Image), typeof(Mask));
				maskGo.transform.SetParent(_minimapRoot, false);
			}
			_maskImage = maskGo.GetComponent<Image>();
			_maskImage.raycastTarget = true;
			_mask = maskGo.GetComponent<Mask>();
			_mask.showMaskGraphic = true;

			// Content root (rotates map + markers as a unit)
			var contentGo = GameObject.Find("AAAMinimap_Content");
			if (contentGo == null || contentGo.transform.parent != maskGo.transform)
			{
				contentGo = new GameObject("AAAMinimap_Content", typeof(RectTransform));
				contentGo.transform.SetParent(maskGo.transform, false);
			}
			_contentRoot = contentGo.GetComponent<RectTransform>();
			_contentRoot.anchorMin = Vector2.zero;
			_contentRoot.anchorMax = Vector2.one;
			_contentRoot.offsetMin = Vector2.zero;
			_contentRoot.offsetMax = Vector2.zero;

			// RawImage for map
			var rawGo = GameObject.Find("AAAMinimap_Map");
			if (rawGo == null || rawGo.transform.parent != contentGo.transform)
			{
				rawGo = new GameObject("AAAMinimap_Map", typeof(RectTransform), typeof(RawImage));
				rawGo.transform.SetParent(contentGo.transform, false);
			}
			_mapRawImage = rawGo.GetComponent<RawImage>();
			_mapRawImage.raycastTarget = false;

			// Marker container
			var markerGo = GameObject.Find("AAAMinimap_Markers");
			if (markerGo == null || markerGo.transform.parent != contentGo.transform)
			{
				markerGo = new GameObject("AAAMinimap_Markers", typeof(RectTransform));
				markerGo.transform.SetParent(contentGo.transform, false);
			}
			_markerContainer = markerGo.GetComponent<RectTransform>();

			// Border overlay
			var borderGo = GameObject.Find("AAAMinimap_Border");
			if (borderGo == null || borderGo.transform.parent != _minimapRoot)
			{
				borderGo = new GameObject("AAAMinimap_Border", typeof(RectTransform), typeof(Image));
				borderGo.transform.SetParent(_minimapRoot, false);
			}
			_borderImage = borderGo.GetComponent<Image>();
			_borderImage.raycastTarget = false;

			// Click + pointer enter/exit interaction
			_eventTrigger = _maskImage.GetComponent<EventTrigger>();
			if (_eventTrigger == null) _eventTrigger = _maskImage.gameObject.AddComponent<EventTrigger>();
			_eventTrigger.triggers ??= new List<EventTrigger.Entry>();
			AddOrReplaceClickHandler(_eventTrigger, OnMinimapClicked);
			AddOrReplaceEnterHandler(_eventTrigger, OnPointerEnter);
			AddOrReplaceExitHandler(_eventTrigger, OnPointerExit);
		}
	}

	private void EnsureEventSystem()
	{
		if (FindObjectOfType<EventSystem>() == null)
		{
			var es = new GameObject("EventSystem", typeof(EventSystem), typeof(StandaloneInputModule));
			es.hideFlags = HideFlags.None;
		}
	}

	private void EnsureCameraAndRenderTexture()
	{
		if (_minimapCamera == null)
		{
			var camGo = GameObject.Find("AAAMinimap_Camera");
			if (camGo == null)
			{
				camGo = new GameObject("AAAMinimap_Camera", typeof(Camera));
				camGo.transform.SetParent(transform, false);
			}
			_minimapCamera = camGo.GetComponent<Camera>();
			_minimapCamera.orthographic = true;
			_minimapCamera.clearFlags = CameraClearFlags.SolidColor;
			_minimapCamera.backgroundColor = cameraBackgroundColor;
			_minimapCamera.cullingMask = ~0; // everything by default
			_minimapCamera.allowHDR = false;
			_minimapCamera.allowMSAA = false;
		}

		if (_renderTexture == null || _renderTexture.width != renderTextureSize)
		{
			CleanupRenderTexture();
			_renderTexture = new RenderTexture(renderTextureSize, renderTextureSize, 16, RenderTextureFormat.ARGB32)
			{
				useMipMap = false,
				antiAliasing = 1,
				wrapMode = TextureWrapMode.Clamp,
				filterMode = FilterMode.Bilinear,
				name = "AAAMinimap_RT"
			};
			_renderTexture.Create();
		}

		_minimapCamera.targetTexture = _renderTexture;
		if (_mapRawImage != null) _mapRawImage.texture = _renderTexture;

		UpdateWorldBounds();
		UpdateCameraAlignmentImmediate();
	}

	private void ApplyLayout()
	{
		if (_minimapRoot == null) return;

		_minimapRoot.anchorMin = new Vector2(1f, 0f);
		_minimapRoot.anchorMax = new Vector2(1f, 0f);
		_minimapRoot.pivot = pivot;
		_minimapRoot.sizeDelta = new Vector2(sizePixels, sizePixels);
		_minimapRoot.anchoredPosition = anchoredPosition;

		if (_canvasGroup != null) _canvasGroup.alpha = opacity;

		if (_maskImage != null)
		{
			var rt = _maskImage.rectTransform;
			rt.anchorMin = Vector2.zero;
			rt.anchorMax = Vector2.one;
			rt.offsetMin = Vector2.zero;
			rt.offsetMax = Vector2.zero;
		}

		if (_contentRoot != null)
		{
			var crt = _contentRoot;
			crt.anchorMin = Vector2.zero;
			crt.anchorMax = Vector2.one;
			crt.offsetMin = Vector2.zero;
			crt.offsetMax = Vector2.zero;
		}

		if (_mapRawImage != null)
		{
			var rt = _mapRawImage.rectTransform;
			rt.anchorMin = Vector2.zero;
			rt.anchorMax = Vector2.one;
			rt.offsetMin = Vector2.zero;
			rt.offsetMax = Vector2.zero;
		}

		if (_markerContainer != null)
		{
			var rt = _markerContainer;
			rt.anchorMin = Vector2.zero;
			rt.anchorMax = Vector2.one;
			rt.offsetMin = Vector2.zero;
			rt.offsetMax = Vector2.zero;
		}

		if (_borderImage != null)
		{
			var rt = _borderImage.rectTransform;
			rt.anchorMin = Vector2.zero;
			rt.anchorMax = Vector2.one;
			rt.offsetMin = Vector2.zero;
			rt.offsetMax = Vector2.zero;
		}
	}
	#endregion

	#region Map Sprite Generation
	private void RebuildMapSprites()
	{
		if (_maskImage == null || _borderImage == null) return;

		// Generate or assign mask sprite
		Sprite maskSprite = null;
		if (mapShape == MapShape.CustomSprite && mapCustomSprite != null)
		{
			maskSprite = mapCustomSprite;
		}
		else
		{
			maskSprite = GenerateShapeSprite(mapShape, Mathf.RoundToInt(sizePixels), mapFillColor, 0f, Color.clear, ref _generatedMaskTexture, ref _generatedMaskSprite);
		}
		_maskImage.sprite = maskSprite;
		_maskImage.type = Image.Type.Simple;
		_maskImage.color = mapFillColor;

		// Border sprite
		Sprite borderSprite = null;
		if (mapShape == MapShape.CustomSprite && mapCustomSprite != null)
		{
			borderSprite = mapCustomSprite;
		}
		else
		{
			borderSprite = GenerateShapeSprite(mapShape, Mathf.RoundToInt(sizePixels), Color.clear, mapBorderThickness, mapBorderColor, ref _generatedBorderTexture, ref _generatedBorderSprite);
		}
		_borderImage.sprite = borderSprite;
		_borderImage.type = Image.Type.Sliced;
		_borderImage.color = mapBorderColor;
	}

	private void CleanupGeneratedSprites()
	{
		if (_generatedMaskSprite != null) { DestroyImmediate(_generatedMaskSprite); _generatedMaskSprite = null; }
		if (_generatedBorderSprite != null) { DestroyImmediate(_generatedBorderSprite); _generatedBorderSprite = null; }
		if (_generatedMaskTexture != null) { DestroyImmediate(_generatedMaskTexture); _generatedMaskTexture = null; }
		if (_generatedBorderTexture != null) { DestroyImmediate(_generatedBorderTexture); _generatedBorderTexture = null; }
	}

	private Sprite GenerateShapeSprite(MapShape shape, int size, Color fill, float borderThickness, Color border, ref Texture2D cacheTex, ref Sprite cacheSprite)
	{
		if (size < 8) size = 8;
		if (cacheTex != null) { DestroyImmediate(cacheTex); cacheTex = null; }
		if (cacheSprite != null) { DestroyImmediate(cacheSprite); cacheSprite = null; }

		var tex = new Texture2D(size, size, TextureFormat.RGBA32, false)
		{
			wrapMode = TextureWrapMode.Clamp,
			filterMode = FilterMode.Bilinear
		};

		Color32[] pixels = new Color32[size * size];
		for (int i = 0; i < pixels.Length; i++) pixels[i] = new Color(0, 0, 0, 0);

		float half = (size - 1) / 2f;
		float radius = half;
		float innerRadius = Mathf.Max(0f, radius - borderThickness);

		// Precompute star polygon if needed
		Vector2[] starVerts = null;
		if (shape == MapShape.Star)
		{
			starVerts = BuildStarVertices(5, radius, radius * 0.5f, new Vector2(half, half));
		}

		for (int y = 0; y < size; y++)
		{
			for (int x = 0; x < size; x++)
			{
				int idx = y * size + x;
				bool inside = false;
				bool inBorder = false;

				switch (shape)
				{
					case MapShape.Circle:
					{
						float dx = x - half;
						float dy = y - half;
						float dist = Mathf.Sqrt(dx * dx + dy * dy);
						inside = dist <= radius + 0.001f;
						inBorder = borderThickness > 0f && dist >= innerRadius && dist <= radius;
						break;
					}
					case MapShape.Square:
					{
						inside = x >= 0 && y >= 0 && x < size && y < size;
						inBorder = borderThickness > 0f && (x <= borderThickness || y <= borderThickness || x >= size - 1 - borderThickness || y >= size - 1 - borderThickness);
						break;
					}
					case MapShape.Star:
					{
						if (starVerts != null)
						{
							inside = PointInPolygon(new Vector2(x, y), starVerts);
							if (borderThickness > 0f)
							{
								float distEdge = DistanceToPolygon(new Vector2(x, y), starVerts);
								inBorder = distEdge <= borderThickness + 0.5f;
							}
						}
						break;
					}
					case MapShape.CustomSprite:
					{
						inside = true; // Use full rect; border approximated as outline
						inBorder = borderThickness > 0f && (x <= borderThickness || y <= borderThickness || x >= size - 1 - borderThickness || y >= size - 1 - borderThickness);
						break;
					}
				}

				if (inside) pixels[idx] = inBorder ? (Color32)border : (Color32)fill;
			}
		}

		tex.SetPixels32(pixels);
		tex.Apply(false);

		var sprite = Sprite.Create(tex, new Rect(0, 0, size, size), new Vector2(0.5f, 0.5f), size);
		cacheTex = tex; cacheSprite = sprite; return sprite;
	}

	private Vector2[] BuildStarVertices(int points, float outerRadius, float innerRadius, Vector2 center)
	{
		var verts = new List<Vector2>();
		float angleStep = Mathf.PI / points;
		float angle = -Mathf.PI / 2f;
		for (int i = 0; i < points * 2; i++)
		{
			float r = (i % 2 == 0) ? outerRadius : innerRadius;
			float x = center.x + Mathf.Cos(angle) * r;
			float y = center.y + Mathf.Sin(angle) * r;
			verts.Add(new Vector2(x, y));
			angle += angleStep;
		}
		return verts.ToArray();
	}

	private bool PointInPolygon(Vector2 p, Vector2[] poly)
	{
		bool inside = false;
		for (int i = 0, j = poly.Length - 1; i < poly.Length; j = i++)
		{
			bool intersect = ((poly[i].y > p.y) != (poly[j].y < p.y)) &&
				(p.x < (poly[j].x - poly[i].x) * (p.y - poly[i].y) / (poly[j].y - poly[i].y + 0.00001f) + poly[i].x);
			if (intersect) inside = !inside;
		}
		return inside;
	}

	private float DistanceToPolygon(Vector2 p, Vector2[] poly)
	{
		float minDist = float.MaxValue;
		for (int i = 0; i < poly.Length; i++)
		{
			Vector2 a = poly[i];
			Vector2 b = poly[(i + 1) % poly.Length];
			float dist = DistancePointToSegment(p, a, b);
			if (dist < minDist) minDist = dist;
		}
		return minDist;
	}

	private float DistancePointToSegment(Vector2 p, Vector2 a, Vector2 b)
	{
		Vector2 ab = b - a;
		float t = Vector2.Dot(p - a, ab) / (ab.sqrMagnitude + 1e-6f);
		t = Mathf.Clamp01(t);
		Vector2 proj = a + t * ab;
		return Vector2.Distance(p, proj);
	}
	#endregion

	#region Camera & World Mapping
	private void UpdateWorldBounds()
	{
		if (autoFitWorldBounds)
		{
			Bounds bounds;
			if (TryGetTerrainBounds(out bounds)) _worldBounds = bounds;
			else if (TryGetSceneRendererBounds(out bounds)) _worldBounds = bounds;
			else _worldBounds = new Bounds(Vector3.zero, new Vector3(manualWorldSizeX, 0f, manualWorldSizeZ));
		}
		else
		{
			_worldBounds = new Bounds(Vector3.zero, new Vector3(manualWorldSizeX, 0f, manualWorldSizeZ));
		}
	}

	private bool TryGetTerrainBounds(out Bounds bounds)
	{
		var terrain = FindObjectOfType<Terrain>();
		if (terrain != null && terrain.terrainData != null)
		{
			var size = terrain.terrainData.size;
			var pos = terrain.transform.position;
			bounds = new Bounds(pos + new Vector3(size.x * 0.5f, 0f, size.z * 0.5f), new Vector3(size.x, 0f, size.z));
			return true;
		}
		bounds = default; return false;
	}

	private bool TryGetSceneRendererBounds(out Bounds bounds)
	{
		var renderers = FindObjectsOfType<Renderer>();
		if (renderers.Length == 0) { bounds = default; return false; }
		var aggregate = new Bounds(renderers[0].bounds.center, Vector3.zero);
		foreach (var r in renderers) aggregate.Encapsulate(r.bounds);
		aggregate.size = new Vector3(aggregate.size.x, 0f, aggregate.size.z);
		bounds = aggregate; return true;
	}

	private void UpdateCameraAlignmentImmediate()
	{
		if (_minimapCamera == null) return;
		Vector3 worldCenter = _worldBounds.center;
		if (player.playerTransform != null && cameraFollowsPlayer)
			worldCenter = new Vector3(player.playerTransform.position.x, worldCenter.y, player.playerTransform.position.z);
		_minimapCamera.transform.position = new Vector3(worldCenter.x, cameraHeight, worldCenter.z);
		_minimapCamera.transform.rotation = Quaternion.Euler(90f, 0f, 0f);
		float sizeX = Mathf.Max(1f, _worldBounds.size.x * 0.5f) * cameraSizeScale;
		float sizeZ = Mathf.Max(1f, _worldBounds.size.z * 0.5f) * cameraSizeScale;
		_minimapCamera.orthographicSize = Mathf.Max(sizeX, sizeZ);
	}

	private void UpdateCameraFollow()
	{
		if (_minimapCamera == null) return;
		if (player.playerTransform != null && cameraFollowsPlayer)
		{
			var p = player.playerTransform.position;
			_minimapCamera.transform.position = new Vector3(p.x, cameraHeight, p.z);
		}
		_minimapCamera.backgroundColor = cameraBackgroundColor;
		float sizeX = Mathf.Max(1f, _worldBounds.size.x * 0.5f) * cameraSizeScale;
		float sizeZ = Mathf.Max(1f, _worldBounds.size.z * 0.5f) * cameraSizeScale;
		_minimapCamera.orthographicSize = Mathf.Max(sizeX, sizeZ);
	}

	private Vector2 WorldToMinimapLocalPosition(Vector3 worldPosition)
	{
		Vector3 center = _worldBounds.center;
		Vector3 size = _worldBounds.size;
		if (size.x < 0.001f) size.x = 0.001f;
		if (size.z < 0.001f) size.z = 0.001f;

		worldPosition.x += worldOffsetXZ.x;
		worldPosition.z += worldOffsetXZ.y;

		float nx = Mathf.InverseLerp(center.x - size.x * 0.5f, center.x + size.x * 0.5f, worldPosition.x);
		float nz = Mathf.InverseLerp(center.z - size.z * 0.5f, center.z + size.z * 0.5f, worldPosition.z);

		var rect = _minimapRoot.rect;
		float lx = (nx - 0.5f) * rect.width;
		float ly = (nz - 0.5f) * rect.height;
		return new Vector2(lx, ly);
	}

	private static Vector2 Rotate2D(Vector2 v, float degrees)
	{
		float rad = degrees * Mathf.Deg2Rad;
		float cos = Mathf.Cos(rad);
		float sin = Mathf.Sin(rad);
		return new Vector2(v.x * cos - v.y * sin, v.x * sin + v.y * cos);
	}
	#endregion

	#region Marker and Waypoint Building
	private void RebuildAllMarkers()
	{
		foreach (var m in _activeMarkers) RecycleMarker(m);
		_activeMarkers.Clear();
		_runtimeStaticMarkers.Clear();
		_runtimeWaypoints.Clear();
		_playerMarkerUI = null;

		// Player marker
		_playerMarkerUI = AcquireMarker(MarkerKind.Player);
		ApplyMarkerVisual(_playerMarkerUI, player.visual);
		_activeMarkers.Add(_playerMarkerUI);

		// Static markers
		for (int i = 0; i < staticMarkers.Count; i++)
		{
			var def = staticMarkers[i];
			var ui = AcquireMarker(MarkerKind.Static);
			ApplyMarkerVisual(ui, def.visual);
			var runtime = new RuntimeStaticMarker { def = def, ui = ui };
			ui.backingData = runtime;
			_runtimeStaticMarkers.Add(runtime);
			_activeMarkers.Add(ui);
		}

		// Waypoints
		for (int i = 0; i < waypoints.Count; i++)
		{
			var def = waypoints[i];
			ApplyWaypointTypeDefaults(def);
			var ui = AcquireMarker(MarkerKind.Waypoint);
			ApplyMarkerVisual(ui, def.visual);
			var runtime = new RuntimeWaypoint { def = def, ui = ui, triggered = false };
			ui.backingData = runtime;
			_runtimeWaypoints.Add(runtime);
			_activeMarkers.Add(ui);
		}
	}

	private void ApplyWaypointTypeDefaults(WaypointDefinition def)
	{
		switch (def.type)
		{
			case WaypointType.Mission:
				if (!def.visual.useCustomIcon)
				{
					def.visual.shape = MapShape.Star;
					def.visual.color = new Color(1f, 0.5f, 0.1f, 1f);
					def.visual.borderColor = new Color(0.4f, 0.1f, 0f, 1f);
				}
				break;
			case WaypointType.Tutorial:
				if (!def.visual.useCustomIcon)
				{
					def.visual.shape = MapShape.Circle;
					def.visual.color = new Color(0.2f, 0.9f, 0.9f, 1f);
					def.visual.borderColor = new Color(0f, 0.3f, 0.3f, 1f);
				}
				break;
		}
	}

	private MarkerUI AcquireMarker(MarkerKind kind)
	{
		MarkerUI ui = _markerPool.Count > 0 ? _markerPool.Dequeue() : CreateMarkerUI();
		ui.kind = kind;
		ui.root.SetActive(true);
		ui.offscreenRoot.SetActive(false);
		return ui;
	}

	private void RecycleMarker(MarkerUI ui)
	{
		if (ui == null) return;
		ui.root.SetActive(false);
		ui.labelText.text = string.Empty;
		ui.image.sprite = null;
		ui.image.color = Color.clear;
		ui.offscreenImage.sprite = null;
		ui.backingData = null;
		_markerPool.Enqueue(ui);
	}

	private MarkerUI CreateMarkerUI()
	{
		var go = new GameObject("AAAMinimap_Marker", typeof(RectTransform));
		go.transform.SetParent(_markerContainer, false);
		var rt = go.GetComponent<RectTransform>();
		rt.sizeDelta = new Vector2(18, 18);

		var imgGo = new GameObject("Icon", typeof(RectTransform), typeof(Image));
		imgGo.transform.SetParent(go.transform, false);
		var imgRt = imgGo.GetComponent<RectTransform>();
		imgRt.anchorMin = imgRt.anchorMax = new Vector2(0.5f, 0.5f);
		imgRt.pivot = new Vector2(0.5f, 0.5f);
		imgRt.sizeDelta = new Vector2(18, 18);
		var img = imgGo.GetComponent<Image>();
		img.raycastTarget = false;

		var labelGo = new GameObject("Label", typeof(RectTransform), typeof(Text));
		labelGo.transform.SetParent(go.transform, false);
		var labelRt = labelGo.GetComponent<RectTransform>();
		labelRt.anchorMin = labelRt.anchorMax = new Vector2(0.5f, 0f);
		labelRt.pivot = new Vector2(0.5f, 1f);
		labelRt.anchoredPosition = new Vector2(0, -4);
		var text = labelGo.GetComponent<Text>();
		text.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
		text.alignment = TextAnchor.UpperCenter;
		text.raycastTarget = false;

		// Offscreen indicator
		var offGo = new GameObject("Offscreen", typeof(RectTransform));
		offGo.transform.SetParent(_markerContainer, false);
		var offRt = offGo.GetComponent<RectTransform>();
		offRt.sizeDelta = new Vector2(18, 18);
		var offImgGo = new GameObject("Icon", typeof(RectTransform), typeof(Image));
		offImgGo.transform.SetParent(offGo.transform, false);
		var offImgRt = offImgGo.GetComponent<RectTransform>();
		offImgRt.anchorMin = offImgRt.anchorMax = new Vector2(0.5f, 0.5f);
		offImgRt.pivot = new Vector2(0.5f, 0.5f);
		offImgRt.sizeDelta = new Vector2(18, 18);
		var offImg = offImgGo.GetComponent<Image>();
		offImg.raycastTarget = false;
		offGo.SetActive(false);

		return new MarkerUI
		{
			root = go,
			rectTransform = rt,
			image = img,
			labelText = text,
			offscreenRoot = offGo,
			offscreenRect = offRt,
			offscreenImage = offImg
		};
	}

	private void ApplyMarkerVisual(MarkerUI ui, MarkerVisual visual)
	{
		ui.rectTransform.sizeDelta = new Vector2(visual.size, visual.size);
		ui.image.rectTransform.sizeDelta = new Vector2(visual.size, visual.size);
		ui.image.color = visual.color;
		ui.labelText.text = string.IsNullOrEmpty(visual.label) ? string.Empty : visual.label;
		ui.labelText.fontSize = visual.labelFontSize;
		ui.labelText.color = visual.labelColor;

		if (visual.useCustomIcon && visual.customSprite != null)
		{
			ui.image.sprite = visual.customSprite;
			ui.image.type = Image.Type.Simple;
		}
		else
		{
			Texture2D tex = null; Sprite spr = null;
			var s = Mathf.RoundToInt(Mathf.Max(8f, visual.size));
			ui.image.sprite = GenerateShapeSprite(visual.shape, s, visual.color, visual.borderThickness, visual.borderColor, ref tex, ref spr);
			ui.image.type = Image.Type.Simple;
		}
	}
	#endregion

	#region Per-Frame Updates
	private void UpdateAllMarkerVisualsImmediate()
	{
		UpdateMarkerPosition(_playerMarkerUI, player.playerTransform != null ? player.playerTransform.position : Vector3.zero, OffscreenIndicatorStyle.None, true);
		foreach (var s in _runtimeStaticMarkers)
		{
			Vector3 pos = s.def.useTransform && s.def.target != null ? s.def.target.position : s.def.worldPosition;
			UpdateMarkerPosition(s.ui, pos, s.def.offscreenIndicator, false);
		}
		foreach (var w in _runtimeWaypoints)
		{
			Vector3 pos = w.def.target != null ? w.def.target.position : w.def.worldPosition;
			UpdateMarkerPosition(w.ui, pos, w.def.offscreenIndicator, false);
		}
	}

	private void UpdateMarkers()
	{
		if (_playerMarkerUI != null)
		{
			Vector3 playerPos = player.playerTransform != null ? player.playerTransform.position : Vector3.zero;
			UpdateMarkerPosition(_playerMarkerUI, playerPos, OffscreenIndicatorStyle.None, true);
			UpdatePlayerArrowRotation();
		}

		for (int i = 0; i < _runtimeStaticMarkers.Count; i++)
		{
			var m = _runtimeStaticMarkers[i];
			Vector3 pos = m.def.useTransform && m.def.target != null ? m.def.target.position : m.def.worldPosition;
			UpdateMarkerPosition(m.ui, pos, m.def.offscreenIndicator, false);
		}
	}

	private void UpdateWaypoints()
	{
		if (player.playerTransform == null) return;
		var p = player.playerTransform.position;
		for (int i = _runtimeWaypoints.Count - 1; i >= 0; i--)
		{
			var w = _runtimeWaypoints[i];
			Vector3 pos = w.def.target != null ? w.def.target.position : w.def.worldPosition;
			UpdateMarkerPosition(w.ui, pos, w.def.offscreenIndicator, false);

			float dist = Vector3.Distance(new Vector3(p.x, 0, p.z), new Vector3(pos.x, 0, pos.z));
			if (dist <= w.def.triggerRadius)
			{
				if (!w.triggered || !w.def.triggerOnce)
				{
					w.triggered = true;
					SafeInvoke(w.def.onReached);
					if (!string.IsNullOrEmpty(w.def.popupText)) ShowPopup(w.def.popupText);
				}

				if (w.def.destroyOnReach)
				{
					RecycleMarker(w.ui);
					_activeMarkers.Remove(w.ui);
					_runtimeWaypoints.RemoveAt(i);
				}
			}
		}
	}

	private void UpdatePlayerArrowRotation()
	{
		if (player.playerTransform == null || _playerMarkerUI == null) return;
		if (player.rotateMapWithPlayer)
		{
			float yaw = player.playerTransform.eulerAngles.y;
			_playerMarkerUI.image.rectTransform.localEulerAngles = new Vector3(0, 0, -yaw);
		}
		else if (player.rotateArrowWithPlayer)
		{
			_playerMarkerUI.image.rectTransform.localEulerAngles = new Vector3(0, 0, -player.playerTransform.eulerAngles.y);
		}
	}

	private void UpdateMarkerPosition(MarkerUI ui, Vector3 worldPos, OffscreenIndicatorStyle offscreenStyle, bool isPlayer)
	{
		if (ui == null) return;
		var local = WorldToMinimapLocalPosition(worldPos);
		var rect = _minimapRoot.rect;
		bool inside = Mathf.Abs(local.x) <= rect.width * 0.5f && Mathf.Abs(local.y) <= rect.height * 0.5f;

		// Distance culling and scaling
		if (!isPlayer && markerMaxDistance > 0f && player.playerTransform != null)
		{
			float dist = Vector3.Distance(new Vector3(player.playerTransform.position.x, 0, player.playerTransform.position.z), new Vector3(worldPos.x, 0, worldPos.z));
			if (dist > markerMaxDistance)
			{
				ui.root.SetActive(false);
				ui.offscreenRoot.SetActive(false);
				return;
			}
			if (scaleMarkersWithDistance)
			{
				float t = Mathf.InverseLerp(markerMaxDistance, 0f, dist);
				float s = Mathf.Lerp(markerMinScaleAtMaxDistance, 1f, t);
				ui.rectTransform.localScale = new Vector3(s, s, 1f);
			}
		}
		else
		{
			ui.rectTransform.localScale = Vector3.one;
		}

		if (inside)
		{
			ui.rectTransform.anchoredPosition = local;
			ui.root.SetActive(true);
			ui.offscreenRoot.SetActive(false);
		}
		else
		{
			if (clampMarkersToEdge)
			{
				Vector2 clamped = ClampToShape(local, rect);
				ui.rectTransform.anchoredPosition = clamped;
				ui.root.SetActive(true);
				ui.offscreenRoot.SetActive(false);
			}
			else
			{
				ui.root.SetActive(false);
				if (offscreenStyle != OffscreenIndicatorStyle.None)
				{
					ui.offscreenRoot.SetActive(true);
					Vector2 edge = ClampToShape(local, rect);
					ui.offscreenRect.anchoredPosition = edge;
					float angle = Mathf.Atan2(local.y, local.x) * Mathf.Rad2Deg;
					ui.offscreenImage.rectTransform.localEulerAngles = new Vector3(0, 0, angle - 90f);
					ApplyOffscreenVisual(ui, offscreenStyle, isPlayer);
				}
				else
				{
					ui.offscreenRoot.SetActive(false);
				}
			}
		}
	}

	private Vector2 ClampToShape(Vector2 local, Rect rect)
	{
		if (mapShape == MapShape.Circle || mapShape == MapShape.Star)
		{
			float rx = rect.width * 0.5f - 4f;
			float ry = rect.height * 0.5f - 4f;
			Vector2 v = local;
			float angle = Mathf.Atan2(v.y, v.x);
			return new Vector2(Mathf.Cos(angle) * rx, Mathf.Sin(angle) * ry);
		}
		else
		{
			float hx = rect.width * 0.5f - 4f;
			float hy = rect.height * 0.5f - 4f;
			return new Vector2(Mathf.Clamp(local.x, -hx, hx), Mathf.Clamp(local.y, -hy, hy));
		}
	}

	private void ApplyOffscreenVisual(MarkerUI ui, OffscreenIndicatorStyle style, bool isPlayer)
	{
		switch (style)
		{
			case OffscreenIndicatorStyle.Arrow:
				ui.offscreenImage.sprite = BuildArrowSprite();
				ui.offscreenImage.color = isPlayer ? player.visual.color : ui.image.color;
				ui.offscreenRect.sizeDelta = new Vector2(18, 18);
				break;
			case OffscreenIndicatorStyle.Dot:
				Texture2D t = null; Sprite s = null;
				ui.offscreenImage.sprite = GenerateShapeSprite(MapShape.Circle, 18, ui.image.color, 0f, Color.clear, ref t, ref s);
				ui.offscreenImage.color = ui.image.color;
				ui.offscreenRect.sizeDelta = new Vector2(12, 12);
				break;
		}
	}

	private Sprite BuildArrowSprite()
	{
		int size = 32;
		var tex = new Texture2D(size, size, TextureFormat.RGBA32, false)
		{
			wrapMode = TextureWrapMode.Clamp,
			filterMode = FilterMode.Bilinear
		};
		Color32[] pixels = new Color32[size * size];
		for (int i = 0; i < pixels.Length; i++) pixels[i] = new Color(0, 0, 0, 0);

		Vector2 p0 = new Vector2(size * 0.5f, size * 0.1f);
		Vector2 p1 = new Vector2(size * 0.9f, size * 0.9f);
		Vector2 p2 = new Vector2(size * 0.1f, size * 0.9f);
		for (int y = 0; y < size; y++)
		{
			for (int x = 0; x < size; x++)
			{
				int idx = y * size + x;
				if (PointInTriangle(new Vector2(x + 0.5f, y + 0.5f), p0, p1, p2)) pixels[idx] = Color.white;
			}
		}
		tex.SetPixels32(pixels);
		tex.Apply(false);
		return Sprite.Create(tex, new Rect(0, 0, size, size), new Vector2(0.5f, 0.5f), size);
	}

	private bool PointInTriangle(Vector2 p, Vector2 p0, Vector2 p1, Vector2 p2)
	{
		float s = p0.y * p2.x - p0.x * p2.y + (p2.y - p0.y) * p.x + (p0.x - p2.x) * p.y;
		float t = p0.x * p1.y - p0.y * p1.x + (p0.y - p1.y) * p.x + (p1.x - p0.x) * p.y;
		if ((s < 0) != (t < 0)) return false;
		float A = -p1.y * p2.x + p0.y * (p2.x - p1.x) + p0.x * (p1.y - p2.y) + p1.x * p2.y;
		if (A < 0.0) { s = -s; t = -t; A = -A; }
		return s > 0 && t > 0 && (s + t) <= A;
	}
	#endregion

	#region Click & Input
	private void AddOrReplaceClickHandler(EventTrigger trigger, Action<BaseEventData> action)
	{
		for (int i = trigger.triggers.Count - 1; i >= 0; i--)
		{
			if (trigger.triggers[i].eventID == EventTriggerType.PointerClick) trigger.triggers.RemoveAt(i);
		}
		var entry = new EventTrigger.Entry { eventID = EventTriggerType.PointerClick };
		entry.callback = new EventTrigger.TriggerEvent();
		entry.callback.AddListener(new UnityAction<BaseEventData>(action));
		trigger.triggers.Add(entry);
	}

	private void AddOrReplaceEnterHandler(EventTrigger trigger, Action<BaseEventData> action)
	{
		for (int i = trigger.triggers.Count - 1; i >= 0; i--)
		{
			if (trigger.triggers[i].eventID == EventTriggerType.PointerEnter) trigger.triggers.RemoveAt(i);
		}
		var entry = new EventTrigger.Entry { eventID = EventTriggerType.PointerEnter };
		entry.callback = new EventTrigger.TriggerEvent();
		entry.callback.AddListener(new UnityAction<BaseEventData>(action));
		trigger.triggers.Add(entry);
	}

	private void AddOrReplaceExitHandler(EventTrigger trigger, Action<BaseEventData> action)
	{
		for (int i = trigger.triggers.Count - 1; i >= 0; i--)
		{
			if (trigger.triggers[i].eventID == EventTriggerType.PointerExit) trigger.triggers.RemoveAt(i);
		}
		var entry = new EventTrigger.Entry { eventID = EventTriggerType.PointerExit };
		entry.callback = new EventTrigger.TriggerEvent();
		entry.callback.AddListener(new UnityAction<BaseEventData>(action));
		trigger.triggers.Add(entry);
	}

	private void OnPointerEnter(BaseEventData _)
	{
		_isPointerOver = true;
	}

	private void OnPointerExit(BaseEventData _)
	{
		_isPointerOver = false;
	}

	private void OnMinimapClicked(BaseEventData eventData)
	{
		if (!clickToCreateWaypoints || _minimapRoot == null) return;
		var ped = eventData as PointerEventData; if (ped == null) return;
		RectTransformUtility.ScreenPointToLocalPointInRectangle(_minimapRoot, ped.position, _canvas.renderMode == RenderMode.ScreenSpaceOverlay ? null : _canvas.worldCamera, out var localPoint);
		Vector3 world = MinimapLocalToWorld(localPoint);
		CreateWaypoint(world, defaultClickWaypoint);
	}

	private Vector3 MinimapLocalToWorld(Vector2 local)
	{
		var rect = _minimapRoot.rect;
		Vector2 normalized = new Vector2(local.x / rect.width + 0.5f, local.y / rect.height + 0.5f);
		Vector3 center = _worldBounds.center; Vector3 size = _worldBounds.size;
		float worldX = Mathf.Lerp(center.x - size.x * 0.5f, center.x + size.x * 0.5f, normalized.x) - worldOffsetXZ.x;
		float worldZ = Mathf.Lerp(center.z - size.z * 0.5f, center.z + size.z * 0.5f, normalized.y) - worldOffsetXZ.y;
		if (player.playerTransform != null && player.rotateMapWithPlayer)
		{
			float yaw = player.playerTransform.eulerAngles.y;
			Vector2 rotated = Rotate2D(local, -yaw);
			Vector2 normalizedRot = new Vector2(rotated.x / rect.width + 0.5f, rotated.y / rect.height + 0.5f);
			worldX = Mathf.Lerp(center.x - size.x * 0.5f, center.x + size.x * 0.5f, normalizedRot.x) - worldOffsetXZ.x;
			worldZ = Mathf.Lerp(center.z - size.z * 0.5f, center.z + size.z * 0.5f, normalizedRot.y) - worldOffsetXZ.y;
		}
		return new Vector3(worldX, 0f, worldZ);
	}

	private void HandleInput()
	{
		if (!Application.isPlaying) return;
		if (allowToggleKey && Input.GetKeyDown(toggleKey))
		{
			bool nowVisible = _canvasGroup.alpha <= 0.01f;
			_canvasGroup.alpha = nowVisible ? opacity : 0f;
			_canvasGroup.blocksRaycasts = nowVisible;
		}

		if (!enableZoomControls) return;
		bool changed = false;
		if (scrollZoom && _isPointerOver)
		{
			float delta = Input.mouseScrollDelta.y;
			if (Mathf.Abs(delta) > 0.0001f)
			{
				cameraSizeScale = Mathf.Clamp(cameraSizeScale * (1f - delta * 0.1f), minZoom, maxZoom);
				changed = true;
			}
		}
		if (Input.GetKeyDown(zoomInKey)) { cameraSizeScale = Mathf.Clamp(cameraSizeScale - zoomStep, minZoom, maxZoom); changed = true; }
		if (Input.GetKeyDown(zoomOutKey)) { cameraSizeScale = Mathf.Clamp(cameraSizeScale + zoomStep, minZoom, maxZoom); changed = true; }
		if (changed) UpdateCameraFollow();
	}
	#endregion

	#region Waypoint & Popup API
	public void CreateWaypoint(Vector3 worldPosition, WaypointDefinition template)
	{
		var def = new WaypointDefinition
		{
			id = Guid.NewGuid().ToString("N").Substring(0, 8),
			target = null,
			worldPosition = worldPosition,
			triggerRadius = template.triggerRadius,
			offscreenIndicator = template.offscreenIndicator,
			destroyOnReach = template.destroyOnReach,
			triggerOnce = template.triggerOnce,
			type = template.type,
			popupText = template.popupText,
			onReached = new UnityEvent(),
			visual = CloneVisual(template.visual)
		};
		waypoints.Add(def);
		ApplyWaypointTypeDefaults(def);
		var ui = AcquireMarker(MarkerKind.Waypoint);
		ApplyMarkerVisual(ui, def.visual);
		var runtime = new RuntimeWaypoint { def = def, ui = ui, triggered = false };
		runtime.ui.backingData = runtime;
		_runtimeWaypoints.Add(runtime);
		_activeMarkers.Add(ui);
	}

	private MarkerVisual CloneVisual(MarkerVisual src)
	{
		return new MarkerVisual
		{
			shape = src.shape,
			customSprite = src.customSprite,
			useCustomIcon = src.useCustomIcon,
			color = src.color,
			borderColor = src.borderColor,
			size = src.size,
			borderThickness = src.borderThickness,
			label = src.label,
			labelColor = src.labelColor,
			labelFontSize = src.labelFontSize
		};
	}

	public void ShowPopup(string message, float seconds = 2.5f)
	{
		var popup = _popupPool.Count > 0 ? _popupPool.Dequeue() : CreatePopupUI();
		popup.text.text = message;
		popup.timeRemaining = seconds;
		popup.root.SetActive(true);
		_activePopups.Add(popup);
		LayoutPopups();
	}

	private PopupUI CreatePopupUI()
	{
		var go = new GameObject("AAAMinimap_Popup", typeof(RectTransform));
		go.transform.SetParent(_minimapRoot, false);
		var rt = go.GetComponent<RectTransform>();
		rt.anchorMin = new Vector2(0.5f, 1f);
		rt.anchorMax = new Vector2(0.5f, 1f);
		rt.pivot = new Vector2(0.5f, 0f);
		rt.anchoredPosition = new Vector2(0, 10f);
		rt.sizeDelta = new Vector2(sizePixels, 28f);

		var bgGo = new GameObject("BG", typeof(RectTransform), typeof(Image));
		bgGo.transform.SetParent(go.transform, false);
		var bgRt = bgGo.GetComponent<RectTransform>();
		bgRt.anchorMin = new Vector2(0f, 0f);
		bgRt.anchorMax = new Vector2(1f, 1f);
		bgRt.offsetMin = new Vector2(0, 0);
		bgRt.offsetMax = new Vector2(0, 0);
		var bg = bgGo.GetComponent<Image>();
		bg.color = new Color(0f, 0f, 0f, 0.75f);

		var textGo = new GameObject("Text", typeof(RectTransform), typeof(Text));
		textGo.transform.SetParent(bgGo.transform, false);
		var textRt = textGo.GetComponent<RectTransform>();
		textRt.anchorMin = new Vector2(0f, 0f);
		textRt.anchorMax = new Vector2(1f, 1f);
		textRt.offsetMin = new Vector2(8, 4);
		textRt.offsetMax = new Vector2(-8, -4);
		var text = textGo.GetComponent<Text>();
		text.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
		text.alignment = TextAnchor.MiddleCenter;
		text.color = Color.white;
		text.resizeTextForBestFit = true;
		text.resizeTextMinSize = 10;
		text.resizeTextMaxSize = 20;

		return new PopupUI { root = go, rectTransform = rt, background = bg, text = text, timeRemaining = 0f };
	}

	private void UpdatePopups(float dt)
	{
		for (int i = _activePopups.Count - 1; i >= 0; i--)
		{
			var p = _activePopups[i];
			p.timeRemaining -= dt;
			if (p.timeRemaining <= 0f)
			{
				p.root.SetActive(false);
				_activePopups.RemoveAt(i);
				_popupPool.Enqueue(p);
			}
		}
		LayoutPopups();
	}

	private void LayoutPopups()
	{
		float y = 10f;
		foreach (var p in _activePopups)
		{
			p.rectTransform.anchoredPosition = new Vector2(0, y);
			y += p.rectTransform.sizeDelta.y + 6f;
		}
	}
	#endregion

	#region Public API - Static Markers & Waypoints
	public void AddStaticMarker(Transform target, MarkerVisual visual, OffscreenIndicatorStyle offscreen = OffscreenIndicatorStyle.Arrow)
	{
		var def = new StaticMarkerDefinition
		{
			name = target != null ? target.name : "Static",
			useTransform = true,
			target = target,
			worldPosition = Vector3.zero,
			offscreenIndicator = offscreen,
			visual = visual
		};
		staticMarkers.Add(def);
		var ui = AcquireMarker(MarkerKind.Static);
		ApplyMarkerVisual(ui, def.visual);
		var runtime = new RuntimeStaticMarker { def = def, ui = ui };
		ui.backingData = runtime;
		_runtimeStaticMarkers.Add(runtime);
		_activeMarkers.Add(ui);
	}

	public void AddStaticMarker(Vector3 worldPosition, MarkerVisual visual, OffscreenIndicatorStyle offscreen = OffscreenIndicatorStyle.Arrow)
	{
		var def = new StaticMarkerDefinition
		{
			name = "Static",
			useTransform = false,
			target = null,
			worldPosition = worldPosition,
			offscreenIndicator = offscreen,
			visual = visual
		};
		staticMarkers.Add(def);
		var ui = AcquireMarker(MarkerKind.Static);
		ApplyMarkerVisual(ui, def.visual);
		var runtime = new RuntimeStaticMarker { def = def, ui = ui };
		ui.backingData = runtime;
		_runtimeStaticMarkers.Add(runtime);
		_activeMarkers.Add(ui);
	}

	public void AddWaypoint(Transform target, WaypointDefinition template)
	{
		var def = new WaypointDefinition
		{
			id = Guid.NewGuid().ToString("N").Substring(0, 8),
			target = target,
			worldPosition = Vector3.zero,
			triggerRadius = template.triggerRadius,
			offscreenIndicator = template.offscreenIndicator,
			destroyOnReach = template.destroyOnReach,
			triggerOnce = template.triggerOnce,
			type = template.type,
			popupText = template.popupText,
			onReached = new UnityEvent(),
			visual = CloneVisual(template.visual)
		};
		waypoints.Add(def);
		ApplyWaypointTypeDefaults(def);
		var ui = AcquireMarker(MarkerKind.Waypoint);
		ApplyMarkerVisual(ui, def.visual);
		var runtime = new RuntimeWaypoint { def = def, ui = ui, triggered = false };
		ui.backingData = runtime;
		_runtimeWaypoints.Add(runtime);
		_activeMarkers.Add(ui);
	}

	public void ClearWaypoints()
	{
		for (int i = _runtimeWaypoints.Count - 1; i >= 0; i--)
		{
			var w = _runtimeWaypoints[i];
			RecycleMarker(w.ui);
			_activeMarkers.Remove(w.ui);
		}
		_runtimeWaypoints.Clear();
		waypoints.Clear();
	}
	#endregion

	#region Overlays & Rotation
	private void EnsureOverlays()
	{
		if (showNorthIndicator)
		{
			if (_northArrowImage == null)
			{
				var northGo = GameObject.Find("AAAMinimap_NorthArrow");
				if (northGo == null || northGo.transform.parent != _minimapRoot)
				{
					northGo = new GameObject("AAAMinimap_NorthArrow", typeof(RectTransform), typeof(Image));
					northGo.transform.SetParent(_minimapRoot, false);
				}
				_northArrowImage = northGo.GetComponent<Image>();
				_northArrowImage.sprite = BuildArrowSprite();
				_northArrowImage.color = northIndicatorColor;
				var rt = _northArrowImage.rectTransform;
				rt.anchorMin = rt.anchorMax = new Vector2(0.5f, 1f);
				rt.pivot = new Vector2(0.5f, 0.5f);
				rt.anchoredPosition = new Vector2(0, 8f);
				rt.sizeDelta = new Vector2(14, 14);
			}
		}
		else if (_northArrowImage != null)
		{
			DestroyImmediate(_northArrowImage.gameObject);
			_northArrowImage = null;
		}

		if (showGridOverlay)
		{
			if (_gridOverlay == null)
			{
				var gridGo = GameObject.Find("AAAMinimap_Grid");
				if (gridGo == null || gridGo.transform.parent != _contentRoot)
				{
					gridGo = new GameObject("AAAMinimap_Grid", typeof(RectTransform), typeof(RawImage));
					gridGo.transform.SetParent(_contentRoot, false);
				}
				_gridOverlay = gridGo.GetComponent<RawImage>();
				_gridOverlay.raycastTarget = false;
				var rt = _gridOverlay.rectTransform; rt.anchorMin = Vector2.zero; rt.anchorMax = Vector2.one; rt.offsetMin = Vector2.zero; rt.offsetMax = Vector2.zero;
			}
			if (_gridTexture == null) _gridTexture = GenerateGridTexture(256, gridColor);
			_gridOverlay.texture = _gridTexture;
			_gridOverlay.color = Color.white;
		}
		else if (_gridOverlay != null)
		{
			DestroyImmediate(_gridOverlay.gameObject);
			_gridOverlay = null;
		}
	}

	private Texture2D GenerateGridTexture(int size, Color lineColor)
	{
		var tex = new Texture2D(size, size, TextureFormat.RGBA32, false) { wrapMode = TextureWrapMode.Clamp, filterMode = FilterMode.Bilinear };
		var px = new Color32[size * size];
		Color32 clear = new Color(0, 0, 0, 0);
		for (int i = 0; i < px.Length; i++) px[i] = clear;
		for (int i = 0; i < size; i++)
		{
			px[i] = lineColor; // top row
			px[(size - 1) * size + i] = lineColor; // bottom row
			px[i * size] = lineColor; // left col
			px[i * size + (size - 1)] = lineColor; // right col
		}
		tex.SetPixels32(px); tex.Apply(false); return tex;
	}

	private void UpdateMapRotation()
	{
		if (_contentRoot == null) return;
		if (player.playerTransform != null && player.rotateMapWithPlayer)
		{
			float yaw = player.playerTransform.eulerAngles.y;
			_contentRoot.localEulerAngles = new Vector3(0, 0, yaw);
		}
		else
		{
			_contentRoot.localEulerAngles = Vector3.zero;
		}
	}

	private void UpdateNorthArrow()
	{
		if (_northArrowImage == null) return;
		float yaw = (player.playerTransform != null && player.rotateMapWithPlayer) ? player.playerTransform.eulerAngles.y : 0f;
		_northArrowImage.rectTransform.localEulerAngles = new Vector3(0, 0, -yaw);
	}
	#endregion

	#region Utilities
	private void SafeInvoke(UnityEvent evt)
	{
		try { evt?.Invoke(); } catch (Exception e) { Debug.LogException(e); }
	}

	private void CleanupRenderTexture()
	{
		if (_renderTexture != null)
		{
			if (_minimapCamera != null && _minimapCamera.targetTexture == _renderTexture) _minimapCamera.targetTexture = null;
			_renderTexture.Release();
			DestroyImmediate(_renderTexture);
			_renderTexture = null;
		}
	}
	#endregion
}