using System;
using System.Collections.Generic;
using UnityEngine;

namespace SaveSystem
{
    [System.Serializable]
    public enum CustomFieldType
    {
        Int,
        Long,
        Float,
        Bool,
        String,
        Vector3,
        Quaternion,
        Color
    }

    [System.Serializable]
    public class CustomField
    {
        [Header("Field Configuration")]
        [SerializeField] private string key = "";
        [SerializeField] private CustomFieldType type = CustomFieldType.Int;
        [SerializeField] private string defaultValue = "";

        public string Key => key;
        public CustomFieldType Type => type;
        public string DefaultValue => defaultValue;

        public CustomField()
        {
            key = Guid.NewGuid().ToString();
        }

        public CustomField(string fieldKey, CustomFieldType fieldType, string defaultVal)
        {
            key = fieldKey;
            type = fieldType;
            defaultValue = defaultVal;
        }

        public object GetTypedDefaultValue()
        {
            return ParseValue(defaultValue, type);
        }

        public static object ParseValue(string value, CustomFieldType type)
        {
            try
            {
                switch (type)
                {
                    case CustomFieldType.Int:
                        return int.Parse(value);
                    case CustomFieldType.Long:
                        return long.Parse(value);
                    case CustomFieldType.Float:
                        return float.Parse(value);
                    case CustomFieldType.Bool:
                        return bool.Parse(value);
                    case CustomFieldType.String:
                        return value;
                    case CustomFieldType.Vector3:
                        return JsonUtility.FromJson<Vector3>(value);
                    case CustomFieldType.Quaternion:
                        return JsonUtility.FromJson<Quaternion>(value);
                    case CustomFieldType.Color:
                        return JsonUtility.FromJson<Color>(value);
                    default:
                        return value;
                }
            }
            catch
            {
                return GetDefaultValueForType(type);
            }
        }

        public static string SerializeValue(object value, CustomFieldType type)
        {
            if (value == null)
                return "";

            switch (type)
            {
                case CustomFieldType.Vector3:
                case CustomFieldType.Quaternion:
                case CustomFieldType.Color:
                    return JsonUtility.ToJson(value);
                default:
                    return value.ToString();
            }
        }

        private static object GetDefaultValueForType(CustomFieldType type)
        {
            switch (type)
            {
                case CustomFieldType.Int:
                    return 0;
                case CustomFieldType.Long:
                    return 0L;
                case CustomFieldType.Float:
                    return 0f;
                case CustomFieldType.Bool:
                    return false;
                case CustomFieldType.String:
                    return "";
                case CustomFieldType.Vector3:
                    return Vector3.zero;
                case CustomFieldType.Quaternion:
                    return Quaternion.identity;
                case CustomFieldType.Color:
                    return Color.white;
                default:
                    return null;
            }
        }
    }

    [System.Serializable]
    public class SaveData
    {
        public string persistentId;
        public string prefabId;
        public Vector3 position;
        public Quaternion rotation;
        public Vector3 scale;
        public bool active;
        public Dictionary<string, object> customFields = new Dictionary<string, object>();
        public bool isBroken = false;
        public bool isDestroyed = false;
        public int version = 2;
        public string sceneName;
        public float lastUpdateTime;
    }

    public class SaveableEntity : MonoBehaviour
    {
        [Header("Identity")]
        [SerializeField] private string persistentId = "";
        [SerializeField] private string prefabId = "";

        [Header("Save Settings")]
        [SerializeField] private bool saveTransform = true;
        [SerializeField] private bool savePosition = true;
        [SerializeField] private bool saveRotation = true;
        [SerializeField] private bool saveScale = true;
        [SerializeField] private bool saveActiveState = true;
        [SerializeField] private bool saveCustomFields = true;

        [Header("Character Tracking")]
        [SerializeField] private bool isCharacter = false;
        [SerializeField] private bool trackMovement = true;
        [SerializeField] private float movementThreshold = 0.1f;
        [SerializeField] private float rotationThreshold = 1f;

