using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;

namespace DarkFantasyTransitions
{
    [System.Serializable]
    public class TransitionSettings
    {
        [Header("Scene Settings")]
        [Tooltip("Name of the scene to transition to")]
        public string targetSceneName;
        
        [Header("Visual Customization")]
        [Tooltip("Custom color for the loading bar during this transition")]
        public Color customLoadingBarColor = new Color(0.8f, 0.4f, 0.9f, 1f);
        
        [Tooltip("Custom color for the loading text during this transition")]
        public Color customTextColor = Color.white;
        
        [Tooltip("Custom fade overlay color")]
        public Color customFadeColor = Color.black;
        
        [Header("Timing Settings")]
        [Tooltip("Custom fade in duration (0 = use default)")]
        [Range(0f, 5f)]
        public float customFadeInDuration = 0f;
        
        [Tooltip("Custom fade out duration (0 = use default)")]
        [Range(0f, 5f)]
        public float customFadeOutDuration = 0f;
        
        [Tooltip("Custom loading duration (0 = use default)")]
        [Range(0f, 10f)]
        public float customLoadingDuration = 0f;
        
        [Header("Audio Settings")]
        [Tooltip("Custom fade in sound for this transition")]
        public AudioClip customFadeInSound;
        
        [Tooltip("Custom fade out sound for this transition")]
        public AudioClip customFadeOutSound;
        
        [Tooltip("Custom loading complete sound")]
        public AudioClip customLoadingCompleteSound;
        
        [Header("Special Effects")]
        [Tooltip("Enable screen shake for this transition")]
        public bool enableScreenShake = false;
        
        [Tooltip("Enable glitch effect for this transition")]
        public bool enableGlitchEffect = false;
        
        [Tooltip("Enable particle effects for this transition")]
        public bool enableParticleEffects = true;
        
        [Header("Custom Quote")]
        [Tooltip("Custom quote to display during this transition (leave empty for random)")]
        [TextArea(2, 4)]
        public string customQuote = "";
        
        [Tooltip("Use only custom quote (don't rotate through default quotes)")]
        public bool useOnlyCustomQuote = false;
    }
    
    [RequireComponent(typeof(Button))]
    public class SceneTransitionButton : MonoBehaviour, IPointerClickHandler, IPointerEnterHandler, IPointerExitHandler
    {
        [Header("Transition Configuration")]
        [SerializeField] private TransitionSettings transitionSettings = new TransitionSettings();
        
        [Header("Button Visual Effects")]
        [SerializeField] private bool enableButtonHoverEffect = true;
        [SerializeField] private Color hoverColor = new Color(1f, 0.8f, 1f, 1f);
        [SerializeField] private float hoverScale = 1.1f;
        [SerializeField] private float hoverTransitionSpeed = 5f;
        
        [Header("Button Audio")]
        [SerializeField] private bool enableButtonAudio = true;
        [SerializeField] private AudioClip buttonClickSound;
        [SerializeField] private AudioClip buttonHoverSound;
        [SerializeField] private float buttonAudioVolume = 0.8f;
        
        [Header("Validation")]
        [SerializeField] private bool validateSceneExists = true;
        [SerializeField] private bool showDebugInfo = false;
        
        // Private variables
        private Button button;
        private AudioSource audioSource;
        private Image buttonImage;
        private TextMeshProUGUI buttonText;
        private Vector3 originalScale;
        private Color originalColor;
        private bool isHovering = false;
        private bool isTransitioning = false;
        
        // Events
        public System.Action<SceneTransitionButton> OnTransitionStarted;
        public System.Action<SceneTransitionButton> OnTransitionCompleted;
        
        private void Awake()
        {
            InitializeComponents();
            SetupButton();
            ValidateConfiguration();
        }
        
        private void Start()
        {
            // Subscribe to transition manager events
            SceneTransitionManager.OnTransitionStarted += OnGlobalTransitionStarted;
            SceneTransitionManager.OnTransitionCompleted += OnGlobalTransitionCompleted;
        }
        
        private void OnDestroy()
        {
            // Unsubscribe from events
            SceneTransitionManager.OnTransitionStarted -= OnGlobalTransitionStarted;
            SceneTransitionManager.OnTransitionCompleted -= OnGlobalTransitionCompleted;
        }
        
