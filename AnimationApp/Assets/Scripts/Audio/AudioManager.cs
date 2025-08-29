using UnityEngine;
using System.Collections.Generic;

namespace AnimationApp.Audio
{
    public class AudioManager : MonoBehaviour
    {
        [Header("Audio Settings")]
        public AudioClip currentAudioClip;
        public float volume = 1f;
        public bool mute = false;
        public float playbackRate = 1f;
        public float audioOffset = 0f;
        
        [Header("Waveform")]
        public Texture2D waveformTexture;
        public int waveformResolution = 512;
        public Color waveformColor = Color.blue;
        public Color waveformBackgroundColor = Color.gray;
        
        private AudioSource audioSource;
        private float[] audioSamples;
        private float[] waveformData;
        
        public System.Action<float> OnAudioTimeChanged;
        public System.Action<bool> OnAudioStateChanged;
        
        public void Initialize()
        {
            audioSource = GetComponent<AudioSource>();
            if (audioSource == null)
                audioSource = gameObject.AddComponent<AudioSource>();
            
            audioSource.playOnAwake = false;
            audioSource.loop = false;
        }
        
        public void LoadAudioClip(AudioClip clip)
        {
            currentAudioClip = clip;
            audioSource.clip = clip;
            
            if (clip != null)
            {
                GenerateWaveform();
            }
        }
        
        public void PlayAudio()
        {
            if (currentAudioClip != null && !mute)
            {
                audioSource.Play();
                OnAudioStateChanged?.Invoke(true);
            }
        }
        
        public void PauseAudio()
        {
            audioSource.Pause();
            OnAudioStateChanged?.Invoke(false);
        }
        
        public void StopAudio()
        {
            audioSource.Stop();
            audioSource.time = 0f;
            OnAudioStateChanged?.Invoke(false);
        }
        
        public void SetAudioTime(float time)
        {
            if (currentAudioClip != null)
            {
                audioSource.time = Mathf.Clamp(time + audioOffset, 0f, currentAudioClip.length);
                OnAudioTimeChanged?.Invoke(audioSource.time);
            }
        }
        
        public float GetAudioTime()
        {
            return audioSource.time;
        }
        
        public void SetVolume(float newVolume)
        {
            volume = Mathf.Clamp01(newVolume);
            audioSource.volume = mute ? 0f : volume;
        }
        
        public void SetMute(bool newMute)
        {
            mute = newMute;
            audioSource.volume = mute ? 0f : volume;
        }
        
        public void SetPlaybackRate(float rate)
        {
            playbackRate = Mathf.Clamp(rate, 0.1f, 3f);
            audioSource.pitch = playbackRate;
        }
        
        public void SetAudioOffset(float offset)
        {
            audioOffset = offset;
        }
        
        private void GenerateWaveform()
        {
            if (currentAudioClip == null) return;
            
            // Get audio data
            audioSamples = new float[currentAudioClip.samples * currentAudioClip.channels];
            currentAudioClip.GetData(audioSamples, 0);
            
            // Generate waveform data
            waveformData = new float[waveformResolution];
            int samplesPerPoint = audioSamples.Length / waveformResolution;
            
            for (int i = 0; i < waveformResolution; i++)
            {
                float sum = 0f;
                int startIndex = i * samplesPerPoint;
                int endIndex = Mathf.Min(startIndex + samplesPerPoint, audioSamples.Length);
                
                for (int j = startIndex; j < endIndex; j++)
                {
                    sum += Mathf.Abs(audioSamples[j]);
                }
                
                waveformData[i] = sum / samplesPerPoint;
            }
            
            // Create waveform texture
            CreateWaveformTexture();
        }
        
        private void CreateWaveformTexture()
        {
            if (waveformTexture == null)
            {
                waveformTexture = new Texture2D(waveformResolution, 64);
            }
            
            Color[] pixels = new Color[waveformResolution * 64];
            
            for (int x = 0; x < waveformResolution; x++)
            {
                float amplitude = waveformData[x];
                int height = Mathf.RoundToInt(amplitude * 64);
                
                for (int y = 0; y < 64; y++)
                {
                    Color color = waveformBackgroundColor;
                    
                    if (y < height)
                    {
                        color = waveformColor;
                    }
                    
                    pixels[y * waveformResolution + x] = color;
                }
            }
            
            waveformTexture.SetPixels(pixels);
            waveformTexture.Apply();
        }
        
        public Texture2D GetWaveformTexture()
        {
            return waveformTexture;
        }
        
        public float[] GetWaveformData()
        {
            return waveformData;
        }
        
        public float GetAudioLength()
        {
            return currentAudioClip != null ? currentAudioClip.length : 0f;
        }
        
        public bool IsAudioPlaying()
        {
            return audioSource.isPlaying;
        }
        
        public void Update()
        {
            if (audioSource.isPlaying)
            {
                OnAudioTimeChanged?.Invoke(audioSource.time);
            }
        }
    }
}
