using UnityEngine;

namespace AnimationApp.Drawing
{
    public abstract class CanvasAction
    {
        protected CanvasManager canvasManager;
        
        public CanvasAction(CanvasManager canvas)
        {
            canvasManager = canvas;
        }
        
        public abstract void Execute();
        public abstract void Undo();
    }
}
