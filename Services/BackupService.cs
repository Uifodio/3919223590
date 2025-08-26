using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Threading.Tasks;

namespace WindowsFileManagerPro.Services
{
    public class BackupService : IBackupService
    {
        private readonly Dictionary<string, DateTime> _scheduledBackups = new();

        public async Task<bool> CreateBackupAsync(string filePath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (!File.Exists(filePath))
                        return false;

                    var backupPath = GetBackupPath(filePath);
                    var backupDir = Path.GetDirectoryName(backupPath);
                    
                    if (!string.IsNullOrEmpty(backupDir) && !Directory.Exists(backupDir))
                    {
                        Directory.CreateDirectory(backupDir);
                    }

                    File.Copy(filePath, backupPath, true);
                    return true;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> RestoreFromBackupAsync(string filePath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    var backupPath = GetBackupPath(filePath);
                    if (File.Exists(backupPath))
                    {
                        File.Copy(backupPath, filePath, true);
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

        public async Task<bool> DeleteBackupAsync(string filePath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    var backupPath = GetBackupPath(filePath);
                    if (File.Exists(backupPath))
                    {
                        File.Delete(backupPath);
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

        public async Task<string[]> GetBackupFilesAsync(string originalFilePath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    var backupDir = GetBackupDirectory(originalFilePath);
                    if (!Directory.Exists(backupDir))
                        return Array.Empty<string>();

                    var backupFiles = Directory.GetFiles(backupDir, $"{Path.GetFileNameWithoutExtension(originalFilePath)}_*{Path.GetExtension(originalFilePath)}.bak");
                    return backupFiles.OrderByDescending(f => File.GetCreationTime(f)).ToArray();
                }
                catch (Exception)
                {
                    return Array.Empty<string>();
                }
            });
        }

        public async Task<string> GetLatestBackupAsync(string originalFilePath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    var backupFiles = GetBackupFilesAsync(originalFilePath).Result;
                    return backupFiles.Length > 0 ? backupFiles[0] : string.Empty;
                }
                catch (Exception)
                {
                    return string.Empty;
                }
            });
        }

        public async Task<bool> CleanupOldBackupsAsync(string originalFilePath, int maxBackups = 10)
        {
            return await Task.Run(() =>
            {
                try
                {
                    var backupFiles = GetBackupFilesAsync(originalFilePath).Result;
                    if (backupFiles.Length <= maxBackups)
                        return true;

                    var filesToDelete = backupFiles.Skip(maxBackups);
                    foreach (var file in filesToDelete)
                    {
                        try
                        {
                            File.Delete(file);
                        }
                        catch
                        {
                            // Continue with other files even if one fails
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

        public async Task<bool> IsBackupAvailableAsync(string filePath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    var backupPath = GetBackupPath(filePath);
                    return File.Exists(backupPath);
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<long> GetBackupSizeAsync(string filePath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    var backupPath = GetBackupPath(filePath);
                    if (File.Exists(backupPath))
                    {
                        return new FileInfo(backupPath).Length;
                    }
                    return 0;
                }
                catch (Exception)
                {
                    return 0;
                }
            });
        }

        public async Task<bool> ValidateBackupAsync(string backupPath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (!File.Exists(backupPath))
                        return false;

                    // Basic validation - check if file can be read
                    using var stream = File.OpenRead(backupPath);
                    var buffer = new byte[1024];
                    var bytesRead = stream.Read(buffer, 0, buffer.Length);
                    return bytesRead > 0;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> CompactBackupsAsync(string originalFilePath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    var backupFiles = GetBackupFilesAsync(originalFilePath).Result;
                    if (backupFiles.Length <= 1)
                        return true;

                    // Keep only the latest backup
                    var latestBackup = backupFiles[0];
                    var backupDir = GetBackupDirectory(originalFilePath);

                    foreach (var backupFile in backupFiles.Skip(1))
                    {
                        try
                        {
                            File.Delete(backupFile);
                        }
                        catch
                        {
                            // Continue with other files even if one fails
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

        public async Task<bool> ExportBackupAsync(string backupPath, string exportPath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (!File.Exists(backupPath))
                        return false;

                    var exportDir = Path.GetDirectoryName(exportPath);
                    if (!string.IsNullOrEmpty(exportDir) && !Directory.Exists(exportDir))
                    {
                        Directory.CreateDirectory(exportDir);
                    }

                    File.Copy(backupPath, exportPath, true);
                    return true;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> ImportBackupAsync(string importPath, string originalFilePath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (!File.Exists(importPath))
                        return false;

                    var backupPath = GetBackupPath(originalFilePath);
                    var backupDir = Path.GetDirectoryName(backupPath);
                    
                    if (!string.IsNullOrEmpty(backupDir) && !Directory.Exists(backupDir))
                    {
                        Directory.CreateDirectory(backupDir);
                    }

                    File.Copy(importPath, backupPath, true);
                    return true;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<BackupInfo> GetBackupInfoAsync(string backupPath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (!File.Exists(backupPath))
                        return new BackupInfo();

                    var fileInfo = new FileInfo(backupPath);
                    var checksum = CalculateChecksum(backupPath);

                    return new BackupInfo
                    {
                        BackupPath = backupPath,
                        CreatedAt = fileInfo.CreationTime,
                        Size = fileInfo.Length,
                        IsValid = ValidateBackupAsync(backupPath).Result,
                        Checksum = checksum
                    };
                }
                catch (Exception)
                {
                    return new BackupInfo();
                }
            });
        }

        public async Task<bool> ScheduleBackupAsync(string filePath, int intervalMinutes)
        {
            return await Task.Run(() =>
            {
                try
                {
                    _scheduledBackups[filePath] = DateTime.Now.AddMinutes(intervalMinutes);
                    return true;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> CancelScheduledBackupAsync(string filePath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    return _scheduledBackups.Remove(filePath);
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        private string GetBackupPath(string originalFilePath)
        {
            var directory = Path.GetDirectoryName(originalFilePath);
            var fileName = Path.GetFileNameWithoutExtension(originalFilePath);
            var extension = Path.GetExtension(originalFilePath);
            var timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
            return Path.Combine(directory ?? "", $"{fileName}_{timestamp}{extension}.bak");
        }

        private string GetBackupDirectory(string originalFilePath)
        {
            return Path.GetDirectoryName(originalFilePath) ?? "";
        }

        private string CalculateChecksum(string filePath)
        {
            try
            {
                using var md5 = MD5.Create();
                using var stream = File.OpenRead(filePath);
                var hash = md5.ComputeHash(stream);
                return BitConverter.ToString(hash).Replace("-", "").ToLowerInvariant();
            }
            catch (Exception)
            {
                return string.Empty;
            }
        }
    }
}