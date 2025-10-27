using UnityEngine;
using AnimationApp.Core;

namespace AnimationApp.Drawing
{
    public class TransformTool : MonoBehaviour
    {
        [Header("Transform Settings")]
        public TransformMode transformMode = TransformMode.Move;
        public bool maintainAspectRatio = true;
        public Vector2 pivot = new Vector2(0.5f, 0.5f);
        
        private CanvasManager canvasManager;
        private Vector2 startPosition;
        private Vector2 currentPosition;
        private bool isTransforming = false;
        
        public void Initialize(CanvasManager manager)
        {
            canvasManager = manager;
        }
        
        public void OnMouseDown(Vector2 position)
        {
            startPosition = position;
            currentPosition = position;
            isTransforming = true;
        }
        
        public void OnMouseDrag(Vector2 position)
        {
            if (isTransforming)
            {
                currentPosition = position;
                ApplyTransform();
            }
        }
        
        public void OnMouseUp()
        {
            isTransforming = false;
        }
        
        private void ApplyTransform()
        {
            Vector2 delta = currentPosition - startPosition;
            
            switch (transformMode)
            {
                case TransformMode.Move:
                    MoveSelection(delta);
                    break;
                case TransformMode.Scale:
                    ScaleSelection(delta);
                    break;
                case TransformMode.Rotate:
                    RotateSelection(delta);
                    break;
            }
        }
        
        private void MoveSelection(Vector2 delta)
        {
            // Move the selected area
            Debug.Log($"Moving selection by {delta}");
        }
        
        private void ScaleSelection(Vector2 delta)
        {
            // Scale the selected area
            Debug.Log($"Scaling selection by {delta}");
        }
        
        private void RotateSelection(Vector2 delta)
        {
            // Rotate the selected area
            float angle = Mathf.Atan2(delta.y, delta.x) * Mathf.Rad2Deg;
            Debug.Log($"Rotating selection by {angle} degrees");
        }
        
        public void SetTransformMode(TransformMode mode)
        {
            transformMode = mode;
        }
        
        public void SetPivot(Vector2 newPivot)
        {
            pivot = newPivot;
        }
    }
    
    public enum TransformMode
    {
        Move,
        Scale,
        Rotate
    }
}
