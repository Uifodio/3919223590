using UnityEngine;
using UnityEngine.UI;

namespace AnimationApp.UI.Windows
{
    public abstract class UIWindow : MonoBehaviour
    {
        [Header("Window Settings")]
        public string windowTitle = "Window";
        public bool isDraggable = true;
        public bool isResizable = true;
        public Vector2 minSize = new Vector2(200, 150);
        public Vector2 defaultSize = new Vector2(400, 300);
        
        [Header("Window Components")]
        public Button closeButton;
        public Button minimizeButton;
        public Button maximizeButton;
        public Text titleText;
        public RectTransform contentArea;
        
        protected bool isVisible = false;
        protected bool isMinimized = false;
        protected bool isMaximized = false;
        protected Vector2 originalSize;
        protected Vector3 originalPosition;
        
        public virtual void Initialize()
        {
            SetupWindowButtons();
            SetupDragging();
            SetupResizing();
            
            if (titleText != null)
                titleText.text = windowTitle;
        }
        
        private void SetupWindowButtons()
        {
            if (closeButton != null)
                closeButton.onClick.AddListener(() => Hide());
            
            if (minimizeButton != null)
                minimizeButton.onClick.AddListener(() => ToggleMinimize());
            
            if (maximizeButton != null)
                maximizeButton.onClick.AddListener(() => ToggleMaximize());
        }
        
        private void SetupDragging()
        {
            if (isDraggable)
            {
                // Add drag functionality
                // This would require additional components or custom implementation
            }
        }
        
        private void SetupResizing()
        {
            if (isResizable)
            {
                // Add resize functionality
                // This would require additional components or custom implementation
            }
        }
        
        public virtual void Show()
        {
            gameObject.SetActive(true);
            isVisible = true;
            OnShow();
        }
        
        public virtual void Hide()
        {
            gameObject.SetActive(false);
            isVisible = false;
            OnHide();
        }
        
        public virtual void ToggleMinimize()
        {
            if (isMinimized)
            {
                Restore();
            }
            else
            {
                Minimize();
            }
        }
        
        public virtual void Minimize()
        {
            if (!isMinimized)
            {
                originalSize = GetComponent<RectTransform>().sizeDelta;
                originalPosition = transform.position;
                
                GetComponent<RectTransform>().sizeDelta = new Vector2(200, 30);
                isMinimized = true;
            }
        }
        
        public virtual void Restore()
        {
            if (isMinimized)
            {
                GetComponent<RectTransform>().sizeDelta = originalSize;
                transform.position = originalPosition;
                isMinimized = false;
            }
        }
        
        public virtual void ToggleMaximize()
        {
            if (isMaximized)
            {
                RestoreMaximize();
            }
            else
            {
                Maximize();
            }
        }
        
        public virtual void Maximize()
        {
            if (!isMaximized)
            {
                originalSize = GetComponent<RectTransform>().sizeDelta;
                originalPosition = transform.position;
                
                // Maximize to fill available space
                RectTransform parent = transform.parent as RectTransform;
                if (parent != null)
                {
                    GetComponent<RectTransform>().sizeDelta = parent.sizeDelta;
                    transform.position = parent.position;
                }
                
                isMaximized = true;
            }
        }
        
        public virtual void RestoreMaximize()
        {
            if (isMaximized)
            {
                GetComponent<RectTransform>().sizeDelta = originalSize;
                transform.position = originalPosition;
                isMaximized = false;
            }
        }
        
        public bool IsVisible()
        {
            return isVisible;
        }
        
        public bool IsMinimized()
        {
            return isMinimized;
        }
        
        public bool IsMaximized()
        {
            return isMaximized;
        }
        
        protected virtual void OnShow() { }
        protected virtual void OnHide() { }
    }
}
