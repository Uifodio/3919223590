using UnityEngine;
using UnityEngine.UI;
using AnimationApp.Timeline;

namespace AnimationApp.UI.Panels
{
    public class PropertiesPanel : MonoBehaviour
    {
        [Header("Layer List")]
        public Transform layerListContent;
        public GameObject layerItemPrefab;
        public Button addLayerButton;
        public Button deleteLayerButton;
        
        [Header("Layer Properties")]
        public InputField layerNameInput;
        public Toggle layerVisibilityToggle;
        public Toggle layerLockToggle;
        public Slider layerOpacitySlider;
        public Dropdown layerBlendingModeDropdown;
        
        public System.Action<LayerData> OnLayerSelected;
        public System.Action<LayerData, bool> OnLayerVisibilityChanged;
        public System.Action<LayerData, bool> OnLayerLockChanged;
        public System.Action<LayerData, float> OnLayerOpacityChanged;
        public System.Action<LayerData, BlendingMode> OnLayerBlendingModeChanged;
        
        public void Initialize()
        {
            SetupLayerButtons();
            SetupLayerProperties();
        }
        
        private void SetupLayerButtons()
        {
            if (addLayerButton != null)
                addLayerButton.onClick.AddListener(() => AddNewLayer());
            
            if (deleteLayerButton != null)
                deleteLayerButton.onClick.AddListener(() => DeleteSelectedLayer());
        }
        
        private void SetupLayerProperties()
        {
            if (layerNameInput != null)
                layerNameInput.onEndEdit.AddListener((name) => UpdateLayerName(name));
            
            if (layerVisibilityToggle != null)
                layerVisibilityToggle.onValueChanged.AddListener((visible) => UpdateLayerVisibility(visible));
            
            if (layerLockToggle != null)
                layerLockToggle.onValueChanged.AddListener((locked) => UpdateLayerLock(locked));
            
            if (layerOpacitySlider != null)
                layerOpacitySlider.onValueChanged.AddListener((opacity) => UpdateLayerOpacity(opacity));
            
            if (layerBlendingModeDropdown != null)
                layerBlendingModeDropdown.onValueChanged.AddListener((index) => UpdateLayerBlendingMode(index));
        }
        
        public void UpdateLayerList(LayerData[] layers)
        {
            // Clear existing layer items
            if (layerListContent != null)
            {
                foreach (Transform child in layerListContent)
                {
                    Destroy(child.gameObject);
                }
            }
            
            // Create new layer items
            for (int i = 0; i < layers.Length; i++)
            {
                CreateLayerItem(layers[i], i);
            }
        }
        
        private void CreateLayerItem(LayerData layer, int index)
        {
            if (layerItemPrefab != null && layerListContent != null)
            {
                GameObject layerItem = Instantiate(layerItemPrefab, layerListContent);
                LayerItemUI layerItemUI = layerItem.GetComponent<LayerItemUI>();
                
                if (layerItemUI != null)
                {
                    layerItemUI.Initialize(layer, index);
                    layerItemUI.OnLayerSelected += (selectedLayer) => OnLayerSelected?.Invoke(selectedLayer);
                }
            }
        }
        
        public void UpdateLayerProperties(LayerData layer)
        {
            if (layer == null) return;
            
            if (layerNameInput != null)
                layerNameInput.text = layer.name;
            
            if (layerVisibilityToggle != null)
                layerVisibilityToggle.isOn = layer.visible;
            
            if (layerLockToggle != null)
                layerLockToggle.isOn = layer.locked;
            
            if (layerOpacitySlider != null)
                layerOpacitySlider.value = layer.opacity;
            
            if (layerBlendingModeDropdown != null)
                layerBlendingModeDropdown.value = (int)layer.blendingMode;
        }
        
        private void AddNewLayer()
        {
            // Add new layer
            Debug.Log("Adding new layer");
        }
        
        private void DeleteSelectedLayer()
        {
            // Delete selected layer
            Debug.Log("Deleting selected layer");
        }
        
        private void UpdateLayerName(string name)
        {
            // Update layer name
            Debug.Log($"Layer name: {name}");
        }
        
        private void UpdateLayerVisibility(bool visible)
        {
            // Update layer visibility
            Debug.Log($"Layer visibility: {visible}");
        }
        
        private void UpdateLayerLock(bool locked)
        {
            // Update layer lock
            Debug.Log($"Layer lock: {locked}");
        }
        
        private void UpdateLayerOpacity(float opacity)
        {
            // Update layer opacity
            Debug.Log($"Layer opacity: {opacity}");
        }
        
        private void UpdateLayerBlendingMode(int index)
        {
            // Update layer blending mode
            BlendingMode mode = (BlendingMode)index;
            Debug.Log($"Layer blending mode: {mode}");
        }
    }
}
