using Microsoft.Extensions.DependencyInjection;
using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using WindowsFileManagerPro.Services;

namespace WindowsFileManagerPro.Views
{
    public partial class EditorView : UserControl
    {
        private readonly IEditorService _editorService;
        private string _currentFilePath = "";
        private string _currentLanguage = "Plain Text";
        private bool _isModified = false;
        private bool _isLoading = false;

        public EditorView()
        {
            InitializeComponent();
            var services = ((App)Application.Current).Services;
            _editorService = services.GetRequiredService<IEditorService>();
            InitializeEditor();
        }

        public EditorView(string filePath) : this()
        {
            LoadFile(filePath);
        }

        private void InitializeEditor()
        {
            try
            {
                // Initialize language combo box
                var languages = _editorService.GetSupportedLanguagesAsync().Result;
                LanguageComboBox.ItemsSource = languages;
                LanguageComboBox.SelectedItem = "Plain Text";

                // Set up scroll synchronization
                EditorScrollViewer.ScrollChanged += EditorScrollViewer_ScrollChanged;
                LineNumbersScrollViewer.ScrollChanged += LineNumbersScrollViewer_ScrollChanged;

                // Set initial text
                EditorTextBox.Text = "// Welcome to Windows File Manager Pro Editor\n// Start typing your code here...";
                UpdateLineNumbers();
                UpdateStatus("Editor ready");
            }
            catch (Exception ex)
            {
                UpdateStatus($"Failed to initialize editor: {ex.Message}");
            }
        }

        public async void LoadFile(string filePath)
        {
            try
            {
                _isLoading = true;
                UpdateStatus("Loading file...");

                if (string.IsNullOrEmpty(filePath) || !File.Exists(filePath))
                {
                    UpdateStatus("Invalid file path");
                    return;
                }

                _currentFilePath = filePath;
                var content = await _editorService.LoadFileAsync(filePath);
                EditorTextBox.Text = content;

                // Detect language
                _currentLanguage = await _editorService.GetSyntaxLanguageAsync(filePath);
                LanguageComboBox.SelectedItem = _currentLanguage;

                // Update UI
                UpdateLineNumbers();
                UpdateStatus($"Loaded: {Path.GetFileName(filePath)}");
                _isModified = false;
            }
            catch (Exception ex)
            {
                UpdateStatus($"Failed to load file: {ex.Message}");
            }
            finally
            {
                _isLoading = false;
            }
        }

        public async void SaveFile()
        {
            try
            {
                if (string.IsNullOrEmpty(_currentFilePath) || _currentFilePath == "untitled")
                {
                    SaveFileAs();
                    return;
                }

                UpdateStatus("Saving file...");
                var success = await _editorService.SaveFileAsync(_currentFilePath, EditorTextBox.Text);
                
                if (success)
                {
                    UpdateStatus($"Saved: {Path.GetFileName(_currentFilePath)}");
                    _isModified = false;
                }
                else
                {
                    UpdateStatus("Failed to save file");
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"Save error: {ex.Message}");
            }
        }

        public async void SaveFileAs()
        {
            try
            {
                var saveDialog = new Microsoft.Win32.SaveFileDialog
                {
                    Title = "Save File As",
                    Filter = "All Files (*.*)|*.*|Text Files (*.txt)|*.txt|Code Files (*.cs,*.js,*.py,*.html,*.css,*.xml,*.json)|*.cs;*.js;*.py;*.html;*.css;*.xml;*.json"
                };

                if (saveDialog.ShowDialog() == true)
                {
                    var newPath = saveDialog.FileName;
                    var success = await _editorService.SaveFileAsAsync(_currentFilePath, newPath, EditorTextBox.Text);
                    
                    if (success)
                    {
                        _currentFilePath = newPath;
                        _currentLanguage = await _editorService.GetSyntaxLanguageAsync(newPath);
                        LanguageComboBox.SelectedItem = _currentLanguage;
                        UpdateStatus($"Saved as: {Path.GetFileName(newPath)}");
                        _isModified = false;
                    }
                    else
                    {
                        UpdateStatus("Failed to save file");
                    }
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"Save as error: {ex.Message}");
            }
        }

        public void Undo()
        {
            try
            {
                if (EditorTextBox.CanUndo)
                {
                    EditorTextBox.Undo();
                    UpdateStatus("Undo");
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"Undo error: {ex.Message}");
            }
        }

        public void Redo()
        {
            try
            {
                if (EditorTextBox.CanRedo)
                {
                    EditorTextBox.Redo();
                    UpdateStatus("Redo");
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"Redo error: {ex.Message}");
            }
        }

        public void Cut()
        {
            try
            {
                EditorTextBox.Cut();
                UpdateStatus("Cut");
            }
            catch (Exception ex)
            {
                UpdateStatus($"Cut error: {ex.Message}");
            }
        }

