using System.Collections.Generic;
using System.Threading.Tasks;
using WindowsFileManagerPro.Models;

namespace WindowsFileManagerPro.Services
{
    public interface IClipboardService
    {
        Task<bool> SetFileListAsync(IEnumerable<FileItem> files);
        Task<IEnumerable<FileItem>> GetFileListAsync();
        Task<bool> SetTextAsync(string text);
        Task<string> GetTextAsync();
        Task<bool> SetImageAsync(string imagePath);
        Task<string> GetImageAsync();
        Task<bool> ClearAsync();
        Task<bool> HasFilesAsync();
        Task<bool> HasTextAsync();
        Task<bool> HasImageAsync();
        Task<string[]> GetFormatsAsync();
        Task<bool> IsEmptyAsync();
        Task<bool> CopyFilesToClipboardAsync(IEnumerable<string> filePaths);
        Task<bool> CutFilesToClipboardAsync(IEnumerable<string> filePaths);
        Task<bool> PasteFilesFromClipboardAsync(string destinationPath);
        Task<bool> IsCutOperationAsync();
        Task<string[]> GetClipboardFilePathsAsync();
    }
}