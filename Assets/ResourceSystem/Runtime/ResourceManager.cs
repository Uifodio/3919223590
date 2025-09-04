using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEngine;

namespace ResourceSystem
{
    [Serializable]
    public class ResourceDefinition
    {
        public string resourceId;
        public string displayName;
        public Sprite icon;
        public double startingAmount = 0;
    }

    [Serializable]
    public class ResourceSave
    {
        public List<string> resourceIds = new List<string>();
        public List<double> amounts = new List<double>();

        public Dictionary<string, double> ToDictionary()
        {
            var map = new Dictionary<string, double>();
            for (int i = 0; i < resourceIds.Count; i++)
            {
                var key = resourceIds[i];
                var value = i < amounts.Count ? amounts[i] : 0d;
                if (!string.IsNullOrEmpty(key))
                {
                    map[key] = value;
                }
            }
            return map;
        }

        public static ResourceSave FromDictionary(Dictionary<string, double> map)
        {
            var save = new ResourceSave();
            foreach (var kv in map)
            {
                save.resourceIds.Add(kv.Key);
                save.amounts.Add(kv.Value);
            }
            return save;
        }
    }

    [Serializable]
    public class CharacterTransformSave
    {
        public string characterId;
        public string sceneName;
        public Vector3 position;
        public Quaternion rotation;
        public double accumulatedPlaytimeSeconds;
        public long lastSavedUnixMs;
    }

    [Serializable]
    public class GlobalSave
    {
        public ResourceSave resources = new ResourceSave();
        public List<CharacterTransformSave> characters = new List<CharacterTransformSave>();
        public long lastSavedUnixMs;
        public bool encryptionEnabled;
        public int saveVersion = 1;
    }

    public class ResourceManager : MonoBehaviour
    {
        public static ResourceManager Instance { get; private set; }

        [Header("Resource Catalog")]
        public List<ResourceDefinition> resourceDefinitions = new List<ResourceDefinition>
        {
            new ResourceDefinition{ resourceId = "money", displayName = "Money", startingAmount = 0 },
            new ResourceDefinition{ resourceId = "wood", displayName = "Wood", startingAmount = 0 },
            new ResourceDefinition{ resourceId = "stone", displayName = "Stone", startingAmount = 0 },
        };

        [Header("Save Settings")]
        [Tooltip("Save file name under Application.persistentDataPath")] public string saveFileName = "ResourceSystem/save.json";
        [Tooltip("Autosave interval in seconds")] public float autosaveIntervalSeconds = 10f;
        [Tooltip("Enable simple XOR+Base64 obfuscation")] public bool encryptSave = false;
        [Tooltip("Obfuscation key for XOR (keep it simple)")] public string encryptionKey = "ChangeThisKey";

        private readonly Dictionary<string, double> resourceAmounts = new Dictionary<string, double>(StringComparer.OrdinalIgnoreCase);
        private readonly Dictionary<string, CharacterTransformSave> characterSaves = new Dictionary<string, CharacterTransformSave>(StringComparer.OrdinalIgnoreCase);

        private float autosaveTimerSeconds = 0f;

        public event Action<string, double> OnResourceChanged;

        void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);

