using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

public class SimpleSaveManager : MonoBehaviour
{
    [Header("Save Settings")]
    public string saveFolderName = "GameSaves";
    public float autoSaveInterval = 5f;
    public bool saveOnPause = true;
    public bool saveOnExit = true;
    
    [Header("Debug")]
    public bool showDebugInfo = true;
    
    public static SimpleSaveManager Instance { get; private set; }
    
    // Events
    public event Action OnSaveCompleted;
    public event Action OnLoadCompleted;
    public event Action<string> OnSaveFailed;
    
    // Private
    private string savePath;
    private float lastSaveTime;
    private bool isSaving = false;
    private bool isLoading = false;
    
    // Save data
    private GameSaveData currentSaveData;
    
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
    
    private void Start()
    {
        // Auto-save every interval
        InvokeRepeating(nameof(AutoSave), autoSaveInterval, autoSaveInterval);
    }
    
    private void OnApplicationPause(bool pauseStatus)
    {
        if (pauseStatus && saveOnPause)
        {
            SaveGame();
        }
    }
    
    private void OnApplicationFocus(bool hasFocus)
    {
        if (!hasFocus && saveOnPause)
        {
            SaveGame();
        }
    }
    
    private void OnApplicationQuit()
    {
        if (saveOnExit)
        {
            SaveGame();
        }
    }
    
    private void Initialize()
    {
        savePath = Path.Combine(Application.persistentDataPath, saveFolderName);
        
        if (!Directory.Exists(savePath))
        {
            Directory.CreateDirectory(savePath);
        }
        
        currentSaveData = new GameSaveData();
        
        if (showDebugInfo)
        {
            Debug.Log($"[SimpleSaveManager] Initialized. Save path: {savePath}");
        }
    }
    
    public void SaveGame()
    {
        if (isSaving) return;
        
        StartCoroutine(SaveGameCoroutine());
    }
    
    private System.Collections.IEnumerator SaveGameCoroutine()
    {
        isSaving = true;
        
        try
        {
            // Collect all save data
            CollectSaveData();
            
            // Save to file
            string json = JsonUtility.ToJson(currentSaveData, true);
            string filePath = Path.Combine(savePath, "save.json");
            
            // Atomic write
            string tempPath = filePath + ".tmp";
            File.WriteAllText(tempPath, json);
            File.Move(tempPath, filePath);
            
            lastSaveTime = Time.time;
            
            if (showDebugInfo)
            {
                Debug.Log("[SimpleSaveManager] Game saved successfully");
            }
            
            OnSaveCompleted?.Invoke();
        }
        catch (Exception ex)
        {
            Debug.LogError($"[SimpleSaveManager] Save failed: {ex.Message}");
            OnSaveFailed?.Invoke(ex.Message);
        }
        finally
        {
            isSaving = false;
        }
        
        yield return null;
    }
    
    public void LoadGame()
    {
        if (isLoading) return;
        
        StartCoroutine(LoadGameCoroutine());
    }
    
    private System.Collections.IEnumerator LoadGameCoroutine()
    {
        isLoading = true;
        
        try
        {
            string filePath = Path.Combine(savePath, "save.json");
            
            if (File.Exists(filePath))
            {
                string json = File.ReadAllText(filePath);
                currentSaveData = JsonUtility.FromJson<GameSaveData>(json);
                
                // Apply loaded data
                ApplySaveData();
                
                if (showDebugInfo)
                {
                    Debug.Log("[SimpleSaveManager] Game loaded successfully");
                }
                
                OnLoadCompleted?.Invoke();
            }
            else
            {
                if (showDebugInfo)
                {
                    Debug.Log("[SimpleSaveManager] No save file found, starting fresh");
                }
            }
        }
        catch (Exception ex)
        {
            Debug.LogError($"[SimpleSaveManager] Load failed: {ex.Message}");
            OnSaveFailed?.Invoke(ex.Message);
        }
        finally
        {
            isLoading = false;
        }
        
        yield return null;
    }
    
    private void CollectSaveData()
    {
        // Collect resources
        if (SimpleResourceManager.Instance != null)
        {
            currentSaveData.resources = SimpleResourceManager.Instance.GetAllResources();
        }
        
        // Collect world state
        if (SimpleWorldManager.Instance != null)
        {
            currentSaveData.worldState = SimpleWorldManager.Instance.GetWorldState();
        }
        
        // Collect character data
        if (SimpleCharacterManager.Instance != null)
        {
            currentSaveData.characterData = SimpleCharacterManager.Instance.GetCharacterData();
        }
        
        // Add metadata
        currentSaveData.saveTime = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
        currentSaveData.playTime = Time.time;
    }
    
    private void ApplySaveData()
    {
        // Apply resources
        if (SimpleResourceManager.Instance != null && currentSaveData.resources != null)
        {
            SimpleResourceManager.Instance.LoadResources(currentSaveData.resources);
        }
        
        // Apply world state
        if (SimpleWorldManager.Instance != null && currentSaveData.worldState != null)
        {
            SimpleWorldManager.Instance.LoadWorldState(currentSaveData.worldState);
        }
        
        // Apply character data
        if (SimpleCharacterManager.Instance != null && currentSaveData.characterData != null)
        {
            SimpleCharacterManager.Instance.LoadCharacterData(currentSaveData.characterData);
        }
    }
    
    private void AutoSave()
    {
        SaveGame();
    }
    
    public bool HasSaveFile()
    {
        string filePath = Path.Combine(savePath, "save.json");
        return File.Exists(filePath);
    }
    
    public GameSaveData GetCurrentSaveData()
    {
        return currentSaveData;
    }
    
    // Debug methods
    [ContextMenu("Save Game Now")]
    public void SaveGameNow()
    {
        SaveGame();
    }
    
    [ContextMenu("Load Game Now")]
    public void LoadGameNow()
    {
        LoadGame();
    }
    
    [ContextMenu("Delete Save File")]
    public void DeleteSaveFile()
    {
        string filePath = Path.Combine(savePath, "save.json");
        if (File.Exists(filePath))
        {
            File.Delete(filePath);
            Debug.Log("[SimpleSaveManager] Save file deleted");
        }
    }
}

[System.Serializable]
public class GameSaveData
{
    public Dictionary<string, long> resources = new Dictionary<string, long>();
    public WorldStateData worldState = new WorldStateData();
    public CharacterData characterData = new CharacterData();
    public string saveTime;
    public float playTime;
}

[System.Serializable]
public class WorldStateData
{
    public List<ObjectState> objects = new List<ObjectState>();
    public List<string> brokenObjects = new List<string>();
    public Dictionary<string, bool> triggers = new Dictionary<string, bool>();
}

[System.Serializable]
public class ObjectState
{
    public string id;
    public Vector3 position;
    public Quaternion rotation;
    public Vector3 scale;
    public bool isActive;
    public Dictionary<string, object> customData = new Dictionary<string, object>();
}

[System.Serializable]
public class CharacterData
{
    public Vector3 position;
    public Quaternion rotation;
    public Vector3 scale;
    public bool isActive;
    public string currentScene;
}