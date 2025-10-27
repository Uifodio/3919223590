using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

namespace SaveSystem
{
    [System.Serializable]
    public class SaveCardData
    {
        public string slotId;
        public string lastSaved;
        public long playTimeSeconds;
        public List<ResourceSummary> topResources;
        public string thumbnailPath;
        public bool hasThumbnail;
    }

    public class UIResourcePanel : MonoBehaviour
    {
        [Header("Top Bar UI")]
        [SerializeField] private Transform topBarContainer;
        [SerializeField] private GameObject resourceDisplayPrefab;
        [SerializeField] private bool showTopBar = true;

        [Header("Save Slots UI")]
        [SerializeField] private Transform saveSlotsContainer;
        [SerializeField] private GameObject saveCardPrefab;
        [SerializeField] private Button newGameButton;
        [SerializeField] private Button loadGameButton;
        [SerializeField] private Button saveGameButton;
        [SerializeField] private Button deleteGameButton;

        [Header("Save Card UI Elements")]
        [SerializeField] private TextMeshProUGUI slotIdText;
        [SerializeField] private TextMeshProUGUI lastSavedText;
        [SerializeField] private TextMeshProUGUI playTimeText;
        [SerializeField] private Transform resourcesContainer;
        [SerializeField] private Image thumbnailImage;
        [SerializeField] private GameObject noThumbnailPlaceholder;

        [Header("Resource Display Settings")]
        [SerializeField] private bool showResourceIcons = false; // Note: No icon fields as requested
        [SerializeField] private bool showResourceCategories = false;
        [SerializeField] private int maxTopBarResources = 5;
        [SerializeField] private string timeFormat = "HH:mm:ss";

        // Private fields
        private List<GameObject> topBarResourceDisplays = new List<GameObject>();
        private List<GameObject> saveCardDisplays = new List<GameObject>();
        private SaveCardData selectedSaveCard;
        private bool isInitialized = false;

        private void Start()
        {
            InitializeUI();
            BindToManagers();
        }

        private void OnDestroy()
        {
            UnbindFromManagers();
        }

        private void InitializeUI()
        {
            if (isInitialized) return;

            // Initialize top bar
            if (showTopBar && topBarContainer != null)
            {
                RefreshTopBar();
            }

            // Initialize save slots
            if (saveSlotsContainer != null)
            {
                ShowSaveSlots();
            }

            // Setup button events
            SetupButtonEvents();

            isInitialized = true;
        }

        private void SetupButtonEvents()
        {
            if (newGameButton != null)
            {
                newGameButton.onClick.AddListener(OnNewGameClicked);
            }

            if (loadGameButton != null)
            {
                loadGameButton.onClick.AddListener(OnLoadGameClicked);
            }

            if (saveGameButton != null)
            {
                saveGameButton.onClick.AddListener(OnSaveGameClicked);
            }

            if (deleteGameButton != null)
            {
                deleteGameButton.onClick.AddListener(OnDeleteGameClicked);
            }
        }

        private void BindToManagers()
        {
            // Bind to ResourceManager events
            if (ResourceManager.Instance != null)
            {
                ResourceManager.Instance.OnResourceChanged += OnResourceChanged;
            }

            // Bind to SaveManager events
            if (SaveManager.Instance != null)
            {
                SaveManager.Instance.OnSaveCompleted += OnSaveCompleted;
                SaveManager.Instance.OnLoadCompleted += OnLoadCompleted;
                SaveManager.Instance.OnSaveFailed += OnSaveFailed;
            }
        }

        private void UnbindFromManagers()
        {
            // Unbind from ResourceManager events
            if (ResourceManager.Instance != null)
            {
                ResourceManager.Instance.OnResourceChanged -= OnResourceChanged;
            }

            // Unbind from SaveManager events
            if (SaveManager.Instance != null)
            {
                SaveManager.Instance.OnSaveCompleted -= OnSaveCompleted;
                SaveManager.Instance.OnLoadCompleted -= OnLoadCompleted;
                SaveManager.Instance.OnSaveFailed -= OnSaveFailed;
            }
        }

        public void RefreshTopBar()
        {
            if (!showTopBar || topBarContainer == null || ResourceManager.Instance == null)
                return;

            // Clear existing displays
            foreach (var display in topBarResourceDisplays)
            {
                if (display != null)
                {
                    Destroy(display);
                }
            }
            topBarResourceDisplays.Clear();

            // Get top bar resources
            var topBarResources = ResourceManager.Instance.GetTopBarResources();
            int displayCount = Math.Min(topBarResources.Count, maxTopBarResources);

            for (int i = 0; i < displayCount; i++)
            {
                var resource = topBarResources[i];
                CreateResourceDisplay(resource);
            }
        }

