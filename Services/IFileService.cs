using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using WindowsFileManagerPro.Models;

namespace WindowsFileManagerPro.Services
{
    public interface IFileService
    {
        Task<IEnumerable<FileItem>> GetDirectoryContentsAsync(string path);
        Task<FileItem> GetFileInfoAsync(string path);
        Task<bool> CreateDirectoryAsync(string path);
        Task<bool> CreateFileAsync(string path);
        Task<bool> DeleteFileAsync(string path);
        Task<bool> DeleteDirectoryAsync(string path, bool recursive = false);
        Task<bool> CopyFileAsync(string sourcePath, string destinationPath, bool overwrite = false);
        Task<bool> MoveFileAsync(string sourcePath, string destinationPath, bool overwrite = false);
        Task<bool> RenameFileAsync(string oldPath, string newName);
        Task<bool> FileExistsAsync(string path);
        Task<bool> DirectoryExistsAsync(string path);
        Task<long> GetFileSizeAsync(string path);
        Task<string> ReadTextFileAsync(string path);
        Task<bool> WriteTextFileAsync(string path, string content);
        Task<bool> IsFileReadOnlyAsync(string path);
        Task<bool> SetFileReadOnlyAsync(string path, bool readOnly);
        Task<bool> IsFileHiddenAsync(string path);
        Task<bool> SetFileHiddenAsync(string path, bool hidden);
        Task<string[]> GetDrivesAsync();
        Task<string[]> GetSpecialFoldersAsync();
        Task<bool> IsArchiveFileAsync(string path);
        Task<IEnumerable<FileItem>> SearchFilesAsync(string searchPath, string searchPattern, bool recursive = false);
        Task<IProgress<int>> GetCopyProgressAsync();
        Task CancelOperationAsync();
    }
}