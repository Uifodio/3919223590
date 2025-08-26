using System;

namespace AAAFileManager.Models
{
    public class FileItem
    {
        public string Name { get; set; } = string.Empty;
        public string FullPath { get; set; } = string.Empty;
        public bool IsDirectory { get; set; }
        public long SizeBytes { get; set; }
        public DateTime ModifiedUtc { get; set; }
        public string Type { get; set; } = string.Empty;

        // For ZIP entries
        public bool IsFromZip { get; set; }
        public string? ZipArchivePath { get; set; }
        public string? ZipInnerPath { get; set; }

        public string SizeDisplay => Services.PathUtils.FormatSize(SizeBytes);
        public string ModifiedDisplay => ModifiedUtc.ToLocalTime().ToString("yyyy-MM-dd HH:mm");
    }
}