        public void Copy()
        {
            try
            {
                EditorTextBox.Copy();
                UpdateStatus("Copy");
            }
            catch (Exception ex)
            {
                UpdateStatus($"Copy error: {ex.Message}");
            }
        }

        public void Paste()
        {
            try
            {
                EditorTextBox.Paste();
                UpdateStatus("Paste");
            }
            catch (Exception ex)
            {
                UpdateStatus($"Paste error: {ex.Message}");
            }
        }

        public void ShowFindDialog()
        {
            try
            {
                var findDialog = new FindReplaceDialog(this, false);
                findDialog.ShowDialog();
            }
            catch (Exception ex)
            {
                UpdateStatus($"Find dialog error: {ex.Message}");
            }
        }

        public void ShowReplaceDialog()
        {
            try
            {
                var replaceDialog = new FindReplaceDialog(this, true);
                replaceDialog.ShowDialog();
            }
            catch (Exception ex)
            {
                UpdateStatus($"Replace dialog error: {ex.Message}");
            }
        }

        private void UpdateLineNumbers()
        {
            try
            {
                var lines = EditorTextBox.Text.Split('\n');
                var lineNumbers = string.Join("\n", Enumerable.Range(1, lines.Length).Select(i => i.ToString()));
                LineNumbersTextBlock.Text = lineNumbers;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to update line numbers: {ex.Message}");
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

        private void UpdatePosition()
        {
            try
            {
                var text = EditorTextBox.Text.Substring(0, EditorTextBox.CaretIndex);
                var lines = text.Split('\n');
                var currentLine = lines.Length;
                var currentColumn = lines[lines.Length - 1].Length + 1;
                PositionText.Text = $"Line {currentLine}, Column {currentColumn}";
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to update position: {ex.Message}");
            }
        }

        #region Event Handlers

        private void EditorTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            if (!_isLoading)
            {
                _isModified = true;
                UpdateLineNumbers();
                UpdateStatus("Modified");
            }
        }

        private void EditorTextBox_SelectionChanged(object sender, RoutedEventArgs e)
        {
            UpdatePosition();
        }

        private void EditorTextBox_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.S && Keyboard.Modifiers == ModifierKeys.Control)
            {
                SaveFile();
                e.Handled = true;
            }
            else if (e.Key == Key.Z && Keyboard.Modifiers == ModifierKeys.Control)
            {
                Undo();
                e.Handled = true;
            }
            else if (e.Key == Key.Y && Keyboard.Modifiers == ModifierKeys.Control)
            {
                Redo();
                e.Handled = true;
            }
            else if (e.Key == Key.F && Keyboard.Modifiers == ModifierKeys.Control)
            {
                ShowFindDialog();
                e.Handled = true;
            }
            else if (e.Key == Key.H && Keyboard.Modifiers == ModifierKeys.Control)
            {
                ShowReplaceDialog();
                e.Handled = true;
            }
            else if (e.Key == Key.Tab)
            {
                // Insert tab character
                var tab = "    "; // 4 spaces
                EditorTextBox.SelectedText = tab;
                e.Handled = true;
            }
        }

        private void EditorScrollViewer_ScrollChanged(object sender, ScrollChangedEventArgs e)
        {
            LineNumbersScrollViewer.ScrollToVerticalOffset(e.VerticalOffset);
        }

        private void LineNumbersScrollViewer_ScrollChanged(object sender, ScrollChangedEventArgs e)
        {
            EditorScrollViewer.ScrollToVerticalOffset(e.VerticalOffset);
        }

        private void SaveButton_Click(object sender, RoutedEventArgs e)
        {
            SaveFile();
        }

        private void SaveAsButton_Click(object sender, RoutedEventArgs e)
        {
            SaveFileAs();
        }

        private void UndoButton_Click(object sender, RoutedEventArgs e)
        {
            Undo();
        }

        private void RedoButton_Click(object sender, RoutedEventArgs e)
        {
            Redo();
        }

        private void FindButton_Click(object sender, RoutedEventArgs e)
        {
            ShowFindDialog();
        }

        private void ReplaceButton_Click(object sender, RoutedEventArgs e)
        {
            ShowReplaceDialog();
        }

