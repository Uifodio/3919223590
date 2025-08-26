using System.Collections.Generic;

namespace WindowsFileManagerPro.Models
{
    public class AppSettings
    {
        public string Theme { get; set; } = "Dark";
        public int WindowWidth { get; set; } = 1200;
        public int WindowHeight { get; set; } = 800;
        public int WindowLeft { get; set; } = -1;
        public int WindowTop { get; set; } = -1;
        public bool Maximized { get; set; } = false;
        public double TreeViewWidth { get; set; } = 250;
        public string DefaultPath { get; set; } = "";
        public List<string> RecentPaths { get; set; } = new List<string>();
        public List<string> FavoritePaths { get; set; } = new List<string>();
        public EditorSettings Editor { get; set; } = new EditorSettings();
        public SearchSettings Search { get; set; } = new SearchSettings();
        public ZipSettings Zip { get; set; } = new ZipSettings();
        public BackupSettings Backup { get; set; } = new BackupSettings();
    }

    public class EditorSettings
    {
        public string FontFamily { get; set; } = "Consolas";
        public double FontSize { get; set; } = 12;
        public bool ShowLineNumbers { get; set; } = true;
        public bool ShowWhitespace { get; set; } = false;
        public bool WordWrap { get; set; } = false;
        public bool AutoSave { get; set; } = true;
        public int AutoSaveInterval { get; set; } = 30; // seconds
        public bool SyntaxHighlighting { get; set; } = true;
        public Dictionary<string, string> FileAssociations { get; set; } = new Dictionary<string, string>();
    }

    public class SearchSettings
    {
        public bool CaseSensitive { get; set; } = false;
        public bool UseRegex { get; set; } = false;
        public bool SearchInArchives { get; set; } = true;
        public int MaxResults { get; set; } = 1000;
        public List<string> ExcludePatterns { get; set; } = new List<string> { "*.tmp", "*.bak", "*.log" };
        public List<string> IncludePatterns { get; set; } = new List<string>();
    }

    public class ZipSettings
    {
        public bool OpenAsFolder { get; set; } = true;
        public bool AutoBackup { get; set; } = true;
        public string BackupExtension { get; set; } = ".bak";
        public bool CompressOnSave { get; set; } = false;
        public int CompressionLevel { get; set; } = 6;
    }

    public class BackupSettings
    {
        public bool AutoBackup { get; set; } = true;
        public string BackupExtension { get; set; } = ".bak";
        public int MaxBackups { get; set; } = 10;
        public bool BackupBeforeEdit { get; set; } = true;
        public bool BackupBeforeDelete { get; set; } = true;
        public List<string> ExcludeFromBackup { get; set; } = new List<string> { "*.tmp", "*.log", "*.bak" };
    }
}