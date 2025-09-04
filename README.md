# 🌟 SIMPLE Save System for Unity

A **SIMPLE** but **COMPLETE** save system for Unity games that automatically saves everything!

## 🚀 **ONE-CLICK INSTALLATION**

1. **Open Unity**
2. **Go to Tools > Simple Save System > 🚀 Install Complete System**
3. **Done! Your game now has automatic save functionality!**

## ✨ **FEATURES**

### 🎮 **Automatic Saving**
- ✅ **Saves automatically every 5 seconds**
- ✅ **Saves when you pause the game**
- ✅ **Saves when you exit the game**
- ✅ **Saves when you lose focus**

### 👤 **Character Tracking**
- ✅ **Automatically finds and tracks player**
- ✅ **Saves position, rotation, scale**
- ✅ **Tracks movement changes**
- ✅ **Works with any character setup**

### 🌍 **World State Management**
- ✅ **Tracks ALL objects in the scene**
- ✅ **Saves broken/destroyed objects**
- ✅ **Saves custom object data**
- ✅ **Maintains world state perfectly**

### 💰 **Resource System**
- ✅ **Add/remove resources easily**
- ✅ **Visual resource display**
- ✅ **Resource limits and validation**
- ✅ **Automatic resource saving**

### 🎯 **Object Persistence**
- ✅ **Mark any object as saveable**
- ✅ **Custom data fields**
- ✅ **Broken/destroyed states**
- ✅ **Visual state changes**

### 🎨 **Simple UI**
- ✅ **Resource display**
- ✅ **Save/Load buttons**
- ✅ **Status messages**
- ✅ **Easy to customize**

## 🛠️ **HOW TO USE**

### **1. Install the System**
```
Tools > Simple Save System > 🚀 Install Complete System
```

### **2. Create a Player**
```
Tools > Simple Save System > 👤 Create Player Character
```

### **3. Create Sample Objects**
```
Tools > Simple Save System > 🌳 Create Sample Trees
Tools > Simple Save System > 💰 Create Resource Pickups
```

### **4. Test the System**
```
Tools > Simple Save System > 🧪 Test Save System
```

## 📝 **CODE EXAMPLES**

### **Add Resources**
```csharp
SimpleResourceManager.Instance.AddResource("coins", 100);
SimpleResourceManager.Instance.AddResource("wood", 50);
```

### **Remove Resources**
```csharp
bool success = SimpleResourceManager.Instance.TryRemoveResource("coins", 25);
```

### **Get Resource Amount**
```csharp
long coins = SimpleResourceManager.Instance.GetResourceAmount("coins");
```

### **Mark Object as Broken**
```csharp
SaveableObject obj = GetComponent<SaveableObject>();
obj.MarkBroken();
```

### **Set Custom Data**
```csharp
SaveableObject obj = GetComponent<SaveableObject>();
obj.SetCustomData("health", 100);
obj.SetCustomData("type", "tree");
```

### **Get Custom Data**
```csharp
SaveableObject obj = GetComponent<SaveableObject>();
int health = obj.GetCustomData<int>("health", 0);
string type = obj.GetCustomData<string>("type", "unknown");
```

### **Save Game Manually**
```csharp
SimpleSaveManager.Instance.SaveGame();
```

### **Load Game Manually**
```csharp
SimpleSaveManager.Instance.LoadGame();
```

## 🎯 **COMPONENTS**

### **SimpleSaveManager**
- Main save system controller
- Handles automatic saving
- Manages save files

### **SimpleResourceManager**
- Manages all game resources
- Handles resource display
- Validates resource operations

### **SimpleWorldManager**
- Tracks all objects in the world
- Manages broken/destroyed states
- Handles world state persistence

### **SimpleCharacterManager**
- Automatically finds and tracks player
- Saves character position and state
- Handles character data

### **SaveableObject**
- Add to any object you want to save
- Handles custom data
- Manages visual states

### **ResourceCollector**
- Add to pickup objects
- Handles resource collection
- Visual effects and sounds

### **SimpleUI**
- Displays resources
- Save/Load buttons
- Status messages

## 🔧 **CUSTOMIZATION**

### **Resource Definitions**
Edit the resource definitions in SimpleResourceManager:
```csharp
public List<ResourceDefinition> resourceDefinitions = new List<ResourceDefinition>();
```

### **Save Settings**
Adjust save settings in SimpleSaveManager:
```csharp
public float autoSaveInterval = 5f;
public bool saveOnPause = true;
public bool saveOnExit = true;
```

### **Character Tracking**
Configure character tracking in SimpleCharacterManager:
```csharp
public string playerTag = "Player";
public bool trackPosition = true;
public bool trackRotation = true;
```

## 🎮 **GAME INTEGRATION**

### **For Idle Games**
- Perfect for idle games
- Saves progress automatically
- Tracks all resources
- Maintains world state

### **For Adventure Games**
- Saves character position
- Tracks world exploration
- Maintains object states
- Saves custom data

### **For Any Game**
- Works with any Unity project
- Easy to integrate
- No complex setup required
- Automatic functionality

## 🚀 **QUICK START**

1. **Install the system** (one click)
2. **Create a player character** (one click)
3. **Add SaveableObject to objects you want to save**
4. **Add ResourceCollector to pickup objects**
5. **Play your game - everything saves automatically!**

## 🎉 **RESULT**

Your Unity game now has:
- ✅ **Automatic saving** - never lose progress
- ✅ **Character tracking** - position saved automatically
- ✅ **World persistence** - everything stays the same
- ✅ **Resource management** - track all resources
- ✅ **Simple UI** - easy to use interface
- ✅ **One-click installation** - works in 30 seconds

## 📱 **Mobile Ready**

- Optimized for mobile devices
- Battery-friendly automatic saving
- Works on Android and iOS
- Handles app pause/resume

---

**This system is SIMPLE, COMPLETE, and WORKS!** 🎯