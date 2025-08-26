using ICSharpCode.AvalonEdit;
using ICSharpCode.AvalonEdit.Highlighting;
using System;
using System.IO;
using System.Windows.Controls;
using System.Windows.Media.Imaging;

namespace AAAFileManager
{
    public partial class PreviewPane : UserControl
    {
        public PreviewPane()
        {
            InitializeComponent();
        }

        public void ShowFile(string path)
        {
            ContentHost.Content = null;
            try
            {
                var ext = Path.GetExtension(path).ToLowerInvariant();
                if (ext == ".png" || ext == ".jpg" || ext == ".jpeg" || ext == ".bmp" || ext == ".gif")
                {
                    var img = new Image();
                    img.Source = new BitmapImage(new Uri(path));
                    img.Stretch = System.Windows.Media.Stretch.Uniform;
                    ContentHost.Content = img;
                    return;
                }
                if (Services.PathUtils.IsTextFileByExtension(path))
                {
                    var editor = new TextEditor { IsReadOnly = true, ShowLineNumbers = true, Text = File.ReadAllText(path) };
                    editor.SyntaxHighlighting = HighlightingManager.Instance.GetDefinitionByExtension(ext);
                    ContentHost.Content = editor;
                    return;
                }
            }
            catch { }
        }

        public void Clear()
        {
            ContentHost.Content = null;
        }
    }
}