using ICSharpCode.AvalonEdit.Search;
using ICSharpCode.AvalonEdit;
using ICSharpCode.AvalonEdit.Highlighting;
using System;
using System.IO;
using System.Timers;
using System.Windows;
using System.Windows.Controls;

namespace AAAFileManager
{
    public partial class EditorTab : UserControl
    {
        private string _filePath = string.Empty;
        private bool _dirty;
        private readonly Timer _autosaveTimer;
        private readonly SearchPanel _searchPanel;

        public string FilePath => _filePath;
        public bool IsDirty => _dirty;

        public event EventHandler<string>? Saved;

        public EditorTab()
        {
            InitializeComponent();
            _searchPanel = SearchPanel.Install(TextEditor.TextArea);
            _searchPanel.IsEnabled = true;
            _autosaveTimer = new Timer(3000);
            _autosaveTimer.AutoReset = true;
            _autosaveTimer.Elapsed += AutosaveTimer_Elapsed;
            TextEditor.TextChanged += (_, __) => { _dirty = true; };
        }

        public void LoadFile(string path)
        {
            _filePath = path;
            TextEditor.FontSize = Services.SettingsService.Instance.Settings.EditorFontSize;
            TextEditor.SyntaxHighlighting = HighlightingManager.Instance.GetDefinitionByExtension(System.IO.Path.GetExtension(path));
            TextEditor.Text = File.ReadAllText(path);
            _dirty = false;
            _autosaveTimer.Start();
        }

        private void AutosaveTimer_Elapsed(object? sender, ElapsedEventArgs e)
        {
            if (!_dirty || string.IsNullOrEmpty(_filePath)) return;
            try
            {
                Services.FileOperationService.CreateBackup(_filePath);
                File.WriteAllText(_filePath, TextEditor.Text);
                _dirty = false;
            }
            catch { }
        }

        private void Save_Click(object sender, RoutedEventArgs e)
        {
            SaveNow();
        }

        public void SaveNow()
        {
            if (string.IsNullOrEmpty(_filePath)) return;
            try
            {
                Services.FileOperationService.CreateBackup(_filePath);
                File.WriteAllText(_filePath, TextEditor.Text);
                _dirty = false;
                Saved?.Invoke(this, _filePath);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Failed to save file: {ex.Message}", "Save Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void Find_Click(object sender, RoutedEventArgs e)
        {
            _searchPanel.IsEnabled = true;
            _searchPanel.Open();
        }

        private void Replace_Click(object sender, RoutedEventArgs e)
        {
            _searchPanel.IsEnabled = true;
            _searchPanel.Open();
            _searchPanel.Replacements.Clear();
        }
    }
}