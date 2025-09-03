using System;
using System.Collections.Generic;
using UnityEngine;

namespace SaveSystem
{
    [System.Serializable]
    public enum ResourceCategory
    {
        Currency,
        Materials,
        Consumables,
        Equipment,
        Special
    }

    [System.Serializable]
    public class ResourceDefinition
    {
        [Header("Basic Info")]
        [SerializeField] private string id = "";
        [SerializeField] private string displayName = "";
        [SerializeField] private long defaultAmount = 0;
        [SerializeField] private ResourceCategory category = ResourceCategory.Currency;
        
        [Header("UI Settings")]
        [SerializeField] private bool showInTopBar = false;
        [SerializeField] private int topBarOrder = 0;
        
        [Header("Validation")]
        [SerializeField] private long minAmount = 0;
        [SerializeField] private long maxAmount = long.MaxValue;
        [SerializeField] private bool allowNegative = false;

        // Properties
        public string Id => id;
        public string DisplayName => displayName;
        public long DefaultAmount => defaultAmount;
        public ResourceCategory Category => category;
        public bool ShowInTopBar => showInTopBar;
        public int TopBarOrder => topBarOrder;
        public long MinAmount => minAmount;
        public long MaxAmount => maxAmount;
        public bool AllowNegative => allowNegative;

        public ResourceDefinition()
        {
            id = Guid.NewGuid().ToString();
        }

        public ResourceDefinition(string resourceId, string name, long defaultValue, ResourceCategory resourceCategory)
        {
            id = resourceId;
            displayName = name;
            defaultAmount = defaultValue;
            category = resourceCategory;
        }

        public bool ValidateAmount(long amount)
        {
            if (!allowNegative && amount < 0)
                return false;
            
            if (amount < minAmount || amount > maxAmount)
                return false;
                
            return true;
        }

        public long ClampAmount(long amount)
        {
            if (!allowNegative && amount < 0)
                return 0;
                
            return Mathf.Clamp(amount, minAmount, maxAmount);
        }
    }

    [CreateAssetMenu(fileName = "ResourceCatalog", menuName = "Save System/Resource Catalog")]
    public class ResourceCatalog : ScriptableObject
    {
        [Header("Resource Definitions")]
        [SerializeField] private List<ResourceDefinition> resources = new List<ResourceDefinition>();
        
        [Header("Top Bar Configuration")]
        [SerializeField] private List<string> topBarResourceIds = new List<string>();

        // Runtime cache
        private Dictionary<string, ResourceDefinition> resourceLookup;
        private bool isInitialized = false;

        private void OnEnable()
        {
            InitializeLookup();
        }

