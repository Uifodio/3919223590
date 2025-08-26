using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Collections.ObjectModel;
using System.Windows.Input;
using WindowsFileManagerPro.Services;

namespace WindowsFileManagerPro.ViewModels
{
    public partial class EditorViewModel : ObservableObject
    {
        private readonly IEditorService _editorService;

        [ObservableProperty]
        private string _filePath = "";

        [ObservableProperty]
        private string _fileName = "Untitled";

        [ObservableProperty]
        private string _content = "";

        [ObservableProperty]
        private string _language = "Plain Text";

        [ObservableProperty]
        private bool _isModified = false;

        [ObservableProperty]
        private bool _isLoading = false;

        [ObservableProperty]
        private string _statusText = "Ready";

        [ObservableProperty]
        private int _currentLine = 1;

        [ObservableProperty]
        private int _currentColumn = 1;

        [ObservableProperty]
        private int _totalLines = 1;

        [ObservableProperty]
        private bool _showLineNumbers = true;

        [ObservableProperty]
        private bool _wordWrap = false;

        [ObservableProperty]
        private string _encoding = "UTF-8";

        [ObservableProperty]
        private ObservableCollection<string> _supportedLanguages = new();

        public ICommand SaveCommand { get; }
        public ICommand SaveAsCommand { get; }
        public ICommand UndoCommand { get; }
        public ICommand RedoCommand { get; }
        public ICommand CutCommand { get; }
        public ICommand CopyCommand { get; }
        public ICommand PasteCommand { get; }
        public ICommand FindCommand { get; }
        public ICommand ReplaceCommand { get; }
        public ICommand FormatCommand { get; }
        public ICommand ToggleLineNumbersCommand { get; }
        public ICommand ToggleWordWrapCommand { get; }

        public EditorViewModel(IEditorService editorService)
        {
            _editorService = editorService;

            SaveCommand = new RelayCommand(Save, CanSave);
            SaveAsCommand = new RelayCommand(SaveAs);
            UndoCommand = new RelayCommand(Undo, CanUndo);
            RedoCommand = new RelayCommand(Redo, CanRedo);
            CutCommand = new RelayCommand(Cut, CanCut);
            CopyCommand = new RelayCommand(Copy, CanCopy);
            PasteCommand = new RelayCommand(Paste, CanPaste);
            FindCommand = new RelayCommand(Find);
            ReplaceCommand = new RelayCommand(Replace);
            FormatCommand = new RelayCommand(Format, CanFormat);
            ToggleLineNumbersCommand = new RelayCommand(ToggleLineNumbers);
            ToggleWordWrapCommand = new RelayCommand(ToggleWordWrap);

            InitializeViewModel();
        }

        private void InitializeViewModel()
        {
            // Load supported languages
            LoadSupportedLanguages();
            
            // Set default content
            Content = "// Welcome to Windows File Manager Pro Editor\n// Start typing your code here...";
            UpdateLineCount();
        }

        private async void LoadSupportedLanguages()
        {
            try
            {
                var languages = await _editorService.GetSupportedLanguagesAsync();
                SupportedLanguages.Clear();
                foreach (var language in languages)
                {
                    SupportedLanguages.Add(language);
                }
            }
            catch (Exception ex)
            {
                StatusText = $"Failed to load languages: {ex.Message}";
            }
        }

