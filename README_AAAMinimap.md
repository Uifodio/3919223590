## AAAMinimap - Single Script AAA Minimap System

### Overview
AAAMinimap is a single C# script that auto-creates a complete, AAA-quality minimap system in Unity. Attach the script to an empty GameObject and it will build a Canvas-based UI, a top-down orthographic camera, RenderTexture, shapes/borders, markers, waypoints, off-screen indicators, overlays, and interactions.

### Key Features
- Map creation and styling
  - Auto Canvas, root, mask, content, border, and map `RawImage` with RenderTexture
  - Map shapes: Circle, Square, Star, or Custom Sprite
  - Border thickness/color, fill color, opacity, size, and screen placement
  - Optional grid overlay and north indicator arrow
- Camera and world alignment
  - Auto-fit to terrain or scene bounds, or manual size
  - Adjustable orthographic size scale (zoom), height, and background color
  - Follow player option; rotate map with player or keep north-up
- Markers and player arrow
  - Player arrow with customizable sprite/shape/size/color/border/label
  - Static markers (by Transform or world coordinates) with custom visuals and off-screen indicators
  - Distance-based culling and optional distance-based marker scaling
- Waypoints
  - Add via Inspector, code API, or by clicking on the minimap
  - Configurable type (Generic/Mission/Tutorial), visuals, label, trigger radius, UnityEvents, popups
  - Off-screen arrow/dot indicators, destroy on reach, trigger once or multiple
- Interactions and UX
  - Click to create waypoints on the minimap
  - Toggle minimap visibility with a key
  - Zoom controls via mouse wheel and optional keys
  - Event popups with pooling and stacked layout
- Performance
  - Update throttling via Updates Per Second
  - Object pooling for markers and popups
  - Lightweight generation of procedural sprites for shapes and arrows
- Inspector-first control
  - All styling, sizes, colors, behaviors, and interactions are configurable from the Inspector
  - Public API for adding markers and waypoints programmatically

### Installation
1. Copy `Assets/Scripts/AAAMinimap.cs` into your project (create the `Scripts` folder if needed).
2. Add an empty GameObject to your scene and attach `AAAMinimap`.
3. Assign the Player Transform under the Player section.
4. Press Play. The minimap UI and camera will be auto-created.

### Setup & Inspector
- Minimap Root & Placement
  - Size Pixels, Opacity, Anchored Position, Pivot
- Map Shape & Style
  - Shape (Circle/Square/Star/Custom), Fill Color, Border Color/Thickness
- Camera & World Alignment
  - Auto-fit world bounds, camera height, background color, follow player
  - Manual world size if auto-fit is off
- Interaction & Updates
  - Click to create waypoints, updates per second, clamp markers to edge
- Player
  - Player Transform, rotate map with player, rotate arrow with player, visuals
- Static Tracked Objects
  - Add entries. Choose by Transform or world position, set visuals, off-screen indicators
- Waypoints
  - Add entries. Type, label, radius, events, popups, visuals
- UX & Controls
  - Toggle key, zoom (wheel/keys), min/max zoom, north indicator, grid overlay
  - Distance culling and distance-based marker scaling

### Usage Examples
- Add static marker by Transform:
```csharp
public AAAMinimap minimap;
public Transform shop;
void Start()
{
	var visual = new AAAMinimap.MarkerVisual { shape = AAAMinimap.MapShape.Square, color = Color.yellow, size = 16f, borderThickness = 2f, borderColor = Color.black, label = "Shop" };
	minimap.AddStaticMarker(shop, visual, AAAMinimap.OffscreenIndicatorStyle.Arrow);
}
```

- Add waypoint at position:
```csharp
public AAAMinimap minimap;
void SetTarget(Vector3 worldPos)
{
	var template = new AAAMinimap.WaypointDefinition { triggerRadius = 3f, destroyOnReach = true };
	template.visual = new AAAMinimap.MarkerVisual { shape = AAAMinimap.MapShape.Star, color = new Color(0.2f, 0.6f, 1f, 1f), borderThickness = 2f, borderColor = new Color(0f, 0.2f, 0.5f, 1f) };
	minimap.CreateWaypoint(worldPos, template);
}
```

- Click to create: Enable "Click To Create Waypoints" in Inspector. Click on the minimap to drop a waypoint.

### Notes & Tips
- For auto-fit, a `Terrain` in the scene is preferred. Otherwise, scene renderers define bounds.
- Use Custom Sprite on the map shape for bespoke frames.
- Use Mission/Tutorial types for default styling presets.
- North indicator remains screen-up and counter-rotates when the map rotates with the player.
- To keep the player arrow screen-up when the map rotates, leave "Rotate Arrow With Player" enabled.

### Public API
- `AddStaticMarker(Transform target, MarkerVisual visual, OffscreenIndicatorStyle offscreen)`
- `AddStaticMarker(Vector3 worldPosition, MarkerVisual visual, OffscreenIndicatorStyle offscreen)`
- `AddWaypoint(Transform target, WaypointDefinition template)`
- `CreateWaypoint(Vector3 worldPosition, WaypointDefinition template)`
- `ClearWaypoints()`
- `ShowPopup(string message, float seconds = 2.5f)`

### Known Limitations
- The procedural star and border are approximate for stylized visuals; for premium art style, provide a custom sprite.
- Grid overlay is a simple edge grid; extend with tiled textures for dense grids if desired.

### Extending Further (Ideas)
- Fog-of-war texture and reveal over time
- Quest chain breadcrumb paths
- Elevation-aware icons (fade by height delta)
- Multi-floor indoor minimaps with level toggle

### License
This sample is provided as-is for your Unity project. Modify freely within your studio workflow.