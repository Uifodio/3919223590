using System.Collections.Generic;
using UnityEngine;

public class SaveableObject : MonoBehaviour
{
    [Header("Object Settings")]
    public string objectId = "";
    public bool generateIdAutomatically = true;
    public bool savePosition = true;
    public bool saveRotation = true;
    public bool saveScale = true;
    public bool saveActiveState = true;
    public bool saveCustomData = true;
    
    [Header("Custom Data")]
    public List<CustomDataField> customFields = new List<CustomDataField>();
    
    [Header("Visual State")]
    public bool isBroken = false;
    public bool isDestroyed = false;
    public Material brokenMaterial;
    public Material destroyedMaterial;
    
    // Private
    private Dictionary<string, object> customData = new Dictionary<string, object>();
    private Renderer objectRenderer;
    private Material originalMaterial;
    
    private void Awake()
    {
        // Generate ID if needed
        if (generateIdAutomatically && string.IsNullOrEmpty(objectId))
        {
            objectId = System.Guid.NewGuid().ToString();
        }
        
        // Get renderer for visual state changes
        objectRenderer = GetComponent<Renderer>();
        if (objectRenderer != null)
        {
            originalMaterial = objectRenderer.material;
        }
        
        // Initialize custom data
        InitializeCustomData();
    }
    
    private void Start()
    {
        // Register with world manager
        if (SimpleWorldManager.Instance != null)
        {
            SimpleWorldManager.Instance.RegisterObject(this);
        }
        
        // Update visual state
        UpdateVisualState();
    }
    
    private void OnDestroy()
    {
        // Unregister from world manager
        if (SimpleWorldManager.Instance != null)
        {
            SimpleWorldManager.Instance.UnregisterObject(objectId);
        }
    }
    
    private void InitializeCustomData()
    {
        customData.Clear();
        foreach (var field in customFields)
        {
            if (!string.IsNullOrEmpty(field.key))
            {
                customData[field.key] = field.GetValue();
            }
        }
    }
    
    public void SetCustomData(string key, object value)
    {
        if (saveCustomData)
        {
            customData[key] = value;
        }
    }
    
    public T GetCustomData<T>(string key, T defaultValue = default(T))
    {
        if (customData.ContainsKey(key))
        {
            try
            {
                return (T)customData[key];
            }
            catch
            {
                return defaultValue;
            }
        }
        return defaultValue;
    }
    
    public Dictionary<string, object> GetCustomData()
    {
        return new Dictionary<string, object>(customData);
    }
    
    public void LoadCustomData(Dictionary<string, object> data)
    {
        if (data != null)
        {
            customData = new Dictionary<string, object>(data);
        }
    }
    
    public void MarkBroken()
    {
        isBroken = true;
        isDestroyed = false;
        UpdateVisualState();
        
        if (SimpleWorldManager.Instance != null)
        {
            SimpleWorldManager.Instance.MarkObjectBroken(objectId);
        }
    }
    
    public void MarkDestroyed()
    {
        isDestroyed = true;
        isBroken = false;
        UpdateVisualState();
        
        if (SimpleWorldManager.Instance != null)
        {
            SimpleWorldManager.Instance.MarkObjectBroken(objectId);
        }
    }
    
    public void Repair()
    {
        isBroken = false;
        isDestroyed = false;
        UpdateVisualState();
        
        if (SimpleWorldManager.Instance != null)
        {
            SimpleWorldManager.Instance.MarkObjectRepaired(objectId);
        }
    }
    
    private void UpdateVisualState()
    {
        if (objectRenderer == null) return;
        
        if (isDestroyed)
        {
            // Hide object
            gameObject.SetActive(false);
        }
        else if (isBroken)
        {
            // Show broken state
            gameObject.SetActive(true);
            if (brokenMaterial != null)
            {
                objectRenderer.material = brokenMaterial;
            }
        }
        else
        {
            // Show normal state
            gameObject.SetActive(true);
            if (originalMaterial != null)
            {
                objectRenderer.material = originalMaterial;
            }
        }
    }
    
    // Debug methods
    [ContextMenu("Mark as Broken")]
    public void MarkBrokenDebug()
    {
        MarkBroken();
    }
    
    [ContextMenu("Mark as Destroyed")]
    public void MarkDestroyedDebug()
    {
        MarkDestroyed();
    }
    
    [ContextMenu("Repair Object")]
    public void RepairDebug()
    {
        Repair();
    }
    
    [ContextMenu("Log Object Data")]
    public void LogObjectData()
    {
        Debug.Log($"[SaveableObject] {gameObject.name} (ID: {objectId})");
        Debug.Log($"  Position: {transform.position}");
        Debug.Log($"  Rotation: {transform.rotation.eulerAngles}");
        Debug.Log($"  Scale: {transform.localScale}");
        Debug.Log($"  Active: {gameObject.activeInHierarchy}");
        Debug.Log($"  Broken: {isBroken}");
        Debug.Log($"  Destroyed: {isDestroyed}");
        Debug.Log($"  Custom Data Count: {customData.Count}");
    }
}

[System.Serializable]
public class CustomDataField
{
    public string key;
    public CustomDataType type;
    public string stringValue;
    public int intValue;
    public float floatValue;
    public bool boolValue;
    public Vector3 vector3Value;
    
    public object GetValue()
    {
        switch (type)
        {
            case CustomDataType.String:
                return stringValue;
            case CustomDataType.Int:
                return intValue;
            case CustomDataType.Float:
                return floatValue;
            case CustomDataType.Bool:
                return boolValue;
            case CustomDataType.Vector3:
                return vector3Value;
            default:
                return stringValue;
        }
    }
}

public enum CustomDataType
{
    String,
    Int,
    Float,
    Bool,
    Vector3
}