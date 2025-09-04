using System;
using System.Collections.Generic;
using UnityEngine;

public class SimpleResourceManager : MonoBehaviour
{
    [Header("Resources")]
    public List<ResourceDefinition> resourceDefinitions = new List<ResourceDefinition>();
    
    [Header("UI")]
    public bool showResourceUI = true;
    public Vector2 uiPosition = new Vector2(10, 10);
    
    public static SimpleResourceManager Instance { get; private set; }
    
    // Events
    public event Action<string, long> OnResourceChanged;
    
    // Private
    private Dictionary<string, long> resources = new Dictionary<string, long>();
    private Dictionary<string, ResourceDefinition> resourceDefs = new Dictionary<string, ResourceDefinition>();
    
    private void Awake()
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
    
    private void Initialize()
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
            Debug.LogWarning($"[SimpleResourceManager] Unknown resource: {resourceId}");
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
        
        OnResourceChanged?.Invoke(resourceId, resources[resourceId]);
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
        OnResourceChanged?.Invoke(resourceId, resources[resourceId]);
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
    
    public Dictionary<string, long> GetAllResources()
    {
        return new Dictionary<string, long>(resources);
    }
    
    public void LoadResources(Dictionary<string, long> loadedResources)
    {
        resources = new Dictionary<string, long>(loadedResources);
        
        // Notify all changes
        foreach (var kvp in resources)
        {
            OnResourceChanged?.Invoke(kvp.Key, kvp.Value);
        }
    }
    
    public ResourceDefinition GetResourceDefinition(string resourceId)
    {
        return resourceDefs.ContainsKey(resourceId) ? resourceDefs[resourceId] : null;
    }
    
    public List<ResourceDefinition> GetTopBarResources()
    {
        var topBarResources = new List<ResourceDefinition>();
        foreach (var def in resourceDefinitions)
        {
            if (def.showInTopBar)
            {
                topBarResources.Add(def);
            }
        }
        return topBarResources;
    }
    
    private void OnGUI()
    {
        if (!showResourceUI) return;
        
        GUILayout.BeginArea(new Rect(uiPosition.x, uiPosition.y, 300, 200));
        GUILayout.Label("Resources", GUI.skin.box);
        
        foreach (var def in GetTopBarResources())
        {
            long amount = GetResourceAmount(def.id);
            GUILayout.Label($"{def.displayName}: {amount:N0}");
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
            Debug.Log($"{kvp.Key}: {kvp.Value}");
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