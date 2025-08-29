using UnityEngine;
using UnityEngine.UI;
using AnimationApp.Core;

namespace AnimationApp.UI.Windows
{
    public class PreferencesWindow : UIWindow
    {
        [Header("General Settings")]
        public Toggle autoSaveToggle;
        public Slider autoSaveIntervalSlider;
        public Toggle showGridToggle;
        public Toggle showRulersToggle;
        public ColorPicker backgroundColorPicker;
        
        [Header("Canvas Settings")]
        public InputField defaultWidthInput;
        public InputField defaultHeightInput;
        public Slider defaultZoomSlider;
        public Dropdown defaultFPSDropdown;
        
        [Header("Brush Settings")]
        public Slider defaultBrushSizeSlider;
        public Slider defaultBrushOpacitySlider;
        public Slider defaultBrushHardnessSlider;
        public Toggle pressureSensitivityToggle;
        
        [Header("Timeline Settings")]
        public Slider onionSkinBeforeSlider;
        public Slider onionSkinAfterSlider;
        public Slider onionSkinOpacitySlider;
        public InputField maxFramesInput;
        
        [Header("Audio Settings")]
        public Slider defaultVolumeSlider;
        public Toggle audioEnabledToggle;
        public Slider audioOffsetSlider;
        
        [Header("Controls")]
        public Button saveButton;
        public Button cancelButton;
        public Button resetButton;
        
        private AnimationAppSettings settings;
        
        public System.Action<AnimationAppSettings> OnSettingsChanged;
        
        public override void Initialize()
        {
            base.Initialize();
            windowTitle = "Preferences";
            
            SetupControls();
            LoadSettings();
        }
        
        private void SetupControls()
        {
            if (saveButton != null)
                saveButton.onClick.AddListener(() => SaveSettings());
            
            if (cancelButton != null)
                cancelButton.onClick.AddListener(() => Hide());
            
            if (resetButton != null)
                resetButton.onClick.AddListener(() => ResetToDefaults());
        }
        
        private void LoadSettings()
        {
            // Load current settings into UI
            if (autoSaveToggle != null)
                autoSaveToggle.isOn = settings.autoSave;
            
            if (autoSaveIntervalSlider != null)
                autoSaveIntervalSlider.value = settings.autoSaveInterval;
            
            if (showGridToggle != null)
                showGridToggle.isOn = settings.showGrid;
            
            if (showRulersToggle != null)
                showRulersToggle.isOn = settings.showRulers;
            
            if (defaultWidthInput != null)
                defaultWidthInput.text = settings.defaultCanvasWidth.ToString();
            
            if (defaultHeightInput != null)
                defaultHeightInput.text = settings.defaultCanvasHeight.ToString();
            
            if (defaultZoomSlider != null)
                defaultZoomSlider.value = settings.defaultZoom;
            
            if (defaultFPSDropdown != null)
                defaultFPSDropdown.value = GetFPSIndex(settings.defaultFPS);
            
            if (defaultBrushSizeSlider != null)
                defaultBrushSizeSlider.value = settings.defaultBrushSize;
            
            if (defaultBrushOpacitySlider != null)
                defaultBrushOpacitySlider.value = settings.defaultBrushOpacity;
            
            if (defaultBrushHardnessSlider != null)
                defaultBrushHardnessSlider.value = settings.defaultBrushHardness;
            
            if (pressureSensitivityToggle != null)
                pressureSensitivityToggle.isOn = settings.pressureSensitivity;
            
            if (onionSkinBeforeSlider != null)
                onionSkinBeforeSlider.value = settings.onionSkinBefore;
            
            if (onionSkinAfterSlider != null)
                onionSkinAfterSlider.value = settings.onionSkinAfter;
            
            if (onionSkinOpacitySlider != null)
                onionSkinOpacitySlider.value = settings.onionSkinOpacity;
            
            if (maxFramesInput != null)
                maxFramesInput.text = settings.maxFrames.ToString();
        }
        
        private void SaveSettings()
        {
            // Save UI values to settings
            if (autoSaveToggle != null)
                settings.autoSave = autoSaveToggle.isOn;
            
            if (autoSaveIntervalSlider != null)
                settings.autoSaveInterval = (int)autoSaveIntervalSlider.value;
            
            if (showGridToggle != null)
                settings.showGrid = showGridToggle.isOn;
            
            if (showRulersToggle != null)
                settings.showRulers = showRulersToggle.isOn;
            
            if (defaultWidthInput != null && int.TryParse(defaultWidthInput.text, out int width))
                settings.defaultCanvasWidth = width;
            
            if (defaultHeightInput != null && int.TryParse(defaultHeightInput.text, out int height))
                settings.defaultCanvasHeight = height;
            
            if (defaultZoomSlider != null)
                settings.defaultZoom = defaultZoomSlider.value;
            
            if (defaultFPSDropdown != null)
                settings.defaultFPS = GetFPSValue(defaultFPSDropdown.value);
            
            if (defaultBrushSizeSlider != null)
                settings.defaultBrushSize = defaultBrushSizeSlider.value;
            
            if (defaultBrushOpacitySlider != null)
                settings.defaultBrushOpacity = defaultBrushOpacitySlider.value;
            
            if (defaultBrushHardnessSlider != null)
                settings.defaultBrushHardness = defaultBrushHardnessSlider.value;
            
            if (pressureSensitivityToggle != null)
                settings.pressureSensitivity = pressureSensitivityToggle.isOn;
            
            if (onionSkinBeforeSlider != null)
                settings.onionSkinBefore = (int)onionSkinBeforeSlider.value;
            
            if (onionSkinAfterSlider != null)
                settings.onionSkinAfter = (int)onionSkinAfterSlider.value;
            
            if (onionSkinOpacitySlider != null)
                settings.onionSkinOpacity = onionSkinOpacitySlider.value;
            
            if (maxFramesInput != null && int.TryParse(maxFramesInput.text, out int maxFrames))
                settings.maxFrames = maxFrames;
            
            // Notify settings changed
            OnSettingsChanged?.Invoke(settings);
            
            Hide();
        }
        
        private void ResetToDefaults()
        {
            settings = new AnimationAppSettings();
            LoadSettings();
        }
        
        private int GetFPSIndex(int fps)
        {
            switch (fps)
            {
                case 12: return 0;
                case 24: return 1;
                case 30: return 2;
                case 60: return 3;
                default: return 1;
            }
        }
        
        private int GetFPSValue(int index)
        {
            switch (index)
            {
                case 0: return 12;
                case 1: return 24;
                case 2: return 30;
                case 3: return 60;
                default: return 24;
            }
        }
        
        public void SetSettings(AnimationAppSettings newSettings)
        {
            settings = newSettings;
            LoadSettings();
        }
    }
    
    // Simple color picker component (placeholder)
    public class ColorPicker : MonoBehaviour
    {
        public Color color = Color.white;
        public System.Action<Color> OnColorChanged;
        
        public void SetColor(Color newColor)
        {
            color = newColor;
            OnColorChanged?.Invoke(color);
        }
    }
}
