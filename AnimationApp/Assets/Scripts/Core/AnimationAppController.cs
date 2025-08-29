using UnityEngine;
using AnimationApp.Drawing;
using AnimationApp.Timeline;
using AnimationApp.Audio;
using AnimationApp.Export;
using AnimationApp.UI;

namespace AnimationApp.Core
{
    public class AnimationAppController : MonoBehaviour
    {
        [Header("Core Systems")]
        public CanvasManager canvasManager;
        public TimelineManager timelineManager;
        public LayerManager layerManager;
        public ToolManager toolManager;
        public AudioManager audioManager;
        public ExportManager exportManager;
        public UIManager uiManager;
        
        [Header("Settings")]
        public AnimationAppSettings settings;
        
        private static AnimationAppController instance;
        public static AnimationAppController Instance => instance;
        
        private void Awake()
        {
            if (instance == null)
            {
                instance = this;
                DontDestroyOnLoad(gameObject);
                InitializeApplication();
            }
            else
            {
                Destroy(gameObject);
            }
        }
        
        private void InitializeApplication()
        {
            // Initialize all core systems
            if (canvasManager != null) canvasManager.Initialize();
            if (timelineManager != null) timelineManager.Initialize();
            if (layerManager != null) layerManager.Initialize();
            if (toolManager != null) toolManager.Initialize();
            if (audioManager != null) audioManager.Initialize();
            if (exportManager != null) exportManager.Initialize();
            if (uiManager != null) uiManager.Initialize();
            
            // Set up event connections
            SetupEventConnections();
            
            Debug.Log("Animation App initialized successfully");
        }
        
        private void SetupEventConnections()
        {
            // Connect timeline events to canvas
            if (timelineManager != null && canvasManager != null)
            {
                timelineManager.OnFrameChanged += canvasManager.OnFrameChanged;
                timelineManager.OnPlaybackStateChanged += canvasManager.OnPlaybackStateChanged;
            }
            
            // Connect layer events
            if (layerManager != null && canvasManager != null)
            {
                layerManager.OnLayerAdded += canvasManager.OnLayerAdded;
                layerManager.OnLayerRemoved += canvasManager.OnLayerRemoved;
                layerManager.OnLayerVisibilityChanged += canvasManager.OnLayerVisibilityChanged;
            }
            
            // Connect tool events
            if (toolManager != null && canvasManager != null)
            {
                toolManager.OnToolChanged += canvasManager.OnToolChanged;
            }
            
            // Connect UI events
            if (uiManager != null && canvasManager != null)
            {
                uiManager.OnUndoRequested += canvasManager.Undo;
                uiManager.OnRedoRequested += canvasManager.Redo;
            }
        }
        
        private void Update()
        {
            // Handle global input
            HandleGlobalInput();
            
            // Update systems
            if (timelineManager != null) timelineManager.Update();
            if (canvasManager != null) canvasManager.Update();
        }
        
        private void HandleGlobalInput()
        {
            // Global keyboard shortcuts
            if (Input.GetKey(KeyCode.LeftControl) || Input.GetKey(KeyCode.RightControl))
            {
                if (Input.GetKeyDown(KeyCode.Z))
                {
                    if (Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift))
                        canvasManager?.Redo();
                    else
                        canvasManager?.Undo();
                }
                else if (Input.GetKeyDown(KeyCode.S))
                {
                    SaveProject();
                }
                else if (Input.GetKeyDown(KeyCode.O))
                {
                    LoadProject();
                }
            }
            
            // Tool shortcuts
            if (Input.GetKeyDown(KeyCode.B))
                toolManager?.SetTool(ToolType.Brush);
            else if (Input.GetKeyDown(KeyCode.E))
                toolManager?.SetTool(ToolType.Eraser);
            else if (Input.GetKeyDown(KeyCode.F))
                toolManager?.SetTool(ToolType.Fill);
            else if (Input.GetKeyDown(KeyCode.T))
                toolManager?.SetTool(ToolType.Transform);
            else if (Input.GetKeyDown(KeyCode.S))
                toolManager?.SetTool(ToolType.Selection);
            else if (Input.GetKeyDown(KeyCode.H))
                toolManager?.SetTool(ToolType.Hand);
            else if (Input.GetKeyDown(KeyCode.Z))
                toolManager?.SetTool(ToolType.Zoom);
            
            // Timeline shortcuts
            if (Input.GetKeyDown(KeyCode.Space))
            {
                if (timelineManager != null)
                {
                    if (timelineManager.isPlaying)
                        timelineManager.Pause();
                    else
                        timelineManager.Play();
                }
            }
            else if (Input.GetKeyDown(KeyCode.RightArrow))
                timelineManager?.NextFrame();
            else if (Input.GetKeyDown(KeyCode.LeftArrow))
                timelineManager?.PreviousFrame();
        }
        
        public void SaveProject()
        {
            // Save current project state
            ProjectData projectData = new ProjectData
            {
                timelineData = timelineManager?.GetTimelineData(),
                layerData = layerManager?.GetTimelineData(),
                canvasData = canvasManager?.GetCanvasData(),
                settings = settings
            };
            
            string json = JsonUtility.ToJson(projectData, true);
            string path = System.IO.Path.Combine(Application.persistentDataPath, "project.json");
            System.IO.File.WriteAllText(path, json);
            Debug.Log($"Project saved to: {path}");
        }
        
        public void LoadProject()
        {
            string path = System.IO.Path.Combine(Application.persistentDataPath, "project.json");
            if (System.IO.File.Exists(path))
            {
                string json = System.IO.File.ReadAllText(path);
                ProjectData projectData = JsonUtility.FromJson<ProjectData>(json);
                
                if (timelineManager != null) timelineManager.LoadTimelineData(projectData.timelineData);
                if (layerManager != null) layerManager.LoadLayerData(projectData.layerData);
                if (canvasManager != null) canvasManager.LoadCanvasData(projectData.canvasData);
                settings = projectData.settings;
                
                Debug.Log($"Project loaded from: {path}");
            }
        }
        
        private void OnApplicationPause(bool pauseStatus)
        {
            if (pauseStatus && settings.autoSave)
            {
                SaveProject(); // Autosave when app is paused
            }
        }
        
        private void OnApplicationFocus(bool hasFocus)
        {
            if (!hasFocus && settings.autoSave)
            {
                SaveProject(); // Autosave when app loses focus
            }
        }
    }
    
    [System.Serializable]
    public class ProjectData
    {
        public TimelineData timelineData;
        public LayerData layerData;
        public CanvasData canvasData;
        public AnimationAppSettings settings;
    }
}
