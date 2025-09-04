using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using UnityEngine;

namespace SaveSystem
{
    [System.Serializable]
    public class ProducerDefinition
    {
        [Header("Basic Info")]
        [SerializeField] private string id = "";
        [SerializeField] private string outputResourceId = "";
        [SerializeField] private float ratePerSecond = 1f;
        [SerializeField] private long capacity = 1000;
        
        [Header("Behavior")]
        [SerializeField] private bool isPassive = true;
        [SerializeField] private int workerCount = 1;
        [SerializeField] private float decayRate = 0f;

        public string Id => id;
        public string OutputResourceId => outputResourceId;
        public float RatePerSecond => ratePerSecond;
        public long Capacity => capacity;
        public bool IsPassive => isPassive;
        public int WorkerCount => workerCount;
        public float DecayRate => decayRate;

        public ProducerDefinition()
        {
            id = Guid.NewGuid().ToString();
        }
    }

    [System.Serializable]
    public class TriggerDefinition
    {
        [SerializeField] private string id = "";
        [SerializeField] private bool defaultValue = false;

        public string Id => id;
        public bool DefaultValue => defaultValue;

        public TriggerDefinition()
        {
            id = Guid.NewGuid().ToString();
        }
    }

    public class WorldStateManager : MonoBehaviour
    {
        [Header("Producer Configuration")]
        [SerializeField] private List<ProducerDefinition> producerDefinitions = new List<ProducerDefinition>();
        
        [Header("Trigger Configuration")]
        [SerializeField] private List<TriggerDefinition> triggerDefinitions = new List<TriggerDefinition>();

        [Header("Offline Simulation")]
        [SerializeField] private bool enableOfflineSimulation = true;
        [SerializeField] private double maxOfflineTimeHours = 24.0;
        [SerializeField] private float simulationUpdateInterval = 1f;

        [Header("Thumbnail Capture")]
        [SerializeField] private Camera thumbnailCamera;
        [SerializeField] private int thumbnailWidth = 256;
        [SerializeField] private int thumbnailHeight = 256;

        public static WorldStateManager Instance { get; private set; }

        // Private fields
        private Dictionary<string, GameObject> spawnablePrefabs = new Dictionary<string, GameObject>();
        private Dictionary<string, bool> triggerStates = new Dictionary<string, bool>();
        private Dictionary<string, ProducerState> producerStates = new Dictionary<string, ProducerState>();
        private List<SaveableEntity> allSaveableEntities = new List<SaveableEntity>();
        private List<SaveableEntity> brokenObjects = new List<SaveableEntity>();
        private SaveableEntity characterEntity;
        private double lastSaveTime;
        private float lastSimulationUpdate;

