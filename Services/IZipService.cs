using System.Collections.Generic;
using System.Threading.Tasks;
using WindowsFileManagerPro.Models;

namespace WindowsFileManagerPro.Services
{
    public interface IZipService
    {
        Task<bool> IsZipFileAsync(string filePath);
        Task<IEnumerable<FileItem>> GetZipContentsAsync(string zipPath);
        Task<bool> ExtractFileFromZipAsync(string zipPath, string fileName, string destinationPath);
        Task<bool> AddFileToZipAsync(string zipPath, string sourcePath, string fileNameInZip);
        Task<bool> RemoveFileFromZipAsync(string zipPath, string fileName);
        Task<bool> CreateZipAsync(string zipPath, IEnumerable<string> sourcePaths);
        Task<bool> ExtractZipAsync(string zipPath, string destinationPath);
        Task<bool> UpdateFileInZipAsync(string zipPath, string fileName, string newContent);
        Task<string> ReadTextFileFromZipAsync(string zipPath, string fileName);
        Task<bool> WriteTextFileToZipAsync(string zipPath, string fileName, string content);
        Task<bool> CreateBackupAsync(string zipPath);
        Task<bool> RestoreFromBackupAsync(string zipPath);
        Task<long> GetZipSizeAsync(string zipPath);
        Task<string[]> GetZipFileNamesAsync(string zipPath);
        Task<bool> ValidateZipAsync(string zipPath);
        Task<bool> RepairZipAsync(string zipPath);
    }
}