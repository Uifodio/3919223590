using Microsoft.Extensions.DependencyInjection;
using System;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using WindowsFileManagerPro.Services;
using WindowsFileManagerPro.ViewModels;

namespace WindowsFileManagerPro.Views
{
    public partial class MainWindow : Window
    {
        private readonly MainWindowViewModel _viewModel;
        private readonly IFileService _fileService;
        private readonly IEditorService _editorService;
        private readonly IConfigurationService _configService;

        public MainWindow()
        {
            InitializeComponent();
            
            var services = App.Services;
            _viewModel = services.GetRequiredService<MainWindowViewModel>();
            _fileService = services.GetRequiredService<IFileService>();
            _editorService = services.GetRequiredService<IEditorService>();
            _configService = services.GetRequiredService<IConfigurationService>();
            
            DataContext = _viewModel;
            LoadSettings();
        }

        private void LoadSettings()
        {
            try
            {
                var settings = _configService.GetSettings();
                if (settings != null)
                {
                    // Apply theme
                    if (settings.Theme == "Light")
                    {
                        LightTheme_Click(this, new RoutedEventArgs());
                    }
                    
                    // Apply window size and position
                    if (settings.WindowWidth > 0 && settings.WindowHeight > 0)
                    {
                        Width = settings.WindowWidth;
                        Height = settings.WindowHeight;
                    }
                    
                    if (settings.WindowLeft >= 0 && settings.WindowTop >= 0)
                    {
                        Left = settings.WindowLeft;
                        Top = settings.WindowTop;
                    }
                }
            }
            catch (Exception ex)
            {
                // Log error but don't crash
                Console.WriteLine($"Failed to load settings: {ex.Message}");
            }
        }

        private void SaveSettings()
        {
            try
            {
                var settings = _configService.GetSettings() ?? new Models.AppSettings();
                settings.WindowWidth = (int)Width;
                settings.WindowHeight = (int)Height;
                settings.WindowLeft = (int)Left;
                settings.WindowTop = (int)Top;
                _configService.SaveSettings(settings);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to save settings: {ex.Message}");
            }
        }

        #region Menu Event Handlers

