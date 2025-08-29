using UnityEngine;
using AnimationApp.Drawing;

namespace AnimationApp.Core
{
    public class ToolManager : MonoBehaviour
    {
        [Header("Available Tools")]
        public BrushTool brushTool;
        public EraserTool eraserTool;
        public FillTool fillTool;
        public TransformTool transformTool;
        public SelectionTool selectionTool;
        public HandTool handTool;
        public ZoomTool zoomTool;
        
        [Header("Current Tool")]
        public ToolType currentTool = ToolType.Brush;
        
        public System.Action<ToolType> OnToolChanged;
        
        public void Initialize()
        {
            // Initialize all tools
            if (brushTool != null) brushTool.Initialize(null);
            if (eraserTool != null) eraserTool.Initialize(null);
            if (fillTool != null) fillTool.Initialize(null);
            if (transformTool != null) transformTool.Initialize(null);
            if (selectionTool != null) selectionTool.Initialize(null);
            if (handTool != null) handTool.Initialize(null);
            if (zoomTool != null) zoomTool.Initialize(null);
            
            // Set initial tool
            SetTool(ToolType.Brush);
        }
        
        public void SetTool(ToolType toolType)
        {
            if (currentTool != toolType)
            {
                currentTool = toolType;
                OnToolChanged?.Invoke(toolType);
                
                // Update tool UI
                UpdateToolUI();
            }
        }
        
        private void UpdateToolUI()
        {
            // This would update the UI to show the current tool
            // and its settings
        }
        
        public void SetBrushSize(float size)
        {
            if (brushTool != null)
            {
                brushTool.SetSize(size);
            }
        }
        
        public void SetBrushOpacity(float opacity)
        {
            if (brushTool != null)
            {
                brushTool.SetOpacity(opacity);
            }
        }
        
        public void SetBrushHardness(float hardness)
        {
            if (brushTool != null)
            {
                brushTool.SetHardness(hardness);
            }
        }
        
        public ToolType GetCurrentTool()
        {
            return currentTool;
        }
        
        public void NextTool()
        {
            int currentIndex = (int)currentTool;
            int nextIndex = (currentIndex + 1) % System.Enum.GetValues(typeof(ToolType)).Length;
            SetTool((ToolType)nextIndex);
        }
        
        public void PreviousTool()
        {
            int currentIndex = (int)currentTool;
            int previousIndex = (currentIndex - 1 + System.Enum.GetValues(typeof(ToolType)).Length) % System.Enum.GetValues(typeof(ToolType)).Length;
            SetTool((ToolType)previousIndex);
        }
    }
    
    public enum ToolType
    {
        Brush,
        Eraser,
        Fill,
        Transform,
        Selection,
        Hand,
        Zoom
    }
}
