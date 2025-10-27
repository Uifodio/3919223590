using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;
using TMPro;
using System;

namespace DarkFantasyTransitions
{
    public class SceneTransitionManager : MonoBehaviour
    {
        [Header("Transition Settings")]
        [SerializeField] private float fadeInDuration = 1.5f;
        [SerializeField] private float fadeOutDuration = 1.5f;
        [SerializeField] private float loadingDuration = 3f;
        [SerializeField] private AnimationCurve fadeCurve = AnimationCurve.EaseInOut(0, 0, 1, 1);
        
        [Header("Loading Bar Settings")]
        [SerializeField] private float loadingBarSpeed = 0.8f;
        [SerializeField] private float pulseIntensity = 0.3f;
        [SerializeField] private float pulseSpeed = 2f;
        [SerializeField] private Color loadingBarColor = new Color(0.8f, 0.4f, 0.9f, 1f);
        [SerializeField] private Color loadingBarGlowColor = new Color(1f, 0.6f, 1f, 1f);
        
        [Header("Text Settings")]
        [SerializeField] private string loadingTextPrefix = "Loading";
        [SerializeField] private string loadingTextSuffix = "%";
        [SerializeField] private float textUpdateInterval = 0.05f;
        [SerializeField] private Color textColor = Color.white;
        [SerializeField] private Color textGlowColor = new Color(0.9f, 0.7f, 1f, 1f);
        
        [Header("Quote System")]
        [SerializeField] private bool enableQuotes = true;
        [SerializeField] private float quoteDisplayDuration = 2f;
        [SerializeField] private float quoteFadeDuration = 0.5f;
        [SerializeField] private List<string> darkFantasyQuotes = new List<string>
        {
            "In the shadows, legends are born...",
            "The darkness holds ancient secrets...",
            "Where light fades, magic begins...",
            "Through the veil of night, power awakens...",
            "In the realm of shadows, heroes rise...",
            "The eternal dance of light and dark...",
            "Where nightmares dwell, courage is tested...",
            "In the depths of darkness, hope flickers...",
            "The ancient magic stirs in the shadows...",
            "Through the mist of time, legends emerge..."
        };
        
        [Header("UI References")]
        [SerializeField] private Canvas transitionCanvas;
        [SerializeField] private Image fadeOverlay;
        [SerializeField] private Image loadingBarBackground;
        [SerializeField] private Image loadingBarFill;
        [SerializeField] private Image loadingBarGlow;
        [SerializeField] private TextMeshProUGUI loadingText;
        [SerializeField] private TextMeshProUGUI quoteText;
        [SerializeField] private GameObject loadingContainer;
        
        [Header("Audio Settings")]
        [SerializeField] private bool enableAudio = true;
        [SerializeField] private AudioClip fadeInSound;
        [SerializeField] private AudioClip fadeOutSound;
        [SerializeField] private AudioClip loadingCompleteSound;
        [SerializeField] private float audioVolume = 0.7f;
        
        [Header("Advanced Effects")]
        [SerializeField] private bool enableParticleEffects = true;
        [SerializeField] private ParticleSystem backgroundParticles;
        [SerializeField] private bool enableScreenShake = false;
        [SerializeField] private float shakeIntensity = 0.1f;
        [SerializeField] private bool enableGlitchEffect = false;
        [SerializeField] private float glitchIntensity = 0.05f;
        
        // Private variables
        private static SceneTransitionManager instance;
        private AudioSource audioSource;
        private Camera mainCamera;
        private Vector3 originalCameraPosition;
        private bool isTransitioning = false;
        private Coroutine currentTransition;
        private int currentQuoteIndex = 0;
        
        // Events
        public static event Action OnTransitionStarted;
        public static event Action OnTransitionCompleted;
        public static event Action<float> OnLoadingProgress;
        
        public static SceneTransitionManager Instance
        {
            get
            {
                if (instance == null)
                {
                    instance = FindObjectOfType<SceneTransitionManager>();
                    if (instance == null)
                    {
                        GameObject go = new GameObject("SceneTransitionManager");
                        instance = go.AddComponent<SceneTransitionManager>();
                        DontDestroyOnLoad(go);
                    }
                }
                return instance;
            }
        }
        
