using System.Collections.Generic;
using UnityEngine;

public class SimpleWorldManager : MonoBehaviour
{
    [Header("World Settings")]
    public bool trackAllObjects = true;
    public bool enableOfflineSimulation = true;
    public float simulationInterval = 1f;
    
    public static SimpleWorldManager Instance { get; private set; }
    
    // Private
    private Dictionary<string, SaveableObject> trackedObjects = new Dictionary<string, SaveableObject>();
    private List<string> brokenObjects = new List<string>();
    private Dictionary<string, bool> triggers = new Dictionary<string, bool>();
    private float lastSimulationTime;
    
    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    private void Start()
    {
        // Find all saveable objects in the scene
        RefreshTrackedObjects();
    }
    
    private void Update()
    {
        if (enableOfflineSimulation && Time.time - lastSimulationTime >= simulationInterval)
        {
            RunOfflineSimulation();
            lastSimulationTime = Time.time;
        }
    }
    
    public void RegisterObject(SaveableObject obj)
    {
        if (obj != null && !string.IsNullOrEmpty(obj.objectId))
        {
            trackedObjects[obj.objectId] = obj;
        }
    }
    
    public void UnregisterObject(string objectId)
    {
        if (trackedObjects.ContainsKey(objectId))
        {
            trackedObjects.Remove(objectId);
        }
    }
    
    public void MarkObjectBroken(string objectId)
    {
        if (!brokenObjects.Contains(objectId))
        {
            brokenObjects.Add(objectId);
        }
    }
    
    public void MarkObjectRepaired(string objectId)
    {
        if (brokenObjects.Contains(objectId))
        {
            brokenObjects.Remove(objectId);
        }
    }
    
    public bool IsObjectBroken(string objectId)
    {
        return brokenObjects.Contains(objectId);
    }
    
    public void SetTrigger(string triggerId, bool value)
    {
        triggers[triggerId] = value;
    }
    
    public bool GetTrigger(string triggerId)
    {
        return triggers.ContainsKey(triggerId) ? triggers[triggerId] : false;
    }
    
    public WorldStateData GetWorldState()
    {
        var worldState = new WorldStateData();
        
        // Collect all object states
        foreach (var kvp in trackedObjects)
        {
            var obj = kvp.Value;
            if (obj != null)
            {
                worldState.objects.Add(new ObjectState
                {
                    id = obj.objectId,
                    position = obj.transform.position,
                    rotation = obj.transform.rotation,
                    scale = obj.transform.localScale,
                    isActive = obj.gameObject.activeInHierarchy,
                    customData = obj.GetCustomData()
                });
            }
        }
        
        // Copy broken objects and triggers
        worldState.brokenObjects = new List<string>(brokenObjects);
        worldState.triggers = new Dictionary<string, bool>(triggers);
        
        return worldState;
    }
    
    public void LoadWorldState(WorldStateData worldState)
    {
        if (worldState == null) return;
        
        // Clear current state
        brokenObjects.Clear();
        triggers.Clear();
        
        // Load broken objects
        if (worldState.brokenObjects != null)
        {
            brokenObjects = new List<string>(worldState.brokenObjects);
        }
        
        // Load triggers
        if (worldState.triggers != null)
        {
            triggers = new Dictionary<string, bool>(worldState.triggers);
        }
        
        // Apply object states
        if (worldState.objects != null)
        {
            foreach (var objState in worldState.objects)
            {
                if (trackedObjects.ContainsKey(objState.id))
                {
                    var obj = trackedObjects[objState.id];
                    if (obj != null)
                    {
                        obj.transform.position = objState.position;
                        obj.transform.rotation = objState.rotation;
                        obj.transform.localScale = objState.scale;
                        obj.gameObject.SetActive(objState.isActive);
                        obj.LoadCustomData(objState.customData);
                    }
                }
            }
        }
        
        // Update visual states
        UpdateObjectVisualStates();
    }
    
    private void UpdateObjectVisualStates()
    {
        foreach (var objectId in brokenObjects)
        {
            if (trackedObjects.ContainsKey(objectId))
            {
                var obj = trackedObjects[objectId];
                if (obj != null)
                {
                    obj.UpdateVisualState();
                }
            }
        }
    }
    
    private void RefreshTrackedObjects()
    {
        trackedObjects.Clear();
        
        var saveableObjects = FindObjectsOfType<SaveableObject>();
        foreach (var obj in saveableObjects)
        {
            if (!string.IsNullOrEmpty(obj.objectId))
            {
                trackedObjects[obj.objectId] = obj;
            }
        }
    }
    
    private void RunOfflineSimulation()
    {
        // Simple offline simulation - could be expanded
        // For now, just log that simulation is running
        if (Application.isPlaying)
        {
            // Add any offline simulation logic here
        }
    }
    
    // Debug methods
    [ContextMenu("Refresh Tracked Objects")]
    public void RefreshTrackedObjectsDebug()
    {
        RefreshTrackedObjects();
        Debug.Log($"[SimpleWorldManager] Found {trackedObjects.Count} tracked objects");
    }
    
    [ContextMenu("Log World State")]
    public void LogWorldState()
    {
        Debug.Log($"[SimpleWorldManager] Tracked Objects: {trackedObjects.Count}");
        Debug.Log($"[SimpleWorldManager] Broken Objects: {brokenObjects.Count}");
        Debug.Log($"[SimpleWorldManager] Triggers: {triggers.Count}");
    }
}