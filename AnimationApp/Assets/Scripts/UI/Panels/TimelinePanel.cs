using UnityEngine;
using UnityEngine.UI;
using AnimationApp.Timeline;

namespace AnimationApp.UI.Panels
{
    public class TimelinePanel : MonoBehaviour
    {
        [Header("Timeline Controls")]
        public Button playButton;
        public Button pauseButton;
        public Button stopButton;
        public Button firstFrameButton;
        public Button lastFrameButton;
        public Button nextFrameButton;
        public Button previousFrameButton;
        
        [Header("Timeline Display")]
        public Slider timelineSlider;
        public Text frameNumberText;
        public Text totalFramesText;
        public Text fpsText;
        
        [Header("Frame Management")]
        public Button insertFrameButton;
        public Button deleteFrameButton;
        public Button duplicateFrameButton;
        
        [Header("Onion Skinning")]
        public Toggle onionSkinToggle;
        public Slider onionSkinBeforeSlider;
        public Slider onionSkinAfterSlider;
        public Slider onionSkinOpacitySlider;
        
        [Header("Audio")]
        public RawImage waveformImage;
        public Slider audioVolumeSlider;
        public Toggle audioMuteToggle;
        
        public System.Action<int> OnFrameChanged;
        public System.Action<bool> OnPlaybackStateChanged;
        public System.Action OnInsertFrame;
        public System.Action OnDeleteFrame;
        public System.Action OnDuplicateFrame;
        
        public void Initialize()
        {
            SetupTimelineControls();
            SetupFrameManagement();
            SetupOnionSkinning();
            SetupAudio();
        }
        
        private void SetupTimelineControls()
        {
            if (playButton != null)
                playButton.onClick.AddListener(() => OnPlaybackStateChanged?.Invoke(true));
            
            if (pauseButton != null)
                pauseButton.onClick.AddListener(() => OnPlaybackStateChanged?.Invoke(false));
            
            if (stopButton != null)
                stopButton.onClick.AddListener(() => StopPlayback());
            
            if (firstFrameButton != null)
                firstFrameButton.onClick.AddListener(() => SetFrame(0));
            
            if (lastFrameButton != null)
                lastFrameButton.onClick.AddListener(() => SetFrame(GetTotalFrames() - 1));
            
            if (nextFrameButton != null)
                nextFrameButton.onClick.AddListener(() => NextFrame());
            
            if (previousFrameButton != null)
                previousFrameButton.onClick.AddListener(() => PreviousFrame());
            
            if (timelineSlider != null)
                timelineSlider.onValueChanged.AddListener((value) => SetFrame((int)value));
        }
        
        private void SetupFrameManagement()
        {
            if (insertFrameButton != null)
                insertFrameButton.onClick.AddListener(() => OnInsertFrame?.Invoke());
            
            if (deleteFrameButton != null)
                deleteFrameButton.onClick.AddListener(() => OnDeleteFrame?.Invoke());
            
            if (duplicateFrameButton != null)
                duplicateFrameButton.onClick.AddListener(() => OnDuplicateFrame?.Invoke());
        }
        
        private void SetupOnionSkinning()
        {
            if (onionSkinToggle != null)
                onionSkinToggle.onValueChanged.AddListener((enabled) => SetOnionSkinEnabled(enabled));
            
            if (onionSkinBeforeSlider != null)
                onionSkinBeforeSlider.onValueChanged.AddListener((value) => SetOnionSkinBefore((int)value));
            
            if (onionSkinAfterSlider != null)
                onionSkinAfterSlider.onValueChanged.AddListener((value) => SetOnionSkinAfter((int)value));
            
            if (onionSkinOpacitySlider != null)
                onionSkinOpacitySlider.onValueChanged.AddListener((value) => SetOnionSkinOpacity(value));
        }
        
        private void SetupAudio()
        {
            if (audioVolumeSlider != null)
                audioVolumeSlider.onValueChanged.AddListener((value) => SetAudioVolume(value));
            
            if (audioMuteToggle != null)
                audioMuteToggle.onValueChanged.AddListener((muted) => SetAudioMute(muted));
        }
        
        public void UpdateTimeline(int currentFrame, int totalFrames)
        {
            if (timelineSlider != null)
            {
                timelineSlider.minValue = 0;
                timelineSlider.maxValue = totalFrames - 1;
                timelineSlider.value = currentFrame;
            }
            
            if (frameNumberText != null)
                frameNumberText.text = currentFrame.ToString();
            
            if (totalFramesText != null)
                totalFramesText.text = totalFrames.ToString();
        }
        
        public void UpdatePlaybackState(bool isPlaying)
        {
            if (playButton != null)
                playButton.interactable = !isPlaying;
            
            if (pauseButton != null)
                pauseButton.interactable = isPlaying;
        }
        
        public void SetFrame(int frameNumber)
        {
            OnFrameChanged?.Invoke(frameNumber);
        }
        
        public void NextFrame()
        {
            int currentFrame = GetCurrentFrame();
            SetFrame(currentFrame + 1);
        }
        
        public void PreviousFrame()
        {
            int currentFrame = GetCurrentFrame();
            SetFrame(currentFrame - 1);
        }
        
        public void StopPlayback()
        {
            OnPlaybackStateChanged?.Invoke(false);
        }
        
        public void SetOnionSkinEnabled(bool enabled)
        {
            // Update onion skinning
        }
        
        public void SetOnionSkinBefore(int frames)
        {
            // Update onion skin before frames
        }
        
        public void SetOnionSkinAfter(int frames)
        {
            // Update onion skin after frames
        }
        
        public void SetOnionSkinOpacity(float opacity)
        {
            // Update onion skin opacity
        }
        
        public void SetAudioVolume(float volume)
        {
            // Update audio volume
        }
        
        public void SetAudioMute(bool muted)
        {
            // Update audio mute state
        }
        
        public void UpdateWaveform(Texture2D waveform)
        {
            if (waveformImage != null)
            {
                waveformImage.texture = waveform;
            }
        }
        
        private int GetCurrentFrame()
        {
            return timelineSlider != null ? (int)timelineSlider.value : 0;
        }
        
        private int GetTotalFrames()
        {
            return timelineSlider != null ? (int)timelineSlider.maxValue + 1 : 100;
        }
    }
}
