using UnityEngine;
using UnityEditor;
using DarkFantasyTransitions;

namespace DarkFantasyTransitions.Editor
{
    [CustomEditor(typeof(SceneTransitionButton))]
    public class SceneTransitionButtonEditor : UnityEditor.Editor
    {
        private SerializedProperty transitionSettings;
        private SerializedProperty enableButtonHoverEffect;
        private SerializedProperty hoverColor;
        private SerializedProperty hoverScale;
        private SerializedProperty hoverTransitionSpeed;
        private SerializedProperty enableButtonAudio;
        private SerializedProperty buttonClickSound;
        private SerializedProperty buttonHoverSound;
        private SerializedProperty buttonAudioVolume;
        private SerializedProperty validateSceneExists;
        private SerializedProperty showDebugInfo;
        
        private bool showTransitionSettings = true;
        private bool showButtonEffects = true;
        private bool showAudioSettings = true;
        private bool showValidation = true;
        private bool showAdvanced = false;
        
        private void OnEnable()
        {
            transitionSettings = serializedObject.FindProperty("transitionSettings");
            enableButtonHoverEffect = serializedObject.FindProperty("enableButtonHoverEffect");
            hoverColor = serializedObject.FindProperty("hoverColor");
            hoverScale = serializedObject.FindProperty("hoverScale");
            hoverTransitionSpeed = serializedObject.FindProperty("hoverTransitionSpeed");
            enableButtonAudio = serializedObject.FindProperty("enableButtonAudio");
            buttonClickSound = serializedObject.FindProperty("buttonClickSound");
            buttonHoverSound = serializedObject.FindProperty("buttonHoverSound");
            buttonAudioVolume = serializedObject.FindProperty("buttonAudioVolume");
            validateSceneExists = serializedObject.FindProperty("validateSceneExists");
            showDebugInfo = serializedObject.FindProperty("showDebugInfo");
        }
        
        public override void OnInspectorGUI()
        {
            serializedObject.Update();
            
            SceneTransitionButton button = (SceneTransitionButton)target;
            
            // Header
            EditorGUILayout.Space();
            EditorGUILayout.LabelField("Dark Fantasy Scene Transition", EditorStyles.boldLabel);
            EditorGUILayout.Space();
            
            // Validation status
            DrawValidationStatus(button);
            EditorGUILayout.Space();
            
            // Transition Settings
            showTransitionSettings = EditorGUILayout.Foldout(showTransitionSettings, "Transition Settings", true);
            if (showTransitionSettings)
            {
                EditorGUI.indentLevel++;
                DrawTransitionSettings();
                EditorGUI.indentLevel--;
            }
            
            EditorGUILayout.Space();
            
            // Button Effects
            showButtonEffects = EditorGUILayout.Foldout(showButtonEffects, "Button Visual Effects", true);
            if (showButtonEffects)
            {
                EditorGUI.indentLevel++;
                DrawButtonEffects();
                EditorGUI.indentLevel--;
            }
            
            EditorGUILayout.Space();
            
            // Audio Settings
            showAudioSettings = EditorGUILayout.Foldout(showAudioSettings, "Audio Settings", true);
            if (showAudioSettings)
            {
                EditorGUI.indentLevel++;
                DrawAudioSettings();
                EditorGUI.indentLevel--;
            }
            
            EditorGUILayout.Space();
            
            // Validation
            showValidation = EditorGUILayout.Foldout(showValidation, "Validation & Debug", true);
            if (showValidation)
            {
                EditorGUI.indentLevel++;
                DrawValidationSettings();
                EditorGUI.indentLevel--;
            }
            
            EditorGUILayout.Space();
            
            // Advanced
            showAdvanced = EditorGUILayout.Foldout(showAdvanced, "Advanced", true);
            if (showAdvanced)
            {
                EditorGUI.indentLevel++;
                DrawAdvancedSettings();
                EditorGUI.indentLevel--;
            }
            
            EditorGUILayout.Space();
            
            // Action Buttons
            DrawActionButtons(button);
            
            serializedObject.ApplyModifiedProperties();
        }
        
        private void DrawValidationStatus(SceneTransitionButton button)
        {
            EditorGUILayout.BeginHorizontal();
            
            bool isValid = button.IsValidConfiguration();
            string status = isValid ? "✓ Configuration Valid" : "⚠ Configuration Invalid";
            Color statusColor = isValid ? Color.green : Color.red;
            
            GUI.color = statusColor;
            EditorGUILayout.LabelField(status, EditorStyles.boldLabel);
            GUI.color = Color.white;
            
            EditorGUILayout.EndHorizontal();
            
            if (!isValid)
            {
                EditorGUILayout.HelpBox("Please set a target scene name in the Transition Settings.", MessageType.Warning);
            }
        }
        