        private void InitializeComponents()
        {
            // Get button component
            button = GetComponent<Button>();
            if (button == null)
            {
                Debug.LogError($"SceneTransitionButton requires a Button component on {gameObject.name}");
                return;
            }
            
            // Get or create audio source
            audioSource = GetComponent<AudioSource>();
            if (audioSource == null)
                audioSource = gameObject.AddComponent<AudioSource>();
            
            audioSource.volume = buttonAudioVolume;
            audioSource.playOnAwake = false;
            
            // Get button image
            buttonImage = GetComponent<Image>();
            if (buttonImage == null)
                buttonImage = gameObject.AddComponent<Image>();
            
            // Get button text
            buttonText = GetComponentInChildren<TextMeshProUGUI>();
            if (buttonText == null)
            {
                // Create text if it doesn't exist
                GameObject textGO = new GameObject("ButtonText");
                textGO.transform.SetParent(transform, false);
                buttonText = textGO.AddComponent<TextMeshProUGUI>();
                buttonText.text = "Transition";
                buttonText.color = Color.white;
                buttonText.fontSize = 24;
                buttonText.alignment = TextAlignmentOptions.Center;
                buttonText.fontStyle = FontStyles.Bold;
                
                RectTransform textRect = buttonText.rectTransform;
                textRect.anchorMin = Vector2.zero;
                textRect.anchorMax = Vector2.one;
                textRect.sizeDelta = Vector2.zero;
                textRect.anchoredPosition = Vector2.zero;
            }
            
            // Store original values
            originalScale = transform.localScale;
            originalColor = buttonImage.color;
        }
        
        private void SetupButton()
        {
            // Remove existing listeners to avoid duplicates
            button.onClick.RemoveAllListeners();
            
            // Add our transition listener
            button.onClick.AddListener(OnButtonClick);
            
            // Setup button appearance
            if (buttonImage != null)
            {
                buttonImage.color = originalColor;
            }
            
            transform.localScale = originalScale;
        }
        
        private void ValidateConfiguration()
        {
            if (string.IsNullOrEmpty(transitionSettings.targetSceneName))
            {
                Debug.LogWarning($"SceneTransitionButton on {gameObject.name} has no target scene name set!");
                return;
            }
            
            if (validateSceneExists)
            {
                // Check if scene exists in build settings
                bool sceneExists = false;
                for (int i = 0; i < UnityEngine.SceneManagement.SceneManager.sceneCountInBuildSettings; i++)
                {
                    string scenePath = UnityEngine.SceneManagement.SceneUtility.GetScenePathByBuildIndex(i);
                    string sceneName = System.IO.Path.GetFileNameWithoutExtension(scenePath);
                    if (sceneName == transitionSettings.targetSceneName)
                    {
                        sceneExists = true;
                        break;
                    }
                }
                
                if (!sceneExists)
                {
                    Debug.LogError($"Scene '{transitionSettings.targetSceneName}' not found in build settings! Please add it to Build Settings > Scenes In Build.");
                }
            }
            
            if (showDebugInfo)
            {
                Debug.Log($"SceneTransitionButton configured: {gameObject.name} -> {transitionSettings.targetSceneName}");
            }
        }
        
        private void OnButtonClick()
        {
            if (isTransitioning)
            {
                if (showDebugInfo)
                    Debug.Log("Transition already in progress, ignoring click.");
                return;
            }
            
            if (string.IsNullOrEmpty(transitionSettings.targetSceneName))
            {
                Debug.LogError($"Cannot transition: No target scene name set on {gameObject.name}");
                return;
            }
            
            // Play click sound
            if (enableButtonAudio && buttonClickSound != null)
                audioSource.PlayOneShot(buttonClickSound);
            
            // Start transition
            StartTransition();
        }
        
        private void StartTransition()
        {
            isTransitioning = true;
            OnTransitionStarted?.Invoke(this);
            
            // Apply custom settings to transition manager
            ApplyCustomSettings();
            
            // Start the transition
            SceneTransitionManager.Instance.TransitionToScene(transitionSettings.targetSceneName);
            
            if (showDebugInfo)
                Debug.Log($"Starting transition from {gameObject.name} to {transitionSettings.targetSceneName}");
        }
        
        private void ApplyCustomSettings()
        {
            SceneTransitionManager manager = SceneTransitionManager.Instance;
            
            // Apply custom colors
            if (transitionSettings.customLoadingBarColor != new Color(0.8f, 0.4f, 0.9f, 1f))
                manager.SetLoadingBarColor(transitionSettings.customLoadingBarColor);
            
            if (transitionSettings.customTextColor != Color.white)
                manager.SetTextColor(transitionSettings.customTextColor);
            
            // Apply custom timing
            if (transitionSettings.customFadeInDuration > 0f || 
                transitionSettings.customFadeOutDuration > 0f || 
                transitionSettings.customLoadingDuration > 0f)
            {
                manager.SetTransitionDuration(
                    transitionSettings.customFadeInDuration > 0f ? transitionSettings.customFadeInDuration : 1.5f,
                    transitionSettings.customFadeOutDuration > 0f ? transitionSettings.customFadeOutDuration : 1.5f,
                    transitionSettings.customLoadingDuration > 0f ? transitionSettings.customLoadingDuration : 3f
                );
            }
            
            // Apply custom quote
            if (!string.IsNullOrEmpty(transitionSettings.customQuote))
            {
                manager.AddCustomQuote(transitionSettings.customQuote);
            }
        }
        