        [Header("Custom Fields")]
        [SerializeField] private List<CustomField> customFields = new List<CustomField>();

        [Header("State")]
        [SerializeField] private bool isBroken = false;
        [SerializeField] private bool isDestroyed = false;

        // Events
        public event Action OnPersistedChanged;
        public event Action OnStateChanged;

        // Private fields
        private Dictionary<string, object> runtimeCustomFields = new Dictionary<string, object>();
        private Vector3 originalPosition;
        private Quaternion originalRotation;
        private Vector3 originalScale;
        private bool originalActiveState;
        private bool hasBeenInitialized = false;
        private Vector3 lastSavedPosition;
        private Quaternion lastSavedRotation;
        private float lastUpdateTime = 0f;

        // Properties
        public string PersistentId => persistentId;
        public string PrefabId => prefabId;
        public bool IsBroken => isBroken;
        public bool IsDestroyed => isDestroyed;
        public bool IsCharacter => isCharacter;

        private void Awake()
        {
            InitializeEntity();
        }

        private void Start()
        {
            if (!hasBeenInitialized)
            {
                InitializeEntity();
            }

            // Register with WorldStateManager if it's a character
            if (isCharacter && WorldStateManager.Instance != null)
            {
                WorldStateManager.Instance.RegisterCharacter(this);
            }
        }

        private void Update()
        {
            // Track movement for characters
            if (isCharacter && trackMovement)
            {
                CheckForMovement();
            }
        }

        private void CheckForMovement()
        {
            if (Vector3.Distance(transform.position, lastSavedPosition) > movementThreshold ||
                Quaternion.Angle(transform.rotation, lastSavedRotation) > rotationThreshold)
            {
                // Mark as dirty for save
                if (SaveManager.Instance != null)
                {
                    SaveManager.Instance.MarkDirty(SaveCategory.CharacterData);
                }
                
                lastSavedPosition = transform.position;
                lastSavedRotation = transform.rotation;
                lastUpdateTime = Time.time;
            }
        }

        private void InitializeEntity()
        {
            // Generate persistent ID if empty
            if (string.IsNullOrEmpty(persistentId))
            {
                persistentId = Guid.NewGuid().ToString();
            }

            // Use asset GUID as prefab ID if empty
            if (string.IsNullOrEmpty(prefabId))
            {
                prefabId = GetAssetGUID();
            }

            // Store original values
            originalPosition = transform.position;
            originalRotation = transform.rotation;
            originalScale = transform.localScale;
            originalActiveState = gameObject.activeInHierarchy;

            // Initialize custom fields
            InitializeCustomFields();

            // Set initial tracking values
            lastSavedPosition = transform.position;
            lastSavedRotation = transform.rotation;
            lastUpdateTime = Time.time;

            hasBeenInitialized = true;
        }

        private void InitializeCustomFields()
        {
            runtimeCustomFields.Clear();
            foreach (var field in customFields)
            {
                if (!string.IsNullOrEmpty(field.Key))
                {
                    runtimeCustomFields[field.Key] = field.GetTypedDefaultValue();
                }
            }
        }

        private string GetAssetGUID()
        {
            #if UNITY_EDITOR
            var prefab = UnityEditor.PrefabUtility.GetCorrespondingObjectFromSource(gameObject);
            if (prefab != null)
            {
                var path = UnityEditor.AssetDatabase.GetAssetPath(prefab);
                return UnityEditor.AssetDatabase.AssetPathToGUID(path);
            }
            #endif
            return gameObject.name; // Fallback to object name
        }