        private void Awake()
        {
            if (instance == null)
            {
                instance = this;
                DontDestroyOnLoad(gameObject);
                InitializeComponents();
            }
            else if (instance != this)
            {
                Destroy(gameObject);
            }
        }
        
        private void InitializeComponents()
        {
            // Get or create audio source
            audioSource = GetComponent<AudioSource>();
            if (audioSource == null)
                audioSource = gameObject.AddComponent<AudioSource>();
            
            audioSource.volume = audioVolume;
            audioSource.playOnAwake = false;
            
            // Get main camera
            mainCamera = Camera.main;
            if (mainCamera != null)
                originalCameraPosition = mainCamera.transform.position;
            
            // Setup canvas
            if (transitionCanvas == null)
            {
                GameObject canvasGO = new GameObject("TransitionCanvas");
                transitionCanvas = canvasGO.AddComponent<Canvas>();
                transitionCanvas.renderMode = RenderMode.ScreenSpaceOverlay;
                transitionCanvas.sortingOrder = 1000;
                
                CanvasScaler scaler = canvasGO.AddComponent<CanvasScaler>();
                scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
                scaler.referenceResolution = new Vector2(1080, 1920);
                scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.MatchWidthOrHeight;
                scaler.matchWidthOrHeight = 0.5f;
                
                canvasGO.AddComponent<GraphicRaycaster>();
                DontDestroyOnLoad(canvasGO);
            }
            
            CreateTransitionUI();
            SetupResponsiveDesign();
        }
        
