using Microsoft.Extensions.DependencyInjection;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using WindowsFileManagerPro.Models;
using WindowsFileManagerPro.Services;

namespace WindowsFileManagerPro.Views
{
    public partial class FileExplorerView : System.Windows.Controls.UserControl
    {
        private readonly IFileService _fileService;
        private readonly IZipService _zipService;
        private string _currentPath = "";
        private List<FileItem> _currentFiles = new();

        public FileExplorerView()
        {
            InitializeComponent();
            var services = App.Services;
            _fileService = services.GetRequiredService<IFileService>();
            _zipService = services.GetRequiredService<IZipService>();
            InitializeExplorer();
        }

        private async void InitializeExplorer()
        {
            try
            {
                // Get drives and special folders
                var drives = await _fileService.GetDrivesAsync();
                var specialFolders = await _fileService.GetSpecialFoldersAsync();

                // Populate tree view
                var thisPC = FolderTreeView.Items[0] as TreeViewItem;
                if (thisPC != null)
                {
                    thisPC.Items.Clear();

                    // Add drives
                    foreach (var drive in drives)
                    {
                        var driveItem = new TreeViewItem { Header = drive };
                        driveItem.Expanded += DriveItem_Expanded;
                        thisPC.Items.Add(driveItem);
                    }

                    // Add special folders
                    foreach (var folder in specialFolders)
                    {
                        var folderName = Path.GetFileName(folder);
                        var folderItem = new TreeViewItem { Header = folderName, Tag = folder };
                        folderItem.Expanded += FolderItem_Expanded;
                        thisPC.Items.Add(folderItem);
                    }
                }

                // Navigate to user profile
                var userProfile = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
                await NavigateToPathAsync(userProfile);
            }
            catch (Exception ex)
            {
                UpdateStatus($"Failed to initialize explorer: {ex.Message}");
            }
        }

        public async void NavigateToFolder(string path)
        {
            await NavigateToPathAsync(path);
        }

        private async Task NavigateToPathAsync(string path)
        {
            try
            {
                if (string.IsNullOrEmpty(path) || !Directory.Exists(path))
                    return;

                _currentPath = path;
                AddressTextBox.Text = path;
                UpdateStatus($"Navigating to: {path}");

                // Load files and folders
                var items = await _fileService.GetDirectoryContentsAsync(path);
                _currentFiles = items.ToList();

                // Update file list
                FileListView.ItemsSource = _currentFiles;
                UpdateFileCount();

                // Update tree view selection
                UpdateTreeViewSelection(path);
            }
            catch (Exception ex)
            {
                UpdateStatus($"Navigation failed: {ex.Message}");
            }
        }

