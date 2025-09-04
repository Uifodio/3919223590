using UnityEngine;
using UnityEngine.UI;

public class GameUI : MonoBehaviour
{
    [Header("UI References")]
    public Text coinsText;
    public Text woodText;
    public Text stoneText;
    public Button saveButton;
    public Button loadButton;
    public Button newGameButton;
    public Text saveStatusText;
    public Text playTimeText;
    
    [Header("Main Menu")]
    public GameObject mainMenuPanel;
    public GameObject gamePanel;
    
    void Start()
    {
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
    
    void Update()
    {
        // Update play time
        if (playTimeText != null)
        {
            float playTime = Time.time;
            int hours = Mathf.FloorToInt(playTime / 3600f);
            int minutes = Mathf.FloorToInt((playTime % 3600f) / 60f);
            int seconds = Mathf.FloorToInt(playTime % 60f);
            playTimeText.text = "Play Time: " + hours.ToString("00") + ":" + minutes.ToString("00") + ":" + seconds.ToString("00");
        }
        
        // Update resources
        UpdateResourceUI();
    }
    
    void UpdateResourceUI()
    {
        if (GameResourceManager.Instance == null) return;
        
        if (coinsText != null)
        {
            long coins = GameResourceManager.Instance.GetResourceAmount("coins");
            coinsText.text = "Coins: " + coins.ToString("N0");
        }
        
        if (woodText != null)
        {
            long wood = GameResourceManager.Instance.GetResourceAmount("wood");
            woodText.text = "Wood: " + wood.ToString("N0");
        }
        
        if (stoneText != null)
        {
            long stone = GameResourceManager.Instance.GetResourceAmount("stone");
            stoneText.text = "Stone: " + stone.ToString("N0");
        }
    }
    
    void UpdateSaveStatus()
    {
        if (saveStatusText != null)
        {
            if (GameSaveManager.Instance != null && GameSaveManager.Instance.HasSaveFile())
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
    
    public void SaveGame()
    {
        if (GameSaveManager.Instance != null)
        {
            GameSaveManager.Instance.SaveGame();
        }
    }
    
    public void LoadGame()
    {
        if (GameSaveManager.Instance != null)
        {
            GameSaveManager.Instance.LoadGame();
        }
    }
    
    public void NewGame()
    {
        if (GameSaveManager.Instance != null)
        {
            GameSaveManager.Instance.DeleteSaveFile();
        }
        
        UpdateSaveStatus();
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