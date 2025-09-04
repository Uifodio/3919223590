using UnityEngine;

public class SimpleCharacterManager : MonoBehaviour
{
    [Header("Character Settings")]
    public string playerTag = "Player";
    public bool autoFindPlayer = true;
    public bool trackPosition = true;
    public bool trackRotation = true;
    public bool trackScale = true;
    public bool trackActiveState = true;
    
    [Header("Movement Tracking")]
    public float positionThreshold = 0.1f;
    public float rotationThreshold = 1f;
    public float saveInterval = 1f;
    
    public static SimpleCharacterManager Instance { get; private set; }
    
    // Private
    private Transform playerTransform;
    private Vector3 lastSavedPosition;
    private Quaternion lastSavedRotation;
    private Vector3 lastSavedScale;
    private bool lastSavedActiveState;
    private float lastSaveTime;
    
    private void Awake()
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
    
    private void Start()
    {
        if (autoFindPlayer)
        {
            FindPlayer();
        }
    }
    
    private void Update()
    {
        if (playerTransform != null && trackPosition)
        {
            CheckForChanges();
        }
    }
    
    private void FindPlayer()
    {
        // Try to find player by tag
        GameObject player = GameObject.FindGameObjectWithTag(playerTag);
        if (player == null)
        {
            // Try to find by name
            player = GameObject.Find("Player");
        }
        if (player == null)
        {
            // Try to find by name
            player = GameObject.Find("Character");
        }
        
        if (player != null)
        {
            playerTransform = player.transform;
            InitializeTracking();
            Debug.Log($"[SimpleCharacterManager] Found player: {player.name}");
        }
        else
        {
            Debug.LogWarning($"[SimpleCharacterManager] No player found with tag '{playerTag}'");
        }
    }
    
    private void InitializeTracking()
    {
        if (playerTransform != null)
        {
            lastSavedPosition = playerTransform.position;
            lastSavedRotation = playerTransform.rotation;
            lastSavedScale = playerTransform.localScale;
            lastSavedActiveState = playerTransform.gameObject.activeInHierarchy;
            lastSaveTime = Time.time;
        }
    }
    
    private void CheckForChanges()
    {
        if (playerTransform == null) return;
        
        bool hasChanged = false;
        
        // Check position
        if (trackPosition && Vector3.Distance(playerTransform.position, lastSavedPosition) > positionThreshold)
        {
            hasChanged = true;
        }
        
        // Check rotation
        if (trackRotation && Quaternion.Angle(playerTransform.rotation, lastSavedRotation) > rotationThreshold)
        {
            hasChanged = true;
        }
        
        // Check scale
        if (trackScale && Vector3.Distance(playerTransform.localScale, lastSavedScale) > positionThreshold)
        {
            hasChanged = true;
        }
        
        // Check active state
        if (trackActiveState && playerTransform.gameObject.activeInHierarchy != lastSavedActiveState)
        {
            hasChanged = true;
        }
        
        // Check save interval
        if (hasChanged && Time.time - lastSaveTime >= saveInterval)
        {
            SaveCharacterState();
        }
    }
    
    private void SaveCharacterState()
    {
        if (playerTransform == null) return;
        
        lastSavedPosition = playerTransform.position;
        lastSavedRotation = playerTransform.rotation;
        lastSavedScale = playerTransform.localScale;
        lastSavedActiveState = playerTransform.gameObject.activeInHierarchy;
        lastSaveTime = Time.time;
        
        // Mark save system as dirty
        if (SimpleSaveManager.Instance != null)
        {
            // This would trigger a save in the main save manager
        }
    }
    
    public CharacterData GetCharacterData()
    {
        if (playerTransform == null)
        {
            return new CharacterData();
        }
        
        return new CharacterData
        {
            position = playerTransform.position,
            rotation = playerTransform.rotation,
            scale = playerTransform.localScale,
            isActive = playerTransform.gameObject.activeInHierarchy,
            currentScene = UnityEngine.SceneManagement.SceneManager.GetActiveScene().name
        };
    }
    
    public void LoadCharacterData(CharacterData data)
    {
        if (playerTransform == null || data == null) return;
        
        if (trackPosition)
        {
            playerTransform.position = data.position;
        }
        
        if (trackRotation)
        {
            playerTransform.rotation = data.rotation;
        }
        
        if (trackScale)
        {
            playerTransform.localScale = data.scale;
        }
        
        if (trackActiveState)
        {
            playerTransform.gameObject.SetActive(data.isActive);
        }
        
        // Update tracking values
        InitializeTracking();
    }
    
    public void SetPlayer(Transform player)
    {
        playerTransform = player;
        InitializeTracking();
    }
    
    public Transform GetPlayer()
    {
        return playerTransform;
    }
    
    // Debug methods
    [ContextMenu("Find Player")]
    public void FindPlayerDebug()
    {
        FindPlayer();
    }
    
    [ContextMenu("Save Character State")]
    public void SaveCharacterStateDebug()
    {
        SaveCharacterState();
    }
    
    [ContextMenu("Log Character Data")]
    public void LogCharacterData()
    {
        var data = GetCharacterData();
        Debug.Log($"[SimpleCharacterManager] Character Data:");
        Debug.Log($"  Position: {data.position}");
        Debug.Log($"  Rotation: {data.rotation.eulerAngles}");
        Debug.Log($"  Scale: {data.scale}");
        Debug.Log($"  Active: {data.isActive}");
        Debug.Log($"  Scene: {data.currentScene}");
    }
}