using System;
using System.IO;
using Newtonsoft.Json;
using WindowsFileManagerPro.Models;
using System.Collections.Generic; // Added missing import for List
using System.Collections.Generic; // Added missing import for Dictionary

namespace WindowsFileManagerPro.Services
{
    public class ConfigurationService : IConfigurationService
    {
        private readonly string _settingsDirectory;
        private readonly string _settingsFilePath;
        private AppSettings? _cachedSettings;

        public ConfigurationService()
        {
            _settingsDirectory = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                "WindowsFileManagerPro");
            _settingsFilePath = Path.Combine(_settingsDirectory, "settings.json");
        }

        public AppSettings? GetSettings()
        {
            try
            {
                if (_cachedSettings != null)
                    return _cachedSettings;

                if (!File.Exists(_settingsFilePath))
                {
                    var defaultSettings = GetDefaultSettings();
                    SaveSettings(defaultSettings);
                    return defaultSettings;
                }

                var json = File.ReadAllText(_settingsFilePath);
                _cachedSettings = JsonConvert.DeserializeObject<AppSettings>(json);
                
                // Validate and fix any corrupted settings
                if (_cachedSettings != null && !ValidateSettings(_cachedSettings))
                {
                    _cachedSettings = GetDefaultSettings();
                    SaveSettings(_cachedSettings);
                }

                return _cachedSettings;
            }
            catch (Exception)
            {
                // Return default settings if loading fails
                return GetDefaultSettings();
            }
        }

        public bool SaveSettings(AppSettings settings)
        {
            try
            {
                if (settings == null)
                    return false;

                // Validate settings before saving
                if (!ValidateSettings(settings))
                    return false;

                // Ensure directory exists
                if (!Directory.Exists(_settingsDirectory))
                {
                    Directory.CreateDirectory(_settingsDirectory);
                }

                // Create backup of existing settings
                if (File.Exists(_settingsFilePath))
                {
                    var backupPath = _settingsFilePath + ".bak";
                    File.Copy(_settingsFilePath, backupPath, true);
                }

                // Serialize and save settings
                var json = JsonConvert.SerializeObject(settings, Formatting.Indented);
                File.WriteAllText(_settingsFilePath, json);

                // Update cache
                _cachedSettings = settings;
                return true;
            }
            catch (Exception)
            {
                return false;
            }
        }

        public AppSettings GetDefaultSettings()
        {
            return new AppSettings
            {
                Theme = "Dark",
                WindowWidth = 1200,
                WindowHeight = 800,
                WindowLeft = -1,
                WindowTop = -1,
                Maximized = false,
                TreeViewWidth = 250,
                DefaultPath = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
                RecentPaths = new List<string>(),
                FavoritePaths = new List<string>(),
                Editor = new EditorSettings
                {
                    FontFamily = "Consolas",
                    FontSize = 12,
                    ShowLineNumbers = true,
                    ShowWhitespace = false,
                    WordWrap = false,
                    AutoSave = true,
                    AutoSaveInterval = 30,
                    SyntaxHighlighting = true,
                    FileAssociations = new Dictionary<string, string>()
                },
                Search = new SearchSettings
                {
                    CaseSensitive = false,
                    UseRegex = false,
                    SearchInArchives = true,
                    MaxResults = 1000,
                    ExcludePatterns = new List<string> { "*.tmp", "*.bak", "*.log" },
                    IncludePatterns = new List<string>()
                },
                Zip = new ZipSettings
                {
                    OpenAsFolder = true,
                    AutoBackup = true,
                    BackupExtension = ".bak",
                    CompressOnSave = false,
                    CompressionLevel = 6
                },
                Backup = new BackupSettings
                {
                    AutoBackup = true,
                    BackupExtension = ".bak",
                    MaxBackups = 10,
                    BackupBeforeEdit = true,
                    BackupBeforeDelete = true,
                    ExcludeFromBackup = new List<string> { "*.tmp", "*.log", "*.bak" }
                }
            };
        }

        public bool ResetToDefaults()
        {
            try
            {
                var defaultSettings = GetDefaultSettings();
                var success = SaveSettings(defaultSettings);
                
                if (success)
                {
                    _cachedSettings = defaultSettings;
                }
                
                return success;
            }
            catch (Exception)
            {
                return false;
            }
        }

        public bool ExportSettings(string filePath)
        {
            try
            {
                var settings = GetSettings();
                if (settings == null)
                    return false;

                var json = JsonConvert.SerializeObject(settings, Formatting.Indented);
                File.WriteAllText(filePath, json);
                return true;
            }
            catch (Exception)
            {
                return false;
            }
        }

        public bool ImportSettings(string filePath)
        {
            try
            {
                if (!File.Exists(filePath))
                    return false;

                var json = File.ReadAllText(filePath);
                var settings = JsonConvert.DeserializeObject<AppSettings>(json);
                
                if (settings == null || !ValidateSettings(settings))
                    return false;

                var success = SaveSettings(settings);
                return success;
            }
            catch (Exception)
            {
                return false;
            }
        }

        public bool ValidateSettings(AppSettings settings)
        {
            if (settings == null)
                return false;

            try
            {
                // Validate theme
                if (string.IsNullOrEmpty(settings.Theme) || 
                    (settings.Theme != "Dark" && settings.Theme != "Light"))
                {
                    settings.Theme = "Dark";
                }

                // Validate window dimensions
                if (settings.WindowWidth < 800) settings.WindowWidth = 800;
                if (settings.WindowHeight < 600) settings.WindowHeight = 600;
                if (settings.WindowWidth > 3000) settings.WindowWidth = 3000;
                if (settings.WindowHeight > 2000) settings.WindowHeight = 2000;

                // Validate tree view width
                if (settings.TreeViewWidth < 150) settings.TreeViewWidth = 150;
                if (settings.TreeViewWidth > 500) settings.TreeViewWidth = 500;

                // Validate editor settings
                if (settings.Editor == null)
                    settings.Editor = new EditorSettings();
                
                if (settings.Editor.FontSize < 8) settings.Editor.FontSize = 8;
                if (settings.Editor.FontSize > 24) settings.Editor.FontSize = 24;
                if (settings.Editor.AutoSaveInterval < 5) settings.Editor.AutoSaveInterval = 5;
                if (settings.Editor.AutoSaveInterval > 300) settings.Editor.AutoSaveInterval = 300;

                // Validate search settings
                if (settings.Search == null)
                    settings.Search = new SearchSettings();
                
                if (settings.Search.MaxResults < 100) settings.Search.MaxResults = 100;
                if (settings.Search.MaxResults > 10000) settings.Search.MaxResults = 10000;

                // Validate ZIP settings
                if (settings.Zip == null)
                    settings.Zip = new ZipSettings();
                
                if (settings.Zip.CompressionLevel < 0) settings.Zip.CompressionLevel = 0;
                if (settings.Zip.CompressionLevel > 9) settings.Zip.CompressionLevel = 9;

                // Validate backup settings
                if (settings.Backup == null)
                    settings.Backup = new BackupSettings();
                
                if (settings.Backup.MaxBackups < 1) settings.Backup.MaxBackups = 1;
                if (settings.Backup.MaxBackups > 100) settings.Backup.MaxBackups = 100;

                return true;
            }
            catch (Exception)
            {
                return false;
            }
        }

        public string GetSettingsFilePath()
        {
            return _settingsFilePath;
        }
    }
}