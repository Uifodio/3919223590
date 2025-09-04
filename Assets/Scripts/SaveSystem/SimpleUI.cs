using UnityEngine;
using UnityEngine.UI;

public class SimpleUI : MonoBehaviour
{
    [Header("UI References")]
    public Text coinsText;
    public Text woodText;
    public Text stoneText;
    public Button saveButton;
    public Button loadButton;
    public Button newGameButton;
    public Text saveStatusText;
    
    [Header("Main Menu")]
    public GameObject mainMenuPanel;
    public GameObject gamePanel;
    public Text playTimeText;
    public Text lastSaveText;
    
    private void Start()
    {
        // Subscribe to events
        if (SimpleResourceManager.Instance != null)
        {
            SimpleResourceManager.Instance.OnResourceChanged += OnResourceChanged;
        }
        
        if (SimpleSaveManager.Instance != null)
        {
            SimpleSaveManager.Instance.OnSaveCompleted += OnSaveCompleted;
            SimpleSaveManager.Instance.OnLoadCompleted += OnLoadCompleted;
            SimpleSaveManager.Instance.OnSaveFailed += OnSaveFailed;
        }
        
        // Setup buttons
        if (saveButton != null)
        {
            saveButton.onClick.AddListener(SaveGame);
        }
        
        if (loadButton != null)
        {
            loadButton.onClick.AddListener(LoadGame);
        }
        
        if (newGameButton != null)
        {
            newGameButton.onClick.AddListener(NewGame);
        }
        
        // Update UI
        UpdateResourceUI();
        UpdateSaveStatus();
    }
    
    private void Update()
    {
        // Update play time
        if (playTimeText != null)
        {
            float playTime = Time.time;
            int hours = Mathf.FloorToInt(playTime / 3600f);
            int minutes = Mathf.FloorToInt((playTime % 3600f) / 60f);
            int seconds = Mathf.FloorToInt(playTime % 60f);
            playTimeText.text = $"Play Time: {hours:00}:{minutes:00}:{seconds:00}";
        }
    }
    
    private void OnResourceChanged(string resourceId, long amount)
    {
        UpdateResourceUI();
    }
    
    private void UpdateResourceUI()
    {
        if (SimpleResourceManager.Instance == null) return;
        
        if (coinsText != null)
        {
            long coins = SimpleResourceManager.Instance.GetResourceAmount("coins");
            coinsText.text = $"Coins: {coins:N0}";
        }
        
        if (woodText != null)
        {
            long wood = SimpleResourceManager.Instance.GetResourceAmount("wood");
            woodText.text = $"Wood: {wood:N0}";
        }
        
        if (stoneText != null)
        {
            long stone = SimpleResourceManager.Instance.GetResourceAmount("stone");
            stoneText.text = $"Stone: {stone:N0}";
        }
    }
    
    private void UpdateSaveStatus()
    {
        if (saveStatusText != null)
        {
            if (SimpleSaveManager.Instance != null && SimpleSaveManager.Instance.HasSaveFile())
            {
                saveStatusText.text = "Save file available";
                saveStatusText.color = Color.green;
            }
            else
            {
                saveStatusText.text = "No save file";
                saveStatusText.color = Color.red;
            }
        }
    }
    
    private void SaveGame()
    {
        if (SimpleSaveManager.Instance != null)
        {
            SimpleSaveManager.Instance.SaveGame();
        }
    }
    
    private void LoadGame()
    {
        if (SimpleSaveManager.Instance != null)
        {
            SimpleSaveManager.Instance.LoadGame();
        }
    }
    
    private void NewGame()
    {
        if (SimpleSaveManager.Instance != null)
        {
            SimpleSaveManager.Instance.DeleteSaveFile();
        }
        
        // Reset resources
        if (SimpleResourceManager.Instance != null)
        {
            // This would reset resources to default
        }
        
        UpdateSaveStatus();
    }
    
    private void OnSaveCompleted()
    {
        if (saveStatusText != null)
        {
            saveStatusText.text = "Game saved!";
            saveStatusText.color = Color.green;
        }
        
        // Hide status after 2 seconds
        Invoke(nameof(UpdateSaveStatus), 2f);
    }
    
    private void OnLoadCompleted()
    {
        if (saveStatusText != null)
        {
            saveStatusText.text = "Game loaded!";
            saveStatusText.color = Color.green;
        }
        
        // Hide status after 2 seconds
        Invoke(nameof(UpdateSaveStatus), 2f);
    }
    
    private void OnSaveFailed(string error)
    {
        if (saveStatusText != null)
        {
            saveStatusText.text = $"Save failed: {error}";
            saveStatusText.color = Color.red;
        }
        
        // Hide status after 3 seconds
        Invoke(nameof(UpdateSaveStatus), 3f);
    }
    
    public void ShowMainMenu()
    {
        if (mainMenuPanel != null)
        {
            mainMenuPanel.SetActive(true);
        }
        
        if (gamePanel != null)
        {
            gamePanel.SetActive(false);
        }
        
        UpdateSaveStatus();
    }
    
    public void ShowGame()
    {
        if (mainMenuPanel != null)
        {
            mainMenuPanel.SetActive(false);
        }
        
        if (gamePanel != null)
        {
            gamePanel.SetActive(true);
        }
    }
    
    // Debug methods
    [ContextMenu("Update UI")]
    public void UpdateUIDebug()
    {
        UpdateResourceUI();
        UpdateSaveStatus();
    }
}