using UnityEngine;
using UnityEngine.UI;

namespace AnimationApp.UI.Panels
{
    public class StatusBar : MonoBehaviour
    {
        [Header("Status Information")]
        public Text currentToolText;
        public Text frameInfoText;
        public Text zoomInfoText;
        public Text playbackStatusText;
        public Text statusText;
        
        public void Initialize()
        {
            UpdateStatus("Ready");
        }
        
        public void UpdateStatus(string status)
        {
            if (statusText != null)
                statusText.text = status;
        }
        
        public void UpdateCurrentTool(string toolName)
        {
            if (currentToolText != null)
                currentToolText.text = $"Tool: {toolName}";
        }
        
        public void UpdateFrameInfo(int currentFrame, int totalFrames)
        {
            if (frameInfoText != null)
                frameInfoText.text = $"Frame: {currentFrame + 1}/{totalFrames}";
        }
        
        public void UpdateZoomInfo(float zoom)
        {
            if (zoomInfoText != null)
                zoomInfoText.text = $"Zoom: {zoom:P0}";
        }
        
        public void UpdatePlaybackStatus(bool isPlaying)
        {
            if (playbackStatusText != null)
                playbackStatusText.text = isPlaying ? "Playing" : "Stopped";
        }
    }
}
