using UnityEngine;
using UnityEngine.UI;
using AnimationApp.Core;

namespace AnimationApp.UI.Panels
{
    public class ToolbarPanel : MonoBehaviour
    {
        [Header("Tool Buttons")]
        public Button brushButton;
        public Button eraserButton;
        public Button fillButton;
        public Button transformButton;
        public Button selectionButton;
        public Button handButton;
        public Button zoomButton;
        
        [Header("Action Buttons")]
        public Button undoButton;
        public Button redoButton;
        public Button onionSkinButton;
        
        [Header("Tool Settings")]
        public Slider brushSizeSlider;
        public Slider brushOpacitySlider;
        public Slider brushHardnessSlider;
        
        public System.Action OnUndoClicked;
        public System.Action OnRedoClicked;
        public System.Action<ToolType> OnToolChanged;
        
        public void Initialize()
        {
            SetupToolButtons();
            SetupActionButtons();
            SetupToolSettings();
        }
        
        private void SetupToolButtons()
        {
            if (brushButton != null)
                brushButton.onClick.AddListener(() => OnToolChanged?.Invoke(ToolType.Brush));
            
            if (eraserButton != null)
                eraserButton.onClick.AddListener(() => OnToolChanged?.Invoke(ToolType.Eraser));
            
            if (fillButton != null)
                fillButton.onClick.AddListener(() => OnToolChanged?.Invoke(ToolType.Fill));
            
            if (transformButton != null)
                transformButton.onClick.AddListener(() => OnToolChanged?.Invoke(ToolType.Transform));
            
            if (selectionButton != null)
                selectionButton.onClick.AddListener(() => OnToolChanged?.Invoke(ToolType.Selection));
            
            if (handButton != null)
                handButton.onClick.AddListener(() => OnToolChanged?.Invoke(ToolType.Hand));
            
            if (zoomButton != null)
                zoomButton.onClick.AddListener(() => OnToolChanged?.Invoke(ToolType.Zoom));
        }
        
        private void SetupActionButtons()
        {
            if (undoButton != null)
                undoButton.onClick.AddListener(() => OnUndoClicked?.Invoke());
            
            if (redoButton != null)
                redoButton.onClick.AddListener(() => OnRedoClicked?.Invoke());
            
            if (onionSkinButton != null)
                onionSkinButton.onClick.AddListener(() => ToggleOnionSkin());
        }
        
        private void SetupToolSettings()
        {
            if (brushSizeSlider != null)
                brushSizeSlider.onValueChanged.AddListener((value) => UpdateBrushSize(value));
            
            if (brushOpacitySlider != null)
                brushOpacitySlider.onValueChanged.AddListener((value) => UpdateBrushOpacity(value));
            
            if (brushHardnessSlider != null)
                brushHardnessSlider.onValueChanged.AddListener((value) => UpdateBrushHardness(value));
        }
        
        private void ToggleOnionSkin()
        {
            // Toggle onion skinning
            Debug.Log("Onion skin toggled");
        }
        
        private void UpdateBrushSize(float size)
        {
            // Update brush size
            Debug.Log($"Brush size: {size}");
        }
        
        private void UpdateBrushOpacity(float opacity)
        {
            // Update brush opacity
            Debug.Log($"Brush opacity: {opacity}");
        }
        
        private void UpdateBrushHardness(float hardness)
        {
            // Update brush hardness
            Debug.Log($"Brush hardness: {hardness}");
        }
        
        public void SetActiveTool(ToolType toolType)
        {
            // Update button states to show active tool
            UpdateToolButtonStates(toolType);
        }
        
        private void UpdateToolButtonStates(ToolType activeTool)
        {
            // Update visual states of tool buttons
            if (brushButton != null)
                brushButton.interactable = (activeTool != ToolType.Brush);
            
            if (eraserButton != null)
                eraserButton.interactable = (activeTool != ToolType.Eraser);
            
            if (fillButton != null)
                fillButton.interactable = (activeTool != ToolType.Fill);
            
            if (transformButton != null)
                transformButton.interactable = (activeTool != ToolType.Transform);
            
            if (selectionButton != null)
                selectionButton.interactable = (activeTool != ToolType.Selection);
            
            if (handButton != null)
                handButton.interactable = (activeTool != ToolType.Hand);
            
            if (zoomButton != null)
                zoomButton.interactable = (activeTool != ToolType.Zoom);
        }
    }
}