        private void OnValidate()
        {
            // Ensure unique IDs
            var usedIds = new HashSet<string>();
            for (int i = 0; i < resources.Count; i++)
            {
                var resource = resources[i];
                if (string.IsNullOrEmpty(resource.Id))
                {
                    // Generate new ID if empty
                    var newId = Guid.NewGuid().ToString();
                    // Use reflection to set the private field
                    var idField = typeof(ResourceDefinition).GetField("id", 
                        System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
                    idField?.SetValue(resource, newId);
                }
                else if (usedIds.Contains(resource.Id))
                {
                    Debug.LogWarning($"Duplicate resource ID found: {resource.Id}. Please ensure all resource IDs are unique.");
                }
                else
                {
                    usedIds.Add(resource.Id);
                }
            }

            // Validate top bar resource IDs
            ValidateTopBarResources();
            
            // Reinitialize lookup after validation
            InitializeLookup();
        }

        private void InitializeLookup()
        {
            resourceLookup = new Dictionary<string, ResourceDefinition>();
            foreach (var resource in resources)
            {
                if (!string.IsNullOrEmpty(resource.Id))
                {
                    resourceLookup[resource.Id] = resource;
                }
            }
            isInitialized = true;
        }

        private void ValidateTopBarResources()
        {
            var validTopBarIds = new List<string>();
            foreach (var id in topBarResourceIds)
            {
                if (resourceLookup != null && resourceLookup.ContainsKey(id))
                {
                    validTopBarIds.Add(id);
                }
                else
                {
                    Debug.LogWarning($"Top bar resource ID '{id}' not found in resource catalog.");
                }
            }
            topBarResourceIds = validTopBarIds;
        }

        public ResourceDefinition GetResource(string id)
        {
            if (!isInitialized)
                InitializeLookup();
                
            return resourceLookup.TryGetValue(id, out var resource) ? resource : null;
        }

        public List<ResourceDefinition> GetAllResources()
        {
            return new List<ResourceDefinition>(resources);
        }

        public List<ResourceDefinition> GetResourcesByCategory(ResourceCategory category)
        {
            var result = new List<ResourceDefinition>();
            foreach (var resource in resources)
            {
                if (resource.Category == category)
                {
                    result.Add(resource);
                }
            }
            return result;
        }

        public List<ResourceDefinition> GetTopBarResources()
        {
            var result = new List<ResourceDefinition>();
            foreach (var id in topBarResourceIds)
            {
                var resource = GetResource(id);
                if (resource != null)
                {
                    result.Add(resource);
                }
            }
            
            // Sort by top bar order
            result.Sort((a, b) => a.TopBarOrder.CompareTo(b.TopBarOrder));
            return result;
        }

        public bool IsValidResource(string id)
        {
            return GetResource(id) != null;
        }

        public bool ValidateResourceAmount(string id, long amount)
        {
            var resource = GetResource(id);
            return resource?.ValidateAmount(amount) ?? false;
        }

        public long ClampResourceAmount(string id, long amount)
        {
            var resource = GetResource(id);
            return resource?.ClampAmount(amount) ?? amount;
        }

        // Editor helper methods
        #if UNITY_EDITOR
        public void AddResource(string id, string displayName, long defaultAmount, ResourceCategory category)
        {
            var newResource = new ResourceDefinition(id, displayName, defaultAmount, category);
            resources.Add(newResource);
            UnityEditor.EditorUtility.SetDirty(this);
        }

        public void RemoveResource(string id)
        {
            resources.RemoveAll(r => r.Id == id);
            topBarResourceIds.Remove(id);
            UnityEditor.EditorUtility.SetDirty(this);
        }

        public void AddToTopBar(string resourceId)
        {
            if (!topBarResourceIds.Contains(resourceId) && IsValidResource(resourceId))
            {
                topBarResourceIds.Add(resourceId);
                UnityEditor.EditorUtility.SetDirty(this);
            }
        }

        public void RemoveFromTopBar(string resourceId)
        {
            topBarResourceIds.Remove(resourceId);
            UnityEditor.EditorUtility.SetDirty(this);
        }

        public void ReorderTopBarResources()
        {
            // Sort top bar resources by their order property
            var topBarResources = new List<ResourceDefinition>();
            foreach (var id in topBarResourceIds)
            {
                var resource = GetResource(id);
                if (resource != null)
                {
                    topBarResources.Add(resource);
                }
            }
            
            topBarResources.Sort((a, b) => a.TopBarOrder.CompareTo(b.TopBarOrder));
            
            topBarResourceIds.Clear();
            foreach (var resource in topBarResources)
            {
                topBarResourceIds.Add(resource.Id);
            }
            
            UnityEditor.EditorUtility.SetDirty(this);
        }
        #endif

        // Validation methods
        public List<string> ValidateCatalog()
        {
            var errors = new List<string>();
            
            if (resources.Count == 0)
            {
                errors.Add("Resource catalog is empty");
            }
            
            var usedIds = new HashSet<string>();
            foreach (var resource in resources)
            {
                if (string.IsNullOrEmpty(resource.Id))
                {
                    errors.Add("Resource with empty ID found");
                }
                else if (usedIds.Contains(resource.Id))
                {
                    errors.Add($"Duplicate resource ID: {resource.Id}");
                }
                else
                {
                    usedIds.Add(resource.Id);
                }
                
                if (string.IsNullOrEmpty(resource.DisplayName))
                {
                    errors.Add($"Resource '{resource.Id}' has empty display name");
                }
                
                if (!resource.ValidateAmount(resource.DefaultAmount))
                {
                    errors.Add($"Resource '{resource.Id}' has invalid default amount: {resource.DefaultAmount}");
                }
            }
            
            // Validate top bar resources
            foreach (var id in topBarResourceIds)
            {
                if (!IsValidResource(id))
                {
                    errors.Add($"Top bar resource ID '{id}' not found in catalog");
                }
            }
            
            return errors;
        }

        public void LogValidationResults()
        {
            var errors = ValidateCatalog();
            if (errors.Count == 0)
            {
                Debug.Log("Resource catalog validation passed");
            }
            else
            {
                Debug.LogError($"Resource catalog validation failed with {errors.Count} errors:");
                foreach (var error in errors)
                {
                    Debug.LogError($"- {error}");
                }
            }
        }
    }
}