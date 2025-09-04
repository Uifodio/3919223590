using UnityEngine;
using System.Collections.Generic;

public class GameWorldManager : MonoBehaviour
{
    [Header("World Settings")]
    public bool trackAllObjects = true;
    public bool enableOfflineSimulation = true;
    public float simulationInterval = 1f;
    
    public static GameWorldManager Instance;
    
    private Dictionary<string, GameWorldObject> trackedObjects = new Dictionary<string, GameWorldObject>();
    private List<string> brokenObjects = new List<string>();
    private List<string> destroyedObjects = new List<string>();
    private Dictionary<string, bool> triggers = new Dictionary<string, bool>();
    private float lastSimulationTime;
    
    void Awake()
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
    
    void Start()
    {
        // Find all world objects in the scene
        RefreshTrackedObjects();
    }
    
    void Update()
    {
        if (enableOfflineSimulation && Time.time - lastSimulationTime >= simulationInterval)
        {
            RunOfflineSimulation();
            lastSimulationTime = Time.time;
        }
    }
    
    public void RegisterObject(GameWorldObject obj)
    {
        if (obj != null && !string.IsNullOrEmpty(obj.objectId))
        {
            trackedObjects[obj.objectId] = obj;
            Debug.Log("[GameWorldManager] Registered object: " + obj.objectId);
        }
    }
    
    public void UnregisterObject(string objectId)
    {
        if (trackedObjects.ContainsKey(objectId))
        {
            trackedObjects.Remove(objectId);
            Debug.Log("[GameWorldManager] Unregistered object: " + objectId);
        }
    }
    
    public void MarkObjectBroken(string objectId)
    {
        if (!brokenObjects.Contains(objectId))
        {
            brokenObjects.Add(objectId);
            Debug.Log("[GameWorldManager] Marked object as broken: " + objectId);
        }
    }
    
    public void MarkObjectDestroyed(string objectId)
    {
        if (!destroyedObjects.Contains(objectId))
        {
            destroyedObjects.Add(objectId);
            Debug.Log("[GameWorldManager] Marked object as destroyed: " + objectId);
        }
    }
    
    public void MarkObjectRepaired(string objectId)
    {
        if (brokenObjects.Contains(objectId))
        {
            brokenObjects.Remove(objectId);
            Debug.Log("[GameWorldManager] Marked object as repaired: " + objectId);
        }
    }
    
    public bool IsObjectBroken(string objectId)
    {
        return brokenObjects.Contains(objectId);
    }
    
    public bool IsObjectDestroyed(string objectId)
    {
        return destroyedObjects.Contains(objectId);
    }
    
    public void SetTrigger(string triggerId, bool value)
    {
        triggers[triggerId] = value;
        Debug.Log("[GameWorldManager] Set trigger " + triggerId + " to " + value);
    }
    
    public bool GetTrigger(string triggerId)
    {
        return triggers.ContainsKey(triggerId) ? triggers[triggerId] : false;
    }
    
    public List<WorldObjectData> GetAllWorldObjects()
    {
        var worldObjects = new List<WorldObjectData>();
        
        foreach (var kvp in trackedObjects)
        {
            var obj = kvp.Value;
            if (obj != null)
            {
                worldObjects.Add(new WorldObjectData
                {
                    id = obj.objectId,
                    position = obj.transform.position,
                    rotation = obj.transform.rotation,
                    scale = obj.transform.localScale,
                    isActive = obj.gameObject.activeInHierarchy,
                    isBroken = IsObjectBroken(obj.objectId),
                    isDestroyed = IsObjectDestroyed(obj.objectId),
                    customData = obj.GetCustomDataList()
                });
            }
        }
        
        return worldObjects;
    }
    
    public void LoadWorldObjects(List<WorldObjectData> worldObjects)
    {
        if (worldObjects == null) return;
        
        // Clear current state
        brokenObjects.Clear();
        destroyedObjects.Clear();
        
        // Load object states
        foreach (var objData in worldObjects)
        {
            if (trackedObjects.ContainsKey(objData.id))
            {
                var obj = trackedObjects[objData.id];
                if (obj != null)
                {
                    obj.transform.position = objData.position;
                    obj.transform.rotation = objData.rotation;
                    obj.transform.localScale = objData.scale;
                    obj.gameObject.SetActive(objData.isActive);
                    obj.LoadCustomDataList(objData.customData);
                    
                    if (objData.isBroken)
                    {
                        MarkObjectBroken(objData.id);
                    }
                    if (objData.isDestroyed)
                    {
                        MarkObjectDestroyed(objData.id);
                    }
                }
            }
        }
        
        Debug.Log("[GameWorldManager] Loaded " + worldObjects.Count + " world objects");
    }
    
    void RefreshTrackedObjects()
    {
        trackedObjects.Clear();
        
        var worldObjects = FindObjectsOfType<GameWorldObject>();
        foreach (var obj in worldObjects)
        {
            if (!string.IsNullOrEmpty(obj.objectId))
            {
                trackedObjects[obj.objectId] = obj;
            }
        }
        
        Debug.Log("[GameWorldManager] Found " + trackedObjects.Count + " tracked objects");
    }
    
    void RunOfflineSimulation()
    {
        // Simple offline simulation
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
    }
    
    [ContextMenu("Log World State")]
    public void LogWorldState()
    {
        Debug.Log("[GameWorldManager] Tracked Objects: " + trackedObjects.Count);
        Debug.Log("[GameWorldManager] Broken Objects: " + brokenObjects.Count);
        Debug.Log("[GameWorldManager] Destroyed Objects: " + destroyedObjects.Count);
        Debug.Log("[GameWorldManager] Triggers: " + triggers.Count);
    }
}