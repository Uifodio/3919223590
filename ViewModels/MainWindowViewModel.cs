using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System;
using System.Collections.ObjectModel;
using System.Windows.Input;
using WindowsFileManagerPro.Models;

namespace WindowsFileManagerPro.ViewModels
{
    public partial class MainWindowViewModel : ObservableObject
    {
        [ObservableProperty]
        private string _title = "Windows File Manager Pro";

        [ObservableProperty]
        private string _currentPath = "";

        [ObservableProperty]
        private string _statusText = "Ready";

        [ObservableProperty]
        private int _fileCount = 0;

        [ObservableProperty]
        private bool _isDarkTheme = true;

        [ObservableProperty]
        private ObservableCollection<FileItem> _recentFiles = new();

        [ObservableProperty]
        private ObservableCollection<string> _favoritePaths = new();

        public ICommand NewWindowCommand { get; }
        public ICommand OpenFileCommand { get; }
        public ICommand SaveFileCommand { get; }
        public ICommand SearchCommand { get; }
        public ICommand ToggleThemeCommand { get; }

        public MainWindowViewModel()
        {
            NewWindowCommand = new RelayCommand(NewWindow);
            OpenFileCommand = new RelayCommand<string>(OpenFile);
            SaveFileCommand = new RelayCommand(SaveFile);
            SearchCommand = new RelayCommand(Search);
            ToggleThemeCommand = new RelayCommand(ToggleTheme);

            InitializeViewModel();
        }

        private void InitializeViewModel()
        {
            // Initialize with default values
            CurrentPath = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
            
            // Load recent files and favorites from settings
            LoadUserPreferences();
        }

        private void NewWindow()
        {
            // This would be handled by the view
        }

        private void OpenFile(string? filePath)
        {
            if (!string.IsNullOrEmpty(filePath))
            {
                // This would be handled by the view
            }
        }

        private void SaveFile()
        {
            // This would be handled by the view
        }

        private void Search()
        {
            // This would be handled by the view
        }

        private void ToggleTheme()
        {
            IsDarkTheme = !IsDarkTheme;
            // Theme switching would be handled by the view
        }

        private void LoadUserPreferences()
        {
            // Load recent files and favorite paths from settings
            // This would integrate with the configuration service
        }

        public void UpdateStatus(string status)
        {
            StatusText = status;
        }

        public void UpdateFileCount(int count)
        {
            FileCount = count;
        }

        public void UpdateCurrentPath(string path)
        {
            CurrentPath = path;
        }

        public void AddRecentFile(FileItem file)
        {
            if (file != null && !RecentFiles.Any(f => f.FullPath == file.FullPath))
            {
                RecentFiles.Insert(0, file);
                
                // Keep only last 20 recent files
                while (RecentFiles.Count > 20)
                {
                    RecentFiles.RemoveAt(RecentFiles.Count - 1);
                }
            }
        }

        public void AddFavoritePath(string path)
        {
            if (!string.IsNullOrEmpty(path) && !FavoritePaths.Contains(path))
            {
                FavoritePaths.Add(path);
            }
        }

        public void RemoveFavoritePath(string path)
        {
            FavoritePaths.Remove(path);
        }
    }
}