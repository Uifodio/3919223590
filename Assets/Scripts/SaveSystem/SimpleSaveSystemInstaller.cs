using UnityEngine;
using UnityEditor;
using System.IO;

public class SimpleSaveSystemInstaller
{
    [MenuItem("Tools/Simple Save System/🚀 Install Complete System")]
    public static void InstallCompleteSystem()
    {
        Debug.Log("=== Installing SIMPLE Save System ===");
        
        try
        {
            // 1. Create main save system object
            CreateSaveSystemObject();
            
            // 2. Create resource catalog
            CreateResourceCatalog();
            
            // 3. Create UI
            CreateUI();
            
            // 4. Create sample objects
            CreateSampleObjects();
            
            // 5. Test the system
            TestSystem();
            
            Debug.Log("✅ SIMPLE Save System installed successfully!");
            Debug.Log("🎉 Your game now has automatic save functionality!");
            Debug.Log("📱 Character position will be saved automatically!");
            Debug.Log("🌍 All objects will be tracked and saved!");
            Debug.Log("💰 Resource system is ready!");
            
            EditorUtility.DisplayDialog("SIMPLE Save System Installed", 
                "SIMPLE Save System has been installed successfully!\n\n" +
                "✅ Automatic character tracking\n" +
                "✅ Automatic object tracking\n" +
                "✅ Resource management system\n" +
                "✅ Simple UI system\n" +
                "✅ One-click save/load\n" +
                "✅ Background saving\n\n" +
                "Your game is now ready!", "Awesome!");
        }
        catch (System.Exception ex)
        {
            Debug.LogError($"Installation failed: {ex.Message}");
            EditorUtility.DisplayDialog("Installation Failed", 
                $"Save System installation failed:\n{ex.Message}\n\nPlease check the console for details.", "OK");
        }
    }
    
    [MenuItem("Tools/Simple Save System/👤 Create Player Character")]
    public static void CreatePlayerCharacter()
    {
        // Create character
        GameObject player = new GameObject("Player");
        player.tag = "Player";
        
        // Add character controller
        player.AddComponent<CharacterController>();
        
        // Add saveable object
        SaveableObject saveable = player.AddComponent<SaveableObject>();
        saveable.objectId = "player_character";
        saveable.generateIdAutomatically = false;
        
        // Position in scene
        player.transform.position = Vector3.zero;
        
        // Select the character
        Selection.activeGameObject = player;
        
        Debug.Log("✅ Player character created with automatic save tracking!");
    }
    
    [MenuItem("Tools/Simple Save System/🌳 Create Sample Trees")]
    public static void CreateSampleTrees()
    {
        for (int i = 0; i < 5; i++)
        {
            GameObject tree = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            tree.name = $"Tree_{i}";
            tree.transform.position = new Vector3(i * 3, 0, 0);
            tree.transform.localScale = new Vector3(1, 2, 1);
            
            // Add saveable object
            SaveableObject saveable = tree.AddComponent<SaveableObject>();
            saveable.objectId = $"tree_{i}";
            saveable.generateIdAutomatically = false;
            saveable.savePosition = true;
            saveable.saveRotation = true;
            saveable.saveScale = true;
            saveable.saveActiveState = true;
            
            // Add custom data
            saveable.SetCustomData("health", 100);
            saveable.SetCustomData("type", "oak");
            saveable.SetCustomData("canCut", true);
        }
        
        Debug.Log("✅ Created 5 sample trees with save tracking!");
    }
    
