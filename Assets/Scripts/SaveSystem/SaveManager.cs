using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Linq;
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
        Settings,
        CharacterData
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
        public bool isCorrupted = false;
        public string version;
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
        public int saveVersion = 3;
        public string lastSaved;
        public long playTimeSeconds;
        public Dictionary<string, long> resources = new Dictionary<string, long>();
        public List<ResourceSnapshot> topResources = new List<ResourceSnapshot>();
        public List<SceneSummary> scenes = new List<SceneSummary>();
        public CharacterSaveData characterData = new CharacterSaveData();
        public bool isCorrupted = false;
        public string checksum;
    }

    [System.Serializable]
    public class CharacterSaveData
    {
        public Vector3 position;
        public Quaternion rotation;
        public Vector3 scale;
        public bool isActive;
        public string currentScene;
        public Dictionary<string, object> customData = new Dictionary<string, object>();
    }

    public class SaveManager : MonoBehaviour
    {
        [Header("Save Configuration")]
        [SerializeField] private string saveRootFolderName = "GameSaves";
        [SerializeField] private bool enableCompression = true;
        [SerializeField] private bool enableEncryption = false;
        [SerializeField] private EncryptionKeySource encryptionKeySource = EncryptionKeySource.None;
        [SerializeField] private string encryptionPassword = "";
        [SerializeField] private float autosaveIntervalSeconds = 5f; // More frequent autosave
        [SerializeField] private bool saveOnPause = true;
        [SerializeField] private bool saveOnFocusLoss = true;
        [SerializeField] private bool saveOneFilePerScene = true;
        [SerializeField] private int maxAutoBackups = 5;
        [SerializeField] private bool debugDumpJsonToConsole = false;
        [SerializeField] private int saveVersion = 3;

        [Header("Instant Save Settings")]
        [SerializeField] private bool enableInstantSave = true;
        [SerializeField] private float instantSaveDelay = 0.1f;
        [SerializeField] private bool saveOnResourceChange = true;
        [SerializeField] private bool saveOnPositionChange = true;

        [Header("Crash Recovery")]
        [SerializeField] private bool enableCrashRecovery = true;
        [SerializeField] private float crashDetectionTime = 2f;
        [SerializeField] private bool autoRepairCorruptedSaves = true;

        [Header("Debug Tools")]
        [SerializeField] private bool createTestSaveOnStart = false;

        public static SaveManager Instance { get; private set; }

        // Events
        public event Action<string> OnSaveCompleted;
        public event Action<string> OnLoadCompleted;
        public event Action<string, string> OnSaveFailed;
        public event Action<string> OnCrashDetected;
        public event Action<string> OnSaveCorrupted;

        // Private fields
        private Dictionary<SaveCategory, bool> dirtyFlags = new Dictionary<SaveCategory, bool>();
        private string currentSlotId = "";
        private float lastAutosaveTime = 0f;
        private bool isSaving = false;
        private bool isLoading = false;
        private string saveRootPath;
        private byte[] encryptionKey;
        private Coroutine instantSaveCoroutine;
        private float lastSaveTime;
        private bool isApplicationPaused = false;
        private bool isApplicationFocused = true;

        // Character tracking
        private Transform characterTransform;
        private Vector3 lastCharacterPosition;
        private Quaternion lastCharacterRotation;

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

            // Find character transform
            FindCharacterTransform();
        }

        private void Update()
        {
            // Check for character position changes
            if (saveOnPositionChange && characterTransform != null)
            {
                if (Vector3.Distance(characterTransform.position, lastCharacterPosition) > 0.1f ||
                    Quaternion.Angle(characterTransform.rotation, lastCharacterRotation) > 1f)
                {
                    MarkDirty(SaveCategory.CharacterData);
                    lastCharacterPosition = characterTransform.position;
                    lastCharacterRotation = characterTransform.rotation;
                }
            }

            // Regular autosave
            if (autosaveIntervalSeconds > 0 && Time.time - lastAutosaveTime >= autosaveIntervalSeconds)
            {
                if (HasDirtyFlags() && !string.IsNullOrEmpty(currentSlotId) && !isSaving)
                {
                    _ = SaveSlotAsync(currentSlotId);
                }
            }

            // Instant save check
            if (enableInstantSave && HasDirtyFlags() && !isSaving && !string.IsNullOrEmpty(currentSlotId))
            {
                if (instantSaveCoroutine == null)
                {
                    instantSaveCoroutine = StartCoroutine(InstantSaveCoroutine());
                }
            }
        }

        private void OnApplicationPause(bool pauseStatus)
        {
            isApplicationPaused = pauseStatus;
            if (pauseStatus && saveOnPause && !string.IsNullOrEmpty(currentSlotId) && !isSaving)
            {
                _ = ForceSaveAsync(currentSlotId);
            }
        }

        private void OnApplicationFocus(bool hasFocus)
        {
            isApplicationFocused = hasFocus;
            if (!hasFocus && saveOnFocusLoss && !string.IsNullOrEmpty(currentSlotId) && !isSaving)
            {
                _ = ForceSaveAsync(currentSlotId);
            }
        }

        private void OnApplicationQuit()
        {
            if (!string.IsNullOrEmpty(currentSlotId) && !isSaving)
            {
                // Force immediate save on quit
                _ = ForceSaveAsync(currentSlotId);
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

            lastSaveTime = Time.time;
        }

        private void FindCharacterTransform()
        {
            // Look for character by tag or name
            GameObject character = GameObject.FindGameObjectWithTag("Player");
            if (character == null)
            {
                character = GameObject.Find("Player");
            }
            if (character == null)
            {
                character = GameObject.Find("Character");
            }

            if (character != null)
            {
                characterTransform = character.transform;
                lastCharacterPosition = characterTransform.position;
                lastCharacterRotation = characterTransform.rotation;
            }
        }

        private System.Collections.IEnumerator InstantSaveCoroutine()
        {
            yield return new WaitForSeconds(instantSaveDelay);
            if (HasDirtyFlags() && !isSaving)
            {
                _ = SaveSlotAsync(currentSlotId);
            }
            instantSaveCoroutine = null;
        }

        public void MarkDirty(SaveCategory category)
        {
            dirtyFlags[category] = true;

            // Trigger instant save for critical categories
            if (saveOnResourceChange && (category == SaveCategory.Resources || category == SaveCategory.CharacterData))
            {
                if (enableInstantSave && instantSaveCoroutine == null)
                {
                    instantSaveCoroutine = StartCoroutine(InstantSaveCoroutine());
                }
            }
        }

        private bool HasDirtyFlags()
        {
            return dirtyFlags.Values.Any(flag => flag);
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
                lastSaveTime = Time.time;

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

        public async Task ForceSaveAsync(string slotId)
        {
            // Force immediate save without delay
            if (isSaving) return;
            
            isSaving = true;
            currentSlotId = slotId;

            try
            {
                string slotPath = Path.Combine(saveRootPath, slotId);
                if (!Directory.Exists(slotPath))
                {
                    Directory.CreateDirectory(slotPath);
                }

                // Force save without backup for speed
                await SaveMetadataAsync(slotPath);
                
                if (saveOneFilePerScene)
                {
                    await SaveSceneDataAsync(slotPath);
                }
                else
                {
                    await SaveGlobalDataAsync(slotPath);
                }

                // Clear dirty flags
                foreach (var key in dirtyFlags.Keys.ToArray())
                {
                    dirtyFlags[key] = false;
                }

                lastAutosaveTime = Time.time;
                lastSaveTime = Time.time;

                OnSaveCompleted?.Invoke(slotId);
                Debug.Log($"Force save completed for slot: {slotId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Force save failed for slot {slotId}: {ex.Message}");
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

                // Check for corruption and attempt recovery
                if (enableCrashRecovery)
                {
                    await CheckAndRepairSaveAsync(slotPath);
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

                // Load character data
                await LoadCharacterDataAsync(metadata.characterData);

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
                            thumbnailPath = Path.Combine(slotPath, "thumbnail.png"),
                            isCorrupted = metadata.isCorrupted,
                            version = metadata.saveVersion.ToString()
                        });
                    }
                    catch (Exception ex)
                    {
                        Debug.LogError($"Failed to read save summary for {slotId}: {ex.Message}");
                        // Add corrupted save entry
                        summaries.Add(new SaveSummary
                        {
                            slotId = slotId,
                            lastSaved = "Unknown",
                            playTimeSeconds = 0,
                            topResources = new List<ResourceSnapshot>(),
                            sceneSummaries = new List<SceneSummary>(),
                            thumbnailPath = "",
                            isCorrupted = true,
                            version = "Unknown"
                        });
                    }
                }
            }

            return summaries;
        }

        private async Task CheckAndRepairSaveAsync(string slotPath)
        {
            string metaPath = Path.Combine(slotPath, "meta.json");
            if (!File.Exists(metaPath)) return;

            try
            {
                string json = ReadFileWithEncryption(metaPath);
                var metadata = JsonConvert.DeserializeObject<SaveMetadata>(json);
                
                // Check if save is older than crash detection time
                if (DateTime.TryParse(metadata.lastSaved, out var lastSaved))
                {
                    var timeSinceLastSave = DateTime.UtcNow - lastSaved;
                    if (timeSinceLastSave.TotalSeconds < crashDetectionTime)
                    {
                        OnCrashDetected?.Invoke(metadata.slotId);
                        
                        if (autoRepairCorruptedSaves)
                        {
                            await RepairCorruptedSaveAsync(slotPath);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error checking save corruption: {ex.Message}");
                OnSaveCorrupted?.Invoke(Path.GetFileName(slotPath));
            }
        }

        private async Task RepairCorruptedSaveAsync(string slotPath)
        {
            try
            {
                // Try to restore from backup
                string backupPath = Path.Combine(slotPath, "backup");
                if (Directory.Exists(backupPath))
                {
                    var backupDirs = Directory.GetDirectories(backupPath, "backup_*")
                        .OrderByDescending(d => d)
                        .ToArray();

                    foreach (var backupDir in backupDirs)
                    {
                        try
                        {
                            // Try to restore from this backup
                            await RestoreFromBackupAsync(slotPath, backupDir);
                            Debug.Log($"Restored save from backup: {backupDir}");
                            return;
                        }
                        catch
                        {
                            // Try next backup
                            continue;
                        }
                    }
                }

                // If no backup works, create a minimal save
                await CreateMinimalSaveAsync(slotPath);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to repair corrupted save: {ex.Message}");
            }
        }

        private async Task RestoreFromBackupAsync(string slotPath, string backupPath)
        {
            // Copy backup files to main slot
            foreach (string file in Directory.GetFiles(backupPath))
            {
                string fileName = Path.GetFileName(file);
                string destPath = Path.Combine(slotPath, fileName);
                await Task.Run(() => File.Copy(file, destPath, true));
            }
        }

        private async Task CreateMinimalSaveAsync(string slotPath)
        {
            var minimalMetadata = new SaveMetadata
            {
                slotId = Path.GetFileName(slotPath),
                saveVersion = saveVersion,
                lastSaved = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ"),
                playTimeSeconds = 0,
                isCorrupted = false
            };

            string json = JsonConvert.SerializeObject(minimalMetadata, Formatting.Indented);
            string metaPath = Path.Combine(slotPath, "meta.json");
            await WriteFileWithEncryptionAsync(metaPath, json);
        }

        private async Task SaveMetadataAsync(string slotPath)
        {
            var metadata = new SaveMetadata
            {
                slotId = currentSlotId,
                saveVersion = saveVersion,
                lastSaved = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ"),
                playTimeSeconds = (long)Time.time,
                isCorrupted = false
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

            // Get character data
            metadata.characterData = GetCharacterSaveData();

            // Calculate checksum
            metadata.checksum = CalculateChecksum(metadata);

            string json = JsonConvert.SerializeObject(metadata, Formatting.Indented);
            string metaPath = Path.Combine(slotPath, "meta.json");
            
            await WriteFileWithEncryptionAsync(metaPath, json);
        }

        private CharacterSaveData GetCharacterSaveData()
        {
            var characterData = new CharacterSaveData();
            
            if (characterTransform != null)
            {
                characterData.position = characterTransform.position;
                characterData.rotation = characterTransform.rotation;
                characterData.scale = characterTransform.localScale;
                characterData.isActive = characterTransform.gameObject.activeInHierarchy;
                characterData.currentScene = UnityEngine.SceneManagement.SceneManager.GetActiveScene().name;
            }

            return characterData;
        }

        private async Task LoadCharacterDataAsync(CharacterSaveData characterData)
        {
            if (characterData == null || characterTransform == null) return;

            characterTransform.position = characterData.position;
            characterTransform.rotation = characterData.rotation;
            characterTransform.localScale = characterData.scale;
            characterTransform.gameObject.SetActive(characterData.isActive);

            lastCharacterPosition = characterData.position;
            lastCharacterRotation = characterData.rotation;
        }

        private string CalculateChecksum(SaveMetadata metadata)
        {
            string json = JsonConvert.SerializeObject(metadata);
            using (var sha256 = SHA256.Create())
            {
                byte[] hash = sha256.ComputeHash(Encoding.UTF8.GetBytes(json));
                return Convert.ToBase64String(hash);
            }
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

        [ContextMenu("Force Save Now")]
        public void ForceSaveNow()
        {
            if (!string.IsNullOrEmpty(currentSlotId))
            {
                _ = ForceSaveAsync(currentSlotId);
            }
        }

        [ContextMenu("Test Crash Recovery")]
        public void TestCrashRecovery()
        {
            OnCrashDetected?.Invoke("test_crash");
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