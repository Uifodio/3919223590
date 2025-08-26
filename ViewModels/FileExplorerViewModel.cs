using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Microsoft.Extensions.DependencyInjection;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using WindowsFileManagerPro.Models;
using WindowsFileManagerPro.Services;

namespace WindowsFileManagerPro.ViewModels
{
    public partial class FileExplorerViewModel : ObservableObject
    {
        private readonly IFileService _fileService;
        private readonly IZipService _zipService;

        [ObservableProperty]
        private string _currentPath = "";

        [ObservableProperty]
        private ObservableCollection<FileItem> _files = new();

        [ObservableProperty]
        private ObservableCollection<FileItem> _selectedFiles = new();

        [ObservableProperty]
        private FileItem? _selectedFile;

        [ObservableProperty]
        private bool _isLoading = false;

        [ObservableProperty]
        private string _statusText = "Ready";

        [ObservableProperty]
        private int _totalFiles = 0;

        [ObservableProperty]
        private int _totalFolders = 0;

        [ObservableProperty]
        private long _totalSize = 0;

        public ICommand RefreshCommand { get; }
        public ICommand NavigateCommand { get; }
        public ICommand OpenFileCommand { get; }
        public ICommand DeleteCommand { get; }
        public ICommand RenameCommand { get; }
        public ICommand CopyCommand { get; }
        public ICommand CutCommand { get; }
        public ICommand PasteCommand { get; }
        public ICommand NewFolderCommand { get; }
        public ICommand NewFileCommand { get; }

        public FileExplorerViewModel(IFileService fileService, IZipService zipService)
        {
            _fileService = fileService;
            _zipService = zipService;

            RefreshCommand = new RelayCommand(Refresh);
            NavigateCommand = new RelayCommand<string>(Navigate);
            OpenFileCommand = new RelayCommand<FileItem>(OpenFile);
            DeleteCommand = new RelayCommand(Delete);
            RenameCommand = new RelayCommand(Rename);
            CopyCommand = new RelayCommand(Copy);
            CutCommand = new RelayCommand(Cut);
            PasteCommand = new RelayCommand(Paste);
            NewFolderCommand = new RelayCommand(NewFolder);
            NewFileCommand = new RelayCommand(NewFile);

            InitializeViewModel();
        }

        private void InitializeViewModel()
        {
            // Initialize with user profile directory
            var userProfile = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
            Navigate(userProfile);
        }

        public async void Navigate(string? path)
        {
            if (string.IsNullOrEmpty(path))
                return;

            try
            {
                IsLoading = true;
                StatusText = "Loading...";

                CurrentPath = path;
                var items = await _fileService.GetDirectoryContentsAsync(path);
                
                Files.Clear();
                foreach (var item in items)
                {
                    Files.Add(item);
                }

                UpdateStatistics();
                StatusText = $"Loaded {Files.Count} items";
            }
            catch (Exception ex)
            {
                StatusText = $"Navigation failed: {ex.Message}";
            }
            finally
            {
                IsLoading = false;
            }
        }

        public async void Refresh()
        {
            if (!string.IsNullOrEmpty(CurrentPath))
            {
                Navigate(CurrentPath);
            }
        }

        private async void OpenFile(FileItem? file)
        {
            if (file == null)
                return;

            try
            {
                if (file.IsDirectory)
                {
                    Navigate(file.FullPath);
                }
                else if (file.IsArchive)
                {
                    // Handle ZIP files
                    await HandleZipFile(file);
                }
                else
                {
                    // Open with default application
                    System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
                    {
                        FileName = file.FullPath,
                        UseShellExecute = true
                    });
                }
            }
            catch (Exception ex)
            {
                StatusText = $"Failed to open file: {ex.Message}";
            }
        }

