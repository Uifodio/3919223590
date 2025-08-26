using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using WindowsFileManagerPro.Models;

namespace WindowsFileManagerPro.Services
{
    public class FileService : IFileService
    {
        private CancellationTokenSource? _cancellationTokenSource;
        private IProgress<int>? _progress;

        public async Task<IEnumerable<FileItem>> GetDirectoryContentsAsync(string path)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (!Directory.Exists(path))
                        return Enumerable.Empty<FileItem>();

                    var directory = new DirectoryInfo(path);
                    var items = new List<FileItem>();

                    // Get directories first
                    try
                    {
                        var directories = directory.GetDirectories()
                            .Where(d => !d.Attributes.HasFlag(FileAttributes.System))
                            .OrderBy(d => d.Name)
                            .Select(d => new FileItem(d));

                        items.AddRange(directories);
                    }
                    catch (UnauthorizedAccessException)
                    {
                        // Skip directories we can't access
                    }

                    // Get files
                    try
                    {
                        var files = directory.GetFiles()
                            .Where(f => !f.Attributes.HasFlag(FileAttributes.System))
                            .OrderBy(f => f.Name)
                            .Select(f => new FileItem(f));

                        items.AddRange(files);
                    }
                    catch (UnauthorizedAccessException)
                    {
                        // Skip files we can't access
                    }

