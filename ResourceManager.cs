using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace SaveSystem
{
    [System.Serializable]
    public class ResourceSnapshot
    {
        public Dictionary<string, long> resources = new Dictionary<string, long>();
        public List<ResourceSummary> topResources = new List<ResourceSummary>();
    }

    [System.Serializable]
    public class ResourceSummary
    {
        public string id;
        public long amount;
        public string displayName;
        public ResourceCategory category;
    }

    public class ResourceManager : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private ResourceCatalog resourceCatalog;
        [SerializeField] private List<string> topBarResourceIds = new List<string>();
        [SerializeField] private float autosaveOnChangeThrottleMs = 1000f;

        [Header("Debug")]
        [SerializeField] private bool logResourceChanges = false;

        public static ResourceManager Instance { get; private set; }

        // Events
        public event Action<string, long> OnResourceChanged;

        // Private fields
        private Dictionary<string, long> resourceAmounts = new Dictionary<string, long>();
        private Dictionary<string, float> lastChangeTime = new Dictionary<string, float>();
        private bool isInitialized = false;

        private void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
                DontDestroyOnLoad(gameObject);
                InitializeResources();
            }
            else
            {
                Destroy(gameObject);
            }
        }

        private void Start()
        {
            if (resourceCatalog == null)
            {
                Debug.LogError("ResourceCatalog is not assigned to ResourceManager!");
                return;
            }

            // Load top bar resource IDs from catalog
            LoadTopBarResourcesFromCatalog();
        }

        private void InitializeResources()
        {
            if (resourceCatalog == null)
            {
                Debug.LogWarning("ResourceCatalog not assigned, using default initialization");
                return;
            }

            // Initialize all resources with their default amounts
            foreach (var resourceDef in resourceCatalog.GetAllResources())
            {
                if (!resourceAmounts.ContainsKey(resourceDef.Id))
                {
                    resourceAmounts[resourceDef.Id] = resourceDef.DefaultAmount;
                }
            }

            isInitialized = true;
        }

        private void LoadTopBarResourcesFromCatalog()
        {
            if (resourceCatalog != null)
            {
                var topBarResources = resourceCatalog.GetTopBarResources();
                topBarResourceIds.Clear();
                foreach (var resource in topBarResources)
                {
                    topBarResourceIds.Add(resource.Id);
                }
            }
        }

        public void AddResource(string id, long amount)
        {
            if (amount <= 0)
            {
                Debug.LogWarning($"Attempted to add non-positive amount ({amount}) to resource '{id}'");
                return;
            }

            if (!IsValidResource(id))
            {
                Debug.LogError($"Invalid resource ID: {id}");
                return;
            }

            var resourceDef = resourceCatalog.GetResource(id);
            long newAmount = resourceAmounts.GetValueOrDefault(id, 0) + amount;
            
            // Clamp to max amount if specified
            if (resourceDef != null)
            {
                newAmount = resourceDef.ClampAmount(newAmount);
            }

            SetResourceAmount(id, newAmount);
        }

        public bool TryRemoveResource(string id, long amount)
        {
            if (amount <= 0)
            {
                Debug.LogWarning($"Attempted to remove non-positive amount ({amount}) from resource '{id}'");
                return false;
            }

            if (!IsValidResource(id))
            {
                Debug.LogError($"Invalid resource ID: {id}");
                return false;
            }

            long currentAmount = GetResourceAmount(id);
            if (currentAmount < amount)
            {
                return false; // Not enough resources
            }

            var resourceDef = resourceCatalog.GetResource(id);
            long newAmount = currentAmount - amount;
            
            // Ensure we don't go below minimum
            if (resourceDef != null && !resourceDef.AllowNegative)
            {
                newAmount = Math.Max(0, newAmount);
            }

            SetResourceAmount(id, newAmount);
            return true;
        }

        public long GetResourceAmount(string id)
        {
            if (!IsValidResource(id))
            {
                Debug.LogError($"Invalid resource ID: {id}");
                return 0;
            }

            return resourceAmounts.GetValueOrDefault(id, 0);
        }

        public ResourceSnapshot GetSnapshot()
        {
            return GetSnapshot(null);
        }

        public ResourceSnapshot GetSnapshot(IEnumerable<string> resourceIds)
        {
            var snapshot = new ResourceSnapshot();
            
            if (resourceIds == null)
            {
                // Get all resources
                foreach (var kvp in resourceAmounts)
                {
                    snapshot.resources[kvp.Key] = kvp.Value;
                }
            }
            else
            {
                // Get specific resources
                foreach (var id in resourceIds)
                {
                    if (resourceAmounts.ContainsKey(id))
                    {
                        snapshot.resources[id] = resourceAmounts[id];
                    }
                }
            }

            // Create top resources list
            var topBarResources = GetTopBarResources();
            foreach (var resource in topBarResources)
            {
                if (snapshot.resources.ContainsKey(resource.Id))
                {
                    snapshot.topResources.Add(new ResourceSummary
                    {
                        id = resource.Id,
                        amount = snapshot.resources[resource.Id],
                        displayName = resource.DisplayName,
                        category = resource.Category
                    });
                }
            }

            return snapshot;
        }

        public void LoadSnapshot(ResourceSnapshot snapshot)
        {
            if (snapshot == null)
            {
                Debug.LogWarning("Attempted to load null resource snapshot");
                return;
            }

            // Clear current resources
            resourceAmounts.Clear();

            // Load resources from snapshot
            foreach (var kvp in snapshot.resources)
            {
                if (IsValidResource(kvp.Key))
                {
                    resourceAmounts[kvp.Key] = kvp.Value;
                }
                else
                {
                    Debug.LogWarning($"Invalid resource ID in snapshot: {kvp.Key}");
                }
            }

            // Ensure all catalog resources exist
            if (resourceCatalog != null)
            {
                foreach (var resourceDef in resourceCatalog.GetAllResources())
                {
                    if (!resourceAmounts.ContainsKey(resourceDef.Id))
                    {
                        resourceAmounts[resourceDef.Id] = resourceDef.DefaultAmount;
                    }
                }
            }

            // Notify all resource changes
            foreach (var kvp in resourceAmounts)
            {
                OnResourceChanged?.Invoke(kvp.Key, kvp.Value);
            }

            // Mark save system as dirty
            if (SaveManager.Instance != null)
            {
                SaveManager.Instance.MarkDirty(SaveCategory.Resources);
            }
        }

        public List<ResourceDefinition> GetTopBarResources()
        {
            var result = new List<ResourceDefinition>();
            
            if (resourceCatalog != null)
            {
                foreach (var id in topBarResourceIds)
                {
                    var resource = resourceCatalog.GetResource(id);
                    if (resource != null)
                    {
                        result.Add(resource);
                    }
                }
            }

            return result;
        }

        public bool IsValidResource(string id)
        {
            return resourceCatalog != null && resourceCatalog.IsValidResource(id);
        }

        public ResourceDefinition GetResourceDefinition(string id)
        {
            return resourceCatalog?.GetResource(id);
        }

        public List<ResourceDefinition> GetAllResourceDefinitions()
        {
            return resourceCatalog?.GetAllResources() ?? new List<ResourceDefinition>();
        }

        public List<ResourceDefinition> GetResourcesByCategory(ResourceCategory category)
        {
            return resourceCatalog?.GetResourcesByCategory(category) ?? new List<ResourceDefinition>();
        }

        private void SetResourceAmount(string id, long amount)
        {
            if (!IsValidResource(id))
            {
                Debug.LogError($"Invalid resource ID: {id}");
                return;
            }

            var resourceDef = resourceCatalog.GetResource(id);
            if (resourceDef != null)
            {
                amount = resourceDef.ClampAmount(amount);
            }

            long oldAmount = resourceAmounts.GetValueOrDefault(id, 0);
            resourceAmounts[id] = amount;

            if (oldAmount != amount)
            {
                if (logResourceChanges)
                {
                    Debug.Log($"Resource '{id}' changed from {oldAmount} to {amount} (delta: {amount - oldAmount})");
                }

                OnResourceChanged?.Invoke(id, amount);
                
                // Mark save system as dirty with throttling
                MarkDirtyWithThrottle(id);
            }
        }

        private void MarkDirtyWithThrottle(string resourceId)
        {
            float currentTime = Time.time;
            float lastTime = lastChangeTime.GetValueOrDefault(resourceId, 0f);
            
            if (currentTime - lastTime >= autosaveOnChangeThrottleMs / 1000f)
            {
                if (SaveManager.Instance != null)
                {
                    SaveManager.Instance.MarkDirty(SaveCategory.Resources);
                }
                lastChangeTime[resourceId] = currentTime;
            }
        }

        // Utility methods
        public bool HasEnoughResources(string id, long amount)
        {
            return GetResourceAmount(id) >= amount;
        }

        public bool HasEnoughResources(Dictionary<string, long> requirements)
        {
            foreach (var kvp in requirements)
            {
                if (!HasEnoughResources(kvp.Key, kvp.Value))
                {
                    return false;
                }
            }
            return true;
        }

        public bool TrySpendResources(Dictionary<string, long> costs)
        {
            // First check if we have enough
            if (!HasEnoughResources(costs))
            {
                return false;
            }

            // Then spend them
            foreach (var kvp in costs)
            {
                if (!TryRemoveResource(kvp.Key, kvp.Value))
                {
                    return false;
                }
            }

            return true;
        }

        public Dictionary<string, long> GetResourceCostsForUpgrade(string upgradeId)
        {
            // This would typically come from a separate upgrade system
            // For now, return empty dictionary
            return new Dictionary<string, long>();
        }

        // Debug methods
        [ContextMenu("Log All Resources")]
        public void LogAllResources()
        {
            Debug.Log("=== Current Resources ===");
            foreach (var kvp in resourceAmounts)
            {
                var resourceDef = resourceCatalog?.GetResource(kvp.Key);
                string displayName = resourceDef?.DisplayName ?? kvp.Key;
                Debug.Log($"{displayName} ({kvp.Key}): {kvp.Value}");
            }
        }

        [ContextMenu("Add Test Resources")]
        public void AddTestResources()
        {
            if (resourceCatalog == null)
            {
                Debug.LogWarning("No resource catalog assigned");
                return;
            }

            var testResources = new Dictionary<string, long>
            {
                { "coins", 1000 },
                { "wood", 500 },
                { "stone", 250 }
            };

            foreach (var kvp in testResources)
            {
                if (IsValidResource(kvp.Key))
                {
                    AddResource(kvp.Key, kvp.Value);
                }
            }
        }

        [ContextMenu("Reset All Resources")]
        public void ResetAllResources()
        {
            if (resourceCatalog == null)
            {
                Debug.LogWarning("No resource catalog assigned");
                return;
            }

            resourceAmounts.Clear();
            InitializeResources();
            
            // Notify all changes
            foreach (var kvp in resourceAmounts)
            {
                OnResourceChanged?.Invoke(kvp.Key, kvp.Value);
            }
        }

        // Editor helper methods
        #if UNITY_EDITOR
        private void OnValidate()
        {
            if (resourceCatalog != null && Application.isPlaying)
            {
                LoadTopBarResourcesFromCatalog();
            }
        }
        #endif
    }
}