        public SaveData Serialize()
        {
            var saveData = new SaveData
            {
                persistentId = persistentId,
                prefabId = prefabId,
                version = 2,
                sceneName = UnityEngine.SceneManagement.SceneManager.GetActiveScene().name,
                lastUpdateTime = Time.time
            };

            // Save transform data
            if (saveTransform)
            {
                if (savePosition)
                    saveData.position = transform.position;
                if (saveRotation)
                    saveData.rotation = transform.rotation;
                if (saveScale)
                    saveData.scale = transform.localScale;
            }

            // Save active state
            if (saveActiveState)
            {
                saveData.active = gameObject.activeInHierarchy;
            }

            // Save custom fields
            if (saveCustomFields)
            {
                saveData.customFields = new Dictionary<string, object>(runtimeCustomFields);
            }

            // Save state
            saveData.isBroken = isBroken;
            saveData.isDestroyed = isDestroyed;

            return saveData;
        }

        public void Deserialize(SaveData data)
        {
            if (data == null)
            {
                Debug.LogWarning($"SaveableEntity {gameObject.name}: Received null save data");
                return;
            }

            // Apply transform data
            if (saveTransform)
            {
                if (savePosition && data.position != Vector3.zero)
                    transform.position = data.position;
                if (saveRotation && data.rotation != Quaternion.identity)
                    transform.rotation = data.rotation;
                if (saveScale && data.scale != Vector3.zero)
                    transform.localScale = data.scale;
            }

            // Apply active state
            if (saveActiveState)
            {
                gameObject.SetActive(data.active);
            }

            // Apply custom fields
            if (saveCustomFields && data.customFields != null)
            {
                foreach (var kvp in data.customFields)
                {
                    runtimeCustomFields[kvp.Key] = kvp.Value;
                }
            }

            // Apply state
            isBroken = data.isBroken;
            isDestroyed = data.isDestroyed;

            // Update tracking values
            lastSavedPosition = transform.position;
            lastSavedRotation = transform.rotation;
            lastUpdateTime = data.lastUpdateTime;

            // Update visual state
            UpdateVisualState();

            OnPersistedChanged?.Invoke();
            OnStateChanged?.Invoke();
        }

        public void MarkBroken()
        {
            if (!isBroken)
            {
                isBroken = true;
                UpdateVisualState();
                OnPersistedChanged?.Invoke();
                OnStateChanged?.Invoke();
                
                // Mark save system as dirty
                if (SaveManager.Instance != null)
                {
                    SaveManager.Instance.MarkDirty(SaveCategory.WorldState);
                }
            }
        }

        public void MarkDestroyed()
        {
            if (!isDestroyed)
            {
                isDestroyed = true;
                UpdateVisualState();
                OnPersistedChanged?.Invoke();
                OnStateChanged?.Invoke();
                
                // Mark save system as dirty
                if (SaveManager.Instance != null)
                {
                    SaveManager.Instance.MarkDirty(SaveCategory.WorldState);
                }
            }
        }

        public void Repair()
        {
            if (isBroken || isDestroyed)
            {
                isBroken = false;
                isDestroyed = false;
                UpdateVisualState();
                OnPersistedChanged?.Invoke();
                OnStateChanged?.Invoke();
                
                // Mark save system as dirty
                if (SaveManager.Instance != null)
                {
                    SaveManager.Instance.MarkDirty(SaveCategory.WorldState);
                }
            }
        }

        private void UpdateVisualState()
        {
            // This method can be overridden in derived classes to handle visual updates
            // For example, changing materials, disabling colliders, etc.
            
            if (isDestroyed)
            {
                // Hide or disable the object
                gameObject.SetActive(false);
            }
            else if (isBroken)
            {
                // Show broken state (could change material, add cracks, etc.)
                gameObject.SetActive(true);
            }
            else
            {
                // Show normal state
                gameObject.SetActive(true);
            }
        }

