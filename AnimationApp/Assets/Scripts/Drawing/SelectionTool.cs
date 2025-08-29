using UnityEngine;
using AnimationApp.Core;

namespace AnimationApp.Drawing
{
    public class SelectionTool : MonoBehaviour
    {
        [Header("Selection Settings")]
        public SelectionType selectionType = SelectionType.Rectangle;
        public bool addToSelection = false;
        public bool subtractFromSelection = false;
        
        private CanvasManager canvasManager;
        private Vector2 startPosition;
        private Vector2 currentPosition;
        private bool isSelecting = false;
        private Rect selectionRect;
        
        public void Initialize(CanvasManager manager)
        {
            canvasManager = manager;
        }
        
        public void OnMouseDown(Vector2 position)
        {
            startPosition = position;
            currentPosition = position;
            isSelecting = true;
            
            if (!addToSelection && !subtractFromSelection)
            {
                ClearSelection();
            }
        }
        
        public void OnMouseDrag(Vector2 position)
        {
            if (isSelecting)
            {
                currentPosition = position;
                UpdateSelection();
            }
        }
        
        public void OnMouseUp()
        {
            isSelecting = false;
            FinalizeSelection();
        }
        
        private void UpdateSelection()
        {
            switch (selectionType)
            {
                case SelectionType.Rectangle:
                    UpdateRectangleSelection();
                    break;
                case SelectionType.Lasso:
                    UpdateLassoSelection();
                    break;
                case SelectionType.MagicWand:
                    UpdateMagicWandSelection();
                    break;
            }
        }
        
        private void UpdateRectangleSelection()
        {
            float minX = Mathf.Min(startPosition.x, currentPosition.x);
            float maxX = Mathf.Max(startPosition.x, currentPosition.x);
            float minY = Mathf.Min(startPosition.y, currentPosition.y);
            float maxY = Mathf.Max(startPosition.y, currentPosition.y);
            
            selectionRect = new Rect(minX, minY, maxX - minX, maxY - minY);
        }
        
        private void UpdateLassoSelection()
        {
            // Implement lasso selection
            Debug.Log("Lasso selection not implemented yet");
        }
        
        private void UpdateMagicWandSelection()
        {
            // Implement magic wand selection
            Debug.Log("Magic wand selection not implemented yet");
        }
        
        private void FinalizeSelection()
        {
            // Finalize the selection based on the current selection type
            Debug.Log($"Finalized selection: {selectionRect}");
        }
        
        private void ClearSelection()
        {
            selectionRect = Rect.zero;
        }
        
        public Rect GetSelectionRect()
        {
            return selectionRect;
        }
        
        public bool HasSelection()
        {
            return selectionRect.width > 0 && selectionRect.height > 0;
        }
        
        public void SetSelectionType(SelectionType type)
        {
            selectionType = type;
        }
    }
    
    public enum SelectionType
    {
        Rectangle,
        Lasso,
        MagicWand
    }
}
