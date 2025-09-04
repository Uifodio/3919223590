using UnityEngine;
using System.Collections.Generic;

public class GameResourceManager : MonoBehaviour
{
    [Header("Resources")]
    public List<ResourceDefinition> resourceDefinitions = new List<ResourceDefinition>();
    
    [Header("UI Display")]
    public bool showResourceUI = true;
    public Vector2 uiPosition = new Vector2(10, 10);
    public int fontSize = 16;
    
    public static GameResourceManager Instance;
    
    private Dictionary<string, long> resources = new Dictionary<string, long>();
    private Dictionary<string, ResourceDefinition> resourceDefs = new Dictionary<string, ResourceDefinition>();
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            Initialize();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    void Initialize()
    {
        // Initialize resource definitions
        foreach (var def in resourceDefinitions)
        {
            resourceDefs[def.id] = def;
            if (!resources.ContainsKey(def.id))
            {
                resources[def.id] = def.defaultAmount;
            }
        }
    }
    
    public void AddResource(string resourceId, long amount)
    {
        if (!resourceDefs.ContainsKey(resourceId))
        {
            Debug.LogWarning("[GameResourceManager] Unknown resource: " + resourceId);
            return;
        }
        
        if (!resources.ContainsKey(resourceId))
        {
            resources[resourceId] = 0;
        }
        
        resources[resourceId] += amount;
        
        // Clamp to max if defined
        var def = resourceDefs[resourceId];
        if (def.maxAmount > 0)
        {
            resources[resourceId] = Mathf.Min(resources[resourceId], def.maxAmount);
        }
        
        Debug.Log("[GameResourceManager] Added " + amount + " " + resourceId + ". Total: " + resources[resourceId]);
    }
    
    public bool TryRemoveResource(string resourceId, long amount)
    {
        if (!resources.ContainsKey(resourceId))
        {
            return false;
        }
        
        if (resources[resourceId] < amount)
        {
            return false;
        }
        
        resources[resourceId] -= amount;
        Debug.Log("[GameResourceManager] Removed " + amount + " " + resourceId + ". Remaining: " + resources[resourceId]);
        return true;
    }
    
    public long GetResourceAmount(string resourceId)
    {
        return resources.ContainsKey(resourceId) ? resources[resourceId] : 0;
    }
    
    public bool HasEnoughResource(string resourceId, long amount)
    {
        return GetResourceAmount(resourceId) >= amount;
    }
    
    public List<ResourceData> GetAllResources()
    {
        var resourceList = new List<ResourceData>();
        foreach (var kvp in resources)
        {
            resourceList.Add(new ResourceData
            {
                id = kvp.Key,
                amount = kvp.Value
            });
        }
        return resourceList;
    }
    
    public void LoadResources(List<ResourceData> loadedResources)
    {
        resources.Clear();
        foreach (var resource in loadedResources)
        {
            resources[resource.id] = resource.amount;
        }
        
        Debug.Log("[GameResourceManager] Loaded " + loadedResources.Count + " resources");
    }
    
    public ResourceDefinition GetResourceDefinition(string resourceId)
    {
        return resourceDefs.ContainsKey(resourceId) ? resourceDefs[resourceId] : null;
    }
    
    void OnGUI()
    {
        if (!showResourceUI) return;
        
        GUILayout.BeginArea(new Rect(uiPosition.x, uiPosition.y, 300, 200));
        
        GUIStyle style = new GUIStyle(GUI.skin.label);
        style.fontSize = fontSize;
        style.normal.textColor = Color.white;
        
        GUILayout.Label("Resources", style);
        
        foreach (var def in resourceDefinitions)
        {
            if (def.showInTopBar)
            {
                long amount = GetResourceAmount(def.id);
                GUILayout.Label(def.displayName + ": " + amount.ToString("N0"), style);
            }
        }
        
        GUILayout.EndArea();
    }
    
    // Debug methods
    [ContextMenu("Add Test Resources")]
    public void AddTestResources()
    {
        AddResource("coins", 1000);
        AddResource("wood", 500);
        AddResource("stone", 250);
    }
    
    [ContextMenu("Log All Resources")]
    public void LogAllResources()
    {
        Debug.Log("=== Current Resources ===");
        foreach (var kvp in resources)
        {
            Debug.Log(kvp.Key + ": " + kvp.Value);
        }
    }
}

[System.Serializable]
public class ResourceDefinition
{
    public string id;
    public string displayName;
    public long defaultAmount;
    public long maxAmount = 0; // 0 = unlimited
    public bool showInTopBar = true;
    public string category = "General";
}