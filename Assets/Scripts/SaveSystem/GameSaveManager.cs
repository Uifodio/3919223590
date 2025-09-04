using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.IO;

public class GameSaveManager : MonoBehaviour
{
    [Header("Save Settings")]
    public float autoSaveInterval = 5f;
    public bool saveOnPause = true;
    public bool saveOnExit = true;
    public string saveFileName = "gamesave.json";
    
    [Header("Debug")]
    public bool showDebugLogs = true;
    
    public static GameSaveManager Instance;
    
    private string savePath;
    private bool isSaving = false;
    private bool isLoading = false;
    private float lastSaveTime = 0f;
    
    // Save data
    private GameSaveData currentSaveData;
    
    void Awake()
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
    
    void Start()
    {
        // Start auto-save coroutine
        StartCoroutine(AutoSaveCoroutine());
    }
    
    void OnApplicationPause(bool pauseStatus)
    {
        if (pauseStatus && saveOnPause)
        {
            SaveGame();
        }
    }
    
    void OnApplicationFocus(bool hasFocus)
    {
        if (!hasFocus && saveOnPause)
        {
            SaveGame();
        }
    }
    
    void OnApplicationQuit()
    {
        if (saveOnExit)
        {
            SaveGame();
        }
    }
    
    void Initialize()
    {
        savePath = Path.Combine(Application.persistentDataPath, saveFileName);
        currentSaveData = new GameSaveData();
        
        if (showDebugLogs)
        {
            Debug.Log("[GameSaveManager] Initialized. Save path: " + savePath);
        }
    }
    
    IEnumerator AutoSaveCoroutine()
    {
        while (true)
        {
            yield return new WaitForSeconds(autoSaveInterval);
            if (!isSaving)
            {
                SaveGame();
            }
        }
    }
    
    public void SaveGame()
    {
        if (isSaving) return;
        
        StartCoroutine(SaveGameCoroutine());
    }
    
    IEnumerator SaveGameCoroutine()
    {
        isSaving = true;
        
        try
        {
            // Collect save data
            CollectSaveData();
            
            // Convert to JSON
            string json = JsonUtility.ToJson(currentSaveData, true);
            
            // Write to file
            File.WriteAllText(savePath, json);
            
            lastSaveTime = Time.time;
            
            if (showDebugLogs)
            {
                Debug.Log("[GameSaveManager] Game saved successfully");
            }
        }
        catch (System.Exception ex)
        {
            Debug.LogError("[GameSaveManager] Save failed: " + ex.Message);
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
    
    IEnumerator LoadGameCoroutine()
    {
        isLoading = true;
        
        try
        {
            if (File.Exists(savePath))
            {
                string json = File.ReadAllText(savePath);
                currentSaveData = JsonUtility.FromJson<GameSaveData>(json);
                
                // Apply loaded data
                ApplySaveData();
                
                if (showDebugLogs)
                {
                    Debug.Log("[GameSaveManager] Game loaded successfully");
                }
            }
            else
            {
                if (showDebugLogs)
                {
                    Debug.Log("[GameSaveManager] No save file found, starting fresh");
                }
            }
        }
        catch (System.Exception ex)
        {
            Debug.LogError("[GameSaveManager] Load failed: " + ex.Message);
        }
        finally
        {
            isLoading = false;
        }
        
        yield return null;
    }
    
    void CollectSaveData()
    {
        // Collect resources
        if (GameResourceManager.Instance != null)
        {
            currentSaveData.resources = GameResourceManager.Instance.GetAllResources();
        }
        
        // Collect world objects
        if (GameWorldManager.Instance != null)
        {
            currentSaveData.worldObjects = GameWorldManager.Instance.GetAllWorldObjects();
        }
        
        // Collect character data
        if (GameCharacterManager.Instance != null)
        {
            currentSaveData.characterData = GameCharacterManager.Instance.GetCharacterData();
        }
        
        // Add metadata
        currentSaveData.saveTime = System.DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
        currentSaveData.playTime = Time.time;
    }
    
    void ApplySaveData()
    {
        // Apply resources
        if (GameResourceManager.Instance != null && currentSaveData.resources != null)
        {
            GameResourceManager.Instance.LoadResources(currentSaveData.resources);
        }
        
        // Apply world objects
        if (GameWorldManager.Instance != null && currentSaveData.worldObjects != null)
        {
            GameWorldManager.Instance.LoadWorldObjects(currentSaveData.worldObjects);
        }
        
        // Apply character data
        if (GameCharacterManager.Instance != null && currentSaveData.characterData != null)
        {
            GameCharacterManager.Instance.LoadCharacterData(currentSaveData.characterData);
        }
    }
    
    public bool HasSaveFile()
    {
        return File.Exists(savePath);
    }
    
    public void DeleteSaveFile()
    {
        if (File.Exists(savePath))
        {
            File.Delete(savePath);
            if (showDebugLogs)
            {
                Debug.Log("[GameSaveManager] Save file deleted");
            }
        }
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
    public void DeleteSaveFileMenu()
    {
        DeleteSaveFile();
    }
}

[System.Serializable]
public class GameSaveData
{
    public List<ResourceData> resources = new List<ResourceData>();
    public List<WorldObjectData> worldObjects = new List<WorldObjectData>();
    public CharacterData characterData = new CharacterData();
    public string saveTime;
    public float playTime;
}

[System.Serializable]
public class ResourceData
{
    public string id;
    public long amount;
}

[System.Serializable]
public class WorldObjectData
{
    public string id;
    public Vector3 position;
    public Quaternion rotation;
    public Vector3 scale;
    public bool isActive;
    public bool isBroken;
    public bool isDestroyed;
    public List<CustomData> customData = new List<CustomData>();
}

[System.Serializable]
public class CustomData
{
    public string key;
    public string value;
    public string type;
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