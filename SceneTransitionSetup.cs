using UnityEngine;
using UnityEngine.UI;
using TMPro;
using DarkFantasyTransitions;

namespace DarkFantasyTransitions
{
    /// <summary>
    /// Utility class for setting up scene transitions in the editor
    /// </summary>
    public static class SceneTransitionSetup
    {
        [MenuItem("Dark Fantasy/Setup Scene Transition System")]
        public static void SetupSceneTransitionSystem()
        {
            // Create the transition manager if it doesn't exist
            SceneTransitionManager manager = Object.FindObjectOfType<SceneTransitionManager>();
            if (manager == null)
            {
                GameObject managerGO = new GameObject("SceneTransitionManager");
                manager = managerGO.AddComponent<SceneTransitionManager>();
                Debug.Log("Created SceneTransitionManager");
            }
            
            // Create a sample transition button
            CreateSampleTransitionButton();
            
            // Create transition UI prefab
            CreateTransitionUIPrefab();
            
            Debug.Log("Scene Transition System setup complete!");
        }
        
        [MenuItem("Dark Fantasy/Create Transition Button")]
        public static void CreateSampleTransitionButton()
        {
            // Create button GameObject
            GameObject buttonGO = new GameObject("Transition Button");
            
            // Add RectTransform
            RectTransform rectTransform = buttonGO.AddComponent<RectTransform>();
            rectTransform.sizeDelta = new Vector2(200, 60);
            rectTransform.anchoredPosition = Vector2.zero;
            
            // Add Image component
            Image buttonImage = buttonGO.AddComponent<Image>();
            buttonImage.color = new Color(0.2f, 0.1f, 0.3f, 0.9f);
            
            // Add Button component
            Button button = buttonGO.AddComponent<Button>();
            
            // Add SceneTransitionButton component
            SceneTransitionButton transitionButton = buttonGO.AddComponent<SceneTransitionButton>();
            
            // Create text child
            GameObject textGO = new GameObject("Text");
            textGO.transform.SetParent(buttonGO.transform, false);
            
            RectTransform textRect = textGO.AddComponent<RectTransform>();
            textRect.anchorMin = Vector2.zero;
            textRect.anchorMax = Vector2.one;
            textRect.sizeDelta = Vector2.zero;
            textRect.anchoredPosition = Vector2.zero;
            
            TextMeshProUGUI text = textGO.AddComponent<TextMeshProUGUI>();
            text.text = "Start Game";
            text.color = Color.white;
            text.fontSize = 24;
            text.alignment = TextAlignmentOptions.Center;
            text.fontStyle = FontStyles.Bold;
            
            // Set default transition settings
            transitionButton.SetTargetScene("MainMenu"); // Change this to your actual scene name
            
            Debug.Log("Created sample transition button: " + buttonGO.name);
        }
        
        [MenuItem("Dark Fantasy/Create Transition UI Prefab")]
        public static void CreateTransitionUIPrefab()
        {
            // Create canvas for transition UI
            GameObject canvasGO = new GameObject("TransitionCanvas");
            Canvas canvas = canvasGO.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 1000;
            
            CanvasScaler scaler = canvasGO.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1080, 1920);
            scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.MatchWidthOrHeight;
            scaler.matchWidthOrHeight = 0.5f;
            
            canvasGO.AddComponent<GraphicRaycaster>();
            
            // Create fade overlay
            GameObject fadeGO = new GameObject("FadeOverlay");
            fadeGO.transform.SetParent(canvasGO.transform, false);
            Image fadeImage = fadeGO.AddComponent<Image>();
            fadeImage.color = Color.black;
            
            RectTransform fadeRect = fadeImage.rectTransform;
            fadeRect.anchorMin = Vector2.zero;
            fadeRect.anchorMax = Vector2.one;
            fadeRect.sizeDelta = Vector2.zero;
            fadeRect.anchoredPosition = Vector2.zero;
            
            // Create loading container
            GameObject containerGO = new GameObject("LoadingContainer");
            containerGO.transform.SetParent(canvasGO.transform, false);
            
            RectTransform containerRect = containerGO.AddComponent<RectTransform>();
            containerRect.anchorMin = new Vector2(0.1f, 0.3f);
            containerRect.anchorMax = new Vector2(0.9f, 0.7f);
            containerRect.sizeDelta = Vector2.zero;
            containerRect.anchoredPosition = Vector2.zero;
            
            // Create loading bar background
            GameObject bgGO = new GameObject("LoadingBarBackground");
            bgGO.transform.SetParent(containerGO.transform, false);
            Image bgImage = bgGO.AddComponent<Image>();
            bgImage.color = new Color(0.1f, 0.1f, 0.1f, 0.8f);
            