        public async void LoadFile(string filePath)
        {
            if (string.IsNullOrEmpty(filePath))
                return;

            try
            {
                IsLoading = true;
                StatusText = "Loading file...";

                FilePath = filePath;
                FileName = Path.GetFileName(filePath);
                
                var content = await _editorService.LoadFileAsync(filePath);
                Content = content;

                // Detect language
                Language = await _editorService.GetSyntaxLanguageAsync(filePath);
                
                UpdateLineCount();
                IsModified = false;
                StatusText = $"Loaded: {FileName}";
            }
            catch (Exception ex)
            {
                StatusText = $"Failed to load file: {ex.Message}";
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async void Save()
        {
            if (string.IsNullOrEmpty(FilePath) || FilePath == "untitled")
            {
                SaveAs();
                return;
            }

            try
            {
                StatusText = "Saving file...";
                var success = await _editorService.SaveFileAsync(FilePath, Content);
                
                if (success)
                {
                    IsModified = false;
                    StatusText = $"Saved: {FileName}";
                }
                else
                {
                    StatusText = "Failed to save file";
                }
            }
            catch (Exception ex)
            {
                StatusText = $"Save error: {ex.Message}";
            }
        }

        private async void SaveAs()
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
                    var success = await _editorService.SaveFileAsAsync(FilePath, newPath, Content);
                    
                    if (success)
                    {
                        FilePath = newPath;
                        FileName = Path.GetFileName(newPath);
                        Language = await _editorService.GetSyntaxLanguageAsync(newPath);
                        IsModified = false;
                        StatusText = $"Saved as: {FileName}";
                    }
                    else
                    {
                        StatusText = "Failed to save file";
                    }
                }
            }
            catch (Exception ex)
            {
                StatusText = $"Save as error: {ex.Message}";
            }
        }

        private void Undo()
        {
            // This would be handled by the view's TextBox
            StatusText = "Undo";
        }

        private void Redo()
        {
            // This would be handled by the view's TextBox
            StatusText = "Redo";
        }

        private void Cut()
        {
            // This would be handled by the view's TextBox
            StatusText = "Cut";
        }

        private void Copy()
        {
            // This would be handled by the view's TextBox
            StatusText = "Copy";
        }

        private void Paste()
        {
            // This would be handled by the view's TextBox
            StatusText = "Paste";
        }

        private void Find()
        {
            // This would be handled by the view
            StatusText = "Find";
        }

        private void Replace()
        {
            // This would be handled by the view
            StatusText = "Replace";
        }

        private async void Format()
        {
            try
            {
                StatusText = "Formatting code...";
                var formattedContent = await _editorService.FormatCodeAsync(Content, Language);
                Content = formattedContent;
                UpdateLineCount();
                StatusText = "Code formatted";
            }
            catch (Exception ex)
            {
                StatusText = $"Format error: {ex.Message}";
            }
        }

        private void ToggleLineNumbers()
        {
            ShowLineNumbers = !ShowLineNumbers;
            StatusText = ShowLineNumbers ? "Line numbers enabled" : "Line numbers disabled";
        }

        private void ToggleWordWrap()
        {
            WordWrap = !WordWrap;
            StatusText = WordWrap ? "Word wrap enabled" : "Word wrap disabled";
        }

        private void UpdateLineCount()
        {
            if (!string.IsNullOrEmpty(Content))
            {
                TotalLines = Content.Split('\n').Length;
            }
        }

        public void UpdateCursorPosition(int line, int column)
        {
            CurrentLine = line;
            CurrentColumn = column;
        }

        public void MarkAsModified()
        {
            IsModified = true;
            StatusText = "Modified";
        }

        private bool CanSave() => !string.IsNullOrEmpty(Content) && (IsModified || string.IsNullOrEmpty(FilePath));
        private bool CanUndo() => true; // Would check TextBox.CanUndo
        private bool CanRedo() => true; // Would check TextBox.CanRedo
        private bool CanCut() => true; // Would check if text is selected
        private bool CanCopy() => true; // Would check if text is selected
        private bool CanPaste() => true; // Would check if clipboard has content
        private bool CanFormat() => !string.IsNullOrEmpty(Content) && Language != "Plain Text";

        partial void OnContentChanged(string value)
        {
            if (!IsLoading)
            {
                IsModified = true;
                UpdateLineCount();
                MarkAsModified();
            }
        }

        partial void OnLanguageChanged(string value)
        {
            StatusText = $"Language: {value}";
        }
    }
}