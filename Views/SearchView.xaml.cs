using Microsoft.Extensions.DependencyInjection;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Forms;
using WindowsFileManagerPro.Services;

namespace WindowsFileManagerPro.Views
{
    public partial class SearchView : Window
    {
        private readonly ISearchService _searchService;
        private readonly IFileService _fileService;
        private List<SearchResult> _searchResults = new();

        public SearchView()
        {
            InitializeComponent();
            var services = App.Services;
            _searchService = services.GetRequiredService<ISearchService>();
            _fileService = services.GetRequiredService<IFileService>();
            InitializeSearchView();
        }

        private void InitializeSearchView()
        {
            try
            {
                // Set default search path to user profile
                var userProfile = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
                SearchPathTextBox.Text = userProfile;
                
                // Focus on search text box
                SearchTextTextBox.Focus();
            }
            catch (Exception ex)
            {
                UpdateStatus($"Failed to initialize search view: {ex.Message}");
            }
        }

        private async void SearchButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var searchPath = SearchPathTextBox.Text.Trim();
                var searchText = SearchTextTextBox.Text.Trim();

                if (string.IsNullOrEmpty(searchPath))
                {
                    System.Windows.MessageBox.Show("Please enter a search path.", "Search Error", System.Windows.MessageBoxButton.OK, System.Windows.MessageBoxImage.Warning);
                    return;
                }

                if (string.IsNullOrEmpty(searchText))
                {
                    System.Windows.MessageBox.Show("Please enter search text.", "Search Error", System.Windows.MessageBoxButton.OK, System.Windows.MessageBoxImage.Warning);
                    return;
                }

                if (!Directory.Exists(searchPath))
                {
                    System.Windows.MessageBox.Show("The specified search path does not exist.", "Search Error", System.Windows.MessageBoxButton.OK, System.Windows.MessageBoxImage.Warning);
                    return;
                }

                await PerformSearchAsync(searchPath, searchText);
            }
            catch (Exception ex)
            {
                UpdateStatus($"Search failed: {ex.Message}");
            }
        }

        private async Task PerformSearchAsync(string searchPath, string searchText)
        {
            try
            {
                // Clear previous results
                _searchResults.Clear();
                ResultsListView.ItemsSource = null;
                UpdateResultCount();

                // Show progress
                SearchProgressBar.Visibility = Visibility.Visible;
                UpdateStatus("Searching...");

                // Get search options
                var caseSensitive = CaseSensitiveCheckBox.IsChecked ?? false;
                var recursive = RecursiveCheckBox.IsChecked ?? true;

                // Perform search
                var results = await _searchService.SearchInDirectoryAsync(
                    searchPath, 
                    searchText, 
                    recursive, 
                    caseSensitive, 
                    false); // useRegex

                _searchResults = results.ToList();

                // Update UI
                ResultsListView.ItemsSource = _searchResults;
                UpdateResultCount();
                UpdateStatus($"Search completed. Found {_searchResults.Count} results.");

                // Hide progress
                SearchProgressBar.Visibility = Visibility.Collapsed;
            }
            catch (Exception ex)
            {
                UpdateStatus($"Search failed: {ex.Message}");
                SearchProgressBar.Visibility = Visibility.Collapsed;
            }
        }

        private void UpdateResultCount()
        {
            try
            {
                var count = _searchResults.Count;
                ResultCountText.Text = $"{count} result{(count == 1 ? "" : "s")} found";
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to update result count: {ex.Message}");
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

        private void BrowseButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var folderDialog = new FolderBrowserDialog
                {
                    Description = "Select folder to search in"
                };

                if (folderDialog.ShowDialog() == System.Windows.Forms.DialogResult.OK)
                {
                    SearchPathTextBox.Text = folderDialog.SelectedPath;
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"Browse failed: {ex.Message}");
            }
        }

        private void ClearResultsButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                _searchResults.Clear();
                ResultsListView.ItemsSource = null;
                UpdateResultCount();
                UpdateStatus("Results cleared");
            }
            catch (Exception ex)
            {
                UpdateStatus($"Clear failed: {ex.Message}");
            }
        }

        private async void ExportResultsButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                if (_searchResults.Count == 0)
                {
                    System.Windows.MessageBox.Show("No results to export.", "Export", System.Windows.MessageBoxButton.OK, System.Windows.MessageBoxImage.Information);
                    return;
                }

                var saveDialog = new Microsoft.Win32.SaveFileDialog
                {
                    Title = "Export Search Results",
                    Filter = "CSV Files (*.csv)|*.csv|Text Files (*.txt)|*.txt",
                    DefaultExt = "csv"
                };

                if (saveDialog.ShowDialog() == true)
                {
                    await ExportResultsAsync(saveDialog.FileName);
                    UpdateStatus($"Results exported to {Path.GetFileName(saveDialog.FileName)}");
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"Export failed: {ex.Message}");
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
            foreach (var result in _searchResults)
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
            
            foreach (var result in _searchResults)
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

        private void ResultsListView_MouseDoubleClick(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            try
            {
                if (ResultsListView.SelectedItem is SearchResult result)
                {
                    // Open the file in the main editor
                    var mainWindow = Owner as MainWindow;
                    if (mainWindow != null)
                    {
                        mainWindow.OpenFileInEditor(result.FilePath);
                        Close();
                    }
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"Failed to open file: {ex.Message}");
            }
        }

        protected override void OnSourceInitialized(EventArgs e)
        {
            base.OnSourceInitialized(e);
            
            // Set owner if available
            if (System.Windows.Application.Current.MainWindow != null && System.Windows.Application.Current.MainWindow != this)
            {
                Owner = System.Windows.Application.Current.MainWindow;
            }
        }
    }
}