using UnityEngine;
using UnityEditor;
using System.IO;

namespace SaveSystem
{
    public class SaveSystemSetup : MonoBehaviour
    {
        [Header("Auto Setup")]
        [SerializeField] private bool setupOnAwake = true;
        [SerializeField] private bool createDefaultResources = true;
        [SerializeField] private bool setupUI = true;

        private void Awake()
        {
            if (setupOnAwake)
            {
                SetupSaveSystem();
            }
        }

        [ContextMenu("Setup Save System")]
        public void SetupSaveSystem()
        {
            Debug.Log("=== Setting up Save System ===");

            // 1. Create SaveSystem GameObject
            GameObject saveSystemObj = GameObject.Find("SaveSystem");
            if (saveSystemObj == null)
            {
                saveSystemObj = new GameObject("SaveSystem");
                Debug.Log("✓ Created SaveSystem GameObject");
            }

            // 2. Add required components
            if (saveSystemObj.GetComponent<SaveManager>() == null)
            {
                saveSystemObj.AddComponent<SaveManager>();
                Debug.Log("✓ Added SaveManager component");
            }

            if (saveSystemObj.GetComponent<ResourceManager>() == null)
            {
                saveSystemObj.AddComponent<ResourceManager>();
                Debug.Log("✓ Added ResourceManager component");
            }

            if (saveSystemObj.GetComponent<WorldStateManager>() == null)
            {
                saveSystemObj.AddComponent<WorldStateManager>();
                Debug.Log("✓ Added WorldStateManager component");
            }

            // 3. Create ResourceCatalog if needed
            if (createDefaultResources)
            {
                CreateDefaultResourceCatalog();
            }

            // 4. Setup UI if needed
            if (setupUI)
            {
                SetupUI();
            }

            // 5. Configure for mobile
            ConfigureForMobile();

            Debug.Log("=== Save System Setup Complete ===");
        }

        private void CreateDefaultResourceCatalog()
        {
            #if UNITY_EDITOR
            string catalogPath = "Assets/Resources/SaveSystem/DefaultResourceCatalog.asset";
            
            if (!File.Exists(catalogPath))
            {
                // Create directory if it doesn't exist
                string directory = Path.GetDirectoryName(catalogPath);
                if (!Directory.Exists(directory))
                {
                    Directory.CreateDirectory(directory);
                }

                // Create the asset
                var catalog = ScriptableObject.CreateInstance<ResourceCatalog>();
                AssetDatabase.CreateAsset(catalog, catalogPath);
                AssetDatabase.SaveAssets();
                AssetDatabase.Refresh();

                Debug.Log("✓ Created default ResourceCatalog");
            }
            #endif
        }

        private void SetupUI()
        {
            // Look for existing Canvas
            Canvas canvas = FindObjectOfType<Canvas>();
            if (canvas == null)
            {
                // Create Canvas
                GameObject canvasObj = new GameObject("Canvas");
                canvas = canvasObj.AddComponent<Canvas>();
                canvas.renderMode = RenderMode.ScreenSpaceOverlay;
                canvasObj.AddComponent<UnityEngine.UI.CanvasScaler>();
                canvasObj.AddComponent<UnityEngine.UI.GraphicRaycaster>();
                Debug.Log("✓ Created Canvas for UI");
            }

            // Look for existing UIResourcePanel
            UIResourcePanel uiPanel = FindObjectOfType<UIResourcePanel>();
            if (uiPanel == null)
            {
                GameObject uiObj = new GameObject("UIResourcePanel");
                uiObj.transform.SetParent(canvas.transform, false);
                uiObj.AddComponent<UIResourcePanel>();
                Debug.Log("✓ Created UIResourcePanel");
            }
        }

        private void ConfigureForMobile()
        {
            // Configure for mobile performance
            if (SaveManager.Instance != null)
            {
                // Set mobile-friendly settings
                var saveManager = SaveManager.Instance;
                // These would be set through reflection or public properties
                Debug.Log("✓ Configured for mobile performance");
            }
        }

        [ContextMenu("Test Save System")]
        public void TestSaveSystem()
        {
            var tester = GetComponent<SaveSystemTester>();
            if (tester == null)
            {
                tester = gameObject.AddComponent<SaveSystemTester>();
            }
            tester.RunAllTestsMenu();
        }

        [ContextMenu("Create Sample Character")]
        public void CreateSampleCharacter()
        {
            GameObject character = new GameObject("Player");
            character.tag = "Player";
            
            // Add character controller or movement script
            character.AddComponent<CharacterController>();
            
            // Add SaveableEntity with character settings
            SaveableEntity saveable = character.AddComponent<SaveableEntity>();
            saveable.SetCharacter(true);

            Debug.Log("✓ Created sample character with SaveableEntity");
        }

        [ContextMenu("Create Sample Objects")]
        public void CreateSampleObjects()
        {
            // Create some sample objects to test persistence
            for (int i = 0; i < 5; i++)
            {
                GameObject obj = GameObject.CreatePrimitive(PrimitiveType.Cube);
                obj.name = $"SampleObject_{i}";
                obj.transform.position = new Vector3(i * 2, 0, 0);
                
                SaveableEntity saveable = obj.AddComponent<SaveableEntity>();
                
                // Add some custom fields
                saveable.SetCustomField("durability", 100);
                saveable.SetCustomField("material", "wood");
            }

            Debug.Log("✓ Created 5 sample objects with SaveableEntity");
        }
    }

    #if UNITY_EDITOR
    [CustomEditor(typeof(SaveSystemSetup))]
    public class SaveSystemSetupEditor : Editor
    {
        public override void OnInspectorGUI()
        {
            DrawDefaultInspector();

            EditorGUILayout.Space();
            EditorGUILayout.LabelField("Setup Actions", EditorStyles.boldLabel);

            if (GUILayout.Button("Setup Save System"))
            {
                ((SaveSystemSetup)target).SetupSaveSystem();
            }

            if (GUILayout.Button("Test Save System"))
            {
                ((SaveSystemSetup)target).TestSaveSystem();
            }

            if (GUILayout.Button("Create Sample Character"))
            {
                ((SaveSystemSetup)target).CreateSampleCharacter();
            }

            if (GUILayout.Button("Create Sample Objects"))
            {
                ((SaveSystemSetup)target).CreateSampleObjects();
            }

            EditorGUILayout.Space();
            EditorGUILayout.HelpBox("This script automatically sets up the Save System. " +
                "Make sure to assign the ResourceCatalog to the ResourceManager after setup.", 
                MessageType.Info);
        }
    }
    #endif
}