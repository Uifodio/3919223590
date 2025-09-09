# Dark Fantasy Scene Transition System

A professional, AAA-quality scene transition system for Unity with comprehensive features designed specifically for dark fantasy games. This system provides smooth fade transitions, animated loading bars, dynamic quotes, and extensive customization options.

## Features

### Core Functionality
- **Smooth Fade Transitions**: Professional fade in/out effects with customizable timing
- **Animated Loading Bar**: Realistic loading progress with pulse effects at completion
- **Dynamic Text Counter**: Percentage display that counts from 0% to 100%
- **Quote System**: Rotating dark fantasy quotes during loading
- **Responsive Design**: Automatically adapts to portrait and landscape orientations
- **Mobile Optimized**: Designed specifically for mobile portrait games

### Advanced Features
- **Audio Integration**: Customizable fade sounds and loading completion audio
- **Visual Effects**: Screen shake, glitch effects, and particle systems
- **Customizable Colors**: Full control over loading bar, text, and fade colors
- **Inspector Controls**: Comprehensive editor interface for easy customization
- **Event System**: Subscribe to transition events for custom behavior
- **Validation**: Automatic scene validation and configuration checking

### Professional Quality
- **AAA Game Standards**: Production-ready code with error handling
- **Performance Optimized**: Efficient rendering and memory usage
- **Extensible Architecture**: Easy to modify and extend
- **Documentation**: Comprehensive code documentation and examples

## Quick Start

### 1. Setup the System
1. In Unity, go to `Dark Fantasy > Setup Scene Transition System`
2. This will create the SceneTransitionManager and sample UI

### 2. Create a Transition Button
1. Go to `Dark Fantasy > Create Transition Button`
2. Set the target scene name in the inspector
3. Customize colors, timing, and effects as needed

### 3. Test the Transition
1. Enter Play mode
2. Click the transition button
3. Watch the professional transition effect

## Usage

### Basic Usage
```csharp
// Simple scene transition
SceneTransitionManager.Instance.TransitionToScene("MainMenu");
```

### Advanced Usage
```csharp
// Customize colors
SceneTransitionManager.Instance.SetLoadingBarColor(Color.purple);
SceneTransitionManager.Instance.SetTextColor(Color.white);

// Add custom quotes
SceneTransitionManager.Instance.AddCustomQuote("Your custom quote here");

// Set custom timing
SceneTransitionManager.Instance.SetTransitionDuration(2f, 2f, 4f);
```

### Event Handling
```csharp
// Subscribe to events
SceneTransitionManager.OnTransitionStarted += OnTransitionStart;
SceneTransitionManager.OnTransitionCompleted += OnTransitionComplete;
SceneTransitionManager.OnLoadingProgress += OnLoadingUpdate;

private void OnTransitionStart()
{
    Debug.Log("Transition started!");
}

private void OnTransitionComplete()
{
    Debug.Log("Transition completed!");
}

private void OnLoadingUpdate(float progress)
{
    Debug.Log($"Loading: {progress * 100}%");
}
```

## Components

### SceneTransitionManager
The core singleton that handles all transition logic. Automatically creates UI elements and manages the transition process.

**Key Features:**
- Singleton pattern for global access
- Automatic UI creation and management
- Responsive design adaptation
- Audio and visual effects integration
- Event system for custom behavior

### SceneTransitionButton
A button component that triggers scene transitions. Simply attach to any button and configure the target scene.

**Key Features:**
- One-click setup
- Comprehensive inspector customization
- Hover effects and audio feedback
- Scene validation
- Custom transition settings per button

### SceneTransitionEditor
Custom editor scripts that provide professional inspector interfaces for easy configuration.

**Key Features:**
- Organized foldout sections
- Real-time validation
- Quick scene selection
- Visual feedback and status indicators
- Test buttons for debugging

## Customization

### Visual Customization
- **Loading Bar Colors**: Customize the main bar and glow colors
- **Text Colors**: Set loading text and glow colors
- **Fade Colors**: Customize the fade overlay color
- **Timing**: Adjust fade in/out and loading durations
- **Effects**: Enable/disable screen shake, glitch, and particle effects

### Audio Customization
- **Fade Sounds**: Custom audio for fade in/out
- **Loading Complete**: Sound when loading reaches 100%
- **Button Audio**: Click and hover sounds for buttons
- **Volume Control**: Adjustable audio levels

### Quote System
- **Default Quotes**: 10+ dark fantasy quotes included
- **Custom Quotes**: Add your own quotes
- **Display Timing**: Control how long quotes are shown
- **Fade Effects**: Smooth quote transitions

## Mobile Optimization

### Portrait Mode
- Optimized for 1080x1920 resolution
- Responsive scaling for different screen sizes
- Touch-friendly button interactions
- Efficient rendering for mobile GPUs

### Landscape Support
- Automatic orientation detection
- Adaptive UI scaling
- Maintains professional appearance
- Optimized for various aspect ratios

## Performance

### Optimization Features
- **Efficient Rendering**: Minimal draw calls
- **Memory Management**: Proper cleanup and disposal
- **Async Loading**: Non-blocking scene loading
- **LOD System**: Automatic quality adjustment

### Best Practices
- Use object pooling for frequent transitions
- Optimize audio files for mobile
- Test on target devices
- Monitor memory usage during transitions

## Troubleshooting

### Common Issues

**Scene not found error:**
- Ensure the scene is added to Build Settings
- Check the scene name spelling
- Use the scene selection menu in the inspector

**UI not appearing:**
- Check Canvas settings
- Verify UI elements are properly assigned
- Ensure the SceneTransitionManager is in the scene

**Audio not playing:**
- Check AudioSource components
- Verify audio files are assigned
- Check volume settings

**Performance issues:**
- Reduce particle effects on low-end devices
- Optimize audio file sizes
- Use lower resolution UI elements

### Debug Features
- Enable "Show Debug Info" in button settings
- Use the validation tools in the inspector
- Check console for error messages
- Use the test transition button in Play mode

## Advanced Usage

### Custom Transitions
Create custom transition effects by extending the base classes:

```csharp
public class CustomTransition : SceneTransitionManager
{
    protected override IEnumerator CustomTransitionEffect()
    {
        // Your custom transition logic
        yield return null;
    }
}
```

### Integration with Other Systems
The transition system integrates seamlessly with:
- Audio managers
- UI systems
- Save/load systems
- Analytics tracking
- Achievement systems

## Support

For issues, questions, or feature requests:
1. Check the troubleshooting section
2. Review the code documentation
3. Test with the provided examples
4. Contact support with detailed information

## License

This scene transition system is provided as-is for use in your projects. Modify and distribute according to your needs.

---

**Dark Fantasy Scene Transition System** - Professional quality transitions for your mobile games.