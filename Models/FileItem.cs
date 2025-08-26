using System;
using System.IO;
using System.Windows.Media;

namespace WindowsFileManagerPro.Models
{
    public class FileItem : IEquatable<FileItem>
    {
        public string Name { get; set; } = "";
        public string FullPath { get; set; } = "";
        public string Extension { get; set; } = "";
        public long Size { get; set; } = 0;
        public DateTime LastModified { get; set; } = DateTime.Now;
        public DateTime Created { get; set; } = DateTime.Now;
        public FileAttributes Attributes { get; set; } = FileAttributes.Normal;
        public bool IsDirectory { get; set; } = false;
        public bool IsArchive { get; set; } = false;
        public bool IsHidden { get; set; } = false;
        public bool IsReadOnly { get; set; } = false;
        public bool IsSystem { get; set; } = false;
        public bool IsCompressed { get; set; } = false;
        public bool IsEncrypted { get; set; } = false;
        public string IconPath { get; set; } = "";
        public ImageSource? Icon { get; set; }
        public bool IsSelected { get; set; } = false;
        public bool IsExpanded { get; set; } = false;
        public bool IsVisible { get; set; } = true;
        public string DisplayName => IsDirectory ? Name : Path.GetFileNameWithoutExtension(Name);
        public string SizeFormatted => IsDirectory ? "" : FormatFileSize(Size);
        public string LastModifiedFormatted => LastModified.ToString("g");

        public FileItem()
        {
        }

        public FileItem(string path)
        {
            if (string.IsNullOrEmpty(path))
                return;

            FullPath = path;
            
            try
            {
                var fileInfo = new FileInfo(path);
                var directoryInfo = new DirectoryInfo(path);

                if (fileInfo.Exists)
                {
                    Name = fileInfo.Name;
                    Extension = fileInfo.Extension;
                    Size = fileInfo.Length;
                    LastModified = fileInfo.LastWriteTime;
                    Created = fileInfo.CreationTime;
                    Attributes = fileInfo.Attributes;
                    IsDirectory = false;
                    IsArchive = fileInfo.Extension.Equals(".zip", StringComparison.OrdinalIgnoreCase) ||
                               fileInfo.Extension.Equals(".rar", StringComparison.OrdinalIgnoreCase) ||
                               fileInfo.Extension.Equals(".7z", StringComparison.OrdinalIgnoreCase);
                }
                else if (directoryInfo.Exists)
                {
                    Name = directoryInfo.Name;
                    Extension = "";
                    Size = 0;
                    LastModified = directoryInfo.LastWriteTime;
                    Created = directoryInfo.CreationTime;
                    Attributes = directoryInfo.Attributes;
                    IsDirectory = true;
                }

                IsHidden = (Attributes & FileAttributes.Hidden) != 0;
                IsReadOnly = (Attributes & FileAttributes.ReadOnly) != 0;
                IsSystem = (Attributes & FileAttributes.System) != 0;
                IsCompressed = (Attributes & FileAttributes.Compressed) != 0;
                IsEncrypted = (Attributes & FileAttributes.Encrypted) != 0;
            }
            catch (Exception)
            {
                // Handle access denied or other errors gracefully
                Name = Path.GetFileName(path);
                FullPath = path;
            }
        }

        public FileItem(FileSystemInfo info)
        {
            if (info == null)
                return;

            Name = info.Name;
            FullPath = info.FullName;
            LastModified = info.LastWriteTime;
            Created = info.CreationTime;
            Attributes = info.Attributes;

            if (info is FileInfo fileInfo)
            {
                Extension = fileInfo.Extension;
                Size = fileInfo.Length;
                IsDirectory = false;
                IsArchive = fileInfo.Extension.Equals(".zip", StringComparison.OrdinalIgnoreCase) ||
                           fileInfo.Extension.Equals(".rar", StringComparison.OrdinalIgnoreCase) ||
                           fileInfo.Extension.Equals(".7z", StringComparison.OrdinalIgnoreCase);
            }
            else if (info is DirectoryInfo)
            {
                Extension = "";
                Size = 0;
                IsDirectory = true;
            }

            IsHidden = (Attributes & FileAttributes.Hidden) != 0;
            IsReadOnly = (Attributes & FileAttributes.ReadOnly) != 0;
            IsSystem = (Attributes & FileAttributes.System) != 0;
            IsCompressed = (Attributes & FileAttributes.Compressed) != 0;
            IsEncrypted = (Attributes & FileAttributes.Encrypted) != 0;
        }

        private static string FormatFileSize(long bytes)
        {
            if (bytes < 1024) return $"{bytes} B";
            if (bytes < 1024 * 1024) return $"{bytes / 1024.0:F1} KB";
            if (bytes < 1024 * 1024 * 1024) return $"{bytes / (1024.0 * 1024.0):F1} MB";
            return $"{bytes / (1024.0 * 1024.0 * 1024.0):F1} GB";
        }

        public bool Equals(FileItem? other)
        {
            if (other is null) return false;
            if (ReferenceEquals(this, other)) return true;
            return FullPath.Equals(other.FullPath, StringComparison.OrdinalIgnoreCase);
        }

        public override bool Equals(object? obj)
        {
            return Equals(obj as FileItem);
        }

        public override int GetHashCode()
        {
            return FullPath.GetHashCode(StringComparison.OrdinalIgnoreCase);
        }

        public override string ToString()
        {
            return Name;
        }

        public FileItem Clone()
        {
            return new FileItem
            {
                Name = Name,
                FullPath = FullPath,
                Extension = Extension,
                Size = Size,
                LastModified = LastModified,
                Created = Created,
                Attributes = Attributes,
                IsDirectory = IsDirectory,
                IsArchive = IsArchive,
                IsHidden = IsHidden,
                IsReadOnly = IsReadOnly,
                IsSystem = IsSystem,
                IsCompressed = IsCompressed,
                IsEncrypted = IsEncrypted,
                IconPath = IconPath,
                Icon = Icon
            };
        }
    }
}