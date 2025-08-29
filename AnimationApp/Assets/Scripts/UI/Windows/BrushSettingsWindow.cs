using UnityEngine;
using UnityEngine.UI;
using AnimationApp.Core;

namespace AnimationApp.UI.Windows
{
    public class BrushSettingsWindow : UIWindow
    {
        [Header("Brush Settings")]
        public Slider sizeSlider;
        public Slider opacitySlider;
        public Slider hardnessSlider;
        public Slider spacingSlider;
        public Slider angleSlider;
        
        [Header("Brush Types")]
        public Dropdown brushTypeDropdown;
        public Toggle pressureSensitivityToggle;
        
        [Header("Brush Preview")]
        public RawImage brushPreview;
        public Slider previewSizeSlider;
        
        public System.Action<float> OnSizeChanged;
        public System.Action<float> OnOpacityChanged;
        public System.Action<float> OnHardnessChanged;
        public System.Action<BrushType> OnBrushTypeChanged;
        public System.Action<bool> OnPressureSensitivityChanged;
        
        public override void Initialize()
        {
            base.Initialize();
            windowTitle = "Brush Settings";
            
            SetupSliders();
            SetupDropdowns();
            SetupToggles();
            SetupPreview();
        }
        
        private void SetupSliders()
        {
            if (sizeSlider != null)
            {
                sizeSlider.minValue = 1f;
                sizeSlider.maxValue = 100f;
                sizeSlider.value = 5f;
                sizeSlider.onValueChanged.AddListener((value) => OnSizeChanged?.Invoke(value));
            }
            
            if (opacitySlider != null)
            {
                opacitySlider.minValue = 0f;
                opacitySlider.maxValue = 1f;
                opacitySlider.value = 1f;
                opacitySlider.onValueChanged.AddListener((value) => OnOpacityChanged?.Invoke(value));
            }
            
            if (hardnessSlider != null)
            {
                hardnessSlider.minValue = 0f;
                hardnessSlider.maxValue = 1f;
                hardnessSlider.value = 0.5f;
                hardnessSlider.onValueChanged.AddListener((value) => OnHardnessChanged?.Invoke(value));
            }
            
            if (spacingSlider != null)
            {
                spacingSlider.minValue = 0.1f;
                spacingSlider.maxValue = 2f;
                spacingSlider.value = 0.5f;
            }
            
            if (angleSlider != null)
            {
                angleSlider.minValue = 0f;
                angleSlider.maxValue = 360f;
                angleSlider.value = 0f;
            }
        }
        
        private void SetupDropdowns()
        {
            if (brushTypeDropdown != null)
            {
                brushTypeDropdown.ClearOptions();
                brushTypeDropdown.AddOptions(new System.Collections.Generic.List<string>
                {
                    "Round",
                    "Square",
                    "Custom"
                });
                brushTypeDropdown.onValueChanged.AddListener((index) => {
                    BrushType brushType = (BrushType)index;
                    OnBrushTypeChanged?.Invoke(brushType);
                });
            }
        }
        
        private void SetupToggles()
        {
            if (pressureSensitivityToggle != null)
            {
                pressureSensitivityToggle.isOn = true;
                pressureSensitivityToggle.onValueChanged.AddListener((enabled) => {
                    OnPressureSensitivityChanged?.Invoke(enabled);
                });
            }
        }
        
        private void SetupPreview()
        {
            if (previewSizeSlider != null)
            {
                previewSizeSlider.minValue = 1f;
                previewSizeSlider.maxValue = 10f;
                previewSizeSlider.value = 1f;
                previewSizeSlider.onValueChanged.AddListener((value) => UpdateBrushPreview(value));
            }
        }
        
        private void UpdateBrushPreview(float size)
        {
            // Update brush preview image
            if (brushPreview != null)
            {
                // This would update the brush preview texture
            }
        }
        
        public void SetBrushSize(float size)
        {
            if (sizeSlider != null)
                sizeSlider.value = size;
        }
        
        public void SetBrushOpacity(float opacity)
        {
            if (opacitySlider != null)
                opacitySlider.value = opacity;
        }
        
        public void SetBrushHardness(float hardness)
        {
            if (hardnessSlider != null)
                hardnessSlider.value = hardness;
        }
        
        public void SetBrushType(BrushType brushType)
        {
            if (brushTypeDropdown != null)
                brushTypeDropdown.value = (int)brushType;
        }
        
        public void SetPressureSensitivity(bool enabled)
        {
            if (pressureSensitivityToggle != null)
                pressureSensitivityToggle.isOn = enabled;
        }
    }
}