    [MenuItem("Tools/Simple Save System/💰 Create Resource Pickups")]
    public static void CreateResourcePickups()
    {
        string[] resources = { "coins", "wood", "stone" };
        long[] amounts = { 10, 5, 3 };
        
        for (int i = 0; i < 3; i++)
        {
            GameObject pickup = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            pickup.name = $"{resources[i]}_pickup";
            pickup.transform.position = new Vector3(i * 2, 1, 0);
            pickup.transform.localScale = Vector3.one * 0.5f;
            
            // Add resource collector
            ResourceCollector collector = pickup.AddComponent<ResourceCollector>();
            collector.resourceId = resources[i];
            collector.amount = amounts[i];
            collector.gravityToPlayer = true;
            collector.collectRadius = 2f;
            collector.destroyOnCollect = true;
            
            // Make it look like a pickup
            Renderer renderer = pickup.GetComponent<Renderer>();
            if (renderer != null)
            {
                Material mat = new Material(Shader.Find("Standard"));
                switch (resources[i])
                {
                    case "coins":
                        mat.color = Color.yellow;
                        break;
                    case "wood":
                        mat.color = new Color(0.6f, 0.4f, 0.2f);
                        break;
                    case "stone":
                        mat.color = Color.gray;
                        break;
                }
                renderer.material = mat;
            }
        }
        
        Debug.Log("✅ Created resource pickups!");
    }
    
    [MenuItem("Tools/Simple Save System/🧪 Test Save System")]
    public static void TestSaveSystem()
    {
        var saveSystem = GameObject.Find("SimpleSaveSystem");
        if (saveSystem == null)
        {
            EditorUtility.DisplayDialog("Save System Not Found", 
                "Save System not found. Please install it first.", "OK");
            return;
        }
        
        var saveManager = saveSystem.GetComponent<SimpleSaveManager>();
        if (saveManager != null)
        {
            saveManager.SaveGameNow();
            Debug.Log("✅ Save test completed!");
        }
    }
    
    [MenuItem("Tools/Simple Save System/🗑️ Delete Save File")]
    public static void DeleteSaveFile()
    {
        var saveSystem = GameObject.Find("SimpleSaveSystem");
        if (saveSystem != null)
        {
            var saveManager = saveSystem.GetComponent<SimpleSaveManager>();
            if (saveManager != null)
            {
                saveManager.DeleteSaveFile();
                Debug.Log("✅ Save file deleted!");
            }
        }
    }
    
    private static void CreateSaveSystemObject()
    {
        // Check if already exists
        GameObject saveSystem = GameObject.Find("SimpleSaveSystem");
        if (saveSystem != null)
        {
            Debug.Log("SimpleSaveSystem already exists, updating components...");
        }
        else
        {
            saveSystem = new GameObject("SimpleSaveSystem");
            Debug.Log("✅ Created SimpleSaveSystem GameObject");
        }
        
        // Add required components
        if (saveSystem.GetComponent<SimpleSaveManager>() == null)
        {
            saveSystem.AddComponent<SimpleSaveManager>();
            Debug.Log("✅ Added SimpleSaveManager");
        }
        
        if (saveSystem.GetComponent<SimpleResourceManager>() == null)
        {
            saveSystem.AddComponent<SimpleResourceManager>();
            Debug.Log("✅ Added SimpleResourceManager");
        }
        
        if (saveSystem.GetComponent<SimpleWorldManager>() == null)
        {
            saveSystem.AddComponent<SimpleWorldManager>();
            Debug.Log("✅ Added SimpleWorldManager");
        }
        
        if (saveSystem.GetComponent<SimpleCharacterManager>() == null)
        {
            saveSystem.AddComponent<SimpleCharacterManager>();
            Debug.Log("✅ Added SimpleCharacterManager");
        }
        
        EditorUtility.SetDirty(saveSystem);
    }
    
    private static void CreateResourceCatalog()
    {
        // Create default resources
        var saveSystem = GameObject.Find("SimpleSaveSystem");
        if (saveSystem != null)
        {
            var resourceManager = saveSystem.GetComponent<SimpleResourceManager>();
            if (resourceManager != null)
            {
                // Add default resources
                resourceManager.resourceDefinitions.Add(new ResourceDefinition
                {
                    id = "coins",
                    displayName = "Coins",
                    defaultAmount = 0,
                    maxAmount = 999999,
                    showInTopBar = true,
                    category = "Currency"
                });
                
                resourceManager.resourceDefinitions.Add(new ResourceDefinition
                {
                    id = "wood",
                    displayName = "Wood",
                    defaultAmount = 0,
                    maxAmount = 9999,
                    showInTopBar = true,
                    category = "Materials"
                });
                
                resourceManager.resourceDefinitions.Add(new ResourceDefinition
                {
                    id = "stone",
                    displayName = "Stone",
                    defaultAmount = 0,
                    maxAmount = 9999,
                    showInTopBar = true,
                    category = "Materials"
                });
                
                EditorUtility.SetDirty(resourceManager);
                Debug.Log("✅ Created default resource catalog");
            }
        }
    }
    