        private async Task HandleZipFile(FileItem file)
        {
            try
            {
                // Check if ZIP should be opened as folder
                var settings = ((App)Application.Current).Services.GetRequiredService<IConfigurationService>().GetSettings();
                if (settings?.Zip.OpenAsFolder == true)
                {
                    // Create temporary extraction directory
                    var tempDir = Path.Combine(Path.GetTempPath(), Path.GetRandomFileName());
                    Directory.CreateDirectory(tempDir);

                    // Extract ZIP contents
                    await _zipService.ExtractZipAsync(file.FullPath, tempDir);
                    
                    // Navigate to extracted contents
                    Navigate(tempDir);
                }
                else
                {
                    // Open in default ZIP application
                    System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
                    {
                        FileName = file.FullPath,
                        UseShellExecute = true
                    });
                }
            }
            catch (Exception ex)
            {
                StatusText = $"Failed to handle ZIP file: {ex.Message}";
            }
        }

        private async void Delete()
        {
            if (SelectedFiles.Count == 0)
                return;

            try
            {
                var result = System.Windows.MessageBox.Show(
                    $"Are you sure you want to delete {SelectedFiles.Count} item(s)?",
                    "Confirm Delete",
                    System.Windows.MessageBoxButton.YesNo,
                    System.Windows.MessageBoxImage.Question);

                if (result == System.Windows.MessageBoxResult.Yes)
                {
                    foreach (var file in SelectedFiles)
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
                    StatusText = $"Deleted {SelectedFiles.Count} item(s)";
                }
            }
            catch (Exception ex)
            {
                StatusText = $"Delete failed: {ex.Message}";
            }
        }

        private void Rename()
        {
            if (SelectedFile == null)
                return;

            // This would be implemented with inline editing in the view
            StatusText = "Rename functionality coming soon!";
        }

        private void Copy()
        {
            if (SelectedFiles.Count == 0)
                return;

            try
            {
                var clipboardService = ((App)Application.Current).Services.GetRequiredService<IClipboardService>();
                clipboardService.CopyFilesToClipboardAsync(SelectedFiles.Select(f => f.FullPath));
                StatusText = $"Copied {SelectedFiles.Count} item(s) to clipboard";
            }
            catch (Exception ex)
            {
                StatusText = $"Copy failed: {ex.Message}";
            }
        }

        private void Cut()
        {
            if (SelectedFiles.Count == 0)
                return;

            try
            {
                var clipboardService = ((App)Application.Current).Services.GetRequiredService<IClipboardService>();
                clipboardService.CutFilesToClipboardAsync(SelectedFiles.Select(f => f.FullPath));
                StatusText = $"Cut {SelectedFiles.Count} item(s) to clipboard";
            }
            catch (Exception ex)
            {
                StatusText = $"Cut failed: {ex.Message}";
            }
        }

        private async void Paste()
        {
            try
            {
                var clipboardService = ((App)Application.Current).Services.GetRequiredService<IClipboardService>();
                var success = await clipboardService.PasteFilesFromClipboardAsync(CurrentPath);
                
                if (success)
                {
                    Refresh();
                    StatusText = "Files pasted successfully";
                }
                else
                {
                    StatusText = "Paste failed";
                }
            }
            catch (Exception ex)
            {
                StatusText = $"Paste failed: {ex.Message}";
            }
        }

        private async void NewFolder()
        {
            try
            {
                var folderName = $"New Folder {DateTime.Now:yyyyMMdd_HHmmss}";
                var folderPath = Path.Combine(CurrentPath, folderName);
                
                var success = await _fileService.CreateDirectoryAsync(folderPath);
                if (success)
                {
                    Refresh();
                    StatusText = $"Created folder: {folderName}";
                }
                else
                {
                    StatusText = "Failed to create folder";
                }
            }
            catch (Exception ex)
            {
                StatusText = $"Create folder failed: {ex.Message}";
            }
        }

        private async void NewFile()
        {
            try
            {
                var fileName = $"New File {DateTime.Now:yyyyMMdd_HHmmss}.txt";
                var filePath = Path.Combine(CurrentPath, fileName);
                
                var success = await _fileService.CreateFileAsync(filePath);
                if (success)
                {
                    Refresh();
                    StatusText = $"Created file: {fileName}";
                }
                else
                {
                    StatusText = "Failed to create file";
                }
            }
            catch (Exception ex)
            {
                StatusText = $"Create file failed: {ex.Message}";
            }
        }

        private void UpdateStatistics()
        {
            TotalFiles = Files.Count(f => !f.IsDirectory);
            TotalFolders = Files.Count(f => f.IsDirectory);
            TotalSize = Files.Where(f => !f.IsDirectory).Sum(f => f.Size);
        }

        partial void OnSelectedFileChanged(FileItem? value)
        {
            if (value != null)
            {
                StatusText = $"Selected: {value.Name}";
            }
        }
    }
}