        private void CreateTransitionUI()
        {
            // Create fade overlay
            if (fadeOverlay == null)
            {
                GameObject fadeGO = new GameObject("FadeOverlay");
                fadeGO.transform.SetParent(transitionCanvas.transform, false);
                fadeOverlay = fadeGO.AddComponent<Image>();
                fadeOverlay.color = Color.black;
                
                RectTransform fadeRect = fadeOverlay.rectTransform;
                fadeRect.anchorMin = Vector2.zero;
                fadeRect.anchorMax = Vector2.one;
                fadeRect.sizeDelta = Vector2.zero;
                fadeRect.anchoredPosition = Vector2.zero;
            }
            
            // Create loading container
            if (loadingContainer == null)
            {
                GameObject containerGO = new GameObject("LoadingContainer");
                containerGO.transform.SetParent(transitionCanvas.transform, false);
                loadingContainer = containerGO;
                
                RectTransform containerRect = containerGO.AddComponent<RectTransform>();
                containerRect.anchorMin = new Vector2(0.1f, 0.3f);
                containerRect.anchorMax = new Vector2(0.9f, 0.7f);
                containerRect.sizeDelta = Vector2.zero;
                containerRect.anchoredPosition = Vector2.zero;
            }
            
            // Create loading bar background
            if (loadingBarBackground == null)
            {
                GameObject bgGO = new GameObject("LoadingBarBackground");
                bgGO.transform.SetParent(loadingContainer.transform, false);
                loadingBarBackground = bgGO.AddComponent<Image>();
                loadingBarBackground.color = new Color(0.1f, 0.1f, 0.1f, 0.8f);
                
                RectTransform bgRect = loadingBarBackground.rectTransform;
                bgRect.anchorMin = new Vector2(0.1f, 0.4f);
                bgRect.anchorMax = new Vector2(0.9f, 0.6f);
                bgRect.sizeDelta = Vector2.zero;
                bgRect.anchoredPosition = Vector2.zero;
            }
            
            // Create loading bar fill
            if (loadingBarFill == null)
            {
                GameObject fillGO = new GameObject("LoadingBarFill");
                fillGO.transform.SetParent(loadingBarBackground.transform, false);
                loadingBarFill = fillGO.AddComponent<Image>();
                loadingBarFill.color = loadingBarColor;
                loadingBarFill.type = Image.Type.Filled;
                loadingBarFill.fillMethod = Image.FillMethod.Horizontal;
                
                RectTransform fillRect = loadingBarFill.rectTransform;
                fillRect.anchorMin = Vector2.zero;
                fillRect.anchorMax = Vector2.one;
                fillRect.sizeDelta = Vector2.zero;
                fillRect.anchoredPosition = Vector2.zero;
            }
            
            // Create loading bar glow
            if (loadingBarGlow == null)
            {
                GameObject glowGO = new GameObject("LoadingBarGlow");
                glowGO.transform.SetParent(loadingBarFill.transform, false);
                loadingBarGlow = glowGO.AddComponent<Image>();
                loadingBarGlow.color = loadingBarGlowColor;
                loadingBarGlow.type = Image.Type.Filled;
                loadingBarGlow.fillMethod = Image.FillMethod.Horizontal;
                
                RectTransform glowRect = loadingBarGlow.rectTransform;
                glowRect.anchorMin = Vector2.zero;
                glowRect.anchorMax = Vector2.one;
                glowRect.sizeDelta = Vector2.zero;
                glowRect.anchoredPosition = Vector2.zero;
            }
            
            // Create loading text
            if (loadingText == null)
            {
                GameObject textGO = new GameObject("LoadingText");
                textGO.transform.SetParent(loadingContainer.transform, false);
                loadingText = textGO.AddComponent<TextMeshProUGUI>();
                loadingText.text = "Loading 0%";
                loadingText.color = textColor;
                loadingText.fontSize = 32;
                loadingText.alignment = TextAlignmentOptions.Center;
                loadingText.fontStyle = FontStyles.Bold;
                
                // Add glow effect
                loadingText.fontSharedMaterial = new Material(Shader.Find("TextMeshPro/Distance Field"));
                loadingText.fontSharedMaterial.SetFloat("_GlowPower", 0.5f);
                loadingText.fontSharedMaterial.SetColor("_GlowColor", textGlowColor);
                
                RectTransform textRect = loadingText.rectTransform;
                textRect.anchorMin = new Vector2(0.1f, 0.7f);
                textRect.anchorMax = new Vector2(0.9f, 0.9f);
                textRect.sizeDelta = Vector2.zero;
                textRect.anchoredPosition = Vector2.zero;
            }
            
            // Create quote text
            if (quoteText == null && enableQuotes)
            {
                GameObject quoteGO = new GameObject("QuoteText");
                quoteGO.transform.SetParent(loadingContainer.transform, false);
                quoteText = quoteGO.AddComponent<TextMeshProUGUI>();
                quoteText.text = "";
                quoteText.color = new Color(0.8f, 0.8f, 0.8f, 0.8f);
                quoteText.fontSize = 18;
                quoteText.alignment = TextAlignmentOptions.Center;
                quoteText.fontStyle = FontStyles.Italic;
                
                RectTransform quoteRect = quoteText.rectTransform;
                quoteRect.anchorMin = new Vector2(0.1f, 0.1f);
                quoteRect.anchorMax = new Vector2(0.9f, 0.3f);
                quoteRect.sizeDelta = Vector2.zero;
                quoteRect.anchoredPosition = Vector2.zero;
            }
            
            // Hide UI initially
            SetUIAlpha(0f);
        }
        
        private void SetupResponsiveDesign()
        {
            if (transitionCanvas == null) return;
            
            CanvasScaler scaler = transitionCanvas.GetComponent<CanvasScaler>();
            if (scaler == null) return;
            
            // Detect orientation and adjust
            if (Screen.width > Screen.height)
            {
                // Landscape
                scaler.referenceResolution = new Vector2(1920, 1080);
                scaler.matchWidthOrHeight = 0f;
            }
            else
            {
                // Portrait
                scaler.referenceResolution = new Vector2(1080, 1920);
                scaler.matchWidthOrHeight = 0.5f;
            }
        }
        
        public void TransitionToScene(string sceneName)
        {
            if (isTransitioning) return;
            
            if (currentTransition != null)
                StopCoroutine(currentTransition);
            
            currentTransition = StartCoroutine(TransitionCoroutine(sceneName));
        }
        
