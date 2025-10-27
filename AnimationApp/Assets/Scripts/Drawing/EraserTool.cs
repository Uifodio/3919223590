using UnityEngine;
using AnimationApp.Core;

namespace AnimationApp.Drawing
{
    public class EraserTool : MonoBehaviour
    {
        [Header("Eraser Settings")]
        public float size = 10f;
        public float opacity = 1f;
        public EraserType eraserType = EraserType.Soft;
        
        private CanvasManager canvasManager;
        
        public void Initialize(CanvasManager manager)
        {
            canvasManager = manager;
        }
        
        public void OnMouseDown(Vector2 position)
        {
            // Start erasing
            EraseAt(position);
        }
        
        public void OnMouseDrag(Vector2 position)
        {
            // Continue erasing
            EraseAt(position);
        }
        
        public void OnMouseUp()
        {
            // Finish erasing
        }
        
        private void EraseAt(Vector2 position)
        {
            // Erase at the specified position
            // This would clear pixels in the eraser area
            Debug.Log($"Erasing at {position} with size {size}");
        }
        
        public void SetSize(float newSize)
        {
            size = Mathf.Clamp(newSize, 1f, 100f);
        }
        
        public void SetOpacity(float newOpacity)
        {
            opacity = Mathf.Clamp01(newOpacity);
        }
    }
    
    public enum EraserType
    {
        Hard,
        Soft
    }
}
