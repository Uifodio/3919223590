using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Windows;
using WindowsFileManagerPro.Models;

namespace WindowsFileManagerPro.Services
{
    public class ClipboardService : IClipboardService
    {
        public async Task<bool> SetTextAsync(string text)
        {
            try
            {
                return await Task.Run(() =>
                {
                    try
                    {
                        System.Windows.Clipboard.SetText(text);
                        return true;
                    }
                    catch
                    {
                        return false;
                    }
                });
            }
            catch
            {
                return false;
            }
        }

        public async Task<string?> GetTextAsync()
        {
            try
            {
                return await Task.Run(() =>
                {
                    try
                    {
                        return System.Windows.Clipboard.ContainsText() ? System.Windows.Clipboard.GetText() : null;
                    }
                    catch
                    {
                        return null;
                    }
                });
            }
            catch
            {
                return null;
            }
        }

        public async Task<bool> SetFilesAsync(IEnumerable<string> filePaths)
        {
            try
            {
                return await Task.Run(() =>
                {
                    try
                    {
                        var dataObject = new System.Windows.DataObject();
                        dataObject.SetData(System.Windows.DataFormats.FileDrop, filePaths);
                        System.Windows.Clipboard.SetDataObject(dataObject);
                        return true;
                    }
                    catch
                    {
                        return false;
                    }
                });
            }
            catch
            {
                return false;
            }
        }

        public async Task<IEnumerable<string>?> GetFilesAsync()
        {
            try
            {
                return await Task.Run(() =>
                {
                    try
                    {
                        if (System.Windows.Clipboard.ContainsFileDropList())
                        {
                            return System.Windows.Clipboard.GetFileDropList();
                        }
                        return null;
                    }
                    catch
                    {
                        return null;
                    }
                });
            }
            catch
            {
                return null;
            }
        }

        public async Task<bool> SetImageAsync(byte[] imageData)
        {
            try
            {
                return await Task.Run(() =>
                {
                    try
                    {
                        var dataObject = new System.Windows.DataObject();
                        dataObject.SetData(System.Windows.DataFormats.Bitmap, imageData);
                        System.Windows.Clipboard.SetDataObject(dataObject);
                        return true;
                    }
                    catch
                    {
                        return false;
                    }
                });
            }
            catch
            {
                return false;
            }
        }

        public async Task<byte[]?> GetImageAsync()
        {
            try
            {
                return await Task.Run(() =>
                {
                    try
                    {
                        if (System.Windows.Clipboard.ContainsImage())
                        {
                            var image = System.Windows.Clipboard.GetImage();
                            // Convert image to bytes - this is a simplified implementation
                            return null; // TODO: Implement proper image conversion
                        }
                        return null;
                    }
                    catch
                    {
                        return null;
                    }
                });
            }
            catch
            {
                return null;
            }
        }

        public async Task<bool> ClearAsync()
        {
            try
            {
                return await Task.Run(() =>
                {
                    try
                    {
                        System.Windows.Clipboard.Clear();
                        return true;
                    }
                    catch
                    {
                        return false;
                    }
                });
            }
            catch
            {
                return false;
            }
        }

        public async Task<bool> ContainsTextAsync()
        {
            try
            {
                return await Task.Run(() =>
                {
                    try
                    {
                        return System.Windows.Clipboard.ContainsText();
                    }
                    catch
                    {
                        return false;
                    }
                });
            }
            catch
            {
                return false;
            }
        }

        public async Task<bool> ContainsFilesAsync()
        {
            try
            {
                return await Task.Run(() =>
                {
                    try
                    {
                        return System.Windows.Clipboard.ContainsFileDropList();
                    }
                    catch
                    {
                        return false;
                    }
                });
            }
            catch
            {
                return false;
            }
        }

        public async Task<bool> ContainsImageAsync()
        {
            try
            {
                return await Task.Run(() =>
                {
                    try
                    {
                        return System.Windows.Clipboard.ContainsImage();
                    }
                    catch
                    {
                        return false;
                    }
                });
            }
            catch
            {
                return false;
            }
        }
    }
}