        private IEnumerator TransitionCoroutine(string sceneName)
        {
            isTransitioning = true;
            OnTransitionStarted?.Invoke();
            
            // Setup UI
            SetupResponsiveDesign();
            SetUIAlpha(0f);
            loadingBarFill.fillAmount = 0f;
            loadingBarGlow.fillAmount = 0f;
            
            // Fade in
            yield return StartCoroutine(FadeIn());
            
            // Start loading
            yield return StartCoroutine(LoadSceneAsync(sceneName));
            
            // Fade out
            yield return StartCoroutine(FadeOut());
            
            isTransitioning = false;
            OnTransitionCompleted?.Invoke();
        }
        
        private IEnumerator FadeIn()
        {
            if (enableAudio && fadeInSound != null)
                audioSource.PlayOneShot(fadeInSound);
            
            float elapsed = 0f;
            while (elapsed < fadeInDuration)
            {
                elapsed += Time.deltaTime;
                float progress = elapsed / fadeInDuration;
                float alpha = fadeCurve.Evaluate(progress);
                
                SetUIAlpha(alpha);
                
                if (enableScreenShake)
                    ApplyScreenShake(progress);
                
                yield return null;
            }
            
            SetUIAlpha(1f);
        }
        
        private IEnumerator FadeOut()
        {
            if (enableAudio && fadeOutSound != null)
                audioSource.PlayOneShot(fadeOutSound);
            
            float elapsed = 0f;
            while (elapsed < fadeOutDuration)
            {
                elapsed += Time.deltaTime;
                float progress = elapsed / fadeOutDuration;
                float alpha = fadeCurve.Evaluate(1f - progress);
                
                SetUIAlpha(alpha);
                
                if (enableScreenShake)
                    ApplyScreenShake(progress);
                
                yield return null;
            }
            
            SetUIAlpha(0f);
        }
        
        private IEnumerator LoadSceneAsync(string sceneName)
        {
            AsyncOperation asyncLoad = SceneManager.LoadSceneAsync(sceneName);
            asyncLoad.allowSceneActivation = false;
            
            float loadingProgress = 0f;
            float elapsed = 0f;
            
            // Start quote rotation
            if (enableQuotes)
                StartCoroutine(RotateQuotes());
            
            while (loadingProgress < 1f)
            {
                elapsed += Time.deltaTime;
                float targetProgress = Mathf.Clamp01(asyncLoad.progress / 0.9f);
                loadingProgress = Mathf.MoveTowards(loadingProgress, targetProgress, loadingBarSpeed * Time.deltaTime);
                
                // Update UI
                UpdateLoadingUI(loadingProgress);
                OnLoadingProgress?.Invoke(loadingProgress);
                
                // Apply effects
                if (enableParticleEffects && backgroundParticles != null)
                    backgroundParticles.startSpeed = loadingProgress * 10f;
                
                if (enableGlitchEffect)
                    ApplyGlitchEffect(loadingProgress);
                
                yield return null;
            }
            
            // Pulse effect when complete
            if (enableAudio && loadingCompleteSound != null)
                audioSource.PlayOneShot(loadingCompleteSound);
            
            yield return StartCoroutine(PulseEffect());
            
            // Allow scene activation
            asyncLoad.allowSceneActivation = true;
            
            // Wait for scene to fully load
            while (!asyncLoad.isDone)
            {
                yield return null;
            }
        }
        
        private void UpdateLoadingUI(float progress)
        {
            // Update loading bar
            loadingBarFill.fillAmount = progress;
            loadingBarGlow.fillAmount = progress;
            
            // Update text
            int percentage = Mathf.RoundToInt(progress * 100f);
            loadingText.text = $"{loadingTextPrefix} {percentage}{loadingTextSuffix}";
            
            // Update colors based on progress
            Color currentColor = Color.Lerp(loadingBarColor, loadingBarGlowColor, progress);
            loadingBarFill.color = currentColor;
        }
        
