# Unity Persistent Save & Resource System

A comprehensive, inspector-driven Unity save and resource management system designed for Android idle games. This system provides persistent data storage, resource management, offline simulation, and a complete UI framework - all configurable through the Unity Inspector without code changes.

## 🚀 Features

### Core Save System
- **JSON-based saves** with optional GZip compression and AES-256-GCM encryption
- **Atomic file writes** with rotating backups to prevent data corruption
- **Multiple save slots** with metadata and thumbnail support
- **Autosave functionality** with configurable intervals
- **Background I/O operations** to prevent UI blocking
- **Cross-platform compatibility** (Android/PC)

### Resource Management
- **Inspector-driven resource definitions** - no code changes needed
- **Real-time resource tracking** with event-driven updates
- **Resource validation** with min/max constraints
- **Category-based organization** (Currency, Materials, Consumables, etc.)
- **Top-bar UI integration** with configurable display order

### Persistent Objects
- **SaveableEntity component** - attach to any GameObject for persistence
- **Delta-based saving** - only saves changes from prefab defaults
- **Custom field system** with multiple data types
- **Broken/Destroyed state management**
- **GUID-based persistent IDs** for stable object references

### Offline Idle Simulation
- **Producer-based resource generation** while offline
- **Configurable offline time limits** and decay rates
- **Worker count and capacity management**
- **Automatic resource crediting** on game return

### UI Framework
- **Top-bar resource display** with real-time updates
- **Save card system** with thumbnails and metadata
- **Save slot management** (New, Load, Save, Delete)
- **Formatted resource amounts** (K, M notation)
- **Event-driven UI updates**

## 📁 Project Structure

```
Assets/
├── Scripts/
│   └── SaveSystem/
│       ├── SaveManager.cs              # Core save/load system
│       ├── ResourceCatalog.cs          # Resource definitions (ScriptableObject)
│       ├── ResourceManager.cs          # Runtime resource management
│       ├── SaveableEntity.cs           # Persistent object component
│       ├── WorldStateManager.cs        # Scene-level state management
│       └── UIResourcePanel.cs          # UI framework
└── Resources/
    └── SaveSystem/
        └── ResourceCatalog.asset       # Default resource catalog
```

## 🛠️ Setup Instructions

### 1. Import the Scripts
1. Copy all `.cs` files to `Assets/Scripts/SaveSystem/`
2. Create a `ResourceCatalog` ScriptableObject:
   - Right-click in Project → Create → Save System → Resource Catalog
   - Configure your resources in the Inspector

### 2. Setup Core Managers
1. Create an empty GameObject named "SaveSystem"
2. Add the following components:
   - `SaveManager`
   - `ResourceManager`
   - `WorldStateManager`
3. Assign the `ResourceCatalog` to the `ResourceManager`

### 3. Configure Resources
1. Open your `ResourceCatalog` asset
2. Add resource definitions with:
   - **ID**: Unique identifier (e.g., "coins", "wood")
   - **Display Name**: UI display name
   - **Default Amount**: Starting value
   - **Category**: Resource type
   - **Show in Top Bar**: Whether to display in UI
   - **Top Bar Order**: Display order (0 = first)

### 4. Setup Persistent Objects
1. Add `SaveableEntity` component to GameObjects you want to persist
2. Configure what to save:
   - ✅ Save Transform (Position, Rotation, Scale)
   - ✅ Save Active State
   - ✅ Save Custom Fields
3. Add custom fields as needed (Int, Long, Float, Bool, String, Vector3)

### 5. Configure UI
1. Create UI prefabs for:
   - Resource display (for top bar)
   - Save card (for save slots)
2. Add `UIResourcePanel` component to your UI manager
3. Assign prefabs and containers in the Inspector

### 6. Setup Producers (Optional)
1. In `WorldStateManager`, add `ProducerDefinition` entries:
   - **ID**: Unique producer identifier
   - **Output Resource ID**: Which resource this produces
   - **Rate Per Second**: Production rate
   - **Capacity**: Maximum stored amount
   - **Is Passive**: Whether it runs while offline
   - **Worker Count**: Number of workers

## 🔧 Configuration

### SaveManager Settings
```csharp
[Header("Save Configuration")]
saveRootFolderName = "GameSaves"           // Save folder name
enableCompression = true                   // Use GZip compression
enableEncryption = false                   // Use AES encryption
autosaveIntervalSeconds = 30f              // Autosave frequency
saveOnPause = true                         // Save when app pauses
maxAutoBackups = 3                         // Number of backup files
```