            RectTransform bgRect = bgImage.rectTransform;
            bgRect.anchorMin = new Vector2(0.1f, 0.4f);
            bgRect.anchorMax = new Vector2(0.9f, 0.6f);
            bgRect.sizeDelta = Vector2.zero;
            bgRect.anchoredPosition = Vector2.zero;
            
            // Create loading bar fill
            GameObject fillGO = new GameObject("LoadingBarFill");
            fillGO.transform.SetParent(bgGO.transform, false);
            Image fillImage = fillGO.AddComponent<Image>();
            fillImage.color = new Color(0.8f, 0.4f, 0.9f, 1f);
            fillImage.type = Image.Type.Filled;
            fillImage.fillMethod = Image.FillMethod.Horizontal;
            
            RectTransform fillRect = fillImage.rectTransform;
            fillRect.anchorMin = Vector2.zero;
            fillRect.anchorMax = Vector2.one;
            fillRect.sizeDelta = Vector2.zero;
            fillRect.anchoredPosition = Vector2.zero;
            
            // Create loading bar glow
            GameObject glowGO = new GameObject("LoadingBarGlow");
            glowGO.transform.SetParent(fillGO.transform, false);
            Image glowImage = glowGO.AddComponent<Image>();
            glowImage.color = new Color(1f, 0.6f, 1f, 1f);
            glowImage.type = Image.Type.Filled;
            glowImage.fillMethod = Image.FillMethod.Horizontal;
            
            RectTransform glowRect = glowImage.rectTransform;
            glowRect.anchorMin = Vector2.zero;
            glowRect.anchorMax = Vector2.one;
            glowRect.sizeDelta = Vector2.zero;
            glowRect.anchoredPosition = Vector2.zero;
            
            // Create loading text
            GameObject textGO = new GameObject("LoadingText");
            textGO.transform.SetParent(containerGO.transform, false);
            TextMeshProUGUI loadingText = textGO.AddComponent<TextMeshProUGUI>();
            loadingText.text = "Loading 0%";
            loadingText.color = Color.white;
            loadingText.fontSize = 32;
            loadingText.alignment = TextAlignmentOptions.Center;
            loadingText.fontStyle = FontStyles.Bold;
            
            RectTransform textRect = loadingText.rectTransform;
            textRect.anchorMin = new Vector2(0.1f, 0.7f);
            textRect.anchorMax = new Vector2(0.9f, 0.9f);
            textRect.sizeDelta = Vector2.zero;
            textRect.anchoredPosition = Vector2.zero;
            
            // Create quote text
            GameObject quoteGO = new GameObject("QuoteText");
            quoteGO.transform.SetParent(containerGO.transform, false);
            TextMeshProUGUI quoteText = quoteGO.AddComponent<TextMeshProUGUI>();
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
            
            Debug.Log("Created transition UI prefab: " + canvasGO.name);
        }
        
        [MenuItem("Dark Fantasy/Setup Dark Fantasy Theme")]
        public static void SetupDarkFantasyTheme()
        {
            SceneTransitionManager manager = Object.FindObjectOfType<SceneTransitionManager>();
            if (manager == null)
            {
                Debug.LogWarning("SceneTransitionManager not found. Please setup the transition system first.");
                return;
            }
            
            // Apply dark fantasy theme
            manager.SetLoadingBarColor(new Color(0.6f, 0.2f, 0.8f, 1f));
            manager.SetTextColor(new Color(0.9f, 0.8f, 1f, 1f));
            
            Debug.Log("Applied Dark Fantasy theme to SceneTransitionManager");
        }
        
        [MenuItem("Dark Fantasy/Add Sample Quotes")]
        public static void AddSampleQuotes()
        {
            SceneTransitionManager manager = Object.FindObjectOfType<SceneTransitionManager>();
            if (manager == null)
            {
                Debug.LogWarning("SceneTransitionManager not found. Please setup the transition system first.");
                return;
            }
            
            // Add additional dark fantasy quotes
            string[] additionalQuotes = {
                "The ancient magic stirs in the shadows...",
                "Through the veil of night, power awakens...",
                "In the realm of shadows, heroes rise...",
                "The eternal dance of light and dark...",
                "Where nightmares dwell, courage is tested...",
                "In the depths of darkness, hope flickers...",
                "The ancient magic stirs in the shadows...",
                "Through the mist of time, legends emerge...",
                "In the shadows, legends are born...",
                "The darkness holds ancient secrets..."
            };
            
            foreach (string quote in additionalQuotes)
            {
                manager.AddCustomQuote(quote);
            }
            
            Debug.Log("Added sample dark fantasy quotes to SceneTransitionManager");
        }
    }
}