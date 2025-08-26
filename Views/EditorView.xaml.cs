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
    /// <summary>
    /// Interaction logic for EditorView.xaml
    /// </summary>
    public partial class EditorView : System.Windows.Controls.UserControl
    {
        private readonly IEditorService _editorService;
        private string _currentFilePath = "";
        private string _currentLanguage = "Plain Text";
        private bool _isModified = false;
        private bool _isLoading = false;

        public EditorView()
        {
            InitializeComponent();
            _editorService = App.Current.Services.GetRequiredService<IEditorService>();
            InitializeEditor();
        }

        public EditorView(string filePath) : this()
        {
            LoadFile(filePath);
        }

        private void InitializeEditor()
        {
            // Initialize language detection
            var languages = _editorService.GetSupportedLanguagesAsync().Result;
            LanguageComboBox.ItemsSource = languages;
            LanguageComboBox.SelectedIndex = 0;

            // Set default values
            LineNumbersCheckBox.IsChecked = true;
            WordWrapCheckBox.IsChecked = false;

            // Update status
            UpdateStatus("Ready");
        }

        public async void LoadFile(string filePath)
        {
            try
            {
                _isLoading = true;
                _currentFilePath = filePath;
                
                var content = await _editorService.LoadFileAsync(filePath);
                EditorTextBox.Text = content;
                
                // Detect language
                var language = await _editorService.GetSyntaxLanguageAsync(filePath);
                LanguageComboBox.SelectedItem = language;
                _currentLanguage = language;
                
                _isModified = false;
                UpdateLineNumbers();
                UpdateStatus($"Loaded: {Path.GetFileName(filePath)}");
            }
            catch (Exception ex)
            {
                UpdateStatus($"Error loading file: {ex.Message}");
            }
            finally
            {
                _isLoading = false;
            }
        }

        public async void SaveFile()
        {
            if (string.IsNullOrEmpty(_currentFilePath))
            {
                SaveFileAs();
                return;
            }

            try
            {
                var content = EditorTextBox.Text;
                var success = await _editorService.SaveFileAsync(_currentFilePath, content);
                
                if (success)
                {
                    _isModified = false;
                    UpdateStatus($"Saved: {Path.GetFileName(_currentFilePath)}");
                }
                else
                {
                    UpdateStatus("Error saving file");
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"Error saving file: {ex.Message}");
            }
        }

        public async void SaveFileAs()
        {
            var dialog = new Microsoft.Win32.SaveFileDialog
            {
                Title = "Save File As",
                Filter = "All Files (*.*)|*.*|Text Files (*.txt)|*.txt|C# Files (*.cs)|*.cs|XML Files (*.xml)|*.xml|JSON Files (*.json)|*.json",
                DefaultExt = Path.GetExtension(_currentFilePath)
            };

            if (dialog.ShowDialog() == true)
            {
                var content = EditorTextBox.Text;
                var success = await _editorService.SaveFileAsAsync(_currentFilePath, dialog.FileName, content);
                
                if (success)
                {
                    _currentFilePath = dialog.FileName;
                    _isModified = false;
                    UpdateStatus($"Saved as: {Path.GetFileName(_currentFilePath)}");
                }
                else
                {
                    UpdateStatus("Error saving file");
                }
            }
        }

        public void Undo()
        {
            EditorTextBox.Undo();
            UpdateStatus("Undo performed");
        }

        public void Redo()
        {
            EditorTextBox.Redo();
            UpdateStatus("Redo performed");
        }

        public void ShowFindDialog()
        {
            var dialog = new FindReplaceDialog(this, true);
            dialog.ShowDialog();
        }

        public void ShowReplaceDialog()
        {
            var dialog = new FindReplaceDialog(this, false);
            dialog.ShowDialog();
        }

        private void UpdateLineNumbers()
        {
            if (LineNumbersCheckBox.IsChecked == true)
            {
                var lines = EditorTextBox.Text.Split('\n');
                var lineNumbers = string.Join("\n", Enumerable.Range(1, lines.Length).Select(i => i.ToString()));
                LineNumbersTextBlock.Text = lineNumbers;
            }
            else
            {
                LineNumbersTextBlock.Text = "";
            }
        }

        private void UpdateStatus(string message)
        {
            StatusText.Text = message;
        }

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
            var line = EditorTextBox.GetLineIndexFromCharacterIndex(EditorTextBox.CaretIndex) + 1;
            var column = EditorTextBox.CaretIndex - EditorTextBox.GetCharacterIndexFromLineIndex(line - 1) + 1;
            PositionText.Text = $"Line {line}, Column {column}";
        }

        private void EditorTextBox_KeyDown(object sender, System.Windows.Input.KeyEventArgs e)
        {
            if (e.Key == System.Windows.Input.Key.S && (Keyboard.Modifiers & ModifierKeys.Control) == ModifierKeys.Control)
            {
                SaveFile();
                e.Handled = true;
            }
            else if (e.Key == System.Windows.Input.Key.Z && (Keyboard.Modifiers & ModifierKeys.Control) == ModifierKeys.Control)
            {
                if ((Keyboard.Modifiers & ModifierKeys.Shift) == ModifierKeys.Shift)
                    Redo();
                else
                    Undo();
                e.Handled = true;
            }
            else if (e.Key == System.Windows.Input.Key.F && (Keyboard.Modifiers & ModifierKeys.Control) == ModifierKeys.Control)
            {
                ShowFindDialog();
                e.Handled = true;
            }
            else if (e.Key == System.Windows.Input.Key.H && (Keyboard.Modifiers & ModifierKeys.Control) == ModifierKeys.Control)
            {
                ShowReplaceDialog();
                e.Handled = true;
            }
        }

        private void SaveButton_Click(object sender, RoutedEventArgs e)
        {
            SaveFile();
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

        private void FormatButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var content = EditorTextBox.Text;
                var formatted = _editorService.FormatCodeAsync(content, _currentLanguage).Result;
                EditorTextBox.Text = formatted;
                UpdateStatus("Code formatted");
            }
            catch (Exception ex)
            {
                UpdateStatus($"Error formatting code: {ex.Message}");
            }
        }

        private void LanguageComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (LanguageComboBox.SelectedItem is string language)
            {
                _currentLanguage = language;
                UpdateStatus($"Language: {language}");
            }
        }

        private void LineNumbersCheckBox_Checked(object sender, RoutedEventArgs e)
        {
            UpdateLineNumbers();
        }

        private void LineNumbersCheckBox_Unchecked(object sender, RoutedEventArgs e)
        {
            UpdateLineNumbers();
        }

        private void WordWrapCheckBox_Checked(object sender, RoutedEventArgs e)
        {
            EditorTextBox.TextWrapping = TextWrapping.Wrap;
        }

        private void WordWrapCheckBox_Unchecked(object sender, RoutedEventArgs e)
        {
            EditorTextBox.TextWrapping = TextWrapping.NoWrap;
        }

        private void EditorScrollViewer_ScrollChanged(object sender, ScrollChangedEventArgs e)
        {
            // Synchronize line numbers scrolling with main editor
            LineNumbersScrollViewer.ScrollToVerticalOffset(e.VerticalOffset);
        }
    }

    public class FindReplaceDialog : System.Windows.Window
    {
        private readonly EditorView _editor;
        private readonly bool _findOnly;

        public FindReplaceDialog(EditorView editor, bool findOnly)
        {
            _editor = editor;
            _findOnly = findOnly;
            
            Title = findOnly ? "Find" : "Find and Replace";
            Width = 400;
            Height = 200;
            WindowStartupLocation = WindowStartupLocation.CenterOwner;
            ResizeMode = ResizeMode.NoResize;

            var grid = new Grid();
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });

            var findLabel = new System.Windows.Controls.Label { Content = "Find:", Margin = new Thickness(5) };
            var findTextBox = new System.Windows.Controls.TextBox { Margin = new Thickness(5), Name = "FindTextBox" };
            
            grid.Children.Add(findLabel);
            Grid.SetRow(findLabel, 0);
            grid.Children.Add(findTextBox);
            Grid.SetRow(findTextBox, 1);

            if (!findOnly)
            {
                var replaceLabel = new System.Windows.Controls.Label { Content = "Replace with:", Margin = new Thickness(5) };
                var replaceTextBox = new System.Windows.Controls.TextBox { Margin = new Thickness(5), Name = "ReplaceTextBox" };
                
                grid.Children.Add(replaceLabel);
                Grid.SetRow(replaceLabel, 2);
                grid.Children.Add(replaceTextBox);
                Grid.SetRow(replaceTextBox, 3);
            }

            var buttonPanel = new StackPanel { Orientation = Orientation.Horizontal, HorizontalAlignment = HorizontalAlignment.Right, Margin = new Thickness(5) };
            var findButton = new System.Windows.Controls.Button { Content = "Find", Width = 80, Margin = new Thickness(5) };
            var closeButton = new System.Windows.Controls.Button { Content = "Close", Width = 80, Margin = new Thickness(5) };

            buttonPanel.Children.Add(findButton);
            buttonPanel.Children.Add(closeButton);

            grid.Children.Add(buttonPanel);
            Grid.SetRow(buttonPanel, findOnly ? 2 : 4);

            closeButton.Click += (s, e) => Close();
            findButton.Click += (s, e) => 
            {
                // TODO: Implement find/replace functionality
                MessageBox.Show("Find/Replace functionality will be implemented in the next version.", "Feature Coming Soon");
            };

            Content = grid;
        }
    }
}