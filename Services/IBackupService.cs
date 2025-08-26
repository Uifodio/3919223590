using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace WindowsFileManagerPro.Services
{
    public interface IBackupService
    {
        Task<bool> CreateBackupAsync(string filePath);
        Task<bool> RestoreFromBackupAsync(string filePath);
        Task<bool> DeleteBackupAsync(string filePath);
        Task<string[]> GetBackupFilesAsync(string originalFilePath);
        Task<string> GetLatestBackupAsync(string originalFilePath);
        Task<bool> CleanupOldBackupsAsync(string originalFilePath, int maxBackups = 10);
        Task<bool> IsBackupAvailableAsync(string filePath);
        Task<long> GetBackupSizeAsync(string filePath);
        Task<bool> ValidateBackupAsync(string backupPath);
        Task<bool> CompactBackupsAsync(string originalFilePath);
        Task<bool> ExportBackupAsync(string backupPath, string exportPath);
        Task<bool> ImportBackupAsync(string importPath, string originalFilePath);
        Task<BackupInfo> GetBackupInfoAsync(string backupPath);
        Task<bool> ScheduleBackupAsync(string filePath, int intervalMinutes);
        Task<bool> CancelScheduledBackupAsync(string filePath);
    }

    public class BackupInfo
    {
        public string OriginalPath { get; set; } = "";
        public string BackupPath { get; set; } = "";
        public DateTime CreatedAt { get; set; }
        public long Size { get; set; }
        public string Reason { get; set; } = "";
        public bool IsValid { get; set; }
        public string Checksum { get; set; } = "";
    }
}