        private void DrawTransitionSettings()
        {
            SerializedProperty targetScene = transitionSettings.FindPropertyRelative("targetSceneName");
            SerializedProperty customLoadingBarColor = transitionSettings.FindPropertyRelative("customLoadingBarColor");
            SerializedProperty customTextColor = transitionSettings.FindPropertyRelative("customTextColor");
            SerializedProperty customFadeColor = transitionSettings.FindPropertyRelative("customFadeColor");
            SerializedProperty customFadeInDuration = transitionSettings.FindPropertyRelative("customFadeInDuration");
            SerializedProperty customFadeOutDuration = transitionSettings.FindPropertyRelative("customFadeOutDuration");
            SerializedProperty customLoadingDuration = transitionSettings.FindPropertyRelative("customLoadingDuration");
            SerializedProperty customFadeInSound = transitionSettings.FindPropertyRelative("customFadeInSound");
            SerializedProperty customFadeOutSound = transitionSettings.FindPropertyRelative("customFadeOutSound");
            SerializedProperty customLoadingCompleteSound = transitionSettings.FindPropertyRelative("customLoadingCompleteSound");
            SerializedProperty enableScreenShake = transitionSettings.FindPropertyRelative("enableScreenShake");
            SerializedProperty enableGlitchEffect = transitionSettings.FindPropertyRelative("enableGlitchEffect");
            SerializedProperty enableParticleEffects = transitionSettings.FindPropertyRelative("enableParticleEffects");
            SerializedProperty customQuote = transitionSettings.FindPropertyRelative("customQuote");
            SerializedProperty useOnlyCustomQuote = transitionSettings.FindPropertyRelative("useOnlyCustomQuote");
            
            // Scene Name
            EditorGUILayout.PropertyField(targetScene, new GUIContent("Target Scene", "Name of the scene to transition to"));
            
            // Quick scene selection
            if (string.IsNullOrEmpty(targetScene.stringValue))
            {
                EditorGUILayout.BeginHorizontal();
                EditorGUILayout.LabelField("Quick Select:", GUILayout.Width(80));
                if (GUILayout.Button("Select Scene", GUILayout.Height(20)))
                {
                    ShowSceneSelectionMenu(targetScene);
                }
                EditorGUILayout.EndHorizontal();
            }
            
            EditorGUILayout.Space();
            
            // Visual Customization
            EditorGUILayout.LabelField("Visual Customization", EditorStyles.boldLabel);
            EditorGUILayout.PropertyField(customLoadingBarColor, new GUIContent("Loading Bar Color", "Custom color for the loading bar"));
            EditorGUILayout.PropertyField(customTextColor, new GUIContent("Text Color", "Custom color for the loading text"));
            EditorGUILayout.PropertyField(customFadeColor, new GUIContent("Fade Color", "Custom color for the fade overlay"));
            
            EditorGUILayout.Space();
            
            // Timing Settings
            EditorGUILayout.LabelField("Timing Settings", EditorStyles.boldLabel);
            EditorGUILayout.PropertyField(customFadeInDuration, new GUIContent("Fade In Duration", "Custom fade in duration (0 = use default)"));
            EditorGUILayout.PropertyField(customFadeOutDuration, new GUIContent("Fade Out Duration", "Custom fade out duration (0 = use default)"));
            EditorGUILayout.PropertyField(customLoadingDuration, new GUIContent("Loading Duration", "Custom loading duration (0 = use default)"));
            
            EditorGUILayout.Space();
            
            // Audio Settings
            EditorGUILayout.LabelField("Audio Settings", EditorStyles.boldLabel);
            EditorGUILayout.PropertyField(customFadeInSound, new GUIContent("Fade In Sound", "Custom fade in sound"));
            EditorGUILayout.PropertyField(customFadeOutSound, new GUIContent("Fade Out Sound", "Custom fade out sound"));
            EditorGUILayout.PropertyField(customLoadingCompleteSound, new GUIContent("Loading Complete Sound", "Custom loading complete sound"));
            
            EditorGUILayout.Space();
            
            // Special Effects
            EditorGUILayout.LabelField("Special Effects", EditorStyles.boldLabel);
            EditorGUILayout.PropertyField(enableScreenShake, new GUIContent("Screen Shake", "Enable screen shake effect"));
            EditorGUILayout.PropertyField(enableGlitchEffect, new GUIContent("Glitch Effect", "Enable glitch effect"));
            EditorGUILayout.PropertyField(enableParticleEffects, new GUIContent("Particle Effects", "Enable particle effects"));
            
            EditorGUILayout.Space();
            
            // Custom Quote
            EditorGUILayout.LabelField("Custom Quote", EditorStyles.boldLabel);
            EditorGUILayout.PropertyField(customQuote, new GUIContent("Custom Quote", "Custom quote to display during transition"));
            EditorGUILayout.PropertyField(useOnlyCustomQuote, new GUIContent("Use Only Custom Quote", "Don't rotate through default quotes"));
        }
        
