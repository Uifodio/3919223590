using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;

namespace AAAFileManager.Services
{
    public class AppSettings
    {
        public string Theme { get; set; } = "Dark";
        public double EditorFontSize { get; set; } = 14;
        public string MonitoredFolder { get; set; } = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile) + Path.DirectorySeparatorChar + "Downloads";
        public int MaxRecent { get; set; } = 15;
        public List<string> RecentLocations { get; set; } = new();
    }

    public sealed class SettingsService
    {
        private static readonly Lazy<SettingsService> _instance = new(() => new SettingsService());
        public static SettingsService Instance => _instance.Value;

        public AppSettings Settings { get; private set; } = new AppSettings();

        private string SettingsDir => Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "AAAFileManager");
        private string SettingsPath => Path.Combine(SettingsDir, "settings.json");

        private SettingsService() { }

        public void Load()
        {
            try
            {
                if (File.Exists(SettingsPath))
                {
                    string json = File.ReadAllText(SettingsPath);
                    var loaded = JsonSerializer.Deserialize<AppSettings>(json);
                    if (loaded != null) Settings = loaded;
                }
                else
                {
                    Directory.CreateDirectory(SettingsDir);
                    Save();
                }
            }
            catch
            {
                // Keep defaults on error
            }
        }

        public void Save()
        {
            try
            {
                Directory.CreateDirectory(SettingsDir);
                var json = JsonSerializer.Serialize(Settings, new JsonSerializerOptions { WriteIndented = true });
                File.WriteAllText(SettingsPath, json);
            }
            catch
            {
            }
        }

        public void AddRecent(string location)
        {
            try
            {
                Settings.RecentLocations.RemoveAll(s => string.Equals(s, location, StringComparison.OrdinalIgnoreCase));
                Settings.RecentLocations.Insert(0, location);
                if (Settings.RecentLocations.Count > Settings.MaxRecent)
                {
                    Settings.RecentLocations.RemoveRange(Settings.MaxRecent, Settings.RecentLocations.Count - Settings.MaxRecent);
                }
                Save();
            }
            catch { }
        }
    }
}