        private IEnumerator PulseEffect()
        {
            float elapsed = 0f;
            Vector3 originalScale = loadingBarFill.transform.localScale;
            
            while (elapsed < 1f)
            {
                elapsed += Time.deltaTime * pulseSpeed;
                float pulse = 1f + Mathf.Sin(elapsed * Mathf.PI * 2f) * pulseIntensity;
                loadingBarFill.transform.localScale = originalScale * pulse;
                loadingBarGlow.transform.localScale = originalScale * pulse;
                
                yield return null;
            }
            
            loadingBarFill.transform.localScale = originalScale;
            loadingBarGlow.transform.localScale = originalScale;
        }
        
        private IEnumerator RotateQuotes()
        {
            if (!enableQuotes || quoteText == null || darkFantasyQuotes.Count == 0)
                yield break;
            
            while (isTransitioning)
            {
                // Fade out current quote
                yield return StartCoroutine(FadeQuote(0f, quoteFadeDuration));
                
                // Set new quote
                quoteText.text = darkFantasyQuotes[currentQuoteIndex];
                currentQuoteIndex = (currentQuoteIndex + 1) % darkFantasyQuotes.Count;
                
                // Fade in new quote
                yield return StartCoroutine(FadeQuote(1f, quoteFadeDuration));
                
                // Display quote
                yield return new WaitForSeconds(quoteDisplayDuration);
            }
        }
        
        private IEnumerator FadeQuote(float targetAlpha, float duration)
        {
            Color startColor = quoteText.color;
            Color targetColor = new Color(startColor.r, startColor.g, startColor.b, targetAlpha);
            
            float elapsed = 0f;
            while (elapsed < duration)
            {
                elapsed += Time.deltaTime;
                float progress = elapsed / duration;
                quoteText.color = Color.Lerp(startColor, targetColor, progress);
                yield return null;
            }
            
            quoteText.color = targetColor;
        }
        
        private void SetUIAlpha(float alpha)
        {
            if (fadeOverlay != null)
            {
                Color color = fadeOverlay.color;
                color.a = alpha;
                fadeOverlay.color = color;
            }
            
            if (loadingContainer != null)
            {
                CanvasGroup canvasGroup = loadingContainer.GetComponent<CanvasGroup>();
                if (canvasGroup == null)
                    canvasGroup = loadingContainer.AddComponent<CanvasGroup>();
                
                canvasGroup.alpha = alpha;
            }
        }
        
        private void ApplyScreenShake(float intensity)
        {
            if (mainCamera == null) return;
            
            Vector3 shakeOffset = new Vector3(
                UnityEngine.Random.Range(-shakeIntensity, shakeIntensity),
                UnityEngine.Random.Range(-shakeIntensity, shakeIntensity),
                0f
            ) * intensity;
            
            mainCamera.transform.position = originalCameraPosition + shakeOffset;
        }
        
        private void ApplyGlitchEffect(float intensity)
        {
            if (loadingText == null) return;
            
            // Simple glitch effect by slightly offsetting text
            Vector3 glitchOffset = new Vector3(
                UnityEngine.Random.Range(-glitchIntensity, glitchIntensity),
                UnityEngine.Random.Range(-glitchIntensity, glitchIntensity),
                0f
            ) * intensity;
            
            loadingText.transform.localPosition = glitchOffset;
        }
        
        private void OnDestroy()
        {
            if (instance == this)
                instance = null;
        }
        
        // Public methods for customization
        public void SetLoadingBarColor(Color color)
        {
            loadingBarColor = color;
            if (loadingBarFill != null)
                loadingBarFill.color = color;
        }
        
        public void SetTextColor(Color color)
        {
            textColor = color;
            if (loadingText != null)
                loadingText.color = color;
        }
        
        public void AddCustomQuote(string quote)
        {
            if (!darkFantasyQuotes.Contains(quote))
                darkFantasyQuotes.Add(quote);
        }
        
        public void SetTransitionDuration(float fadeIn, float fadeOut, float loading)
        {
            fadeInDuration = fadeIn;
            fadeOutDuration = fadeOut;
            loadingDuration = loading;
        }
    }
}