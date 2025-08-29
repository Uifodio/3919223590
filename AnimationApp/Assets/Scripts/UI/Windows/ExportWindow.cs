using UnityEngine;
using UnityEngine.UI;
using AnimationApp.Export;

namespace AnimationApp.UI.Windows
{
    public class ExportWindow : UIWindow
    {
        [Header("Export Settings")]
        public Dropdown formatDropdown;
        public Slider fpsSlider;
        public Slider scaleSlider;
        public Toggle transparentBackgroundToggle;
        public InputField startFrameInput;
        public InputField endFrameInput;
        public Slider qualitySlider;
        
        [Header("Export Controls")]
        public Button exportButton;
        public Button cancelButton;
        public Slider progressSlider;
        public Text progressText;
        
        [Header("Preview")]
        public RawImage previewImage;
        public Text fileSizeText;
        public Text durationText;
        
        public System.Action<ExportSettings> OnExportRequested;
        
        private ExportSettings exportSettings;
        
        public override void Initialize()
        {
            base.Initialize();
            windowTitle = "Export Animation";
            
            SetupExportSettings();
            SetupControls();
            UpdatePreview();
        }
        
        private void SetupExportSettings()
        {
            exportSettings = new ExportSettings();
            
            if (formatDropdown != null)
            {
                formatDropdown.ClearOptions();
                formatDropdown.AddOptions(new System.Collections.Generic.List<string>
                {
                    "MP4",
                    "MOV",
                    "AVI",
                    "PNG Sequence",
                    "JPEG Sequence",
                    "GIF",
                    "XFL"
                });
                formatDropdown.onValueChanged.AddListener((index) => {
                    exportSettings.format = (ExportFormat)index;
                    UpdatePreview();
                });
            }
            
            if (fpsSlider != null)
            {
                fpsSlider.minValue = 1;
                fpsSlider.maxValue = 120;
                fpsSlider.value = 24;
                fpsSlider.onValueChanged.AddListener((value) => {
                    exportSettings.fps = (int)value;
                    UpdatePreview();
                });
            }
            
            if (scaleSlider != null)
            {
                scaleSlider.minValue = 0.1f;
                scaleSlider.maxValue = 5f;
                scaleSlider.value = 1f;
                scaleSlider.onValueChanged.AddListener((value) => {
                    exportSettings.scale = value;
                    UpdatePreview();
                });
            }
            
            if (transparentBackgroundToggle != null)
            {
                transparentBackgroundToggle.isOn = false;
                transparentBackgroundToggle.onValueChanged.AddListener((enabled) => {
                    exportSettings.transparentBackground = enabled;
                });
            }
            
            if (startFrameInput != null)
            {
                startFrameInput.text = "0";
                startFrameInput.onEndEdit.AddListener((text) => {
                    if (int.TryParse(text, out int value))
                    {
                        exportSettings.startFrame = value;
                        UpdatePreview();
                    }
                });
            }
            
            if (endFrameInput != null)
            {
                endFrameInput.text = "100";
                endFrameInput.onEndEdit.AddListener((text) => {
                    if (int.TryParse(text, out int value))
                    {
                        exportSettings.endFrame = value;
                        UpdatePreview();
                    }
                });
            }
            
            if (qualitySlider != null)
            {
                qualitySlider.minValue = 1;
                qualitySlider.maxValue = 100;
                qualitySlider.value = 80;
                qualitySlider.onValueChanged.AddListener((value) => {
                    exportSettings.quality = (int)value;
                });
            }
        }
        
        private void SetupControls()
        {
            if (exportButton != null)
                exportButton.onClick.AddListener(() => StartExport());
            
            if (cancelButton != null)
                cancelButton.onClick.AddListener(() => Hide());
        }
        
        private void UpdatePreview()
        {
            // Update preview information
            if (durationText != null)
            {
                float duration = (float)(exportSettings.endFrame - exportSettings.startFrame) / exportSettings.fps;
                durationText.text = $"Duration: {duration:F2}s";
            }
            
            if (fileSizeText != null)
            {
                // Estimate file size based on settings
                int frameCount = exportSettings.endFrame - exportSettings.startFrame;
                float estimatedSize = frameCount * exportSettings.scale * exportSettings.scale * 0.1f; // MB
                fileSizeText.text = $"Estimated Size: {estimatedSize:F1} MB";
            }
        }
        
        private void StartExport()
        {
            if (OnExportRequested != null)
            {
                OnExportRequested(exportSettings);
            }
            
            // Show progress
            if (progressSlider != null)
                progressSlider.gameObject.SetActive(true);
            
            if (progressText != null)
                progressText.text = "Exporting...";
        }
        
        public void UpdateProgress(float progress)
        {
            if (progressSlider != null)
                progressSlider.value = progress;
            
            if (progressText != null)
                progressText.text = $"Exporting... {progress:P0}";
        }
        
        public void ExportComplete(bool success)
        {
            if (progressText != null)
                progressText.text = success ? "Export Complete!" : "Export Failed!";
            
            if (success)
            {
                // Hide window after successful export
                Invoke(nameof(Hide), 2f);
            }
        }
    }
    
    [System.Serializable]
    public class ExportSettings
    {
        public ExportFormat format = ExportFormat.MP4;
        public int fps = 24;
        public float scale = 1f;
        public bool transparentBackground = false;
        public int startFrame = 0;
        public int endFrame = 100;
        public int quality = 80;
    }
}
