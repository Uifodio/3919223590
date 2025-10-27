using UnityEngine;
using AnimationApp.UI.Panels;
using AnimationApp.UI.Windows;
using AnimationApp.Core;

namespace AnimationApp.UI
{
    public class UIManager : MonoBehaviour
    {
        [Header("Main UI Panels")]
        public MainMenuBar mainMenuBar;
        public ToolbarPanel toolbarPanel;
        public TimelinePanel timelinePanel;
        public PropertiesPanel propertiesPanel;
        public StatusBar statusBar;
        
        [Header("Floating Windows")]
        public BrushSettingsWindow brushSettingsWindow;
        public ExportWindow exportWindow;
        public PreferencesWindow preferencesWindow;
        
        [Header("UI Settings")]
        public bool showGrid = true;
        public bool showRulers = true;
        public Color uiThemeColor = Color.blue;
        
        public System.Action OnUndoRequested;
        public System.Action OnRedoRequested;
        
        public void Initialize()
        {
            // Initialize all UI panels
            if (mainMenuBar != null) mainMenuBar.Initialize();
            if (toolbarPanel != null) toolbarPanel.Initialize();
            if (timelinePanel != null) timelinePanel.Initialize();
            if (propertiesPanel != null) propertiesPanel.Initialize();
            if (statusBar != null) statusBar.Initialize();
            
            // Initialize floating windows
            if (brushSettingsWindow != null) brushSettingsWindow.Initialize();
            if (exportWindow != null) exportWindow.Initialize();
            if (preferencesWindow != null) preferencesWindow.Initialize();
            
            // Set up event connections
            SetupEventConnections();
            
            // Apply UI theme
            ApplyUITheme();
        }
        
        private void SetupEventConnections()
        {
            // Connect toolbar events
            if (toolbarPanel != null)
            {
                toolbarPanel.OnUndoClicked += () => OnUndoRequested?.Invoke();
                toolbarPanel.OnRedoClicked += () => OnRedoRequested?.Invoke();
                toolbarPanel.OnToolChanged += (toolType) => {
                    // Handle tool change
                };
            }
            
            // Connect timeline events
            if (timelinePanel != null)
            {
                timelinePanel.OnFrameChanged += (frame) => {
                    // Handle frame change
                };
                timelinePanel.OnPlaybackStateChanged += (playing) => {
                    // Handle playback state change
                };
            }
            
            // Connect properties panel events
            if (propertiesPanel != null)
            {
                propertiesPanel.OnLayerSelected += (layer) => {
                    // Handle layer selection
                };
                propertiesPanel.OnLayerVisibilityChanged += (layer, visible) => {
                    // Handle layer visibility change
                };
            }
        }
        
        private void ApplyUITheme()
        {
            // Apply the UI theme color to all UI elements
            // This would update colors, styles, etc.
        }
        
        public void ShowWindow(UIWindow window)
        {
            if (window != null)
            {
                window.Show();
            }
        }
        
        public void HideWindow(UIWindow window)
        {
            if (window != null)
            {
                window.Hide();
            }
        }
        
        public void ToggleWindow(UIWindow window)
        {
            if (window != null)
            {
                if (window.IsVisible())
                {
                    window.Hide();
                }
                else
                {
                    window.Show();
                }
            }
        }
        
        public void UpdateStatus(string status)
        {
            if (statusBar != null)
            {
                statusBar.UpdateStatus(status);
            }
        }
        
        public void UpdateFrameInfo(int currentFrame, int totalFrames)
        {
            if (statusBar != null)
            {
                statusBar.UpdateFrameInfo(currentFrame, totalFrames);
            }
        }
        
        public void UpdateZoomInfo(float zoom)
        {
            if (statusBar != null)
            {
                statusBar.UpdateZoomInfo(zoom);
            }
        }
        
        public void SetShowGrid(bool show)
        {
            showGrid = show;
            // Update grid visibility
        }
        
        public void SetShowRulers(bool show)
        {
            showRulers = show;
            // Update rulers visibility
        }
    }
}