        private async void FormatButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                UpdateStatus("Formatting code...");
                var formattedContent = await _editorService.FormatCodeAsync(EditorTextBox.Text, _currentLanguage);
                EditorTextBox.Text = formattedContent;
                UpdateStatus("Code formatted");
            }
            catch (Exception ex)
            {
                UpdateStatus($"Format error: {ex.Message}");
            }
        }

        private void LanguageComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (LanguageComboBox.SelectedItem != null)
            {
                _currentLanguage = LanguageComboBox.SelectedItem.ToString() ?? "Plain Text";
                UpdateStatus($"Language: {_currentLanguage}");
            }
        }

        private void LineNumbersCheckBox_Checked(object sender, RoutedEventArgs e)
        {
            LineNumbersScrollViewer.Visibility = Visibility.Visible;
        }

        private void LineNumbersCheckBox_Unchecked(object sender, RoutedEventArgs e)
        {
            LineNumbersScrollViewer.Visibility = Visibility.Collapsed;
        }

        private void WordWrapCheckBox_Checked(object sender, RoutedEventArgs e)
        {
            EditorTextBox.TextWrapping = TextWrapping.Wrap;
        }

        private void WordWrapCheckBox_Unchecked(object sender, RoutedEventArgs e)
        {
            EditorTextBox.TextWrapping = TextWrapping.NoWrap;
        }

        #endregion
    }

    // Simple Find/Replace Dialog
    public class FindReplaceDialog : Window
    {
        private readonly EditorView _editor;
        private readonly bool _isReplace;
        private TextBox _findTextBox;
        private TextBox _replaceTextBox;
        private CheckBox _caseSensitiveCheckBox;
        private CheckBox _wholeWordCheckBox;

        public FindReplaceDialog(EditorView editor, bool isReplace)
        {
            _editor = editor;
            _isReplace = isReplace;
            InitializeDialog();
        }

        private void InitializeDialog()
        {
            Title = _isReplace ? "Find and Replace" : "Find";
            Width = 400;
            Height = _isReplace ? 200 : 150;
            WindowStartupLocation = WindowStartupLocation.CenterOwner;
            ResizeMode = ResizeMode.NoResize;

            var grid = new Grid();
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });

            // Find text
            var findLabel = new Label { Content = "Find:", Margin = new Thickness(5) };
            _findTextBox = new TextBox { Margin = new Thickness(5) };
            Grid.SetRow(findLabel, 0);
            Grid.SetRow(_findTextBox, 0);
            Grid.SetColumn(_findTextBox, 1);
            grid.Children.Add(findLabel);
            grid.Children.Add(_findTextBox);

            // Replace text (only for replace dialog)
            if (_isReplace)
            {
                var replaceLabel = new Label { Content = "Replace:", Margin = new Thickness(5) };
                _replaceTextBox = new TextBox { Margin = new Thickness(5) };
                Grid.SetRow(replaceLabel, 1);
                Grid.SetRow(_replaceTextBox, 1);
                Grid.SetColumn(_replaceTextBox, 1);
                grid.Children.Add(replaceLabel);
                grid.Children.Add(_replaceTextBox);
            }

            // Options
            var optionsPanel = new StackPanel { Orientation = Orientation.Horizontal, Margin = new Thickness(5) };
            _caseSensitiveCheckBox = new CheckBox { Content = "Case Sensitive", Margin = new Thickness(5) };
            _wholeWordCheckBox = new CheckBox { Content = "Whole Word", Margin = new Thickness(5) };
            optionsPanel.Children.Add(_caseSensitiveCheckBox);
            optionsPanel.Children.Add(_wholeWordCheckBox);
            Grid.SetRow(optionsPanel, _isReplace ? 2 : 1);
            grid.Children.Add(optionsPanel);

            // Buttons
            var buttonPanel = new StackPanel { Orientation = Orientation.Horizontal, HorizontalAlignment = HorizontalAlignment.Right, Margin = new Thickness(5) };
            var findButton = new Button { Content = "Find", Width = 80, Margin = new Thickness(5) };
            findButton.Click += FindButton_Click;
            buttonPanel.Children.Add(findButton);

            if (_isReplace)
            {
                var replaceButton = new Button { Content = "Replace", Width = 80, Margin = new Thickness(5) };
                replaceButton.Click += ReplaceButton_Click;
                buttonPanel.Children.Add(replaceButton);

                var replaceAllButton = new Button { Content = "Replace All", Width = 80, Margin = new Thickness(5) };
                replaceAllButton.Click += ReplaceAllButton_Click;
                buttonPanel.Children.Add(replaceAllButton);
            }

            var closeButton = new Button { Content = "Close", Width = 80, Margin = new Thickness(5) };
            closeButton.Click += (s, e) => Close();
            buttonPanel.Children.Add(closeButton);

            Grid.SetRow(buttonPanel, _isReplace ? 3 : 2);
            grid.Children.Add(buttonPanel);

            Content = grid;
            _findTextBox.Focus();
        }

        private void FindButton_Click(object sender, RoutedEventArgs e)
        {
            // Implement find functionality
            MessageBox.Show("Find functionality coming soon!", "Find", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void ReplaceButton_Click(object sender, RoutedEventArgs e)
        {
            // Implement replace functionality
            MessageBox.Show("Replace functionality coming soon!", "Replace", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void ReplaceAllButton_Click(object sender, RoutedEventArgs e)
        {
            // Implement replace all functionality
            MessageBox.Show("Replace All functionality coming soon!", "Replace All", MessageBoxButton.OK, MessageBoxImage.Information);
        }
    }
}