        private void CreateResourceDisplay(ResourceDefinition resource)
        {
            if (resourceDisplayPrefab == null || topBarContainer == null)
                return;

            var displayObj = Instantiate(resourceDisplayPrefab, topBarContainer);
            topBarResourceDisplays.Add(displayObj);

            // Setup display components
            var nameText = displayObj.GetComponentInChildren<TextMeshProUGUI>();
            var amountText = displayObj.GetComponentsInChildren<TextMeshProUGUI>().LastOrDefault();

            if (nameText != null)
            {
                nameText.text = resource.DisplayName;
            }

            if (amountText != null)
            {
                long currentAmount = ResourceManager.Instance.GetResourceAmount(resource.Id);
                amountText.text = FormatResourceAmount(currentAmount);
            }

            // Add click handler for resource details (optional)
            var button = displayObj.GetComponent<Button>();
            if (button != null)
            {
                button.onClick.AddListener(() => OnResourceDisplayClicked(resource.Id));
            }
        }

        private void UpdateResourceDisplay(string resourceId, long amount)
        {
            if (!showTopBar) return;

            // Find the display for this resource
            for (int i = 0; i < topBarResourceDisplays.Count; i++)
            {
                var display = topBarResourceDisplays[i];
                if (display == null) continue;

                var amountTexts = display.GetComponentsInChildren<TextMeshProUGUI>();
                if (amountTexts.Length > 1)
                {
                    var amountText = amountTexts[1]; // Assuming amount is second text component
                    amountText.text = FormatResourceAmount(amount);
                }
            }
        }

        public void ShowSaveSlots()
        {
            if (saveSlotsContainer == null || SaveManager.Instance == null)
                return;

            // Clear existing save cards
            foreach (var card in saveCardDisplays)
            {
                if (card != null)
                {
                    Destroy(card);
                }
            }
            saveCardDisplays.Clear();

            // Get save summaries
            var saveSummaries = SaveManager.Instance.GetSaveSummaries();

            foreach (var summary in saveSummaries)
            {
                CreateSaveCard(summary);
            }
        }

        private void CreateSaveCard(SaveSummary summary)
        {
            if (saveCardPrefab == null || saveSlotsContainer == null)
                return;

            var cardObj = Instantiate(saveCardPrefab, saveSlotsContainer);
            saveCardDisplays.Add(cardObj);

            // Setup card data
            var saveCardData = new SaveCardData
            {
                slotId = summary.slotId,
                lastSaved = summary.lastSaved,
                playTimeSeconds = summary.playTimeSeconds,
                topResources = summary.topResources,
                thumbnailPath = summary.thumbnailPath,
                hasThumbnail = System.IO.File.Exists(summary.thumbnailPath)
            };

            // Setup UI elements
            SetupSaveCardUI(cardObj, saveCardData);

            // Add click handler
            var button = cardObj.GetComponent<Button>();
            if (button != null)
            {
                button.onClick.AddListener(() => OnSaveCardClicked(saveCardData));
            }
        }

        private void SetupSaveCardUI(GameObject cardObj, SaveCardData data)
        {
            // Find UI elements in the card
            var slotIdText = cardObj.GetComponentInChildren<TextMeshProUGUI>();
            var lastSavedText = cardObj.GetComponentsInChildren<TextMeshProUGUI>().Skip(1).FirstOrDefault();
            var playTimeText = cardObj.GetComponentsInChildren<TextMeshProUGUI>().Skip(2).FirstOrDefault();
            var thumbnailImage = cardObj.GetComponentInChildren<Image>();

            if (slotIdText != null)
            {
                slotIdText.text = data.slotId;
            }

            if (lastSavedText != null)
            {
                if (DateTime.TryParse(data.lastSaved, out var lastSaved))
                {
                    lastSavedText.text = lastSaved.ToString("yyyy-MM-dd HH:mm");
                }
                else
                {
                    lastSavedText.text = "Unknown";
                }
            }

            if (playTimeText != null)
            {
                playTimeText.text = FormatPlayTime(data.playTimeSeconds);
            }

            if (thumbnailImage != null)
            {
                if (data.hasThumbnail)
                {
                    LoadThumbnail(thumbnailImage, data.thumbnailPath);
                }
                else
                {
                    // Show placeholder or hide image
                    thumbnailImage.gameObject.SetActive(false);
                }
            }
        }

