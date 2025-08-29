using UnityEngine;
using UnityEngine.UI;
using AnimationApp.Timeline;

namespace AnimationApp.UI.Components
{
    public class LayerItemUI : MonoBehaviour
    {
        [Header("UI Elements")]
        public Text layerNameText;
        public Toggle visibilityToggle;
        public Toggle lockToggle;
        public Slider opacitySlider;
        public Button layerButton;
        public Image layerIcon;
        
        private LayerData layerData;
        private int layerIndex;
        
        public System.Action<LayerData> OnLayerSelected;
        
        public void Initialize(LayerData data, int index)
        {
            layerData = data;
            layerIndex = index;
            
            SetupUI();
            UpdateUI();
        }
        
        private void SetupUI()
        {
            if (layerNameText != null)
                layerNameText.text = layerData.name;
            
            if (visibilityToggle != null)
                visibilityToggle.isOn = layerData.visible;
            
            if (lockToggle != null)
                lockToggle.isOn = layerData.locked;
            
            if (opacitySlider != null)
                opacitySlider.value = layerData.opacity;
            
            if (layerButton != null)
                layerButton.onClick.AddListener(() => OnLayerSelected?.Invoke(layerData));
            
            if (visibilityToggle != null)
                visibilityToggle.onValueChanged.AddListener((visible) => {
                    layerData.visible = visible;
                    // Notify layer manager
                });
            
            if (lockToggle != null)
                lockToggle.onValueChanged.AddListener((locked) => {
                    layerData.locked = locked;
                    // Notify layer manager
                });
            
            if (opacitySlider != null)
                opacitySlider.onValueChanged.AddListener((opacity) => {
                    layerData.opacity = opacity;
                    // Notify layer manager
                });
        }
        
        private void UpdateUI()
        {
            if (layerNameText != null)
                layerNameText.text = layerData.name;
            
            if (visibilityToggle != null)
                visibilityToggle.isOn = layerData.visible;
            
            if (lockToggle != null)
                lockToggle.isOn = layerData.locked;
            
            if (opacitySlider != null)
                opacitySlider.value = layerData.opacity;
            
            // Update layer icon based on type
            if (layerIcon != null)
            {
                // Set appropriate icon for layer type
                layerIcon.color = layerData.visible ? Color.white : Color.gray;
            }
        }
        
        public void SetSelected(bool selected)
        {
            if (layerButton != null)
            {
                ColorBlock colors = layerButton.colors;
                colors.normalColor = selected ? Color.blue : Color.white;
                layerButton.colors = colors;
            }
        }
        
        public LayerData GetLayerData()
        {
            return layerData;
        }
        
        public int GetLayerIndex()
        {
            return layerIndex;
        }
    }
}