        // Custom field management
        public void SetCustomField(string key, object value)
        {
            if (runtimeCustomFields.ContainsKey(key))
            {
                runtimeCustomFields[key] = value;
                OnPersistedChanged?.Invoke();
                
                // Mark save system as dirty
                if (SaveManager.Instance != null)
                {
                    SaveManager.Instance.MarkDirty(SaveCategory.WorldState);
                }
            }
            else
            {
                Debug.LogWarning($"Custom field '{key}' not found in SaveableEntity {gameObject.name}");
            }
        }

        public T GetCustomField<T>(string key, T defaultValue = default(T))
        {
            if (runtimeCustomFields.TryGetValue(key, out var value))
            {
                try
                {
                    return (T)Convert.ChangeType(value, typeof(T));
                }
                catch
                {
                    return defaultValue;
                }
            }
            return defaultValue;
        }

        public bool HasCustomField(string key)
        {
            return runtimeCustomFields.ContainsKey(key);
        }

        public Dictionary<string, object> GetAllCustomFields()
        {
            return new Dictionary<string, object>(runtimeCustomFields);
        }

        // Utility methods
        public bool HasChangedFromOriginal()
        {
            if (!hasBeenInitialized)
                return false;

            if (savePosition && Vector3.Distance(transform.position, originalPosition) > 0.001f)
                return true;
            if (saveRotation && Quaternion.Angle(transform.rotation, originalRotation) > 0.001f)
                return true;
            if (saveScale && Vector3.Distance(transform.localScale, originalScale) > 0.001f)
                return true;
            if (saveActiveState && gameObject.activeInHierarchy != originalActiveState)
                return true;
            if (isBroken || isDestroyed)
                return true;

            return false;
        }

        public void ResetToOriginal()
        {
            if (savePosition)
                transform.position = originalPosition;
            if (saveRotation)
                transform.rotation = originalRotation;
            if (saveScale)
                transform.localScale = originalScale;
            if (saveActiveState)
                gameObject.SetActive(originalActiveState);

            isBroken = false;
            isDestroyed = false;
            UpdateVisualState();
            OnPersistedChanged?.Invoke();
            OnStateChanged?.Invoke();
        }

        public void ForceUpdate()
        {
            // Force an update of tracking values
            lastSavedPosition = transform.position;
            lastSavedRotation = transform.rotation;
            lastUpdateTime = Time.time;
        }

        // Editor helper methods
        #if UNITY_EDITOR
        private void OnValidate()
        {
            if (string.IsNullOrEmpty(persistentId))
            {
                persistentId = Guid.NewGuid().ToString();
            }

            // Validate custom fields
            var usedKeys = new HashSet<string>();
            for (int i = 0; i < customFields.Count; i++)
            {
                var field = customFields[i];
                if (string.IsNullOrEmpty(field.Key))
                {
                    // Generate new key
                    var newKey = Guid.NewGuid().ToString();
                    var keyField = typeof(CustomField).GetField("key", 
                        System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
                    keyField?.SetValue(field, newKey);
                }
                else if (usedKeys.Contains(field.Key))
                {
                    Debug.LogWarning($"Duplicate custom field key '{field.Key}' in SaveableEntity {gameObject.name}");
                }
                else
                {
                    usedKeys.Add(field.Key);
                }
            }
        }

        [ContextMenu("Generate New Persistent ID")]
        public void GenerateNewPersistentId()
        {
            persistentId = Guid.NewGuid().ToString();
            UnityEditor.EditorUtility.SetDirty(this);
        }

        [ContextMenu("Add Custom Field")]
        public void AddCustomField()
        {
            customFields.Add(new CustomField());
            UnityEditor.EditorUtility.SetDirty(this);
        }

        [ContextMenu("Log Save Data")]
        public void LogSaveData()
        {
            var saveData = Serialize();
            Debug.Log($"SaveableEntity {gameObject.name} Save Data:\n{JsonUtility.ToJson(saveData, true)}");
        }

        [ContextMenu("Force Update Position")]
        public void ForceUpdatePosition()
        {
            ForceUpdate();
        }
        #endif
    }
}