        private void LoadThumbnail(Image image, string thumbnailPath)
        {
            if (string.IsNullOrEmpty(thumbnailPath) || !System.IO.File.Exists(thumbnailPath))
                return;

            try
            {
                byte[] imageData = System.IO.File.ReadAllBytes(thumbnailPath);
                Texture2D texture = new Texture2D(2, 2);
                texture.LoadImage(imageData);
                
                Sprite sprite = Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), new Vector2(0.5f, 0.5f));
                image.sprite = sprite;
                image.gameObject.SetActive(true);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to load thumbnail: {ex.Message}");
                image.gameObject.SetActive(false);
            }
        }

        public void BindToSlot(string slotId)
        {
            // This method can be used to bind UI to a specific save slot
            // For example, showing slot-specific information or enabling/disabling buttons
            Debug.Log($"UI bound to slot: {slotId}");
        }

        // Event handlers
        private void OnResourceChanged(string resourceId, long newAmount)
        {
            UpdateResourceDisplay(resourceId, newAmount);
        }

        private void OnSaveCompleted(string slotId)
        {
            Debug.Log($"Save completed: {slotId}");
            ShowSaveSlots(); // Refresh save slots display
        }

        private void OnLoadCompleted(string slotId)
        {
            Debug.Log($"Load completed: {slotId}");
            RefreshTopBar(); // Refresh resource display
        }

        private void OnSaveFailed(string slotId, string error)
        {
            Debug.LogError($"Save failed for slot {slotId}: {error}");
            // Could show error dialog here
        }

        private void OnResourceDisplayClicked(string resourceId)
        {
            // Optional: Show detailed resource information
            Debug.Log($"Resource display clicked: {resourceId}");
        }

        private void OnSaveCardClicked(SaveCardData saveCardData)
        {
            selectedSaveCard = saveCardData;
            Debug.Log($"Save card selected: {saveCardData.slotId}");
            
            // Update button states
            UpdateButtonStates();
        }

        private void OnNewGameClicked()
        {
            Debug.Log("New game clicked");
            // Implement new game logic
        }

        private void OnLoadGameClicked()
        {
            if (selectedSaveCard != null && SaveManager.Instance != null)
            {
                _ = SaveManager.Instance.LoadSlotAsync(selectedSaveCard.slotId);
            }
            else
            {
                Debug.LogWarning("No save slot selected");
            }
        }

        private void OnSaveGameClicked()
        {
            if (SaveManager.Instance != null)
            {
                string slotId = selectedSaveCard?.slotId ?? "auto_save";
                _ = SaveManager.Instance.SaveSlotAsync(slotId);
            }
        }

        private void OnDeleteGameClicked()
        {
            if (selectedSaveCard != null && SaveManager.Instance != null)
            {
                // Show confirmation dialog (implement as needed)
                _ = SaveManager.Instance.DeleteSlotAsync(selectedSaveCard.slotId);
                selectedSaveCard = null;
                ShowSaveSlots(); // Refresh display
            }
        }

        private void UpdateButtonStates()
        {
            bool hasSelection = selectedSaveCard != null;
            
            if (loadGameButton != null)
            {
                loadGameButton.interactable = hasSelection;
            }
            
            if (deleteGameButton != null)
            {
                deleteGameButton.interactable = hasSelection;
            }
        }

        // Utility methods
        private string FormatResourceAmount(long amount)
        {
            if (amount >= 1000000)
            {
                return $"{amount / 1000000f:F1}M";
            }
            else if (amount >= 1000)
            {
                return $"{amount / 1000f:F1}K";
            }
            else
            {
                return amount.ToString();
            }
        }

        private string FormatPlayTime(long playTimeSeconds)
        {
            var timeSpan = TimeSpan.FromSeconds(playTimeSeconds);
            
            if (timeSpan.TotalHours >= 1)
            {
                return $"{(int)timeSpan.TotalHours}h {timeSpan.Minutes}m";
            }
            else if (timeSpan.TotalMinutes >= 1)
            {
                return $"{timeSpan.Minutes}m {timeSpan.Seconds}s";
            }
            else
            {
                return $"{timeSpan.Seconds}s";
            }
        }

        // Public methods for external access
        public void SetTopBarVisible(bool visible)
        {
            showTopBar = visible;
            if (topBarContainer != null)
            {
                topBarContainer.gameObject.SetActive(visible);
            }
        }

        public void RefreshAll()
        {
            RefreshTopBar();
            ShowSaveSlots();
        }

        // Debug methods
        [ContextMenu("Refresh Top Bar")]
        public void RefreshTopBarDebug()
        {
            RefreshTopBar();
        }

        [ContextMenu("Refresh Save Slots")]
        public void RefreshSaveSlotsDebug()
        {
            ShowSaveSlots();
        }

        [ContextMenu("Log UI State")]
        public void LogUIState()
        {
            Debug.Log("=== UI Resource Panel State ===");
            Debug.Log($"Top Bar Visible: {showTopBar}");
            Debug.Log($"Top Bar Resources: {topBarResourceDisplays.Count}");
            Debug.Log($"Save Cards: {saveCardDisplays.Count}");
            Debug.Log($"Selected Save Card: {selectedSaveCard?.slotId ?? "None"}");
        }
    }
}