        private void UpdateTreeViewSelection(string path)
        {
            try
            {
                // Find and select the corresponding tree view item
                var pathParts = path.Split(Path.DirectorySeparatorChar);
                var currentItem = FolderTreeView.Items[0] as TreeViewItem; // This PC

                foreach (var part in pathParts)
                {
                    if (string.IsNullOrEmpty(part)) continue;

                    var found = false;
                    foreach (TreeViewItem item in currentItem.Items)
                    {
                        if (item.Header.ToString() == part || item.Tag?.ToString() == part)
                        {
                            currentItem = item;
                            currentItem.IsExpanded = true;
                            found = true;
                            break;
                        }
                    }

                    if (!found) break;
                }

                if (currentItem != null)
                {
                    currentItem.IsSelected = true;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to update tree view selection: {ex.Message}");
            }
        }

        private void UpdateFileCount()
        {
            try
            {
                var count = _currentFiles.Count;
                FileCountText.Text = $"{count} item{(count == 1 ? "" : "s")}";
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to update file count: {ex.Message}");
            }
        }

        private void UpdateStatus(string message)
        {
            try
            {
                StatusText.Text = message;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to update status: {ex.Message}");
            }
        }

        public void Refresh()
        {
            if (!string.IsNullOrEmpty(_currentPath))
            {
                _ = NavigateToPathAsync(_currentPath);
            }
        }

        #region Event Handlers

        private async void DriveItem_Expanded(object sender, RoutedEventArgs e)
        {
            try
            {
                var driveItem = sender as TreeViewItem;
                if (driveItem?.Items.Count == 0)
                {
                    var drivePath = driveItem.Header.ToString();
                    await LoadDirectoryContentsAsync(driveItem, drivePath);
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"Failed to expand drive: {ex.Message}");
            }
        }

        private async void FolderItem_Expanded(object sender, RoutedEventArgs e)
        {
            try
            {
                var folderItem = sender as TreeViewItem;
                if (folderItem?.Items.Count == 0)
                {
                    var folderPath = folderItem.Tag?.ToString() ?? folderItem.Header.ToString();
                    if (!string.IsNullOrEmpty(folderPath))
                    {
                        await LoadDirectoryContentsAsync(folderItem, folderPath);
                    }
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"Failed to expand folder: {ex.Message}");
            }
        }

        private async Task LoadDirectoryContentsAsync(TreeViewItem parentItem, string path)
        {
            try
            {
                var items = await _fileService.GetDirectoryContentsAsync(path);
                foreach (var item in items.Where(i => i.IsDirectory))
                {
                    var childItem = new TreeViewItem { Header = item.Name, Tag = item.FullPath };
                    childItem.Expanded += FolderItem_Expanded;
                    parentItem.Items.Add(childItem);
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"Failed to load directory contents: {ex.Message}");
            }
        }

        private async void FolderTreeView_SelectedItemChanged(object sender, RoutedPropertyChangedEventArgs<object> e)
        {
            try
            {
                if (e.NewValue is TreeViewItem selectedItem && selectedItem.Tag is string path)
                {
                    await NavigateToPathAsync(path);
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"Failed to navigate from tree view: {ex.Message}");
            }
        }

        private async void FileListView_MouseDoubleClick(object sender, MouseButtonEventArgs e)
        {
            try
            {
                if (FileListView.SelectedItem is FileItem selectedFile)
                {
                    if (selectedFile.IsDirectory)
                    {
                        await NavigateToPathAsync(selectedFile.FullPath);
                    }
                    else if (selectedFile.IsArchive)
                    {
                        // Handle ZIP files
                        await HandleZipFileAsync(selectedFile.FullPath);
                    }
                    else
                    {
                        // Open file in default application or editor
                        OpenFile(selectedFile.FullPath);
                    }
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"Failed to open item: {ex.Message}");
            }
        }

        private async Task HandleZipFileAsync(string zipPath)
        {
            try
            {
                // Check if ZIP should be opened as folder
                var settings = App.Services.GetRequiredService<IConfigurationService>().GetSettings();
                if (settings?.Zip.OpenAsFolder == true)
                {
                    // Create temporary extraction directory
                    var tempDir = Path.Combine(Path.GetTempPath(), Path.GetRandomFileName());
                    Directory.CreateDirectory(tempDir);

                    // Extract ZIP contents
                    await _zipService.ExtractZipAsync(zipPath, tempDir);
                    
                    // Navigate to extracted contents
                    await NavigateToPathAsync(tempDir);
                }
                else
                {
                    // Open in default ZIP application
                    OpenFile(zipPath);
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"Failed to handle ZIP file: {ex.Message}");
            }
        }

        private void OpenFile(string filePath)
        {
            try
            {
                // Try to open with default application
                System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
                {
                    FileName = filePath,
                    UseShellExecute = true
                });
            }
            catch (Exception ex)
            {
                UpdateStatus($"Failed to open file: {ex.Message}");
            }
        }

        private void FileListView_KeyDown(object sender, System.Windows.Input.KeyEventArgs e)
        {
            try
            {
                if (e.Key == Key.F5)
                {
                    Refresh();
                    e.Handled = true;
                }
                else if (e.Key == Key.Delete)
                {
                    DeleteSelectedFiles();
                    e.Handled = true;
                }
                else if (e.Key == Key.F2)
                {
                    RenameSelectedFile();
                    e.Handled = true;
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"Key handling failed: {ex.Message}");
            }
        }

        private async void DeleteSelectedFiles()
        {
            try
            {
                var selectedFiles = FileListView.SelectedItems.Cast<FileItem>().ToList();
                if (selectedFiles.Count == 0) return;

                var result = System.Windows.MessageBox.Show(
                    $"Are you sure you want to delete {selectedFiles.Count} item(s)?",
                    "Confirm Delete",
                    System.Windows.MessageBoxButton.YesNo,
                    System.Windows.MessageBoxImage.Question);

                if (result == System.Windows.MessageBoxResult.Yes)
                {
                    foreach (var file in selectedFiles)
                    {
                        if (file.IsDirectory)
                        {
                            await _fileService.DeleteDirectoryAsync(file.FullPath, true);
                        }
                        else
                        {
                            await _fileService.DeleteFileAsync(file.FullPath);
                        }
                    }

                    Refresh();
                    UpdateStatus($"Deleted {selectedFiles.Count} item(s)");
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"Delete failed: {ex.Message}");
            }
        }

        private void RenameSelectedFile()
        {
            try
            {
                if (FileListView.SelectedItem is FileItem selectedFile)
                {
                    // Implement inline renaming
                    UpdateStatus("Rename functionality coming soon!");
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"Rename failed: {ex.Message}");
            }
        }

        private async void AddressTextBox_KeyDown(object sender, System.Windows.Input.KeyEventArgs e)
        {
            if (e.Key == Key.Enter)
            {
                e.Handled = true;
                await NavigateToPathAsync(AddressTextBox.Text);
            }
        }

        private async void UpButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                if (!string.IsNullOrEmpty(_currentPath))
                {
                    var parentPath = Directory.GetParent(_currentPath)?.FullName;
                    if (!string.IsNullOrEmpty(parentPath))
                    {
                        await NavigateToPathAsync(parentPath);
                    }
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"Failed to go up: {ex.Message}");
            }
        }

        private void RefreshButton_Click(object sender, RoutedEventArgs e)
        {
            Refresh();
        }

        #endregion
    }
}