            InitializeResourceMapWithDefaults();
            LoadFromDiskIfExists();
        }

        void Update()
        {
            autosaveTimerSeconds += Time.unscaledDeltaTime;
            if (autosaveTimerSeconds >= autosaveIntervalSeconds && autosaveIntervalSeconds > 0)
            {
                autosaveTimerSeconds = 0f;
                SaveToDisk();
            }
        }

        private void InitializeResourceMapWithDefaults()
        {
            resourceAmounts.Clear();
            foreach (var def in resourceDefinitions)
            {
                if (string.IsNullOrWhiteSpace(def.resourceId)) continue;
                if (!resourceAmounts.ContainsKey(def.resourceId))
                {
                    resourceAmounts[def.resourceId] = def.startingAmount;
                }
            }
        }

        public bool HasResource(string resourceId)
        {
            return resourceAmounts.ContainsKey(resourceId);
        }

        public void EnsureResource(string resourceId)
        {
            if (!resourceAmounts.ContainsKey(resourceId))
            {
                resourceAmounts[resourceId] = 0d;
            }
        }

        public void AddResource(string resourceId, double amount)
        {
            if (string.IsNullOrWhiteSpace(resourceId)) return;
            EnsureResource(resourceId);
            resourceAmounts[resourceId] += amount;
            OnResourceChanged?.Invoke(resourceId, resourceAmounts[resourceId]);
        }

        public bool SpendResource(string resourceId, double amount)
        {
            if (string.IsNullOrWhiteSpace(resourceId)) return false;
            EnsureResource(resourceId);
            var current = resourceAmounts[resourceId];
            if (current < amount) return false;
            resourceAmounts[resourceId] = current - amount;
            OnResourceChanged?.Invoke(resourceId, resourceAmounts[resourceId]);
            return true;
        }

        public double GetResourceAmount(string resourceId)
        {
            if (string.IsNullOrWhiteSpace(resourceId)) return 0d;
            return resourceAmounts.TryGetValue(resourceId, out var value) ? value : 0d;
        }

        public void RegisterOrUpdateCharacterState(string characterId, Vector3 position, Quaternion rotation, string sceneName, double sessionPlaytimeDeltaSeconds)
        {
            if (string.IsNullOrWhiteSpace(characterId)) return;
            if (!characterSaves.TryGetValue(characterId, out var save))
            {
                save = new CharacterTransformSave
                {
                    characterId = characterId,
                    position = position,
                    rotation = rotation,
                    sceneName = sceneName,
                    accumulatedPlaytimeSeconds = 0,
                    lastSavedUnixMs = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()
                };
                characterSaves[characterId] = save;
            }
            else
            {
                save.position = position;
                save.rotation = rotation;
                save.sceneName = sceneName;
                save.lastSavedUnixMs = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
            }

            save.accumulatedPlaytimeSeconds += Math.Max(0, sessionPlaytimeDeltaSeconds);
        }

        public bool TryGetCharacterState(string characterId, out CharacterTransformSave state)
        {
            return characterSaves.TryGetValue(characterId, out state);
        }

        public void SaveToDisk()
        {
            try
            {
                var data = new GlobalSave
                {
                    resources = ResourceSave.FromDictionary(resourceAmounts),
                    characters = new List<CharacterTransformSave>(characterSaves.Values),
                    lastSavedUnixMs = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
                    encryptionEnabled = encryptSave
                };

                var json = JsonUtility.ToJson(data, true);
                var output = encryptSave ? Encrypt(json, encryptionKey) : json;
                var fullPath = Path.Combine(Application.persistentDataPath, saveFileName);
                var dir = Path.GetDirectoryName(fullPath);
                if (!Directory.Exists(dir)) Directory.CreateDirectory(dir);
                File.WriteAllText(fullPath, output, Encoding.UTF8);
#if UNITY_EDITOR
                Debug.Log($"[ResourceManager] Saved to {fullPath}");
#endif
            }
            catch (Exception ex)
            {
                Debug.LogError($"[ResourceManager] Save failed: {ex}");
            }
        }

        private void LoadFromDiskIfExists()
        {
            try
            {
                var fullPath = Path.Combine(Application.persistentDataPath, saveFileName);
                if (!File.Exists(fullPath))
                {
                    // Initialize with defaults and save once to create file
                    SaveToDisk();
                    return;
                }
                var input = File.ReadAllText(fullPath, Encoding.UTF8);

                string jsonCandidate = input;
                // Attempt decrypt first; if fails, fall back to plain
                try
                {
                    jsonCandidate = Decrypt(input, encryptionKey);
                }
                catch
                {
                    // not encrypted or wrong key: try parse as-is
                    jsonCandidate = input;
                }

                var data = JsonUtility.FromJson<GlobalSave>(jsonCandidate);
                if (data != null)
                {
                    // resources
                    resourceAmounts.Clear();
                    foreach (var kv in data.resources.ToDictionary())
                    {
                        resourceAmounts[kv.Key] = kv.Value;
                    }
                    // characters
                    characterSaves.Clear();
                    foreach (var ch in data.characters)
                    {
                        if (!string.IsNullOrWhiteSpace(ch.characterId))
                        {
                            characterSaves[ch.characterId] = ch;
                        }
                    }
                    encryptSave = data.encryptionEnabled;
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"[ResourceManager] Load failed: {ex}");
            }
        }

        public void DeleteSaveFromDisk()
        {
            try
            {
                var fullPath = Path.Combine(Application.persistentDataPath, saveFileName);
                if (File.Exists(fullPath))
                {
                    File.Delete(fullPath);
                }
#if UNITY_EDITOR
                Debug.Log($"[ResourceManager] Deleted save file at {fullPath}");
#endif
            }
            catch (Exception ex)
            {
                Debug.LogError($"[ResourceManager] Delete save failed: {ex}");
            }
        }

        private static string Encrypt(string plainText, string key)
        {
            if (string.IsNullOrEmpty(plainText)) return plainText;
            var textBytes = Encoding.UTF8.GetBytes(plainText);
            var keyBytes = Encoding.UTF8.GetBytes(string.IsNullOrEmpty(key) ? "k" : key);
            for (int i = 0; i < textBytes.Length; i++)
            {
                textBytes[i] ^= keyBytes[i % keyBytes.Length];
            }
            return Convert.ToBase64String(textBytes);
        }

        private static string Decrypt(string cipherTextBase64, string key)
        {
            if (string.IsNullOrEmpty(cipherTextBase64)) return cipherTextBase64;
            var bytes = Convert.FromBase64String(cipherTextBase64);
            var keyBytes = Encoding.UTF8.GetBytes(string.IsNullOrEmpty(key) ? "k" : key);
            for (int i = 0; i < bytes.Length; i++)
            {
                bytes[i] ^= keyBytes[i % keyBytes.Length];
            }
            return Encoding.UTF8.GetString(bytes);
        }
    }
}

