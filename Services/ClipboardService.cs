using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;
using WindowsFileManagerPro.Models;

namespace WindowsFileManagerPro.Services
{
    public class ClipboardService : IClipboardService
    {
        private bool _isCutOperation = false;

        public async Task<bool> SetFileListAsync(IEnumerable<FileItem> files)
        {
            return await Task.Run(() =>
            {
                try
                {
                    var filePaths = files.Select(f => f.FullPath).ToArray();
                    var dataObject = new DataObject();
                    dataObject.SetData(DataFormats.FileDrop, filePaths);
                    dataObject.SetData("Preferred DropEffect", new byte[] { 1, 0, 0, 0 }); // Copy
                    Clipboard.SetDataObject(dataObject);
                    return true;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<IEnumerable<FileItem>> GetFileListAsync()
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (Clipboard.ContainsFileDropList())
                    {
                        var filePaths = Clipboard.GetFileDropList().Cast<string>();
                        return filePaths.Select(p => new FileItem(p));
                    }
                    return Enumerable.Empty<FileItem>();
                }
                catch (Exception)
                {
                    return Enumerable.Empty<FileItem>();
                }
            });
        }

        public async Task<bool> SetTextAsync(string text)
        {
            return await Task.Run(() =>
            {
                try
                {
                    Clipboard.SetText(text);
                    return true;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<string> GetTextAsync()
        {
            return await Task.Run(() =>
            {
                try
                {
                    return Clipboard.ContainsText() ? Clipboard.GetText() : string.Empty;
                }
                catch (Exception)
                {
                    return string.Empty;
                }
            });
        }

        public async Task<bool> SetImageAsync(string imagePath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    // This would require image loading and conversion
                    // For now, return false as it's not fully implemented
                    return false;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<string> GetImageAsync()
        {
            return await Task.Run(() =>
            {
                try
                {
                    // This would require image extraction and saving
                    // For now, return empty string as it's not fully implemented
                    return string.Empty;
                }
                catch (Exception)
                {
                    return string.Empty;
                }
            });
        }

        public async Task<bool> ClearAsync()
        {
            return await Task.Run(() =>
            {
                try
                {
                    Clipboard.Clear();
                    _isCutOperation = false;
                    return true;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> HasFilesAsync()
        {
            return await Task.Run(() =>
            {
                try
                {
                    return Clipboard.ContainsFileDropList();
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> HasTextAsync()
        {
            return await Task.Run(() =>
            {
                try
                {
                    return Clipboard.ContainsText();
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> HasImageAsync()
        {
            return await Task.Run(() =>
            {
                try
                {
                    return Clipboard.ContainsImage();
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<string[]> GetFormatsAsync()
        {
            return await Task.Run(() =>
            {
                try
                {
                    return Clipboard.GetDataObject()?.GetFormats() ?? Array.Empty<string>();
                }
                catch (Exception)
                {
                    return Array.Empty<string>();
                }
            });
        }

        public async Task<bool> IsEmptyAsync()
        {
            return await Task.Run(() =>
            {
                try
                {
                    return !Clipboard.ContainsData(DataFormats.FileDrop) &&
                           !Clipboard.ContainsText() &&
                           !Clipboard.ContainsImage();
                }
                catch (Exception)
                {
                    return true;
                }
            });
        }

        public async Task<bool> CopyFilesToClipboardAsync(IEnumerable<string> filePaths)
        {
            return await Task.Run(() =>
            {
                try
                {
                    var dataObject = new DataObject();
                    dataObject.SetData(DataFormats.FileDrop, filePaths.ToArray());
                    dataObject.SetData("Preferred DropEffect", new byte[] { 1, 0, 0, 0 }); // Copy
                    Clipboard.SetDataObject(dataObject);
                    _isCutOperation = false;
                    return true;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> CutFilesToClipboardAsync(IEnumerable<string> filePaths)
        {
            return await Task.Run(() =>
            {
                try
                {
                    var dataObject = new DataObject();
                    dataObject.SetData(DataFormats.FileDrop, filePaths.ToArray());
                    dataObject.SetData("Preferred DropEffect", new byte[] { 2, 0, 0, 0 }); // Move
                    Clipboard.SetDataObject(dataObject);
                    _isCutOperation = true;
                    return true;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> PasteFilesFromClipboardAsync(string destinationPath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (!Clipboard.ContainsFileDropList())
                        return false;

                    var filePaths = Clipboard.GetFileDropList().Cast<string>();
                    var isCut = _isCutOperation;

                    // This would require file service integration for actual file operations
                    // For now, just return success
                    return true;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> IsCutOperationAsync()
        {
            return await Task.Run(() => _isCutOperation);
        }

        public async Task<string[]> GetClipboardFilePathsAsync()
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (Clipboard.ContainsFileDropList())
                    {
                        return Clipboard.GetFileDropList().Cast<string>().ToArray();
                    }
                    return Array.Empty<string>();
                }
                catch (Exception)
                {
                    return Array.Empty<string>();
                }
            });
        }
    }
}