### Encryption Options
- **None**: No encryption (fastest)
- **Password**: User-entered password with PBKDF2 key derivation
- **AndroidKeyStore**: Platform keystore (requires native plugin)
- **Generated**: Auto-generated key (obfuscation only)

### ResourceManager Settings
```csharp
[Header("Configuration")]
autosaveOnChangeThrottleMs = 1000f        // Throttle autosave calls
```

## 📖 API Reference

### SaveManager
```csharp
// Save/Load operations
Task SaveSlotAsync(string slotId)
Task LoadSlotAsync(string slotId)
Task DeleteSlotAsync(string slotId)

// Get save information
IEnumerable<SaveSummary> GetSaveSummaries()

// Mark data as changed
void MarkDirty(SaveCategory category)

// Events
event Action<string> OnSaveCompleted
event Action<string> OnLoadCompleted
event Action<string, string> OnSaveFailed
```

### ResourceManager
```csharp
// Resource operations
void AddResource(string id, long amount)
bool TryRemoveResource(string id, long amount)
long GetResourceAmount(string id)

// Get resource information
ResourceSnapshot GetSnapshot(IEnumerable<string> ids)
List<ResourceDefinition> GetTopBarResources()

// Events
event Action<string, long> OnResourceChanged
```

### SaveableEntity
```csharp
// Save/Load
SaveData Serialize()
void Deserialize(SaveData data)

// State management
void MarkBroken()
void MarkDestroyed()
void Repair()

// Custom fields
void SetCustomField(string key, object value)
T GetCustomField<T>(string key, T defaultValue)

// Events
event Action OnPersistedChanged
```

### WorldStateManager
```csharp
// Object management
void RegisterSpawnablePrefab(string prefabId, GameObject prefab)
IEnumerable<BrokenObjectInfo> GetBrokenObjects()

// Triggers
void RegisterTrigger(string triggerId, bool value)
bool QueryTrigger(string triggerId)

// Offline simulation
Task SimulateOfflineAsync(double deltaSeconds)
```

## 🎮 Usage Examples

### Adding Resources
```csharp
// Add coins to player
ResourceManager.Instance.AddResource("coins", 100);

// Check if player can afford something
bool canAfford = ResourceManager.Instance.HasEnoughResources("coins", 50);
```

### Making Objects Persistent
```csharp
// Get SaveableEntity component
var saveable = GetComponent<SaveableEntity>();

// Set custom field
saveable.SetCustomField("durability", 100);

// Mark as broken
saveable.MarkBroken();
```

### Save/Load Operations
```csharp
// Save current game
await SaveManager.Instance.SaveSlotAsync("slot_1");

// Load a save
await SaveManager.Instance.LoadSlotAsync("slot_1");

// Get all save slots
var saves = SaveManager.Instance.GetSaveSummaries();
```

### Setting Triggers
```csharp
// Set a trigger
WorldStateManager.Instance.RegisterTrigger("gate_open", true);

// Check trigger state
bool gateOpen = WorldStateManager.Instance.QueryTrigger("gate_open");
```

## 🔒 Security Notes

- **Password encryption**: Uses PBKDF2 with 100,000 iterations
- **AndroidKeyStore**: Recommended for production (requires native plugin)
- **Generated keys**: Obfuscation only, not secure
- **File permissions**: Saves are stored in app-private directory

## 🧪 Testing

### Performance Testing
- Test with 1000+ objects (only 10 changed) - measure file size and save time
- Toggle encryption on/off - verify load works with chosen key source
- Simulate 7 days offline - check production math and caps
- Test crash during save - verify atomic write and backup restore

### Debug Tools
- `SaveManager`: Context menu options for test saves, load latest, clear all
- `ResourceManager`: Context menu for test resources, reset, log all
- `SaveableEntity`: Context menu for new ID, add fields, log data
- `WorldStateManager`: Context menu for refresh, log state, simulate offline

## 📱 Android Considerations

- Uses `Application.persistentDataPath` for proper Android storage
- Handles app pause/resume for autosave
- Supports Android KeyStore for encryption (with native plugin)
- Optimized for mobile performance with background I/O

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, please open an issue on GitHub or contact the development team.

## 🔄 Version History

- **v1.0.0** - Initial release with core save/resource system
- **v1.1.0** - Added offline simulation and UI framework
- **v1.2.0** - Enhanced encryption and performance optimizations

---

**Note**: This system is designed for Unity 2022.3+ and requires TextMeshPro for UI components. No additional packages or plugins are required for basic functionality.