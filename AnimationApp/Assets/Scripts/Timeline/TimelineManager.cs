using UnityEngine;
using System.Collections.Generic;
using System.Collections;

namespace AnimationApp.Timeline
{
    public class TimelineManager : MonoBehaviour
    {
        [Header("Timeline Settings")]
        public int currentFrame = 0;
        public int totalFrames = 100;
        public int fps = 24;
        public bool isPlaying = false;
        public bool isLooping = true;
        
        [Header("Onion Skinning")]
        public bool onionSkinEnabled = true;
        public int onionSkinBefore = 2;
        public int onionSkinAfter = 2;
        public float onionSkinOpacity = 0.3f;
        
        [Header("Audio")]
        public AudioClip audioClip;
        public bool audioEnabled = true;
        public float audioOffset = 0f;
        
        private List<FrameData> frames;
        private float frameTimer = 0f;
        private AudioSource audioSource;
        
        public System.Action<int> OnFrameChanged;
        public System.Action<bool> OnPlaybackStateChanged;
        public System.Action<float> OnTimeChanged;
        
        public void Initialize()
        {
            frames = new List<FrameData>();
            audioSource = GetComponent<AudioSource>();
            
            if (audioSource == null)
                audioSource = gameObject.AddComponent<AudioSource>();
            
            // Initialize frames
            for (int i = 0; i < totalFrames; i++)
            {
                frames.Add(new FrameData { frameNumber = i, exposure = 1 });
            }
            
            // Set up audio
            if (audioClip != null)
            {
                audioSource.clip = audioClip;
                audioSource.playOnAwake = false;
            }
        }
        
        public void Update()
        {
            if (isPlaying)
            {
                UpdatePlayback();
            }
        }
        
        private void UpdatePlayback()
        {
            frameTimer += Time.deltaTime;
            float frameTime = 1f / fps;
            
            if (frameTimer >= frameTime)
            {
                frameTimer -= frameTime;
                NextFrame();
            }
            
            // Update audio sync
            if (audioEnabled && audioSource.clip != null)
            {
                float currentTime = (float)currentFrame / fps;
                if (Mathf.Abs(audioSource.time - currentTime) > 0.1f)
                {
                    audioSource.time = currentTime + audioOffset;
                }
            }
            
            OnTimeChanged?.Invoke(GetCurrentTime());
        }
        
        public void Play()
        {
            isPlaying = true;
            OnPlaybackStateChanged?.Invoke(true);
            
            if (audioEnabled && audioSource.clip != null)
            {
                audioSource.Play();
            }
        }
        
        public void Pause()
        {
            isPlaying = false;
            OnPlaybackStateChanged?.Invoke(false);
            
            if (audioSource.isPlaying)
            {
                audioSource.Pause();
            }
        }
        
        public void Stop()
        {
            isPlaying = false;
            OnPlaybackStateChanged?.Invoke(false);
            
            currentFrame = 0;
            frameTimer = 0f;
            
            if (audioSource.isPlaying)
            {
                audioSource.Stop();
                audioSource.time = 0f;
            }
        }
        
        public void NextFrame()
        {
            if (currentFrame < totalFrames - 1)
            {
                currentFrame++;
                OnFrameChanged?.Invoke(currentFrame);
            }
            else if (isLooping)
            {
                currentFrame = 0;
                OnFrameChanged?.Invoke(currentFrame);
            }
            else
            {
                Pause();
            }
        }
        
        public void PreviousFrame()
        {
            if (currentFrame > 0)
            {
                currentFrame--;
                OnFrameChanged?.Invoke(currentFrame);
            }
        }
        
        public void SetFrame(int frameNumber)
        {
            frameNumber = Mathf.Clamp(frameNumber, 0, totalFrames - 1);
            if (frameNumber != currentFrame)
            {
                currentFrame = frameNumber;
                OnFrameChanged?.Invoke(currentFrame);
                
                // Update audio position
                if (audioEnabled && audioSource.clip != null)
                {
                    audioSource.time = (float)currentFrame / fps + audioOffset;
                }
            }
        }
        
        public void InsertFrame(int frameNumber)
        {
            if (frameNumber >= 0 && frameNumber <= totalFrames)
            {
                frames.Insert(frameNumber, new FrameData { frameNumber = frameNumber, exposure = 1 });
                totalFrames++;
                
                // Update frame numbers
                for (int i = frameNumber + 1; i < frames.Count; i++)
                {
                    frames[i].frameNumber = i;
                }
            }
        }
        
        public void DeleteFrame(int frameNumber)
        {
            if (frameNumber >= 0 && frameNumber < frames.Count)
            {
                frames.RemoveAt(frameNumber);
                totalFrames--;
                
                // Update frame numbers
                for (int i = frameNumber; i < frames.Count; i++)
                {
                    frames[i].frameNumber = i;
                }
                
                if (currentFrame >= totalFrames)
                {
                    currentFrame = totalFrames - 1;
                }
            }
        }
        
        public void DuplicateFrame(int frameNumber)
        {
            if (frameNumber >= 0 && frameNumber < frames.Count)
            {
                FrameData duplicate = new FrameData
                {
                    frameNumber = frameNumber + 1,
                    exposure = frames[frameNumber].exposure
                };
                
                frames.Insert(frameNumber + 1, duplicate);
                totalFrames++;
                
                // Update frame numbers
                for (int i = frameNumber + 2; i < frames.Count; i++)
                {
                    frames[i].frameNumber = i;
                }
            }
        }
        
        public float GetCurrentTime()
        {
            return (float)currentFrame / fps;
        }
        
        public void SetFPS(int newFPS)
        {
            fps = Mathf.Clamp(newFPS, 1, 120);
        }
        
        public void SetAudioClip(AudioClip clip)
        {
            audioClip = clip;
            if (audioSource != null)
            {
                audioSource.clip = clip;
            }
        }
        
        public TimelineData GetTimelineData()
        {
            return new TimelineData
            {
                currentFrame = currentFrame,
                totalFrames = totalFrames,
                fps = fps,
                isPlaying = isPlaying,
                isLooping = isLooping,
                onionSkinEnabled = onionSkinEnabled,
                onionSkinBefore = onionSkinBefore,
                onionSkinAfter = onionSkinAfter,
                onionSkinOpacity = onionSkinOpacity,
                audioEnabled = audioEnabled,
                audioOffset = audioOffset,
                frames = frames.ToArray()
            };
        }
        
        public void LoadTimelineData(TimelineData data)
        {
            currentFrame = data.currentFrame;
            totalFrames = data.totalFrames;
            fps = data.fps;
            isPlaying = data.isPlaying;
            isLooping = data.isLooping;
            onionSkinEnabled = data.onionSkinEnabled;
            onionSkinBefore = data.onionSkinBefore;
            onionSkinAfter = data.onionSkinAfter;
            onionSkinOpacity = data.onionSkinOpacity;
            audioEnabled = data.audioEnabled;
            audioOffset = data.audioOffset;
            
            frames.Clear();
            frames.AddRange(data.frames);
        }
    }
    
    [System.Serializable]
    public class FrameData
    {
        public int frameNumber;
        public int exposure = 1;
        public bool isKeyframe = false;
    }
    
    [System.Serializable]
    public class TimelineData
    {
        public int currentFrame;
        public int totalFrames;
        public int fps;
        public bool isPlaying;
        public bool isLooping;
        public bool onionSkinEnabled;
        public int onionSkinBefore;
        public int onionSkinAfter;
        public float onionSkinOpacity;
        public bool audioEnabled;
        public float audioOffset;
        public FrameData[] frames;
    }
}
