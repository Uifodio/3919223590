using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace SaveSystem
{
    [System.Serializable]
    public class ResourceTransaction
    {
        public string resourceId;
        public long amount;
        public long previousAmount;
        public long newAmount;
        public DateTime timestamp;
        public string reason;
    }

    public class ResourceManager : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private ResourceCatalog resourceCatalog;
        [SerializeField] private List<string> topBarResourceIds = new List<string>();
        [SerializeField] private float autosaveOnChangeThrottleMs = 500f;

        [Header("Professional Features")]
        [SerializeField] private bool enableTransactionLogging = true;
        [SerializeField] private int maxTransactionHistory = 1000;
        [SerializeField] private bool enableResourceValidation = true;
        [SerializeField] private bool enableResourceLimits = true;
        [SerializeField] private bool enableResourceDecay = false;
        [SerializeField] private float decayIntervalSeconds = 60f;

        [Header("Debug")]
        [SerializeField] private bool logResourceChanges = false;
        [SerializeField] private bool showResourceDebugUI = false;

        public static ResourceManager Instance { get; private set; }

        // Events
        public event Action<string, long> OnResourceChanged;
        public event Action<ResourceTransaction> OnResourceTransaction;
        public event Action<string, long, long> OnResourceLimitReached;

        // Private fields
        private Dictionary<string, long> resourceAmounts = new Dictionary<string, long>();
        private Dictionary<string, float> lastChangeTime = new Dictionary<string, float>();
        private List<ResourceTransaction> transactionHistory = new List<ResourceTransaction>();
        private bool isInitialized = false;
        private float lastDecayTime = 0f;

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

        private void Update()
        {
            // Handle resource decay
            if (enableResourceDecay && Time.time - lastDecayTime >= decayIntervalSeconds)
            {
                ProcessResourceDecay();
                lastDecayTime = Time.time;
            }
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

        public void AddResource(string id, long amount, string reason = "Unknown")
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
            long previousAmount = resourceAmounts.GetValueOrDefault(id, 0);
            long newAmount = previousAmount + amount;
            
            // Apply limits if enabled
            if (enableResourceLimits && resourceDef != null)
            {
                newAmount = resourceDef.ClampAmount(newAmount);
                
                // Check if limit was reached
                if (newAmount >= resourceDef.MaxAmount)
                {
                    OnResourceLimitReached?.Invoke(id, newAmount, resourceDef.MaxAmount);
                }
            }

            SetResourceAmount(id, newAmount, reason, previousAmount);
        }

        public bool TryRemoveResource(string id, long amount, string reason = "Unknown")
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

            SetResourceAmount(id, newAmount, reason, currentAmount);
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
                    snapshot.topResources.Add(new ResourceSnapshot
                    {
                        id = resource.Id,
                        amount = snapshot.resources[resource.Id]
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

        private void SetResourceAmount(string id, long amount, string reason, long previousAmount)
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

                // Log transaction
                if (enableTransactionLogging)
                {
                    var transaction = new ResourceTransaction
                    {
                        resourceId = id,
                        amount = amount - oldAmount,
                        previousAmount = oldAmount,
                        newAmount = amount,
                        timestamp = DateTime.UtcNow,
                        reason = reason
                    };
                    
                    transactionHistory.Add(transaction);
                    
                    // Limit transaction history
                    if (transactionHistory.Count > maxTransactionHistory)
                    {
                        transactionHistory.RemoveAt(0);
                    }
                    
                    OnResourceTransaction?.Invoke(transaction);
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

        private void ProcessResourceDecay()
        {
            if (resourceCatalog == null) return;

            foreach (var resourceDef in resourceCatalog.GetAllResources())
            {
                // Check if resource has decay rate (this would need to be added to ResourceDefinition)
                // For now, skip decay processing
                continue;
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

        public bool TrySpendResources(Dictionary<string, long> costs, string reason = "Purchase")
        {
            // First check if we have enough
            if (!HasEnoughResources(costs))
            {
                return false;
            }

            // Then spend them
            foreach (var kvp in costs)
            {
                if (!TryRemoveResource(kvp.Key, kvp.Value, reason))
                {
                    return false;
                }
            }

            return true;
        }

        public List<ResourceTransaction> GetTransactionHistory(string resourceId = null, int limit = 100)
        {
            var transactions = transactionHistory.AsEnumerable();
            
            if (!string.IsNullOrEmpty(resourceId))
            {
                transactions = transactions.Where(t => t.resourceId == resourceId);
            }
            
            return transactions.TakeLast(limit).ToList();
        }

        public void ClearTransactionHistory()
        {
            transactionHistory.Clear();
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
                    AddResource(kvp.Key, kvp.Value, "Test");
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
            transactionHistory.Clear();
            InitializeResources();
            
            // Notify all changes
            foreach (var kvp in resourceAmounts)
            {
                OnResourceChanged?.Invoke(kvp.Key, kvp.Value);
            }
        }

        [ContextMenu("Log Transaction History")]
        public void LogTransactionHistory()
        {
            Debug.Log("=== Transaction History ===");
            foreach (var transaction in transactionHistory.TakeLast(10))
            {
                Debug.Log($"{transaction.timestamp:HH:mm:ss} - {transaction.resourceId}: {transaction.previousAmount} -> {transaction.newAmount} ({transaction.amount:+0;-0}) - {transaction.reason}");
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

        private void OnGUI()
        {
            if (showResourceDebugUI && Application.isPlaying)
            {
                GUILayout.BeginArea(new Rect(10, 10, 300, 200));
                GUILayout.Label("Resource Debug UI", EditorStyles.boldLabel);
                
                if (ResourceManager.Instance != null)
                {
                    var snapshot = ResourceManager.Instance.GetSnapshot();
                    foreach (var resource in snapshot.topResources.Take(5))
                    {
                        GUILayout.Label($"{resource.id}: {resource.amount}");
                    }
                }
                
                GUILayout.EndArea();
            }
        }
        #endif
    }
}