        private void DrawButtonEffects()
        {
            EditorGUILayout.PropertyField(enableButtonHoverEffect, new GUIContent("Enable Hover Effect", "Enable visual effects on hover"));
            
            if (enableButtonHoverEffect.boolValue)
            {
                EditorGUI.indentLevel++;
                EditorGUILayout.PropertyField(hoverColor, new GUIContent("Hover Color", "Color when hovering over button"));
                EditorGUILayout.PropertyField(hoverScale, new GUIContent("Hover Scale", "Scale multiplier when hovering"));
                EditorGUILayout.PropertyField(hoverTransitionSpeed, new GUIContent("Transition Speed", "Speed of hover animations"));
                EditorGUI.indentLevel--;
            }
        }
        
        private void DrawAudioSettings()
        {
            EditorGUILayout.PropertyField(enableButtonAudio, new GUIContent("Enable Button Audio", "Enable audio feedback for button interactions"));
            
            if (enableButtonAudio.boolValue)
            {
                EditorGUI.indentLevel++;
                EditorGUILayout.PropertyField(buttonClickSound, new GUIContent("Click Sound", "Sound played when button is clicked"));
                EditorGUILayout.PropertyField(buttonHoverSound, new GUIContent("Hover Sound", "Sound played when hovering over button"));
                EditorGUILayout.PropertyField(buttonAudioVolume, new GUIContent("Audio Volume", "Volume for button audio"));
                EditorGUI.indentLevel--;
            }
        }
        
        private void DrawValidationSettings()
        {
            EditorGUILayout.PropertyField(validateSceneExists, new GUIContent("Validate Scene Exists", "Check if target scene exists in build settings"));
            EditorGUILayout.PropertyField(showDebugInfo, new GUIContent("Show Debug Info", "Show debug information in console"));
        }
        
        private void DrawAdvancedSettings()
        {
            EditorGUILayout.HelpBox("Advanced settings are automatically configured. Modify these only if you understand the implications.", MessageType.Info);
            
            // Show some read-only advanced info
            EditorGUILayout.LabelField("Current Configuration:", EditorStyles.boldLabel);
            EditorGUILayout.LabelField($"Target Scene: {transitionSettings.FindPropertyRelative("targetSceneName").stringValue}");
            EditorGUILayout.LabelField($"Is Transitioning: {((SceneTransitionButton)target).IsTransitioning()}");
        }
        
        private void DrawActionButtons(SceneTransitionButton button)
        {
            EditorGUILayout.BeginHorizontal();
            
            GUI.enabled = Application.isPlaying && button.IsValidConfiguration();
            if (GUILayout.Button("Test Transition", GUILayout.Height(25)))
            {
                button.SendMessage("OnButtonClick");
            }
            GUI.enabled = true;
            
            if (GUILayout.Button("Validate Configuration", GUILayout.Height(25)))
            {
                button.SendMessage("ValidateConfigurationEditor");
            }
            
            EditorGUILayout.EndHorizontal();
            
            if (!Application.isPlaying)
            {
                EditorGUILayout.HelpBox("Test Transition can only be used in Play mode.", MessageType.Info);
            }
        }
        
        private void ShowSceneSelectionMenu(SerializedProperty targetSceneProperty)
        {
            GenericMenu menu = new GenericMenu();
            
            // Get all scenes in build settings
            for (int i = 0; i < UnityEngine.SceneManagement.SceneManager.sceneCountInBuildSettings; i++)
            {
                string scenePath = UnityEngine.SceneManagement.SceneUtility.GetScenePathByBuildIndex(i);
                string sceneName = System.IO.Path.GetFileNameWithoutExtension(scenePath);
                
                menu.AddItem(new GUIContent(sceneName), false, () => {
                    targetSceneProperty.stringValue = sceneName;
                    serializedObject.ApplyModifiedProperties();
                });
            }
            
            if (menu.GetItemCount() == 0)
            {
                menu.AddDisabledItem(new GUIContent("No scenes in build settings"));
            }
            
            menu.ShowAsContext();
        }
    }
    
