using UnityEngine;
using AnimationApp.Core;

namespace AnimationApp.Drawing
{
    public class HandTool : MonoBehaviour
    {
        private CanvasManager canvasManager;
        private Vector2 lastMousePosition;
        private bool isPanning = false;
        
        public void Initialize(CanvasManager manager)
        {
            canvasManager = manager;
        }
        
        public void OnMouseDown(Vector2 position)
        {
            lastMousePosition = position;
            isPanning = true;
        }
        
        public void OnMouseDrag(Vector2 position)
        {
            if (isPanning)
            {
                Vector2 delta = position - lastMousePosition;
                canvasManager.pan += delta;
                lastMousePosition = position;
            }
        }
        
        public void OnMouseUp()
        {
            isPanning = false;
        }
    }
}
