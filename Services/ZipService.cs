using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Threading.Tasks;
using WindowsFileManagerPro.Models;

namespace WindowsFileManagerPro.Services
{
    public class ZipService : IZipService
    {
        public async Task<bool> IsZipFileAsync(string filePath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (!File.Exists(filePath))
                        return false;

                    var extension = Path.GetExtension(filePath).ToLowerInvariant();
                    return extension == ".zip" || extension == ".jar" || extension == ".war" || extension == ".ear";
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<IEnumerable<FileItem>> GetZipContentsAsync(string zipPath)
        {
            return await Task.Run(() =>
            {
                var items = new List<FileItem>();

                try
                {
                    using var archive = ZipFile.OpenRead(zipPath);
                    foreach (var entry in archive.Entries)
                    {
                        var item = new FileItem
                        {
                            Name = entry.Name,
                            FullPath = entry.FullName,
                            Size = entry.Length,
                            LastModified = entry.LastWriteTime.DateTime,
                            IsDirectory = string.IsNullOrEmpty(entry.Name),
                            IsArchive = false,
                            IsCompressed = true
                        };

                        items.Add(item);
                    }
                }
                catch (Exception)
                {
                    // Return empty list if zip is corrupted
                }

                return items.OrderBy(i => i.IsDirectory).ThenBy(i => i.Name);
            });
        }

        public async Task<bool> ExtractFileFromZipAsync(string zipPath, string fileName, string destinationPath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    using var archive = ZipFile.OpenRead(zipPath);
                    var entry = archive.GetEntry(fileName);
                    if (entry != null)
                    {
                        var directory = Path.GetDirectoryName(destinationPath);
                        if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
                        {
                            Directory.CreateDirectory(directory);
                        }

                        entry.ExtractToFile(destinationPath, true);
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

        public async Task<bool> AddFileToZipAsync(string zipPath, string sourcePath, string fileNameInZip)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (!File.Exists(sourcePath))
                        return false;

                    using var archive = ZipFile.Open(zipPath, ZipArchiveMode.Update);
                    archive.CreateEntryFromFile(sourcePath, fileNameInZip);
                    return true;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> RemoveFileFromZipAsync(string zipPath, string fileName)
        {
            return await Task.Run(() =>
            {
                try
                {
                    using var archive = ZipFile.Open(zipPath, ZipArchiveMode.Update);
                    var entry = archive.GetEntry(fileName);
                    if (entry != null)
                    {
                        entry.Delete();
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

        public async Task<bool> CreateZipAsync(string zipPath, IEnumerable<string> sourcePaths)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (File.Exists(zipPath))
                        File.Delete(zipPath);

                    using var archive = ZipFile.Open(zipPath, ZipArchiveMode.Create);
                    foreach (var sourcePath in sourcePaths)
                    {
                        if (File.Exists(sourcePath))
                        {
                            var fileName = Path.GetFileName(sourcePath);
                            archive.CreateEntryFromFile(sourcePath, fileName);
                        }
                        else if (Directory.Exists(sourcePath))
                        {
                            var directoryName = Path.GetFileName(sourcePath);
                            AddDirectoryToZip(archive, sourcePath, directoryName);
                        }
                    }
                    return true;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> ExtractZipAsync(string zipPath, string destinationPath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (!Directory.Exists(destinationPath))
                        Directory.CreateDirectory(destinationPath);

                    ZipFile.ExtractToDirectory(zipPath, destinationPath);
                    return true;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> UpdateFileInZipAsync(string zipPath, string fileName, string newContent)
        {
            return await Task.Run(() =>
            {
                try
                {
                    using var archive = ZipFile.Open(zipPath, ZipArchiveMode.Update);
                    var entry = archive.GetEntry(fileName);
                    if (entry != null)
                    {
                        entry.Delete();
                    }

                    var newEntry = archive.CreateEntry(fileName);
                    using var writer = new StreamWriter(newEntry.Open());
                    writer.Write(newContent);
                    return true;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<string> ReadTextFileFromZipAsync(string zipPath, string fileName)
        {
            return await Task.Run(() =>
            {
                try
                {
                    using var archive = ZipFile.OpenRead(zipPath);
                    var entry = archive.GetEntry(fileName);
                    if (entry != null)
                    {
                        using var reader = new StreamReader(entry.Open());
                        return reader.ReadToEnd();
                    }
                    return string.Empty;
                }
                catch (Exception)
                {
                    return string.Empty;
                }
            });
        }

        public async Task<bool> WriteTextFileToZipAsync(string zipPath, string fileName, string content)
        {
            return await Task.Run(() =>
            {
                try
                {
                    using var archive = ZipFile.Open(zipPath, ZipArchiveMode.Update);
                    var entry = archive.GetEntry(fileName);
                    if (entry != null)
                    {
                        entry.Delete();
                    }

                    var newEntry = archive.CreateEntry(fileName);
                    using var writer = new StreamWriter(newEntry.Open());
                    writer.Write(content);
                    return true;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> CreateBackupAsync(string zipPath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (!File.Exists(zipPath))
                        return false;

                    var backupPath = GetBackupPath(zipPath);
                    File.Copy(zipPath, backupPath, true);
                    return true;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> RestoreFromBackupAsync(string zipPath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    var backupPath = GetBackupPath(zipPath);
                    if (File.Exists(backupPath))
                    {
                        File.Copy(backupPath, zipPath, true);
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

        public async Task<long> GetZipSizeAsync(string zipPath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (File.Exists(zipPath))
                    {
                        return new FileInfo(zipPath).Length;
                    }
                    return 0;
                }
                catch (Exception)
                {
                    return 0;
                }
            });
        }

        public async Task<string[]> GetZipFileNamesAsync(string zipPath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    using var archive = ZipFile.OpenRead(zipPath);
                    return archive.Entries.Select(e => e.FullName).ToArray();
                }
                catch (Exception)
                {
                    return Array.Empty<string>();
                }
            });
        }

        public async Task<bool> ValidateZipAsync(string zipPath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    using var archive = ZipFile.OpenRead(zipPath);
                    var entries = archive.Entries.ToList();
                    return entries.Count > 0;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> RepairZipAsync(string zipPath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    // Basic repair: try to extract and recreate
                    var tempDir = Path.Combine(Path.GetTempPath(), Path.GetRandomFileName());
                    Directory.CreateDirectory(tempDir);

                    try
                    {
                        ZipFile.ExtractToDirectory(zipPath, tempDir);
                        var files = Directory.GetFiles(tempDir, "*", SearchOption.AllDirectories);
                        
                        if (File.Exists(zipPath))
                            File.Delete(zipPath);

                        using var archive = ZipFile.Open(zipPath, ZipArchiveMode.Create);
                        foreach (var file in files)
                        {
                            var relativePath = Path.GetRelativePath(tempDir, file);
                            archive.CreateEntryFromFile(file, relativePath);
                        }

                        return true;
                    }
                    finally
                    {
                        if (Directory.Exists(tempDir))
                            Directory.Delete(tempDir, true);
                    }
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        private void AddDirectoryToZip(ZipArchive archive, string sourceDir, string directoryName)
        {
            var files = Directory.GetFiles(sourceDir);
            var subdirs = Directory.GetDirectories(sourceDir);

            foreach (var file in files)
            {
                var fileName = Path.GetFileName(file);
                var entryName = Path.Combine(directoryName, fileName);
                archive.CreateEntryFromFile(file, entryName);
            }

            foreach (var subdir in subdirs)
            {
                var subdirName = Path.GetFileName(subdir);
                var newDirName = Path.Combine(directoryName, subdirName);
                AddDirectoryToZip(archive, subdir, newDirName);
            }
        }

        private string GetBackupPath(string zipPath)
        {
            var directory = Path.GetDirectoryName(zipPath);
            var fileName = Path.GetFileNameWithoutExtension(zipPath);
            var extension = Path.GetExtension(zipPath);
            var timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
            return Path.Combine(directory ?? "", $"{fileName}_{timestamp}{extension}.bak");
        }
    }
}