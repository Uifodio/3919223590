Unity Minimap System (Single Script)

Drop `MinimapSystem` on any GameObject and configure everything in the Inspector. It auto-creates a Camera, Canvas, RenderTexture, masked UI, static markers, waypoints, pooling, and optional popups. Includes an expanded overlay map toggle.

Quick Start
1) Copy `Assets/Scripts/MinimapSystem.cs` and `Assets/Scripts/MinimapClickCatcher.cs` into your project.
2) Add `MinimapSystem` to an empty GameObject.
3) In Inspector: set `Player` to your player transform. Optionally assign `Default UI Font`.
4) Add static map objects via `Map Objects (static markers)`; pick shape/color/size.
5) Add waypoints (transform or world position); set label/color/radius/UnityEvent.
6) Choose map shape (Circle/Square/Star/Custom); adjust border/background.
7) Placement: enable `Use Custom Position` to freely place the minimap via anchors/pivot/position.
8) Expanded Map: enable `Enable Expanded Map`; toggle with `M` (configurable). Enable `Click To Create On Expanded` to place waypoints there. Disable small-map clicks via `Click To Create On Minimap` if desired.

Key Features
- Self-contained: auto-creates Canvas, Camera, RenderTexture, UI, and markers.
- Player arrow: custom sprite/size/color; rotate with player or North-Up.
- Static map objects: configurable shapes/icons/colors, optional offscreen hide or clamp-to-edge.
- Waypoints: label, radius, UnityEvent on reach, edge arrows when off-screen.
- Click-to-create: separate toggles for small and expanded map.
- Map styles: Circle, Square, Star, or Custom; matching border; background color/opacity.
- Placement: corner presets or fully custom anchors/pivot/position.
- Performance: simple pooling and smooth marker movement.
- Popups: optional simple popup or custom prefab.

Notes
- The minimap camera is orthographic and looks straight down from `Camera Height`.
- `UI Scale` and `UI Scale Fine` tune UI sizing; `World Offset` adjusts world alignment.
- Assign `Default UI Font` to avoid built-in font issues.

Scripting
- `CreateWaypoint(Vector3 worldPosition, string label = null, Color? color = null)` to add waypoints at runtime.
- You can toggle the expanded map by setting `enableExpandedMap` and changing `expandedToggleKey`.

### Unity Minimap System (Single Script)

Drop `MinimapSystem` on any GameObject and configure everything from the Inspector. It auto-creates a render camera, canvas, UI, markers, waypoints, shape masks, pooling, and optional mission/tutorial popups.

### Quick Start
1. Copy `Assets/Scripts/MinimapSystem.cs` (and `MinimapClickCatcher.cs`) into your Unity project.
2. Add `MinimapSystem` to an empty GameObject in your scene.
3. In the Inspector:
   - Set Player Arrow > Player to your player transform.
   - Optionally tweak size, color, rotation behavior.
   - Add Tracked Objects via the list (+) and choose shape/color or a custom sprite.
   - Add Waypoints via the list (+). You can set a transform or fixed world position, label, color, trigger radius, and UnityEvent actions.
   - Style the map: choose Circle/Square/Star/Custom mask, set border/background.
   - Adjust Alignment: world offset and UI scale; or enable Auto-Fit To Terrain.
   - Enable Click-To-Create Waypoints to create waypoints by clicking the minimap.

### Features
- Self-contained: creates its own `Canvas`, `Camera`, `RenderTexture`, and UI.
- Player arrow: custom sprite/size/color, rotate with player or north-up.
- Tracked objects: arbitrary scene transforms as static markers, shapes or custom icons.
- Waypoints: label, radius, UnityEvent on reach, edge arrows when off-screen.
- Click-to-create waypoints: click inside the minimap during play to add.
- Map styles: circle, square, star, or custom mask; border thickness/color; background.
- Alignment: scale/offset controls; terrain auto-fit.
- Performance: simple pooling and smooth marker movement.
- Popups: built-in simple popup with optional custom prefab; useful for missions/tutorials.

### Notes
- The minimap camera is orthographic and looks straight down.
- For world alignment, tune `UI Scale Fine` and `World Offset` to match terrain/world coordinates.
- For a custom mask, provide a 9-sliced or standard sprite; the system applies an Image+Mask.

### Extensibility
- Use `CreateWaypoint(Vector3 worldPosition, string label = null, Color? color = null)` at runtime to add waypoints from code.
- Assign UnityEvents on waypoints to start missions or show tutorial steps when reached.