        private void NewWindow_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var newWindow = new MainWindow();
                newWindow.Show();
                UpdateStatus("New window opened");
            }
            catch (Exception ex)
            {
                ShowError("Failed to open new window", ex);
            }
        }

        private void Open_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var openFileDialog = new Microsoft.Win32.OpenFileDialog
                {
                    Title = "Open File",
                    Filter = "All Files (*.*)|*.*|Text Files (*.txt)|*.txt|Code Files (*.cs,*.js,*.py,*.html,*.css,*.xml,*.json)|*.cs;*.js;*.py;*.html;*.css;*.xml;*.json"
                };

                if (openFileDialog.ShowDialog() == true)
                {
                    OpenFileInEditor(openFileDialog.FileName);
                }
            }
            catch (Exception ex)
            {
                ShowError("Failed to open file", ex);
            }
        }

        private void Save_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var currentTab = MainTabControl.SelectedItem as TabItem;
                if (currentTab?.Content is EditorView editorView)
                {
                    editorView.SaveFile();
                    UpdateStatus("File saved successfully");
                }
                else
                {
                    System.Windows.MessageBox.Show("No file is currently open for editing.", "Save", System.Windows.MessageBoxButton.OK, System.Windows.MessageBoxImage.Information);
                }
            }
            catch (Exception ex)
            {
                ShowError("Failed to save file", ex);
            }
        }

        private void Exit_Click(object sender, RoutedEventArgs e)
        {
            SaveSettings();
            Close();
        }

        private void Undo_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var currentTab = MainTabControl.SelectedItem as TabItem;
                if (currentTab?.Content is EditorView editorView)
                {
                    editorView.Undo();
                }
            }
            catch (Exception ex)
            {
                ShowError("Failed to undo", ex);
            }
        }

        private void Redo_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var currentTab = MainTabControl.SelectedItem as TabItem;
                if (currentTab?.Content is EditorView editorView)
                {
                    editorView.Redo();
                }
            }
            catch (Exception ex)
            {
                ShowError("Failed to redo", ex);
            }
        }

        private void Cut_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var currentTab = MainTabControl.SelectedItem as TabItem;
                if (currentTab?.Content is EditorView editorView)
                {
                    editorView.Cut();
                }
            }
            catch (Exception ex)
            {
                ShowError("Failed to cut", ex);
            }
        }

        private void Copy_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var currentTab = MainTabControl.SelectedItem as TabItem;
                if (currentTab?.Content is EditorView editorView)
                {
                    editorView.Copy();
                }
            }
            catch (Exception ex)
            {
                ShowError("Failed to copy", ex);
            }
        }

        private void Paste_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var currentTab = MainTabControl.SelectedItem as TabItem;
                if (currentTab?.Content is EditorView editorView)
                {
                    editorView.Paste();
                }
            }
            catch (Exception ex)
            {
                ShowError("Failed to paste", ex);
            }
        }

        private void Find_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var currentTab = MainTabControl.SelectedItem as TabItem;
                if (currentTab?.Content is EditorView editorView)
                {
                    editorView.ShowFindDialog();
                }
            }
            catch (Exception ex)
            {
                ShowError("Failed to show find dialog", ex);
            }
        }

        private void Replace_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var currentTab = MainTabControl.SelectedItem as TabItem;
                if (currentTab?.Content is EditorView editorView)
                {
                    editorView.ShowReplaceDialog();
                }
            }
            catch (Exception ex)
            {
                ShowError("Failed to show replace dialog", ex);
            }
        }

        private void DarkTheme_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                            System.Windows.Application.Current.Resources.MergedDictionaries.Clear();
            System.Windows.Application.Current.Resources.MergedDictionaries.Add(
                new ResourceDictionary { Source = new Uri("Themes/DarkTheme.xaml", UriKind.Relative) });
                
                var settings = _configService.GetSettings() ?? new Models.AppSettings();
                settings.Theme = "Dark";
                _configService.SaveSettings(settings);
                
                UpdateStatus("Dark theme applied");
            }
            catch (Exception ex)
            {
                ShowError("Failed to apply dark theme", ex);
            }
        }

        private void LightTheme_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                            System.Windows.Application.Current.Resources.MergedDictionaries.Clear();
            System.Windows.Application.Current.Resources.MergedDictionaries.Add(
                new ResourceDictionary { Source = new Uri("Themes/LightTheme.xaml", UriKind.Relative) });
                
                var settings = _configService.GetSettings() ?? new Models.AppSettings();
                settings.Theme = "Light";
                _configService.SaveSettings(settings);
                
                UpdateStatus("Light theme applied");
            }
            catch (Exception ex)
            {
                ShowError("Failed to apply light theme", ex);
            }
        }

        private void TreeView_Click(object sender, RoutedEventArgs e)
        {
            // Implement view switching
            UpdateStatus("Tree view selected");
        }

        private void ListView_Click(object sender, RoutedEventArgs e)
        {
            // Implement view switching
            UpdateStatus("List view selected");
        }

        private void DetailsView_Click(object sender, RoutedEventArgs e)
        {
            // Implement view switching
            UpdateStatus("Details view selected");
        }

        private void Search_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var searchWindow = new SearchView();
                searchWindow.Show();
                UpdateStatus("Search window opened");
            }
            catch (Exception ex)
            {
                ShowError("Failed to open search window", ex);
            }
        }

        private void ZipManager_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                // Implement ZIP manager
                System.Windows.MessageBox.Show("ZIP Manager feature coming soon!", "ZIP Manager", System.Windows.MessageBoxButton.OK, System.Windows.MessageBoxImage.Information);
                UpdateStatus("ZIP Manager requested");
            }
            catch (Exception ex)
            {
                ShowError("Failed to open ZIP manager", ex);
            }
        }

        private void BackupManager_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                // Implement backup manager
                System.Windows.MessageBox.Show("Backup Manager feature coming soon!", "Backup Manager", System.Windows.MessageBoxButton.OK, System.Windows.MessageBoxImage.Information);
                UpdateStatus("Backup Manager requested");
            }
            catch (Exception ex)
            {
                ShowError("Failed to open backup manager", ex);
            }
        }

        private void About_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                System.Windows.MessageBox.Show(
                    "Windows File Manager Pro\nVersion 1.0.0\n\nProfessional file management with built-in editor\n\nBuilt with ❤️ for Windows developers and power users",
                    "About",
                    System.Windows.MessageBoxButton.OK,
                    System.Windows.MessageBoxImage.Information);
            }
            catch (Exception ex)
            {
                ShowError("Failed to show about dialog", ex);
            }
        }

        private void Documentation_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                // Open documentation
                System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
                {
                    FileName = "https://github.com/yourusername/windows-file-manager-pro",
                    UseShellExecute = true
                });
                UpdateStatus("Documentation opened");
            }
            catch (Exception ex)
            {
                ShowError("Failed to open documentation", ex);
            }
        }

        #endregion

        #region Toolbar Event Handlers

        private void Delete_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                // Implement delete functionality
                UpdateStatus("Delete operation requested");
            }
            catch (Exception ex)
            {
                ShowError("Failed to delete", ex);
            }
        }

        private void Rename_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                // Implement rename functionality
                UpdateStatus("Rename operation requested");
            }
            catch (Exception ex)
            {
                ShowError("Failed to rename", ex);
            }
        }

        private void Refresh_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                FileExplorer.Refresh();
                UpdateStatus("File explorer refreshed");
            }
            catch (Exception ex)
            {
                ShowError("Failed to refresh", ex);
            }
        }

        #endregion

        #region Welcome Tab Event Handlers

        private void OpenFolder_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var folderDialog = new System.Windows.Forms.FolderBrowserDialog
                {
                    Description = "Select a folder to open"
                };

                if (folderDialog.ShowDialog() == System.Windows.Forms.DialogResult.OK)
                {
                    FileExplorer.NavigateToFolder(folderDialog.SelectedPath);
                    UpdateStatus($"Opened folder: {folderDialog.SelectedPath}");
                }
            }
            catch (Exception ex)
            {
                ShowError("Failed to open folder", ex);
            }
        }

        private void NewFile_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                CreateNewFileTab();
                UpdateStatus("New file created");
            }
            catch (Exception ex)
            {
                ShowError("Failed to create new file", ex);
            }
        }

        #endregion

        #region Helper Methods

        public void OpenFileInEditor(string filePath)
        {
            try
            {
                if (File.Exists(filePath))
                {
                    CreateFileTab(filePath);
                    UpdateStatus($"Opened file: {Path.GetFileName(filePath)}");
                }
            }
            catch (Exception ex)
            {
                ShowError($"Failed to open file: {filePath}", ex);
            }
        }

        private void CreateFileTab(string filePath)
        {
            try
            {
                var fileName = Path.GetFileName(filePath);
                var editorView = new EditorView(filePath);
                
                var tabItem = new TabItem
                {
                    Header = fileName,
                    Content = editorView,
                    Tag = filePath
                };

                MainTabControl.Items.Add(tabItem);
                MainTabControl.SelectedItem = tabItem;
            }
            catch (Exception ex)
            {
                ShowError("Failed to create file tab", ex);
            }
        }

        private void CreateNewFileTab()
        {
            try
            {
                var editorView = new EditorView();
                
                var tabItem = new TabItem
                {
                    Header = "Untitled",
                    Content = editorView,
                    Tag = "untitled"
                };

                MainTabControl.Items.Add(tabItem);
                MainTabControl.SelectedItem = tabItem;
            }
            catch (Exception ex)
            {
                ShowError("Failed to create new file tab", ex);
            }
        }

        private void UpdateStatus(string message)
        {
            StatusText.Text = message;
            FileCountText.Text = $"{MainTabControl.Items.Count} tabs";
        }

        private void ShowError(string message, Exception ex)
        {
                            System.Windows.MessageBox.Show($"{message}: {ex.Message}", "Error", System.Windows.MessageBoxButton.OK, System.Windows.MessageBoxImage.Error);
            UpdateStatus($"Error: {message}");
        }

        #endregion

        protected override void OnClosed(EventArgs e)
        {
            SaveSettings();
            base.OnClosed(e);
        }
    }
}