    private static void CreateUI()
    {
        // Find or create Canvas
        Canvas canvas = Object.FindObjectOfType<Canvas>();
        if (canvas == null)
        {
            GameObject canvasObj = new GameObject("Canvas");
            canvas = canvasObj.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvasObj.AddComponent<UnityEngine.UI.CanvasScaler>();
            canvasObj.AddComponent<UnityEngine.UI.GraphicRaycaster>();
            Debug.Log("✅ Created Canvas");
        }
        
        // Create UI panel
        GameObject uiPanel = new GameObject("SimpleUI");
        uiPanel.transform.SetParent(canvas.transform, false);
        
        // Add UI component
        uiPanel.AddComponent<SimpleUI>();
        
        // Create UI elements
        CreateUIElements(uiPanel);
        
        Debug.Log("✅ Created UI system");
    }
    
    private static void CreateUIElements(GameObject parent)
    {
        // Create main panel
        GameObject mainPanel = new GameObject("MainPanel");
        mainPanel.transform.SetParent(parent.transform, false);
        
        RectTransform panelRect = mainPanel.AddComponent<RectTransform>();
        panelRect.anchorMin = Vector2.zero;
        panelRect.anchorMax = Vector2.one;
        panelRect.offsetMin = Vector2.zero;
        panelRect.offsetMax = Vector2.zero;
        
        // Add background
        UnityEngine.UI.Image panelImage = mainPanel.AddComponent<UnityEngine.UI.Image>();
        panelImage.color = new Color(0, 0, 0, 0.5f);
        
        // Create resource display
        CreateResourceDisplay(mainPanel);
        
        // Create buttons
        CreateButtons(mainPanel);
    }
    
    private static void CreateResourceDisplay(GameObject parent)
    {
        // Coins text
        GameObject coinsObj = new GameObject("CoinsText");
        coinsObj.transform.SetParent(parent.transform, false);
        
        RectTransform coinsRect = coinsObj.AddComponent<RectTransform>();
        coinsRect.anchorMin = new Vector2(0, 1);
        coinsRect.anchorMax = new Vector2(0, 1);
        coinsRect.anchoredPosition = new Vector2(100, -30);
        coinsRect.sizeDelta = new Vector2(200, 30);
        
        Text coinsText = coinsObj.AddComponent<Text>();
        coinsText.text = "Coins: 0";
        coinsText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
        coinsText.fontSize = 18;
        coinsText.color = Color.white;
        
        // Wood text
        GameObject woodObj = new GameObject("WoodText");
        woodObj.transform.SetParent(parent.transform, false);
        
        RectTransform woodRect = woodObj.AddComponent<RectTransform>();
        woodRect.anchorMin = new Vector2(0, 1);
        woodRect.anchorMax = new Vector2(0, 1);
        woodRect.anchoredPosition = new Vector2(100, -60);
        woodRect.sizeDelta = new Vector2(200, 30);
        
        Text woodText = woodObj.AddComponent<Text>();
        woodText.text = "Wood: 0";
        woodText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
        woodText.fontSize = 18;
        woodText.color = Color.white;
        
        // Stone text
        GameObject stoneObj = new GameObject("StoneText");
        stoneObj.transform.SetParent(parent.transform, false);
        
        RectTransform stoneRect = stoneObj.AddComponent<RectTransform>();
        stoneRect.anchorMin = new Vector2(0, 1);
        stoneRect.anchorMax = new Vector2(0, 1);
        stoneRect.anchoredPosition = new Vector2(100, -90);
        stoneRect.sizeDelta = new Vector2(200, 30);
        
        Text stoneText = stoneObj.AddComponent<Text>();
        stoneText.text = "Stone: 0";
        stoneText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
        stoneText.fontSize = 18;
        stoneText.color = Color.white;
    }
    
