using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System;
using System.Collections.ObjectModel;
using System.IO;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Windows.Input;
using WindowsFileManagerPro.Services;

namespace WindowsFileManagerPro.ViewModels
{
    public partial class SearchViewModel : ObservableObject
    {
        private readonly ISearchService _searchService;

        [ObservableProperty]
        private string _searchPath = "";

        [ObservableProperty]
        private string _searchText = "";

        [ObservableProperty]
        private bool _caseSensitive = false;

        [ObservableProperty]
        private bool _useRegex = false;

        [ObservableProperty]
        private bool _recursive = true;

        [ObservableProperty]
        private string _fileTypes = "*.txt,*.cs,*.js,*.py,*.html,*.css,*.xml,*.json";

        [ObservableProperty]
        private string _excludePatterns = "*.tmp,*.bak,*.log";

        [ObservableProperty]
        private bool _isSearching = false;

        [ObservableProperty]
        private string _statusText = "Ready";

        [ObservableProperty]
        private int _progressValue = 0;

        [ObservableProperty]
        private int _resultCount = 0;

        [ObservableProperty]
        private ObservableCollection<SearchResult> _searchResults = new();

        [ObservableProperty]
        private SearchResult? _selectedResult;

        public ICommand SearchCommand { get; }
        public ICommand StopSearchCommand { get; }
        public ICommand ClearResultsCommand { get; }
        public ICommand ExportResultsCommand { get; }
        public ICommand BrowsePathCommand { get; }
        public ICommand OpenFileCommand { get; }

        public SearchViewModel(ISearchService searchService)
        {
            _searchService = searchService;

            SearchCommand = new RelayCommand(Search, CanSearch);
            StopSearchCommand = new RelayCommand(StopSearch, CanStopSearch);
            ClearResultsCommand = new RelayCommand(ClearResults);
            ExportResultsCommand = new RelayCommand(ExportResults, CanExportResults);
            BrowsePathCommand = new RelayCommand(BrowsePath);
            OpenFileCommand = new RelayCommand<SearchResult>(OpenFile);

            InitializeViewModel();
        }

        private void InitializeViewModel()
        {
            // Set default search path to user profile
            SearchPath = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
        }

        private async void Search()
        {
            if (string.IsNullOrEmpty(SearchText))
                return;

            try
            {
                IsSearching = true;
                StatusText = "Searching...";
                ProgressValue = 0;
                SearchResults.Clear();
                ResultCount = 0;

                // Perform search
                var results = await _searchService.SearchInDirectoryAsync(
                    SearchPath, 
                    SearchText, 
                    Recursive, 
                    CaseSensitive, 
                    UseRegex);

                // Process results
                foreach (var result in results)
                {
                    SearchResults.Add(result);
                    ResultCount = SearchResults.Count;
                }

                StatusText = $"Search completed. Found {ResultCount} results.";
            }
            catch (Exception ex)
            {
                StatusText = $"Search failed: {ex.Message}";
            }
            finally
            {
                IsSearching = false;
                ProgressValue = 100;
            }
        }

        private void StopSearch()
        {
            try
            {
                _searchService.CancelSearchAsync();
                StatusText = "Search cancelled";
            }
            catch (Exception ex)
            {
                StatusText = $"Failed to cancel search: {ex.Message}";
            }
        }

        private void ClearResults()
        {
            SearchResults.Clear();
            ResultCount = 0;
            StatusText = "Results cleared";
        }

        private async void ExportResults()
        {
            if (SearchResults.Count == 0)
                return;

            try
            {
                var saveDialog = new Microsoft.Win32.SaveFileDialog
                {
                    Title = "Export Search Results",
                    Filter = "CSV Files (*.csv)|*.csv|Text Files (*.txt)|*.txt",
                    DefaultExt = "csv"
                };

                if (saveDialog.ShowDialog() == true)
                {
                    await ExportResultsAsync(saveDialog.FileName);
                    StatusText = $"Results exported to {Path.GetFileName(saveDialog.FileName)}";
                }
            }
            catch (Exception ex)
            {
                StatusText = $"Export failed: {ex.Message}";
            }
        }

        private async Task ExportResultsAsync(string filePath)
        {
            await Task.Run(() =>
            {
                try
                {
                    var extension = Path.GetExtension(filePath).ToLowerInvariant();
                    
                    if (extension == ".csv")
                    {
                        ExportToCsv(filePath);
                    }
                    else
                    {
                        ExportToText(filePath);
                    }
                }
                catch (Exception ex)
                {
                    throw new Exception($"Export failed: {ex.Message}");
                }
            });
        }

        private void ExportToCsv(string filePath)
        {
            using var writer = new StreamWriter(filePath);
            
            // Write header
            writer.WriteLine("File,Path,Line,Context,Found At");
            
            // Write data
            foreach (var result in SearchResults)
            {
                var line = $"\"{result.FileName}\",\"{result.FilePath}\",{result.LineNumber},\"{result.Context}\",\"{result.FoundAt:yyyy-MM-dd HH:mm:ss}\"";
                writer.WriteLine(line);
            }
        }

        private void ExportToText(string filePath)
        {
            using var writer = new StreamWriter(filePath);
            
            writer.WriteLine("Search Results");
            writer.WriteLine("==============");
            writer.WriteLine();
            
            foreach (var result in SearchResults)
            {
                writer.WriteLine($"File: {result.FileName}");
                writer.WriteLine($"Path: {result.FilePath}");
                writer.WriteLine($"Line: {result.LineNumber}");
                writer.WriteLine($"Context: {result.Context}");
                writer.WriteLine($"Found: {result.FoundAt:yyyy-MM-dd HH:mm:ss}");
                writer.WriteLine(new string('-', 50));
                writer.WriteLine();
            }
        }

        private void BrowsePath()
        {
            try
            {
                var folderDialog = new System.Windows.Forms.FolderBrowserDialog
                {
                    Description = "Select folder to search in"
                };

                if (folderDialog.ShowDialog() == System.Windows.Forms.DialogResult.OK)
                {
                    SearchPath = folderDialog.SelectedPath;
                }
            }
            catch (Exception ex)
            {
                StatusText = $"Browse failed: {ex.Message}";
            }
        }

        private void OpenFile(SearchResult? result)
        {
            if (result == null)
                return;

            try
            {
                // This would be handled by the main window to open the file
                StatusText = $"Opening: {result.FileName}";
            }
            catch (Exception ex)
            {
                StatusText = $"Failed to open file: {ex.Message}";
            }
        }

        private bool CanSearch() => !IsSearching && !string.IsNullOrEmpty(SearchText) && !string.IsNullOrEmpty(SearchPath);
        private bool CanStopSearch() => IsSearching;
        private bool CanExportResults() => SearchResults.Count > 0;

        partial void OnSearchTextChanged(string value)
        {
            // Commands automatically update their CanExecute state
        }

        partial void OnSearchPathChanged(string value)
        {
            // Commands automatically update their CanExecute state
        }

        partial void OnIsSearchingChanged(bool value)
        {
            // Commands automatically update their CanExecute state
        }

        partial void OnSearchResultsChanged(ObservableCollection<SearchResult> value)
        {
            // Commands automatically update their CanExecute state
        }
    }
}