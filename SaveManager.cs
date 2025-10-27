using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;
using Newtonsoft.Json;

namespace SaveSystem
{
    [System.Serializable]
    public enum SaveCategory
    {
        Resources,
        WorldState,
        SceneState,
        PlayerData,
        Settings
    }

    [System.Serializable]
    public enum EncryptionKeySource
    {
        None,
        Password,
        AndroidKeyStore,
        Generated
    }

    [System.Serializable]
    public class SaveSummary
    {
        public string slotId;
        public string lastSaved;
        public long playTimeSeconds;
        public List<ResourceSnapshot> topResources;
        public List<SceneSummary> sceneSummaries;
        public string thumbnailPath;
    }

    [System.Serializable]
    public class ResourceSnapshot
    {
        public string id;
        public long amount;
    }

    [System.Serializable]
    public class SceneSummary
    {
        public string name;
        public int objectCount;
        public int brokenCount;
    }

    [System.Serializable]
    public class SaveMetadata
    {
        public string slotId;
        public int saveVersion = 2;
        public string lastSaved;
        public long playTimeSeconds;
        public Dictionary<string, long> resources = new Dictionary<string, long>();
        public List<ResourceSnapshot> topResources = new List<ResourceSnapshot>();
        public List<SceneSummary> scenes = new List<SceneSummary>();
    }

    public class SaveManager : MonoBehaviour
    {
        [Header("Save Configuration")]
        [SerializeField] private string saveRootFolderName = "GameSaves";
        [SerializeField] private bool enableCompression = true;
        [SerializeField] private bool enableEncryption = false;
        [SerializeField] private EncryptionKeySource encryptionKeySource = EncryptionKeySource.None;
        [SerializeField] private string encryptionPassword = "";
        [SerializeField] private float autosaveIntervalSeconds = 30f;
        [SerializeField] private bool saveOnPause = true;
        [SerializeField] private bool saveOneFilePerScene = true;
        [SerializeField] private int maxAutoBackups = 3;
        [SerializeField] private bool debugDumpJsonToConsole = false;
        [SerializeField] private int saveVersion = 2;

        [Header("Debug Tools")]
        [SerializeField] private bool createTestSaveOnStart = false;

        public static SaveManager Instance { get; private set; }

        // Events
        public event Action<string> OnSaveCompleted;
        public event Action<string> OnLoadCompleted;
        public event Action<string, string> OnSaveFailed;

        // Private fields
        private Dictionary<SaveCategory, bool> dirtyFlags = new Dictionary<SaveCategory, bool>();
        private string currentSlotId = "";
        private float lastAutosaveTime = 0f;
        private bool isSaving = false;
        private bool isLoading = false;
        private string saveRootPath;
        private byte[] encryptionKey;

