# Changelog

All notable changes to the Unity Save & Resource System will be documented in this file.

## [1.0.0] - 2024-01-XX

### Added
- **SaveManager.cs**: Core save/load system with JSON serialization, optional encryption (AES-256-GCM), compression (GZip), and atomic file writes
- **ResourceCatalog.cs**: ScriptableObject for designer-configurable resource definitions with validation
- **ResourceManager.cs**: Runtime resource management singleton with event-driven updates and throttled autosave
- **SaveableEntity.cs**: Component for persistent objects with custom field system and delta-based saving
- **WorldStateManager.cs**: Scene-level state management with offline simulation, producers, and triggers
- **UIResourcePanel.cs**: Complete UI framework for resource display and save slot management
- **Comprehensive documentation**: README.md with full API reference and usage examples
- **Setup guide**: Step-by-step configuration instructions
- **Sample assets**: Default ResourceCatalog with common game resources
- **Project structure**: Proper Unity folder organization with .gitignore

### Features
- Inspector-driven configuration (no code changes needed for new resources)
- Multiple save slots with metadata and thumbnail support
- Offline idle simulation with configurable producers
- Event-driven architecture for clean separation of concerns
- Android-optimized storage using Application.persistentDataPath
- Performance optimized with delta-based saving and background I/O
- Security options: None, Password, AndroidKeyStore, Generated encryption
- Cross-platform compatibility (Android/PC)
- Debug tools and context menu options for testing

### Technical Details
- Unity 2022.3+ compatibility
- Requires TextMeshPro and Newtonsoft.Json packages
- Uses GUID-based persistent IDs for stable object references
- Implements rotating backup system for data safety
- Supports custom field types: Int, Long, Float, Bool, String, Vector3
- Resource categories: Currency, Materials, Consumables, Equipment, Special
- Configurable autosave intervals and pause/exit saving
- Atomic file operations to prevent corruption during saves