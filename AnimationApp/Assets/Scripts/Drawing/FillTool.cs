using UnityEngine;
using AnimationApp.Core;

namespace AnimationApp.Drawing
{
    public class FillTool : MonoBehaviour
    {
        [Header("Fill Settings")]
        public Color fillColor = Color.white;
        public float tolerance = 0.1f;
        public FillType fillType = FillType.Flood;
        
        private CanvasManager canvasManager;
        
        public void Initialize(CanvasManager manager)
        {
            canvasManager = manager;
        }
        
        public void OnMouseDown(Vector2 position)
        {
            FillAt(position);
        }
        
        private void FillAt(Vector2 position)
        {
            // Perform flood fill at the specified position
            Debug.Log($"Filling at {position} with color {fillColor}");
        }
        
        public void SetFillColor(Color color)
        {
            fillColor = color;
        }
        
        public void SetTolerance(float newTolerance)
        {
            tolerance = Mathf.Clamp01(newTolerance);
        }
    }
    
    public enum FillType
    {
        Flood,
        Pattern
    }
}