        private void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
                DontDestroyOnLoad(gameObject);
                InitializeSaveSystem();
            }
            else
            {
                Destroy(gameObject);
            }
        }

        private void Start()
        {
            if (createTestSaveOnStart)
            {
                CreateTestSave();
            }
        }

        private void Update()
        {
            if (autosaveIntervalSeconds > 0 && Time.time - lastAutosaveTime >= autosaveIntervalSeconds)
            {
                if (HasDirtyFlags() && !string.IsNullOrEmpty(currentSlotId) && !isSaving)
                {
                    _ = SaveSlotAsync(currentSlotId);
                }
            }
        }

        private void OnApplicationPause(bool pauseStatus)
        {
            if (pauseStatus && saveOnPause && !string.IsNullOrEmpty(currentSlotId) && !isSaving)
            {
                _ = SaveSlotAsync(currentSlotId);
            }
        }

        private void OnApplicationFocus(bool hasFocus)
        {
            if (!hasFocus && saveOnPause && !string.IsNullOrEmpty(currentSlotId) && !isSaving)
            {
                _ = SaveSlotAsync(currentSlotId);
            }
        }

        private void InitializeSaveSystem()
        {
            saveRootPath = Path.Combine(Application.persistentDataPath, saveRootFolderName);
            
            if (!Directory.Exists(saveRootPath))
            {
                Directory.CreateDirectory(saveRootPath);
            }

            if (enableEncryption)
            {
                InitializeEncryption();
            }

            // Initialize dirty flags
            foreach (SaveCategory category in Enum.GetValues(typeof(SaveCategory)))
            {
                dirtyFlags[category] = false;
            }
        }

        private void InitializeEncryption()
        {
            switch (encryptionKeySource)
            {
                case EncryptionKeySource.Password:
                    if (string.IsNullOrEmpty(encryptionPassword))
                    {
                        Debug.LogError("Encryption password is required when using Password key source");
                        return;
                    }
                    // Generate key from password using PBKDF2
                    var salt = new byte[32];
                    using (var rng = RandomNumberGenerator.Create())
                    {
                        rng.GetBytes(salt);
                    }
                    using (var pbkdf2 = new Rfc2898DeriveBytes(encryptionPassword, salt, 100000, HashAlgorithmName.SHA256))
                    {
                        encryptionKey = pbkdf2.GetBytes(32);
                    }
                    break;

                case EncryptionKeySource.Generated:
                    encryptionKey = new byte[32];
                    using (var rng = RandomNumberGenerator.Create())
                    {
                        rng.GetBytes(encryptionKey);
                    }
                    break;

                case EncryptionKeySource.AndroidKeyStore:
                    // Note: This would require a native plugin for Android KeyStore
                    // For now, fall back to generated key
                    Debug.LogWarning("AndroidKeyStore encryption requires native plugin - falling back to generated key");
                    encryptionKey = new byte[32];
                    using (var rng = RandomNumberGenerator.Create())
                    {
                        rng.GetBytes(encryptionKey);
                    }
                    break;
            }
        }

        public void MarkDirty(SaveCategory category)
        {
            dirtyFlags[category] = true;
        }

        private bool HasDirtyFlags()
        {
            foreach (var flag in dirtyFlags.Values)
            {
                if (flag) return true;
            }
            return false;
        }

        public async Task SaveSlotAsync(string slotId)
        {
            if (isSaving)
            {
                Debug.LogWarning("Save already in progress");
                return;
            }

            isSaving = true;
            currentSlotId = slotId;

            try
            {
                string slotPath = Path.Combine(saveRootPath, slotId);
                if (!Directory.Exists(slotPath))
                {
                    Directory.CreateDirectory(slotPath);
                }

                // Create backup of existing save
                await CreateBackupAsync(slotPath);

                // Save metadata
                await SaveMetadataAsync(slotPath);

                // Save scene data
                if (saveOneFilePerScene)
                {
                    await SaveSceneDataAsync(slotPath);
                }
                else
                {
                    await SaveGlobalDataAsync(slotPath);
                }

                // Capture thumbnail
                await CaptureThumbnailAsync(slotPath);

                // Clear dirty flags
                foreach (var key in dirtyFlags.Keys.ToArray())
                {
                    dirtyFlags[key] = false;
                }

                lastAutosaveTime = Time.time;

                OnSaveCompleted?.Invoke(slotId);
                Debug.Log($"Save completed for slot: {slotId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Save failed for slot {slotId}: {ex.Message}");
                OnSaveFailed?.Invoke(slotId, ex.Message);
            }
            finally
            {
                isSaving = false;
            }
        }

        public async Task LoadSlotAsync(string slotId)
        {
            if (isLoading)
            {
                Debug.LogWarning("Load already in progress");
                return;
            }

            isLoading = true;
            currentSlotId = slotId;

            try
            {
                string slotPath = Path.Combine(saveRootPath, slotId);
                if (!Directory.Exists(slotPath))
                {
                    throw new DirectoryNotFoundException($"Save slot not found: {slotId}");
                }

                // Load metadata
                var metadata = await LoadMetadataAsync(slotPath);

                // Load scene data
                if (saveOneFilePerScene)
                {
                    await LoadSceneDataAsync(slotPath);
                }
                else
                {
                    await LoadGlobalDataAsync(slotPath);
                }

                // Clear dirty flags
                foreach (var key in dirtyFlags.Keys.ToArray())
                {
                    dirtyFlags[key] = false;
                }

                OnLoadCompleted?.Invoke(slotId);
                Debug.Log($"Load completed for slot: {slotId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Load failed for slot {slotId}: {ex.Message}");
                OnSaveFailed?.Invoke(slotId, ex.Message);
            }
            finally
            {
                isLoading = false;
            }
        }

        public async Task DeleteSlotAsync(string slotId)
        {
            try
            {
                string slotPath = Path.Combine(saveRootPath, slotId);
                if (Directory.Exists(slotPath))
                {
                    await Task.Run(() => Directory.Delete(slotPath, true));
                    Debug.Log($"Deleted save slot: {slotId}");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to delete slot {slotId}: {ex.Message}");
                throw;
            }
        }

        public IEnumerable<SaveSummary> GetSaveSummaries()
        {
            var summaries = new List<SaveSummary>();

            if (!Directory.Exists(saveRootPath))
                return summaries;

            foreach (string slotPath in Directory.GetDirectories(saveRootPath))
            {
                string slotId = Path.GetFileName(slotPath);
                string metaPath = Path.Combine(slotPath, "meta.json");

                if (File.Exists(metaPath))
                {
                    try
                    {
                        string json = ReadFileWithEncryption(metaPath);
                        var metadata = JsonConvert.DeserializeObject<SaveMetadata>(json);
                        
                        summaries.Add(new SaveSummary
                        {
                            slotId = metadata.slotId,
                            lastSaved = metadata.lastSaved,
                            playTimeSeconds = metadata.playTimeSeconds,
                            topResources = metadata.topResources,
                            sceneSummaries = metadata.scenes,
                            thumbnailPath = Path.Combine(slotPath, "thumbnail.png")
                        });
                    }
                    catch (Exception ex)
                    {
                        Debug.LogError($"Failed to read save summary for {slotId}: {ex.Message}");
                    }
                }
            }

            return summaries;
        }

        private async Task SaveMetadataAsync(string slotPath)
        {
            var metadata = new SaveMetadata
            {
                slotId = currentSlotId,
                saveVersion = saveVersion,
                lastSaved = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ"),
                playTimeSeconds = (long)Time.time
            };

            // Get resource data from ResourceManager
            if (ResourceManager.Instance != null)
            {
                var resourceSnapshot = ResourceManager.Instance.GetSnapshot();
                metadata.resources = resourceSnapshot.resources;
                metadata.topResources = resourceSnapshot.topResources;
            }

            // Get scene data from WorldStateManager
            if (WorldStateManager.Instance != null)
            {
                metadata.scenes = WorldStateManager.Instance.GetSceneSummaries();
            }

            string json = JsonConvert.SerializeObject(metadata, Formatting.Indented);
            string metaPath = Path.Combine(slotPath, "meta.json");
            
            await WriteFileWithEncryptionAsync(metaPath, json);
        }

        private async Task<SaveMetadata> LoadMetadataAsync(string slotPath)
        {
            string metaPath = Path.Combine(slotPath, "meta.json");
            string json = await ReadFileWithEncryptionAsync(metaPath);
            return JsonConvert.DeserializeObject<SaveMetadata>(json);
        }

        private async Task SaveSceneDataAsync(string slotPath)
        {
            if (WorldStateManager.Instance != null)
            {
                var sceneData = WorldStateManager.Instance.SerializeSceneData();
                string json = JsonConvert.SerializeObject(sceneData, Formatting.Indented);
                string scenePath = Path.Combine(slotPath, $"scene_{UnityEngine.SceneManagement.SceneManager.GetActiveScene().name}.json");
                await WriteFileWithEncryptionAsync(scenePath, json);
            }
        }

        private async Task LoadSceneDataAsync(string slotPath)
        {
            string sceneName = UnityEngine.SceneManagement.SceneManager.GetActiveScene().name;
            string scenePath = Path.Combine(slotPath, $"scene_{sceneName}.json");
            
            if (File.Exists(scenePath))
            {
                string json = await ReadFileWithEncryptionAsync(scenePath);
                var sceneData = JsonConvert.DeserializeObject<SceneSaveData>(json);
                
                if (WorldStateManager.Instance != null)
                {
                    WorldStateManager.Instance.DeserializeSceneData(sceneData);
                }
            }
        }

        private async Task SaveGlobalDataAsync(string slotPath)
        {
            var globalData = new GlobalSaveData();
            
            // Collect data from all managers
            if (ResourceManager.Instance != null)
            {
                globalData.resources = ResourceManager.Instance.GetSnapshot();
            }

            if (WorldStateManager.Instance != null)
            {
                globalData.worldState = WorldStateManager.Instance.SerializeWorldState();
            }

            string json = JsonConvert.SerializeObject(globalData, Formatting.Indented);
            string globalPath = Path.Combine(slotPath, "global.json");
            await WriteFileWithEncryptionAsync(globalPath, json);
        }

        private async Task LoadGlobalDataAsync(string slotPath)
        {
            string globalPath = Path.Combine(slotPath, "global.json");
            
            if (File.Exists(globalPath))
            {
                string json = await ReadFileWithEncryptionAsync(globalPath);
                var globalData = JsonConvert.DeserializeObject<GlobalSaveData>(json);
                
                if (ResourceManager.Instance != null && globalData.resources != null)
                {
                    ResourceManager.Instance.LoadSnapshot(globalData.resources);
                }

                if (WorldStateManager.Instance != null && globalData.worldState != null)
                {
                    WorldStateManager.Instance.DeserializeWorldState(globalData.worldState);
                }
            }
        }

        private async Task CaptureThumbnailAsync(string slotPath)
        {
            // This would require a thumbnail camera setup
            // For now, just create a placeholder
            Debug.Log("Thumbnail capture not implemented - requires thumbnail camera setup");
        }

        private async Task CreateBackupAsync(string slotPath)
        {
            if (maxAutoBackups <= 0) return;

            try
            {
                string backupPath = Path.Combine(slotPath, "backup");
                if (Directory.Exists(backupPath))
                {
                    // Rotate backups
                    for (int i = maxAutoBackups - 1; i > 0; i--)
                    {
                        string oldBackup = Path.Combine(backupPath, $"backup_{i}");
                        string newBackup = Path.Combine(backupPath, $"backup_{i + 1}");
                        
                        if (Directory.Exists(oldBackup))
                        {
                            if (Directory.Exists(newBackup))
                                Directory.Delete(newBackup, true);
                            Directory.Move(oldBackup, newBackup);
                        }
                    }

                    // Create new backup
                    string currentBackup = Path.Combine(backupPath, "backup_1");
                    if (Directory.Exists(currentBackup))
                        Directory.Delete(currentBackup, true);
                    
                    await Task.Run(() => CopyDirectory(slotPath, currentBackup, new[] { "backup" }));
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to create backup: {ex.Message}");
            }
        }

        private async Task WriteFileWithEncryptionAsync(string filePath, string content)
        {
            byte[] data = Encoding.UTF8.GetBytes(content);
            
            if (enableCompression)
            {
                data = CompressData(data);
            }

            if (enableEncryption && encryptionKey != null)
            {
                data = EncryptData(data);
            }

            // Atomic write
            string tempPath = filePath + ".tmp";
            await File.WriteAllBytesAsync(tempPath, data);
            File.Move(tempPath, filePath);
        }

        private async Task<string> ReadFileWithEncryptionAsync(string filePath)
        {
            byte[] data = await File.ReadAllBytesAsync(filePath);
            
            if (enableEncryption && encryptionKey != null)
            {
                data = DecryptData(data);
            }

            if (enableCompression)
            {
                data = DecompressData(data);
            }

            return Encoding.UTF8.GetString(data);
        }

        private string ReadFileWithEncryption(string filePath)
        {
            byte[] data = File.ReadAllBytes(filePath);
            
            if (enableEncryption && encryptionKey != null)
            {
                data = DecryptData(data);
            }

            if (enableCompression)
            {
                data = DecompressData(data);
            }

            return Encoding.UTF8.GetString(data);
        }

        private byte[] CompressData(byte[] data)
        {
            using (var output = new MemoryStream())
            {
                using (var gzip = new GZipStream(output, CompressionMode.Compress))
                {
                    gzip.Write(data, 0, data.Length);
                }
                return output.ToArray();
            }
        }

        private byte[] DecompressData(byte[] data)
        {
            using (var input = new MemoryStream(data))
            using (var gzip = new GZipStream(input, CompressionMode.Decompress))
            using (var output = new MemoryStream())
            {
                gzip.CopyTo(output);
                return output.ToArray();
            }
        }

        private byte[] EncryptData(byte[] data)
        {
            using (var aes = Aes.Create())
            {
                aes.Key = encryptionKey;
                aes.GenerateIV();
                aes.Mode = CipherMode.GCM;
                
                using (var encryptor = aes.CreateEncryptor())
                using (var msEncrypt = new MemoryStream())
                {
                    // Write IV
                    msEncrypt.Write(aes.IV, 0, aes.IV.Length);
                    
                    using (var csEncrypt = new CryptoStream(msEncrypt, encryptor, CryptoStreamMode.Write))
                    {
                        csEncrypt.Write(data, 0, data.Length);
                    }
                    
                    // Write authentication tag
                    var tag = aes.Tag;
                    msEncrypt.Write(tag, 0, tag.Length);
                    
                    return msEncrypt.ToArray();
                }
            }
        }

        private byte[] DecryptData(byte[] data)
        {
            using (var aes = Aes.Create())
            {
                aes.Key = encryptionKey;
                aes.Mode = CipherMode.GCM;
                
                // Read IV
                byte[] iv = new byte[16];
                Array.Copy(data, 0, iv, 0, 16);
                aes.IV = iv;
                
                // Read tag
                byte[] tag = new byte[16];
                Array.Copy(data, data.Length - 16, tag, 0, 16);
                aes.Tag = tag;
                
                // Decrypt
                byte[] ciphertext = new byte[data.Length - 32];
                Array.Copy(data, 16, ciphertext, 0, ciphertext.Length);
                
                using (var decryptor = aes.CreateDecryptor())
                using (var msDecrypt = new MemoryStream(ciphertext))
                using (var csDecrypt = new CryptoStream(msDecrypt, decryptor, CryptoStreamMode.Read))
                using (var msPlain = new MemoryStream())
                {
                    csDecrypt.CopyTo(msPlain);
                    return msPlain.ToArray();
                }
            }
        }

        private void CopyDirectory(string sourceDir, string destDir, string[] excludeDirs)
        {
            Directory.CreateDirectory(destDir);
            
            foreach (string file in Directory.GetFiles(sourceDir))
            {
                string fileName = Path.GetFileName(file);
                string destFile = Path.Combine(destDir, fileName);
                File.Copy(file, destFile);
            }
            
            foreach (string subDir in Directory.GetDirectories(sourceDir))
            {
                string dirName = Path.GetFileName(subDir);
                if (excludeDirs.Contains(dirName)) continue;
                
                string destSubDir = Path.Combine(destDir, dirName);
                CopyDirectory(subDir, destSubDir, excludeDirs);
            }
        }

        // Debug methods
        [ContextMenu("Create Test Save")]
        public void CreateTestSave()
        {
            _ = SaveSlotAsync("test_save");
        }

        [ContextMenu("Load Latest Save")]
        public void LoadLatestSave()
        {
            var summaries = GetSaveSummaries();
            if (summaries.Any())
            {
                var latest = summaries.OrderByDescending(s => s.lastSaved).First();
                _ = LoadSlotAsync(latest.slotId);
            }
        }

        [ContextMenu("Clear All Saves")]
        public void ClearAllSaves()
        {
            if (Directory.Exists(saveRootPath))
            {
                Directory.Delete(saveRootPath, true);
                Directory.CreateDirectory(saveRootPath);
                Debug.Log("All saves cleared");
            }
        }
    }

    // Data transfer objects
    [System.Serializable]
    public class GlobalSaveData
    {
        public ResourceSnapshot resources;
        public WorldStateSaveData worldState;
    }

    [System.Serializable]
    public class SceneSaveData
    {
        public string sceneName;
        public List<SaveableEntityData> spawnables = new List<SaveableEntityData>();
        public List<string> broken = new List<string>();
        public Dictionary<string, bool> triggers = new Dictionary<string, bool>();
    }

    [System.Serializable]
    public class WorldStateSaveData
    {
        public List<BrokenObjectInfo> brokenObjects = new List<BrokenObjectInfo>();
        public Dictionary<string, bool> triggers = new Dictionary<string, bool>();
        public List<ProducerState> producers = new List<ProducerState>();
    }

    [System.Serializable]
    public class SaveableEntityData
    {
        public string persistentId;
        public string prefabId;
        public Vector3 position;
        public Quaternion rotation;
        public Vector3 scale;
        public bool active;
        public Dictionary<string, object> customFields = new Dictionary<string, object>();
    }

    [System.Serializable]
    public class BrokenObjectInfo
    {
        public string persistentId;
        public string prefabId;
        public bool isDestroyed;
        public Dictionary<string, object> customFields = new Dictionary<string, object>();
    }

    [System.Serializable]
    public class ProducerState
    {
        public string id;
        public double lastUpdateTime;
        public long currentOutput;
        public int workerCount;
    }
}