                    return items;
                }
                catch (Exception)
                {
                    return Enumerable.Empty<FileItem>();
                }
            });
        }

        public async Task<FileItem> GetFileInfoAsync(string path)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (File.Exists(path))
                    {
                        return new FileItem(new FileInfo(path));
                    }
                    else if (Directory.Exists(path))
                    {
                        return new FileItem(new DirectoryInfo(path));
                    }
                    else
                    {
                        return new FileItem { FullPath = path };
                    }
                }
                catch (Exception)
                {
                    return new FileItem { FullPath = path };
                }
            });
        }

        public async Task<bool> CreateDirectoryAsync(string path)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (!Directory.Exists(path))
                    {
                        Directory.CreateDirectory(path);
                        return true;
                    }
                    return false;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> CreateFileAsync(string path)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (!File.Exists(path))
                    {
                        File.Create(path).Dispose();
                        return true;
                    }
                    return false;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> DeleteFileAsync(string path)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (File.Exists(path))
                    {
                        File.Delete(path);
                        return true;
                    }
                    return false;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> DeleteDirectoryAsync(string path, bool recursive = false)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (Directory.Exists(path))
                    {
                        Directory.Delete(path, recursive);
                        return true;
                    }
                    return false;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> CopyFileAsync(string sourcePath, string destinationPath, bool overwrite = false)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (File.Exists(sourcePath))
                    {
                        var destinationDir = Path.GetDirectoryName(destinationPath);
                        if (!string.IsNullOrEmpty(destinationDir) && !Directory.Exists(destinationDir))
                        {
                            Directory.CreateDirectory(destinationDir);
                        }

                        File.Copy(sourcePath, destinationPath, overwrite);
                        return true;
                    }
                    return false;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> MoveFileAsync(string sourcePath, string destinationPath, bool overwrite = false)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (File.Exists(sourcePath))
                    {
                        var destinationDir = Path.GetDirectoryName(destinationPath);
                        if (!string.IsNullOrEmpty(destinationDir) && !Directory.Exists(destinationDir))
                        {
                            Directory.CreateDirectory(destinationDir);
                        }

                        if (overwrite && File.Exists(destinationPath))
                        {
                            File.Delete(destinationPath);
                        }

                        File.Move(sourcePath, destinationPath);
                        return true;
                    }
                    return false;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> RenameFileAsync(string oldPath, string newName)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (File.Exists(oldPath))
                    {
                        var directory = Path.GetDirectoryName(oldPath);
                        var newPath = Path.Combine(directory ?? "", newName);
                        
                        if (File.Exists(newPath))
                            return false;

                        File.Move(oldPath, newPath);
                        return true;
                    }
                    else if (Directory.Exists(oldPath))
                    {
                        var parentDir = Directory.GetParent(oldPath)?.FullName ?? "";
                        var newPath = Path.Combine(parentDir, newName);
                        
                        if (Directory.Exists(newPath))
                            return false;

                        Directory.Move(oldPath, newPath);
                        return true;
                    }
                    return false;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> FileExistsAsync(string path)
        {
            return await Task.Run(() => File.Exists(path));
        }

        public async Task<bool> DirectoryExistsAsync(string path)
        {
            return await Task.Run(() => Directory.Exists(path));
        }

        public async Task<long> GetFileSizeAsync(string path)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (File.Exists(path))
                    {
                        return new FileInfo(path).Length;
                    }
                    return 0;
                }
                catch (Exception)
                {
                    return 0;
                }
            });
        }

        public async Task<string> ReadTextFileAsync(string path)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (File.Exists(path))
                    {
                        return File.ReadAllText(path);
                    }
                    return string.Empty;
                }
                catch (Exception)
                {
                    return string.Empty;
                }
            });
        }

        public async Task<bool> WriteTextFileAsync(string path, string content)
        {
            return await Task.Run(() =>
            {
                try
                {
                    var directory = Path.GetDirectoryName(path);
                    if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
                    {
                        Directory.CreateDirectory(directory);
                    }

                    File.WriteAllText(path, content);
                    return true;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> IsFileReadOnlyAsync(string path)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (File.Exists(path))
                    {
                        var attributes = File.GetAttributes(path);
                        return attributes.HasFlag(FileAttributes.ReadOnly);
                    }
                    return false;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> SetFileReadOnlyAsync(string path, bool readOnly)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (File.Exists(path))
                    {
                        var attributes = File.GetAttributes(path);
                        if (readOnly)
                        {
                            attributes |= FileAttributes.ReadOnly;
                        }
                        else
                        {
                            attributes &= ~FileAttributes.ReadOnly;
                        }
                        File.SetAttributes(path, attributes);
                        return true;
                    }
                    return false;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> IsFileHiddenAsync(string path)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (File.Exists(path))
                    {
                        var attributes = File.GetAttributes(path);
                        return attributes.HasFlag(FileAttributes.Hidden);
                    }
                    return false;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> SetFileHiddenAsync(string path, bool hidden)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (File.Exists(path))
                    {
                        var attributes = File.GetAttributes(path);
                        if (hidden)
                        {
                            attributes |= FileAttributes.Hidden;
                        }
                        else
                        {
                            attributes &= ~FileAttributes.Hidden;
                        }
                        File.SetAttributes(path, attributes);
                        return true;
                    }
                    return false;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<string[]> GetDrivesAsync()
        {
            return await Task.Run(() =>
            {
                try
                {
                    return DriveInfo.GetDrives()
                        .Where(d => d.IsReady)
                        .Select(d => d.Name)
                        .ToArray();
                }
                catch (Exception)
                {
                    return Array.Empty<string>();
                }
            });
        }

        public async Task<string[]> GetSpecialFoldersAsync()
        {
            return await Task.Run(() =>
            {
                try
                {
                    var folders = new List<string>();
                    
                    var desktop = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
                    var documents = Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments);
                    var downloads = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile) + "\\Downloads";
                    var pictures = Environment.GetFolderPath(Environment.SpecialFolder.MyPictures);
                    var music = Environment.GetFolderPath(Environment.SpecialFolder.MyMusic);
                    var videos = Environment.GetFolderPath(Environment.SpecialFolder.MyVideos);

                    if (!string.IsNullOrEmpty(desktop)) folders.Add(desktop);
                    if (!string.IsNullOrEmpty(documents)) folders.Add(documents);
                    if (!string.IsNullOrEmpty(downloads)) folders.Add(downloads);
                    if (!string.IsNullOrEmpty(pictures)) folders.Add(pictures);
                    if (!string.IsNullOrEmpty(music)) folders.Add(music);
                    if (!string.IsNullOrEmpty(videos)) folders.Add(videos);

                    return folders.ToArray();
                }
                catch (Exception)
                {
                    return Array.Empty<string>();
                }
            });
        }

        public async Task<bool> IsArchiveFileAsync(string path)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (File.Exists(path))
                    {
                        var extension = Path.GetExtension(path).ToLowerInvariant();
                        return extension == ".zip" || extension == ".rar" || extension == ".7z" ||
                               extension == ".tar" || extension == ".gz" || extension == ".bz2";
                    }
                    return false;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<IEnumerable<FileItem>> SearchFilesAsync(string searchPath, string searchPattern, bool recursive = false)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (!Directory.Exists(searchPath))
                        return Enumerable.Empty<FileItem>();

                    var searchOption = recursive ? SearchOption.AllDirectories : SearchOption.TopDirectoryOnly;
                    var files = Directory.GetFiles(searchPath, searchPattern, searchOption);
                    
                    return files.Select(f => new FileItem(f));
                }
                catch (Exception)
                {
                    return Enumerable.Empty<FileItem>();
                }
            });
        }

        public async Task<IProgress<int>> GetCopyProgressAsync()
        {
            return await Task.Run(() =>
            {
                _progress = new Progress<int>(value => { });
                return _progress;
            });
        }

        public async Task CancelOperationAsync()
        {
            await Task.Run(() =>
            {
                _cancellationTokenSource?.Cancel();
            });
        }
    }
}