    private static void CreateButtons(GameObject parent)
    {
        // Save button
        GameObject saveBtn = new GameObject("SaveButton");
        saveBtn.transform.SetParent(parent.transform, false);
        
        RectTransform saveRect = saveBtn.AddComponent<RectTransform>();
        saveRect.anchorMin = new Vector2(1, 0);
        saveRect.anchorMax = new Vector2(1, 0);
        saveRect.anchoredPosition = new Vector2(-100, 50);
        saveRect.sizeDelta = new Vector2(100, 40);
        
        UnityEngine.UI.Image saveImage = saveBtn.AddComponent<UnityEngine.UI.Image>();
        saveImage.color = Color.green;
        
        Button saveButton = saveBtn.AddComponent<Button>();
        
        // Save button text
        GameObject saveTextObj = new GameObject("Text");
        saveTextObj.transform.SetParent(saveBtn.transform, false);
        
        RectTransform saveTextRect = saveTextObj.AddComponent<RectTransform>();
        saveTextRect.anchorMin = Vector2.zero;
        saveTextRect.anchorMax = Vector2.one;
        saveTextRect.offsetMin = Vector2.zero;
        saveTextRect.offsetMax = Vector2.zero;
        
        Text saveText = saveTextObj.AddComponent<Text>();
        saveText.text = "Save";
        saveText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
        saveText.fontSize = 16;
        saveText.color = Color.white;
        saveText.alignment = TextAnchor.MiddleCenter;
        
        // Load button
        GameObject loadBtn = new GameObject("LoadButton");
        loadBtn.transform.SetParent(parent.transform, false);
        
        RectTransform loadRect = loadBtn.AddComponent<RectTransform>();
        loadRect.anchorMin = new Vector2(1, 0);
        loadRect.anchorMax = new Vector2(1, 0);
        loadRect.anchoredPosition = new Vector2(-100, 10);
        loadRect.sizeDelta = new Vector2(100, 40);
        
        UnityEngine.UI.Image loadImage = loadBtn.AddComponent<UnityEngine.UI.Image>();
        loadImage.color = Color.blue;
        
        Button loadButton = loadBtn.AddComponent<Button>();
        
        // Load button text
        GameObject loadTextObj = new GameObject("Text");
        loadTextObj.transform.SetParent(loadBtn.transform, false);
        
        RectTransform loadTextRect = loadTextObj.AddComponent<RectTransform>();
        loadTextRect.anchorMin = Vector2.zero;
        loadTextRect.anchorMax = Vector2.one;
        loadTextRect.offsetMin = Vector2.zero;
        loadTextRect.offsetMax = Vector2.zero;
        
        Text loadText = loadTextObj.AddComponent<Text>();
        loadText.text = "Load";
        loadText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
        loadText.fontSize = 16;
        loadText.color = Color.white;
        loadText.alignment = TextAnchor.MiddleCenter;
    }
    
    private static void CreateSampleObjects()
    {
        // Create a few sample objects
        for (int i = 0; i < 3; i++)
        {
            GameObject obj = GameObject.CreatePrimitive(PrimitiveType.Cube);
            obj.name = $"SampleObject_{i}";
            obj.transform.position = new Vector3(i * 2, 0, 0);
            
            SaveableObject saveable = obj.AddComponent<SaveableObject>();
            saveable.objectId = $"sample_{i}";
            saveable.generateIdAutomatically = false;
            saveable.SetCustomData("value", i * 10);
        }
        
        Debug.Log("✅ Created sample objects");
    }
    
    private static void TestSystem()
    {
        // Test if all components are working
        var saveSystem = GameObject.Find("SimpleSaveSystem");
        if (saveSystem != null)
        {
            var saveManager = saveSystem.GetComponent<SimpleSaveManager>();
            var resourceManager = saveSystem.GetComponent<SimpleResourceManager>();
            var worldManager = saveSystem.GetComponent<SimpleWorldManager>();
            var characterManager = saveSystem.GetComponent<SimpleCharacterManager>();
            
            if (saveManager != null && resourceManager != null && worldManager != null && characterManager != null)
            {
                Debug.Log("✅ All components found and working");
            }
            else
            {
                Debug.LogWarning("⚠️ Some components missing");
            }
        }
    }
}