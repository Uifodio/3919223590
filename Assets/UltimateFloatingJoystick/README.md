# Ultimate Floating Joystick

Drag-and-drop, professional floating joystick for Unity UI. Appears at first touch, supports full/half-screen activation, dead zone, smooth handle motion, glow/fade visuals, and a configurable instructional placeholder.

## Quick Start

1. Open your Unity project.
2. Copy the `Assets/UltimateFloatingJoystick` folder into your project's `Assets/`.
3. From the Unity menu: GameObject → UI → Ultimate Floating Joystick. This creates a Canvas (if needed), EventSystem, and the joystick rig.
4. Enter Play: touch/click anywhere to spawn the joystick at your finger. Release to hide (configurable).

## Structure

- FloatingJoystick (script on a full-screen transparent Image, the activation area)
  - JoystickContainer (CanvasGroup)
    - Background (Image)
    - Handle (Image)
  - Placeholder (CanvasGroup)

## Inspector Parameters

- Handle Range: Max handle distance in pixels.
- Dead Zone Radius: Ignore small touches within this radius.
- Renormalize After Dead Zone: Rescale input so values remain [0..1] beyond dead zone.
- Handle Smooth Time: SmoothDamp time for handle motion.
- Hide On Release: Fade joystick out when finger lifts.
- Joystick Fade Speed: Alpha change speed.
- Activation Restriction: FullScreen, LeftHalf, or RightHalf.
- Glow: Enable glow on press, with intensity and fade speed.
- Placeholder: Enable, timed visibility, duration, fade speed, and reappear on release.
- Images: Assign your own sprites for Background and Handle.

## API

- Properties: `Horizontal`, `Vertical`, `Direction`, `IsPressed`.
- Methods: `SetSprites(Sprite background, Sprite handle)`, `SetRange(float)`, `SetDeadZone(float)`, `SetHideOnRelease(bool)`.

## Notes

- The activation area image is invisible but raycast-enabled to capture touches.
- Input values are normalized to [-1, 1]. With renormalization on, small offsets within the dead zone output zero, then smoothly scale to full range.
- For camera/world movement, read `Direction` every frame.

