using UnityEngine;
using AnimationApp.Core;

namespace AnimationApp.Drawing
{
    public class BrushTool : MonoBehaviour
    {
        [Header("Brush Settings")]
        public float size = 5f;
        public float opacity = 1f;
        public float hardness = 0.5f;
        public Texture2D brushTexture;
        public bool pressureSensitivity = true;
        
        [Header("Brush Types")]
        public BrushType brushType = BrushType.Round;
        public float spacing = 0.5f;
        public float angle = 0f;
        
        private CanvasManager canvasManager;
        private Vector2 lastPosition;
        private bool isDrawing = false;
        private Material brushMaterial;
        
        public void Initialize(CanvasManager manager)
        {
            canvasManager = manager;
            brushMaterial = new Material(Shader.Find("Unlit/Texture"));
            
            if (brushTexture == null)
            {
                CreateDefaultBrushTexture();
            }
        }
        
        private void CreateDefaultBrushTexture()
        {
            brushTexture = new Texture2D(64, 64);
            Color[] pixels = new Color[64 * 64];
            
            for (int y = 0; y < 64; y++)
            {
                for (int x = 0; x < 64; x++)
                {
                    float distance = Vector2.Distance(new Vector2(x, y), new Vector2(32, 32));
                    float alpha = Mathf.Clamp01(1f - (distance / 32f));
                    alpha = Mathf.Pow(alpha, hardness);
                    pixels[y * 64 + x] = new Color(1, 1, 1, alpha);
                }
            }
            
            brushTexture.SetPixels(pixels);
            brushTexture.Apply();
        }
        
        public void OnMouseDown(Vector2 position)
        {
            lastPosition = position;
            isDrawing = true;
            
            // Start new stroke
            DrawBrushStroke(position, position);
        }
        
        public void OnMouseDrag(Vector2 position)
        {
            if (isDrawing)
            {
                // Draw line between last position and current position
                DrawLine(lastPosition, position);
                lastPosition = position;
            }
        }
        
        public void OnMouseUp()
        {
            isDrawing = false;
            
            // Create undo action
            BrushStrokeAction action = new BrushStrokeAction(canvasManager, lastPosition);
            canvasManager.AddAction(action);
        }
        
        private void DrawLine(Vector2 start, Vector2 end)
        {
            float distance = Vector2.Distance(start, end);
            int steps = Mathf.CeilToInt(distance / (size * spacing));
            
            for (int i = 0; i <= steps; i++)
            {
                float t = (float)i / steps;
                Vector2 position = Vector2.Lerp(start, end, t);
                DrawBrushStroke(position, position);
            }
        }
        
        private void DrawBrushStroke(Vector2 position, Vector2 pressure)
        {
            // Calculate brush size based on pressure
            float currentSize = size;
            if (pressureSensitivity)
            {
                // Simulate pressure sensitivity (in real implementation, this would come from input device)
                currentSize *= Random.Range(0.8f, 1.2f);
            }
            
            // Create brush stamp at position
            Vector2 stampSize = new Vector2(currentSize, currentSize);
            Vector2 stampPosition = position - stampSize * 0.5f;
            
            // Apply brush texture to canvas
            ApplyBrushStamp(stampPosition, stampSize);
        }
        
        private void ApplyBrushStamp(Vector2 position, Vector2 size)
        {
            // This would apply the brush texture to the canvas at the specified position
            // In a real implementation, this would use Graphics.Blit or similar
            // For now, we'll just log the action
            Debug.Log($"Brush stamp at {position} with size {size}");
        }
        
        public void SetSize(float newSize)
        {
            size = Mathf.Clamp(newSize, 1f, 100f);
        }
        
        public void SetOpacity(float newOpacity)
        {
            opacity = Mathf.Clamp01(newOpacity);
        }
        
        public void SetHardness(float newHardness)
        {
            hardness = Mathf.Clamp01(newHardness);
            if (brushTexture != null)
            {
                CreateDefaultBrushTexture(); // Recreate with new hardness
            }
        }
    }
    
    public enum BrushType
    {
        Round,
        Square,
        Custom
    }
    
    public class BrushStrokeAction : CanvasAction
    {
        private Vector2 position;
        private RenderTexture previousState;
        
        public BrushStrokeAction(CanvasManager canvas, Vector2 pos)
        {
            position = pos;
            // Store previous state for undo
            previousState = new RenderTexture(canvas.canvasTexture);
            Graphics.Blit(canvas.canvasTexture, previousState);
        }
        
        public override void Execute()
        {
            // Apply brush stroke
        }
        
        public override void Undo()
        {
            // Restore previous state
            Graphics.Blit(previousState, canvasManager.canvasTexture);
        }
    }
}
