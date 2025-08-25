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