        private void OnGlobalTransitionStarted()
        {
            // This is called when any transition starts
            if (isTransitioning)
            {
                // Disable button during transition
                button.interactable = false;
                
                // Visual feedback
                if (buttonImage != null)
                {
                    Color disabledColor = originalColor;
                    disabledColor.a = 0.5f;
                    buttonImage.color = disabledColor;
                }
            }
        }
        
        private void OnGlobalTransitionCompleted()
        {
            // This is called when any transition completes
            if (isTransitioning)
            {
                isTransitioning = false;
                OnTransitionCompleted?.Invoke(this);
                
                // Re-enable button
                button.interactable = true;
                
                // Restore visual state
                if (buttonImage != null)
                    buttonImage.color = originalColor;
                
                transform.localScale = originalScale;
            }
        }
        
        public void OnPointerClick(PointerEventData eventData)
        {
            // This is called by the EventSystem when the button is clicked
            // The Button component will handle the actual click logic
        }
        
        public void OnPointerEnter(PointerEventData eventData)
        {
            if (!enableButtonHoverEffect || isTransitioning) return;
            
            isHovering = true;
            
            // Play hover sound
            if (enableButtonAudio && buttonHoverSound != null)
                audioSource.PlayOneShot(buttonHoverSound);
            
            // Start hover animation
            StartCoroutine(HoverAnimation(true));
        }
        
        public void OnPointerExit(PointerEventData eventData)
        {
            if (!enableButtonHoverEffect || isTransitioning) return;
            
            isHovering = false;
            
            // Start exit animation
            StartCoroutine(HoverAnimation(false));
        }
        
        private System.Collections.IEnumerator HoverAnimation(bool isEntering)
        {
            Vector3 targetScale = isEntering ? originalScale * hoverScale : originalScale;
            Color targetColor = isEntering ? hoverColor : originalColor;
            
            Vector3 startScale = transform.localScale;
            Color startColor = buttonImage != null ? buttonImage.color : originalColor;
            
            float elapsed = 0f;
            while (elapsed < 1f / hoverTransitionSpeed)
            {
                elapsed += Time.deltaTime;
                float progress = elapsed * hoverTransitionSpeed;
                
                transform.localScale = Vector3.Lerp(startScale, targetScale, progress);
                if (buttonImage != null)
                    buttonImage.color = Color.Lerp(startColor, targetColor, progress);
                
                yield return null;
            }
            
            transform.localScale = targetScale;
            if (buttonImage != null)
                buttonImage.color = targetColor;
        }
        
        // Public methods for runtime configuration
        public void SetTargetScene(string sceneName)
        {
            transitionSettings.targetSceneName = sceneName;
            ValidateConfiguration();
        }
        
        public void SetCustomColors(Color loadingBarColor, Color textColor, Color fadeColor)
        {
            transitionSettings.customLoadingBarColor = loadingBarColor;
            transitionSettings.customTextColor = textColor;
            transitionSettings.customFadeColor = fadeColor;
        }
        
        public void SetCustomTiming(float fadeIn, float fadeOut, float loading)
        {
            transitionSettings.customFadeInDuration = fadeIn;
            transitionSettings.customFadeOutDuration = fadeOut;
            transitionSettings.customLoadingDuration = loading;
        }
        
        public void SetCustomAudio(AudioClip fadeIn, AudioClip fadeOut, AudioClip complete)
        {
            transitionSettings.customFadeInSound = fadeIn;
            transitionSettings.customFadeOutSound = fadeOut;
            transitionSettings.customLoadingCompleteSound = complete;
        }
        
        public void SetCustomQuote(string quote, bool useOnlyCustom = false)
        {
            transitionSettings.customQuote = quote;
            transitionSettings.useOnlyCustomQuote = useOnlyCustom;
        }
        
        public void EnableSpecialEffects(bool screenShake, bool glitch, bool particles)
        {
            transitionSettings.enableScreenShake = screenShake;
            transitionSettings.enableGlitchEffect = glitch;
            transitionSettings.enableParticleEffects = particles;
        }
        
        // Validation methods
        public bool IsValidConfiguration()
        {
            return !string.IsNullOrEmpty(transitionSettings.targetSceneName);
        }
        
        public string GetTargetSceneName()
        {
            return transitionSettings.targetSceneName;
        }
        
        public bool IsTransitioning()
        {
            return isTransitioning;
        }
        
        // Editor helper methods
        #if UNITY_EDITOR
        [ContextMenu("Validate Configuration")]
        private void ValidateConfigurationEditor()
        {
            ValidateConfiguration();
        }
        
        [ContextMenu("Test Transition (Editor Only)")]
        private void TestTransitionEditor()
        {
            if (Application.isPlaying)
            {
                OnButtonClick();
            }
            else
            {
                Debug.Log("Test transition can only be run in Play mode.");
            }
        }
        #endif
    }
}