    [CustomEditor(typeof(SceneTransitionManager))]
    public class SceneTransitionManagerEditor : UnityEditor.Editor
    {
        private bool showGeneralSettings = true;
        private bool showLoadingBarSettings = true;
        private bool showTextSettings = true;
        private bool showQuoteSystem = true;
        private bool showAudioSettings = true;
        private bool showAdvancedEffects = true;
        
        public override void OnInspectorGUI()
        {
            serializedObject.Update();
            
            SceneTransitionManager manager = (SceneTransitionManager)target;
            
            // Header
            EditorGUILayout.Space();
            EditorGUILayout.LabelField("Dark Fantasy Scene Transition Manager", EditorStyles.boldLabel);
            EditorGUILayout.Space();
            
            // Status
            EditorGUILayout.BeginHorizontal();
            EditorGUILayout.LabelField("Status:", EditorStyles.boldLabel);
            EditorGUILayout.LabelField(manager.IsTransitioning() ? "Transitioning" : "Ready", 
                manager.IsTransitioning() ? EditorStyles.boldLabel : EditorStyles.label);
            EditorGUILayout.EndHorizontal();
            
            EditorGUILayout.Space();
            
            // General Settings
            showGeneralSettings = EditorGUILayout.Foldout(showGeneralSettings, "General Settings", true);
            if (showGeneralSettings)
            {
                EditorGUI.indentLevel++;
                DrawProperty("fadeInDuration");
                DrawProperty("fadeOutDuration");
                DrawProperty("loadingDuration");
                DrawProperty("fadeCurve");
                EditorGUI.indentLevel--;
            }
            
            EditorGUILayout.Space();
            
            // Loading Bar Settings
            showLoadingBarSettings = EditorGUILayout.Foldout(showLoadingBarSettings, "Loading Bar Settings", true);
            if (showLoadingBarSettings)
            {
                EditorGUI.indentLevel++;
                DrawProperty("loadingBarSpeed");
                DrawProperty("pulseIntensity");
                DrawProperty("pulseSpeed");
                DrawProperty("loadingBarColor");
                DrawProperty("loadingBarGlowColor");
                EditorGUI.indentLevel--;
            }
            
            EditorGUILayout.Space();
            
            // Text Settings
            showTextSettings = EditorGUILayout.Foldout(showTextSettings, "Text Settings", true);
            if (showTextSettings)
            {
                EditorGUI.indentLevel++;
                DrawProperty("loadingTextPrefix");
                DrawProperty("loadingTextSuffix");
                DrawProperty("textUpdateInterval");
                DrawProperty("textColor");
                DrawProperty("textGlowColor");
                EditorGUI.indentLevel--;
            }
            
            EditorGUILayout.Space();
            
            // Quote System
            showQuoteSystem = EditorGUILayout.Foldout(showQuoteSystem, "Quote System", true);
            if (showQuoteSystem)
            {
                EditorGUI.indentLevel++;
                DrawProperty("enableQuotes");
                DrawProperty("quoteDisplayDuration");
                DrawProperty("quoteFadeDuration");
                DrawProperty("darkFantasyQuotes");
                EditorGUI.indentLevel--;
            }
            
            EditorGUILayout.Space();
            
            // Audio Settings
            showAudioSettings = EditorGUILayout.Foldout(showAudioSettings, "Audio Settings", true);
            if (showAudioSettings)
            {
                EditorGUI.indentLevel++;
                DrawProperty("enableAudio");
                DrawProperty("fadeInSound");
                DrawProperty("fadeOutSound");
                DrawProperty("loadingCompleteSound");
                DrawProperty("audioVolume");
                EditorGUI.indentLevel--;
            }
            
            EditorGUILayout.Space();
            
            // Advanced Effects
            showAdvancedEffects = EditorGUILayout.Foldout(showAdvancedEffects, "Advanced Effects", true);
            if (showAdvancedEffects)
            {
                EditorGUI.indentLevel++;
                DrawProperty("enableParticleEffects");
                DrawProperty("backgroundParticles");
                DrawProperty("enableScreenShake");
                DrawProperty("shakeIntensity");
                DrawProperty("enableGlitchEffect");
                DrawProperty("glitchIntensity");
                EditorGUI.indentLevel--;
            }
            
            serializedObject.ApplyModifiedProperties();
        }
        
        private void DrawProperty(string propertyName)
        {
            SerializedProperty property = serializedObject.FindProperty(propertyName);
            if (property != null)
            {
                EditorGUILayout.PropertyField(property);
            }
        }
    }
}