using UnityEngine;
using System.Collections.Generic;
using AnimationApp.Core;
using AnimationApp.Timeline;

namespace AnimationApp.Drawing
{
    public class CanvasManager : MonoBehaviour
    {
        [Header("Canvas Components")]
        public Camera canvasCamera;
        public RenderTexture canvasTexture;
        public Material canvasMaterial;
        
        [Header("Drawing Tools")]
        public BrushTool brushTool;
        public EraserTool eraserTool;
        public FillTool fillTool;
        public TransformTool transformTool;
        public SelectionTool selectionTool;
        
        [Header("Canvas Settings")]
        public int canvasWidth = 1920;
        public int canvasHeight = 1080;
        public float zoom = 1f;
        public Vector2 pan = Vector2.zero;
        public float rotation = 0f;
        
        private Dictionary<int, RenderTexture> frameTextures;
        private Stack<CanvasAction> undoStack;
        private Stack<CanvasAction> redoStack;
        private int currentFrame = 0;
        private bool isPlaying = false;
        
        public System.Action<int> OnFrameChanged;
        public System.Action<bool> OnPlaybackStateChanged;
        
        public void Initialize()
        {
            frameTextures = new Dictionary<int, RenderTexture>();
            undoStack = new Stack<CanvasAction>();
            redoStack = new Stack<CanvasAction>();
            
            // Initialize canvas texture
            canvasTexture = new RenderTexture(canvasWidth, canvasHeight, 0, RenderTextureFormat.ARGB32);
            canvasTexture.Create();
            
            // Initialize tools
            brushTool.Initialize(this);
            eraserTool.Initialize(this);
            fillTool.Initialize(this);
            transformTool.Initialize(this);
            selectionTool.Initialize(this);
            
            // Set up camera
            if (canvasCamera != null)
            {
                canvasCamera.targetTexture = canvasTexture;
                UpdateCameraTransform();
            }
            
            // Create first frame
            CreateFrame(0);
        }
        
        public void Update()
        {
            if (isPlaying)
            {
                // Handle playback
                HandlePlayback();
            }
            else
            {
                // Handle drawing input
                HandleDrawingInput();
            }
            
            // Handle canvas navigation
            HandleCanvasNavigation();
        }
        
        private void HandleDrawingInput()
        {
            // Handle mouse/touch input for drawing
            if (Input.GetMouseButton(0) || Input.GetMouseButton(1))
            {
                Vector2 mousePos = Input.mousePosition;
                Vector2 canvasPos = ScreenToCanvasPosition(mousePos);
                
                if (Input.GetMouseButton(0)) // Left click - draw
                {
                    brushTool.OnMouseDown(canvasPos);
                    brushTool.OnMouseDrag(canvasPos);
                }
                else if (Input.GetMouseButton(1)) // Right click - context menu
                {
                    ShowContextMenu(mousePos);
                }
            }
            
            if (Input.GetMouseButtonUp(0))
            {
                brushTool.OnMouseUp();
            }
        }
        
        private void HandlePlayback()
        {
            // Auto-advance frames during playback
            // This would be handled by the timeline manager
        }
        
        private void HandleCanvasNavigation()
        {
            // Handle zoom with mouse wheel
            if (Input.GetAxis("Mouse ScrollWheel") != 0)
            {
                float zoomDelta = Input.GetAxis("Mouse ScrollWheel") * 0.1f;
                zoom = Mathf.Clamp(zoom + zoomDelta, 0.1f, 10f);
                UpdateCameraTransform();
            }
            
            // Handle pan with middle mouse button
            if (Input.GetMouseButton(2))
            {
                Vector2 mouseDelta = new Vector2(Input.GetAxis("Mouse X"), Input.GetAxis("Mouse Y"));
                pan += mouseDelta * zoom;
                UpdateCameraTransform();
            }
        }
        
        private Vector2 ScreenToCanvasPosition(Vector2 screenPos)
        {
            // Convert screen position to canvas position
            Vector3 worldPos = canvasCamera.ScreenToWorldPoint(new Vector3(screenPos.x, screenPos.y, 0));
            return new Vector2(worldPos.x, worldPos.y);
        }
        
        private void UpdateCameraTransform()
        {
            if (canvasCamera != null)
            {
                canvasCamera.orthographicSize = canvasHeight / (2f * zoom);
                canvasCamera.transform.position = new Vector3(pan.x, pan.y, -10);
                canvasCamera.transform.rotation = Quaternion.Euler(0, 0, rotation);
            }
        }
        
        public void CreateFrame(int frameNumber)
        {
            if (!frameTextures.ContainsKey(frameNumber))
            {
                RenderTexture newFrame = new RenderTexture(canvasWidth, canvasHeight, 0, RenderTextureFormat.ARGB32);
                newFrame.Create();
                frameTextures[frameNumber] = newFrame;
            }
        }
        
        public void SetCurrentFrame(int frameNumber)
        {
            if (frameNumber != currentFrame)
            {
                currentFrame = frameNumber;
                CreateFrame(frameNumber);
                
                // Load frame texture to canvas
                if (frameTextures.ContainsKey(frameNumber))
                {
                    Graphics.Blit(frameTextures[frameNumber], canvasTexture);
                }
                
                OnFrameChanged?.Invoke(frameNumber);
            }
        }
        
        public void Undo()
        {
            if (undoStack.Count > 0)
            {
                CanvasAction action = undoStack.Pop();
                action.Undo();
                redoStack.Push(action);
            }
        }
        
        public void Redo()
        {
            if (redoStack.Count > 0)
            {
                CanvasAction action = redoStack.Pop();
                action.Execute();
                undoStack.Push(action);
            }
        }
        
        public void AddAction(CanvasAction action)
        {
            action.Execute();
            undoStack.Push(action);
            redoStack.Clear(); // Clear redo stack when new action is added
        }
        
        private void ShowContextMenu(Vector2 position)
        {
            // Show context menu for canvas
            // This would be implemented in the UI system
        }
        
        // Event handlers for timeline
        public void OnFrameChanged(int frameNumber)
        {
            SetCurrentFrame(frameNumber);
        }
        
        public void OnPlaybackStateChanged(bool playing)
        {
            isPlaying = playing;
            OnPlaybackStateChanged?.Invoke(playing);
        }
        
        // Event handlers for layers
        public void OnLayerAdded(LayerData layerData) { }
        public void OnLayerRemoved(LayerData layerData) { }
        public void OnLayerVisibilityChanged(LayerData layerData) { }
        
        // Event handlers for tools
        public void OnToolChanged(ToolType toolType) { }
        
        // Data serialization
        public CanvasData GetCanvasData()
        {
            return new CanvasData
            {
                canvasWidth = canvasWidth,
                canvasHeight = canvasHeight,
                zoom = zoom,
                pan = pan,
                rotation = rotation,
                currentFrame = currentFrame
            };
        }
        
        public void LoadCanvasData(CanvasData data)
        {
            canvasWidth = data.canvasWidth;
            canvasHeight = data.canvasHeight;
            zoom = data.zoom;
            pan = data.pan;
            rotation = data.rotation;
            currentFrame = data.currentFrame;
            
            UpdateCameraTransform();
        }
    }
    
    [System.Serializable]
    public class CanvasData
    {
        public int canvasWidth;
        public int canvasHeight;
        public float zoom;
        public Vector2 pan;
        public float rotation;
        public int currentFrame;
    }
}
