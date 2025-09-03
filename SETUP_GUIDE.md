# Unity Save & Resource System - Setup Guide

This guide will walk you through setting up the Unity Save & Resource System in your project.

## Prerequisites

- Unity 2022.3 or later
- TextMeshPro package (for UI components)
- Newtonsoft.Json package (for JSON serialization)

## Step-by-Step Setup

### 1. Install Required Packages

1. Open **Window → Package Manager**
2. Install the following packages:
   - **TextMeshPro** (if not already installed)
   - **Newtonsoft.Json** (from Unity Registry)

### 2. Import Scripts

1. Copy all `.cs` files to `Assets/Scripts/SaveSystem/`
2. Unity will automatically compile the scripts

### 3. Create Resource Catalog

1. Right-click in Project window
2. Select **Create → Save System → Resource Catalog**
3. Name it "GameResourceCatalog"
4. Configure your resources in the Inspector:
   - Add resource definitions
   - Set display names and default amounts
   - Configure which resources show in top bar
   - Set resource categories

### 4. Setup Core Managers

1. Create an empty GameObject named "SaveSystem"
2. Add these components:
   - `SaveManager`
   - `ResourceManager` 
   - `WorldStateManager`
3. Configure each component:

#### SaveManager Configuration
```
Save Root Folder Name: "GameSaves"
Enable Compression: ✓
Enable Encryption: (optional)
Autosave Interval: 30 seconds
Save On Pause: ✓
Max Auto Backups: 3
```

#### ResourceManager Configuration
```
Resource Catalog: [Assign your ResourceCatalog asset]
Autosave On Change Throttle: 1000ms
```

#### WorldStateManager Configuration
```
Enable Offline Simulation: ✓
Max Offline Time Hours: 24
Simulation Update Interval: 1 second
```

### 5. Setup Persistent Objects

1. Add `SaveableEntity` component to GameObjects you want to persist
2. Configure save settings:
   - ✓ Save Transform
   - ✓ Save Position/Rotation/Scale
   - ✓ Save Active State
   - ✓ Save Custom Fields
3. Add custom fields as needed

### 6. Create UI Prefabs

#### Resource Display Prefab
1. Create UI → Text - TextMeshPro
2. Add a Button component
3. Structure:
   ```
   ResourceDisplay
   ├── ResourceName (TextMeshPro)
   └── ResourceAmount (TextMeshPro)
   ```

#### Save Card Prefab
1. Create UI → Button
2. Structure:
   ```
   SaveCard
   ├── Thumbnail (Image)
   ├── SlotId (TextMeshPro)
   ├── LastSaved (TextMeshPro)
   ├── PlayTime (TextMeshPro)
   └── ResourcesContainer
       └── [Resource displays]
   ```

### 7. Setup UI Panel

1. Create a Canvas for your UI
2. Add `UIResourcePanel` component
3. Configure:
   - Top Bar Container
   - Resource Display Prefab
   - Save Slots Container
   - Save Card Prefab
   - Button references

### 8. Configure Producers (Optional)

In WorldStateManager, add ProducerDefinition entries:

```csharp
// Example: Wood producer
ID: "wood_producer"
Output Resource ID: "wood"
Rate Per Second: 0.1
Capacity: 1000
Is Passive: true
Worker Count: 1
```

### 9. Test the System

1. **Test Resource System**:
   ```csharp
   // In a test script
   ResourceManager.Instance.AddResource("coins", 100);
   Debug.Log($"Coins: {ResourceManager.Instance.GetResourceAmount("coins")}");
   ```

2. **Test Save System**:
   ```csharp
   // Save current state
   await SaveManager.Instance.SaveSlotAsync("test_save");
   
   // Load save
   await SaveManager.Instance.LoadSlotAsync("test_save");
   ```

3. **Test Persistent Objects**:
   - Move/rotate objects with SaveableEntity
   - Save the game
   - Load the game
   - Verify objects return to saved positions

## Common Issues & Solutions

### Issue: Scripts not compiling
**Solution**: Ensure all required packages are installed (Newtonsoft.Json, TextMeshPro)

### Issue: ResourceManager not finding ResourceCatalog
**Solution**: Assign the ResourceCatalog asset to the ResourceManager component

### Issue: Save files not persisting on Android
**Solution**: Ensure you're using `Application.persistentDataPath` (which the system does automatically)

### Issue: UI not updating
**Solution**: Check that UI components are properly assigned in UIResourcePanel

### Issue: Custom fields not saving
**Solution**: Ensure "Save Custom Fields" is checked on SaveableEntity

## Performance Tips

1. **Limit top bar resources** to 5 or fewer for best performance
2. **Use delta saving** - only save objects that have changed
3. **Enable compression** for large save files
4. **Set appropriate autosave intervals** (30+ seconds recommended)
5. **Use object pooling** for frequently spawned/destroyed objects

## Security Considerations

1. **For production**: Use AndroidKeyStore encryption (requires native plugin)
2. **For testing**: Password-based encryption is sufficient
3. **Never hardcode encryption keys** in your build
4. **Validate all save data** on load to prevent exploits

## Next Steps

1. Create your game's specific resource types
2. Design your save slot UI
3. Implement game-specific producers
4. Add custom fields to your game objects
5. Test thoroughly on target platforms

## Support

If you encounter issues:
1. Check the console for error messages
2. Verify all components are properly configured
3. Test with the debug context menu options
4. Open an issue on GitHub with details