        private void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
                DontDestroyOnLoad(gameObject);
                InitializeWorldState();
            }
            else
            {
                Destroy(gameObject);
            }
        }

        private void Start()
        {
            // Initialize triggers with default values
            InitializeTriggers();
            
            // Initialize producers
            InitializeProducers();
            
            // Find all saveable entities in the scene
            RefreshSaveableEntities();
            
            // Set initial save time
            lastSaveTime = GetCurrentTime();
        }

        private void Update()
        {
            if (enableOfflineSimulation && Time.time - lastSimulationUpdate >= simulationUpdateInterval)
            {
                UpdateProducers();
                lastSimulationUpdate = Time.time;
            }
        }

        private void InitializeWorldState()
        {
            lastSaveTime = GetCurrentTime();
        }

        private void InitializeTriggers()
        {
            triggerStates.Clear();
            foreach (var triggerDef in triggerDefinitions)
            {
                if (!string.IsNullOrEmpty(triggerDef.Id))
                {
                    triggerStates[triggerDef.Id] = triggerDef.DefaultValue;
                }
            }
        }

        private void InitializeProducers()
        {
            producerStates.Clear();
            foreach (var producerDef in producerDefinitions)
            {
                if (!string.IsNullOrEmpty(producerDef.Id))
                {
                    producerStates[producerDef.Id] = new ProducerState
                    {
                        id = producerDef.Id,
                        lastUpdateTime = GetCurrentTime(),
                        currentOutput = 0,
                        workerCount = producerDef.WorkerCount,
                        isActive = true
                    };
                }
            }
        }

        public void RefreshSaveableEntities()
        {
            allSaveableEntities.Clear();
            brokenObjects.Clear();
            
            var entities = FindObjectsOfType<SaveableEntity>();
            foreach (var entity in entities)
            {
                allSaveableEntities.Add(entity);
                
                if (entity.IsBroken || entity.IsDestroyed)
                {
                    brokenObjects.Add(entity);
                }
            }
        }

        private void UpdateProducers()
        {
            if (ResourceManager.Instance == null) return;

            double currentTime = GetCurrentTime();
            double deltaTime = currentTime - lastSaveTime;

            foreach (var kvp in producerStates)
            {
                var producerState = kvp.Value;
                var producerDef = GetProducerDefinition(producerState.id);
                
                if (producerDef == null || !producerState.isActive) continue;

                // Calculate production
                float productionRate = producerDef.RatePerSecond * producerState.workerCount;
                long produced = (long)(productionRate * deltaTime);
                
                // Apply decay if specified
                if (producerDef.DecayRate > 0)
                {
                    float decayFactor = Mathf.Exp(-producerDef.DecayRate * (float)deltaTime);
                    produced = (long)(produced * decayFactor);
                }
                
                // Clamp to capacity
                long newOutput = Math.Min(producerState.currentOutput + produced, producerDef.Capacity);
                long actualProduced = newOutput - producerState.currentOutput;
                
                if (actualProduced > 0)
                {
                    // Add to resource manager
                    ResourceManager.Instance.AddResource(producerDef.OutputResourceId, actualProduced);
                    producerState.currentOutput = newOutput;
                }
                
                producerState.lastUpdateTime = currentTime;
            }
        }

        public async Task SimulateOfflineAsync(double deltaSeconds)
        {
            if (!enableOfflineSimulation || ResourceManager.Instance == null)
                return;

            // Clamp delta time to maximum offline time
            double maxDeltaSeconds = maxOfflineTimeHours * 3600.0;
            deltaSeconds = Math.Min(deltaSeconds, maxDeltaSeconds);

            Debug.Log($"Simulating offline time: {deltaSeconds} seconds");

            foreach (var kvp in producerStates)
            {
                var producerState = kvp.Value;
                var producerDef = GetProducerDefinition(producerState.id);
                
                if (producerDef == null || !producerState.isActive) continue;

                // Calculate production for offline time
                float productionRate = producerDef.RatePerSecond * producerState.workerCount;
                long produced = (long)(productionRate * deltaSeconds);
                
                // Apply decay if specified
                if (producerDef.DecayRate > 0)
                {
                    float decayFactor = Mathf.Exp(-producerDef.DecayRate * (float)deltaSeconds);
                    produced = (long)(produced * decayFactor);
                }
                
                // Clamp to capacity
                long newOutput = Math.Min(producerState.currentOutput + produced, producerDef.Capacity);
                long actualProduced = newOutput - producerState.currentOutput;
                
                if (actualProduced > 0)
                {
                    // Add to resource manager
                    ResourceManager.Instance.AddResource(producerDef.OutputResourceId, actualProduced);
                    producerState.currentOutput = newOutput;
                }
                
                producerState.lastUpdateTime = GetCurrentTime();
            }

            // Update last save time
            lastSaveTime = GetCurrentTime();

            await Task.CompletedTask;
        }

        public void RegisterSpawnablePrefab(string prefabId, GameObject prefab)
        {
            if (!string.IsNullOrEmpty(prefabId) && prefab != null)
            {
                spawnablePrefabs[prefabId] = prefab;
            }
        }

        public void RegisterCharacter(SaveableEntity character)
        {
            characterEntity = character;
            Debug.Log($"Character registered: {character.PersistentId}");
        }

        public SaveableEntity GetCharacter()
        {
            return characterEntity;
        }

        public IEnumerable<BrokenObjectInfo> GetBrokenObjects()
        {
            var brokenInfos = new List<BrokenObjectInfo>();
            
            foreach (var entity in brokenObjects)
            {
                brokenInfos.Add(new BrokenObjectInfo
                {
                    persistentId = entity.PersistentId,
                    prefabId = entity.PrefabId,
                    isDestroyed = entity.IsDestroyed,
                    customFields = entity.GetAllCustomFields()
                });
            }
            
            return brokenInfos;
        }

        public void RegisterTrigger(string triggerId, bool value)
        {
            triggerStates[triggerId] = value;
            
            // Mark save system as dirty
            if (SaveManager.Instance != null)
            {
                SaveManager.Instance.MarkDirty(SaveCategory.WorldState);
            }
        }

        public bool QueryTrigger(string triggerId)
        {
            return triggerStates.GetValueOrDefault(triggerId, false);
        }

        public List<SceneSummary> GetSceneSummaries()
        {
            var summaries = new List<SceneSummary>();
            var currentScene = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            
            RefreshSaveableEntities();
            
            summaries.Add(new SceneSummary
            {
                name = currentScene.name,
                objectCount = allSaveableEntities.Count,
                brokenCount = brokenObjects.Count
            });
            
            return summaries;
        }

        public SceneSaveData SerializeSceneData()
        {
            RefreshSaveableEntities();
            
            var sceneData = new SceneSaveData
            {
                sceneName = UnityEngine.SceneManagement.SceneManager.GetActiveScene().name
            };

            // Serialize spawnable entities
            foreach (var entity in allSaveableEntities)
            {
                if (entity.HasChangedFromOriginal())
                {
                    var saveData = entity.Serialize();
                    sceneData.spawnables.Add(new SaveableEntityData
                    {
                        persistentId = saveData.persistentId,
                        prefabId = saveData.prefabId,
                        position = saveData.position,
                        rotation = saveData.rotation,
                        scale = saveData.scale,
                        active = saveData.active,
                        customFields = saveData.customFields
                    });
                }
            }

            // Serialize broken objects
            foreach (var entity in brokenObjects)
            {
                sceneData.broken.Add(entity.PersistentId);
            }

            // Serialize triggers
            sceneData.triggers = new Dictionary<string, bool>(triggerStates);

            // Serialize producers
            sceneData.producers = new List<ProducerState>(producerStates.Values);

            return sceneData;
        }

        public void DeserializeSceneData(SceneSaveData sceneData)
        {
            if (sceneData == null) return;

            // Clear current state
            allSaveableEntities.Clear();
            brokenObjects.Clear();

            // Deserialize spawnable entities
            foreach (var entityData in sceneData.spawnables)
            {
                var existingEntity = FindSaveableEntity(entityData.persistentId);
                if (existingEntity != null)
                {
                    // Apply overrides to existing entity
                    var saveData = new SaveData
                    {
                        persistentId = entityData.persistentId,
                        prefabId = entityData.prefabId,
                        position = entityData.position,
                        rotation = entityData.rotation,
                        scale = entityData.scale,
                        active = entityData.active,
                        customFields = entityData.customFields
                    };
                    existingEntity.Deserialize(saveData);
                }
                else
                {
                    // Spawn new entity from prefab
                    SpawnEntityFromData(entityData);
                }
            }

            // Deserialize broken objects
            foreach (var brokenId in sceneData.broken)
            {
                var entity = FindSaveableEntity(brokenId);
                if (entity != null)
                {
                    entity.MarkBroken();
                }
            }

            // Deserialize triggers
            triggerStates = new Dictionary<string, bool>(sceneData.triggers);

            // Deserialize producers
            producerStates.Clear();
            foreach (var producerState in sceneData.producers)
            {
                producerStates[producerState.id] = producerState;
            }

            RefreshSaveableEntities();
        }

        public WorldStateSaveData SerializeWorldState()
        {
            return new WorldStateSaveData
            {
                brokenObjects = GetBrokenObjects().ToList(),
                triggers = new Dictionary<string, bool>(triggerStates),
                producers = new List<ProducerState>(producerStates.Values)
            };
        }

        public void DeserializeWorldState(WorldStateSaveData worldStateData)
        {
            if (worldStateData == null) return;

            // Deserialize triggers
            triggerStates = new Dictionary<string, bool>(worldStateData.triggers);

            // Deserialize producers
            producerStates.Clear();
            foreach (var producerState in worldStateData.producers)
            {
                producerStates[producerState.id] = producerState;
            }

            // Deserialize broken objects
            foreach (var brokenInfo in worldStateData.brokenObjects)
            {
                var entity = FindSaveableEntity(brokenInfo.persistentId);
                if (entity != null)
                {
                    if (brokenInfo.isDestroyed)
                    {
                        entity.MarkDestroyed();
                    }
                    else
                    {
                        entity.MarkBroken();
                    }
                }
            }
        }

        private SaveableEntity FindSaveableEntity(string persistentId)
        {
            return allSaveableEntities.FirstOrDefault(e => e.PersistentId == persistentId);
        }

        private void SpawnEntityFromData(SaveableEntityData entityData)
        {
            if (spawnablePrefabs.TryGetValue(entityData.prefabId, out var prefab))
            {
                var instance = Instantiate(prefab);
                var saveableEntity = instance.GetComponent<SaveableEntity>();
                
                if (saveableEntity != null)
                {
                    var saveData = new SaveData
                    {
                        persistentId = entityData.persistentId,
                        prefabId = entityData.prefabId,
                        position = entityData.position,
                        rotation = entityData.rotation,
                        scale = entityData.scale,
                        active = entityData.active,
                        customFields = entityData.customFields
                    };
                    saveableEntity.Deserialize(saveData);
                    allSaveableEntities.Add(saveableEntity);
                }
            }
            else
            {
                Debug.LogWarning($"Prefab not found for ID: {entityData.prefabId}");
            }
        }

        private ProducerDefinition GetProducerDefinition(string id)
        {
            return producerDefinitions.FirstOrDefault(p => p.Id == id);
        }

        private double GetCurrentTime()
        {
            return DateTime.UtcNow.ToOADate();
        }

        // Debug methods
        [ContextMenu("Refresh Saveable Entities")]
        public void RefreshSaveableEntitiesDebug()
        {
            RefreshSaveableEntities();
        }

        [ContextMenu("Log World State")]
        public void LogWorldState()
        {
            Debug.Log("=== World State ===");
            Debug.Log($"Total Saveable Entities: {allSaveableEntities.Count}");
            Debug.Log($"Broken Objects: {brokenObjects.Count}");
            Debug.Log($"Active Triggers: {triggerStates.Count(kvp => kvp.Value)}");
            Debug.Log($"Active Producers: {producerStates.Count(kvp => kvp.Value.isActive)}");
        }

        [ContextMenu("Simulate 1 Hour Offline")]
        public void SimulateOneHourOffline()
        {
            _ = SimulateOfflineAsync(3600.0);
        }

        [ContextMenu("Simulate 1 Day Offline")]
        public void SimulateOneDayOffline()
        {
            _ = SimulateOfflineAsync(86400.0);
        }

        // Editor helper methods
        #if UNITY_EDITOR
        private void OnValidate()
        {
            // Validate producer definitions
            var usedIds = new HashSet<string>();
            for (int i = 0; i < producerDefinitions.Count; i++)
            {
                var producer = producerDefinitions[i];
                if (string.IsNullOrEmpty(producer.Id))
                {
                    // Generate new ID
                    var newId = Guid.NewGuid().ToString();
                    var idField = typeof(ProducerDefinition).GetField("id", 
                        System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
                    idField?.SetValue(producer, newId);
                }
                else if (usedIds.Contains(producer.Id))
                {
                    Debug.LogWarning($"Duplicate producer ID found: {producer.Id}");
                }
                else
                {
                    usedIds.Add(producer.Id);
                }
            }

            // Validate trigger definitions
            usedIds.Clear();
            for (int i = 0; i < triggerDefinitions.Count; i++)
            {
                var trigger = triggerDefinitions[i];
                if (string.IsNullOrEmpty(trigger.Id))
                {
                    // Generate new ID
                    var newId = Guid.NewGuid().ToString();
                    var idField = typeof(TriggerDefinition).GetField("id", 
                        System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
                    idField?.SetValue(trigger, newId);
                }
                else if (usedIds.Contains(trigger.Id))
                {
                    Debug.LogWarning($"Duplicate trigger ID found: {trigger.Id}");
                }
                else
                {
                    usedIds.Add(trigger.Id);
                }
            }
        }
        #endif
    }
}