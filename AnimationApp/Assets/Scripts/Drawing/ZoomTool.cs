using UnityEngine;
using AnimationApp.Core;

namespace AnimationApp.Drawing
{
    public class ZoomTool : MonoBehaviour
    {
        private CanvasManager canvasManager;
        private float zoomSpeed = 0.1f;
        
        public void Initialize(CanvasManager manager)
        {
            canvasManager = manager;
        }
        
        public void OnMouseDown(Vector2 position)
        {
            // Zoom in at position
            ZoomAt(position, 1.2f);
        }
        
        public void OnMouseDrag(Vector2 position)
        {
            // Handle zoom drag
        }
        
        public void OnMouseUp()
        {
            // Finish zoom
        }
        
        private void ZoomAt(Vector2 position, float zoomFactor)
        {
            // Zoom at the specified position
            canvasManager.zoom *= zoomFactor;
            canvasManager.zoom = Mathf.Clamp(canvasManager.zoom, 0.1f, 10f);
        }
        
        public void ZoomIn()
        {
            canvasManager.zoom *= 1.2f;
            canvasManager.zoom = Mathf.Clamp(canvasManager.zoom, 0.1f, 10f);
        }
        
        public void ZoomOut()
        {
            canvasManager.zoom /= 1.2f;
            canvasManager.zoom = Mathf.Clamp(canvasManager.zoom, 0.1f, 10f);
        }
        
        public void ZoomToFit()
        {
            // Zoom to fit canvas in view
            canvasManager.zoom = 1f;
        }
    }
}
