using AAAFileManager.Models;
using AAAFileManager.Services;
using Microsoft.Win32;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Threading;

namespace AAAFileManager
{
    public partial class MainWindow : Window
    {
        private string _currentPath = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
        private readonly List<FileItem> _items = new();

        // Zip mode state
        private bool _isZipMode;
        private string? _currentZipPath;
        private string _zipInnerDir = string.Empty;

        // Inbox watcher
        private FileSystemWatcher? _inboxWatcher;
        private readonly ObservableCollection<string> _inboxItems = new();
        private Point _inboxDragStart;

        public MainWindow()
        {
            InitializeComponent();
            PathBox.Text = _currentPath;
            InboxPath.Text = SettingsService.Instance.Settings.MonitoredFolder;
            InboxList.ItemsSource = _inboxItems;
            SetupInboxWatcher();

            LoadFolderTreeRoots();
            _ = LoadDirectoryAsync(_currentPath);
            PopulateRecent();

            InboxList.PreviewMouseLeftButtonDown += (s, e) => _inboxDragStart = e.GetPosition(null);
            InboxList.PreviewMouseMove += InboxList_PreviewMouseMove;
        }

        private void LoadFolderTreeRoots()
        {
            FolderTree.Items.Clear();
            foreach (var drive in DriveInfo.GetDrives().Where(d => d.IsReady))
            {
                var item = new TreeViewItem { Header = drive.Name, Tag = drive.RootDirectory.FullName };
                item.Items.Add("Loading...");
                item.Expanded += Folder_Expanded;
                FolderTree.Items.Add(item);
            }
        }

        private void Folder_Expanded(object sender, RoutedEventArgs e)
        {
            if (sender is TreeViewItem tvi)
            {
                if (tvi.Items.Count == 1 && tvi.Items[0] is string)
                {
                    tvi.Items.Clear();
                    try
                    {
                        var dir = tvi.Tag as string ?? string.Empty;
                        foreach (var sub in Directory.EnumerateDirectories(dir))
                        {
                            var subItem = new TreeViewItem { Header = System.IO.Path.GetFileName(sub), Tag = sub };
                            subItem.Items.Add("Loading...");
                            subItem.Expanded += Folder_Expanded;
                            tvi.Items.Add(subItem);
                        }
                    }
                    catch { }
                }
            }
        }

        private async Task LoadDirectoryAsync(string path)
        {
            // Exit zip mode if any
            _isZipMode = false;
            _currentZipPath = null;
            _zipInnerDir = string.Empty;

            _currentPath = path;
            PathBox.Text = path;
            StatusText.Text = "Loading...";
            _items.Clear();
            FileList.ItemsSource = null;
            await Task.Run(() =>
            {
                try
                {
                    foreach (var dir in Directory.EnumerateDirectories(path))
                    {
                        var di = new DirectoryInfo(dir);
                        _items.Add(new FileItem
                        {
                            Name = di.Name,
                            FullPath = di.FullName,
                            IsDirectory = true,
                            SizeBytes = 0,
                            ModifiedUtc = di.LastWriteTimeUtc,
                            Type = "Folder"
                        });
                    }
                    foreach (var file in Directory.EnumerateFiles(path))
                    {
                        var fi = new FileInfo(file);
                        _items.Add(new FileItem
                        {
                            Name = fi.Name,
                            FullPath = fi.FullName,
                            IsDirectory = false,
                            SizeBytes = fi.Length,
                            ModifiedUtc = fi.LastWriteTimeUtc,
                            Type = PathUtils.GetTypeDisplay(fi.FullName, false)
                        });
                    }
                }
                catch { }
            });
            FileList.ItemsSource = _items.OrderByDescending(i => i.IsDirectory).ThenBy(i => i.Name, StringComparer.OrdinalIgnoreCase).ToList();
            StatusText.Text = "Ready";
            SettingsService.Instance.AddRecent(path);
            PopulateRecent();
        }

        private async Task LoadZipDirectoryAsync(string zipPath, string innerDir)
        {
            _isZipMode = true;
            _currentZipPath = zipPath;
            _zipInnerDir = innerDir ?? string.Empty;
            _currentPath = zipPath;
            PathBox.Text = $"{zipPath} :: {(_zipInnerDir.Length == 0 ? "/" : _zipInnerDir)}";
            StatusText.Text = "Loading ZIP...";
            var items = await Task.Run(() => ZipFileSystem.List(zipPath, _zipInnerDir).ToList());
            FileList.ItemsSource = items;
            StatusText.Text = "Ready";
            SettingsService.Instance.AddRecent(zipPath);
            PopulateRecent();
        }

        private void PopulateRecent()
        {
            if (RecentMenu == null) return;
            RecentMenu.Items.Clear();
            var recents = SettingsService.Instance.Settings.RecentLocations;
            if (recents.Count == 0)
            {
                RecentMenu.Items.Add(new MenuItem { Header = "(empty)", IsEnabled = false });
                return;
            }
            foreach (var loc in recents)
            {
                var mi = new MenuItem { Header = loc, Tag = loc };
                mi.Click += async (_, __) =>
                {
                    if (Directory.Exists(loc))
                    {
                        await LoadDirectoryAsync(loc);
                    }
                    else if (File.Exists(loc) && string.Equals(System.IO.Path.GetExtension(loc), ".zip", StringComparison.OrdinalIgnoreCase))
                    {
                        await LoadZipDirectoryAsync(loc, string.Empty);
                    }
                    else
                    {
                        MessageBox.Show($"Location not found: {loc}");
                    }
                };
                RecentMenu.Items.Add(mi);
            }
        }

        private void FolderTree_SelectedItemChanged(object sender, RoutedPropertyChangedEventArgs<object> e)
        {
            if (FolderTree.SelectedItem is TreeViewItem tvi)
            {
                string? path = tvi.Tag as string;
                if (!string.IsNullOrEmpty(path)) _ = LoadDirectoryAsync(path);
            }
        }

        private void Go_Click(object sender, RoutedEventArgs e)
        {
            var path = PathBox.Text.Trim();
            if (Directory.Exists(path)) _ = LoadDirectoryAsync(path);
            else if (File.Exists(path) && string.Equals(System.IO.Path.GetExtension(path), ".zip", StringComparison.OrdinalIgnoreCase)) _ = LoadZipDirectoryAsync(path, string.Empty);
        }

        private void PathBox_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.Enter) Go_Click(sender!, e);
        }

        private void FileList_MouseDoubleClick(object sender, MouseButtonEventArgs e)
        {
            if (FileList.SelectedItem is FileItem item)
            {
                if (_isZipMode)
                {
                    if (item.IsDirectory && item.ZipArchivePath != null && item.ZipInnerPath != null)
                    {
                        _ = LoadZipDirectoryAsync(item.ZipArchivePath, item.ZipInnerPath);
                    }
                    else if (!item.IsDirectory && item.ZipArchivePath != null && item.ZipInnerPath != null)
                    {
                        OpenZipEntryInEditor(item);
                    }
                    return;
                }

                if (item.IsDirectory)
                {
                    _ = LoadDirectoryAsync(item.FullPath);
                }
                else if (string.Equals(System.IO.Path.GetExtension(item.FullPath), ".zip", StringComparison.OrdinalIgnoreCase))
                {
                    _ = LoadZipDirectoryAsync(item.FullPath, string.Empty);
                }
                else
                {
                    OpenFileInEditor(item);
                }
            }
        }

        private void OpenZipEntryInEditor(FileItem item)
        {
            if (item.ZipArchivePath == null || item.ZipInnerPath == null) return;
            var temp = ZipFileSystem.ExtractEntryToTemp(item.ZipArchivePath, item.ZipInnerPath);
            var tab = new TabItem { Header = item.Name };
            var editor = new EditorTab();
            editor.LoadFile(temp);
            tab.Content = editor;
            tab.Tag = new ZipEditContext(item.ZipArchivePath, item.ZipInnerPath, temp);
            editor.Saved += (_, _) =>
            {
                if (tab.Tag is ZipEditContext z)
                {
                    ZipFileSystem.WriteEntryFromFile(z.ZipPath, z.InnerPath, z.TempFilePath);
                    StatusText.Text = $"Saved into {System.IO.Path.GetFileName(z.ZipPath)}";
                }
            };
            EditorTabs.Items.Add(tab);
            EditorTabs.SelectedItem = tab;
        }

        private void OpenFileInEditor(FileItem item)
        {
            var tab = new TabItem { Header = item.Name };
            var editor = new EditorTab();
            editor.LoadFile(item.FullPath);
            editor.Saved += (_, path) => StatusText.Text = $"Saved {System.IO.Path.GetFileName(path)}";
            tab.Content = editor;
            EditorTabs.Items.Add(tab);
            EditorTabs.SelectedItem = tab;
        }

        private void Copy_Click(object sender, RoutedEventArgs e)
        {
            var selected = FileList.SelectedItems.Cast<FileItem>().ToList();
            if (selected.Count == 0) return;
            var paths = new List<string>();
            foreach (var it in selected)
            {
                if (it.IsFromZip && !it.IsDirectory && it.ZipArchivePath != null && it.ZipInnerPath != null)
                {
                    // Extract to temp for drag/copy clipboard
                    try { paths.Add(ZipFileSystem.ExtractEntryToTemp(it.ZipArchivePath, it.ZipInnerPath)); } catch { }
                }
                else
                {
                    paths.Add(it.FullPath);
                }
            }
            var col = new System.Collections.Specialized.StringCollection();
            foreach (var p in paths) col.Add(p);
            Clipboard.SetFileDropList(col);
            StatusText.Text = $"Copied {paths.Count} items";
        }

        private async void Paste_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var list = Clipboard.GetFileDropList();
                if (list == null || list.Count == 0) return;
                var files = list.Cast<string>().ToList();
                if (_isZipMode && _currentZipPath != null)
                {
                    foreach (var f in files) ZipFileSystem.AddExternalFile(_currentZipPath, _zipInnerDir, f);
                    await LoadZipDirectoryAsync(_currentZipPath, _zipInnerDir);
                }
                else
                {
                    var progress = new Progress<double>(v => OperationProgress.Value = v);
                    await FileOperationService.CopyAsync(files, _currentPath, progress);
                    await LoadDirectoryAsync(_currentPath);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message, "Paste Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private async void Delete_Click(object sender, RoutedEventArgs e)
        {
            var selected = FileList.SelectedItems.Cast<FileItem>().ToList();
            if (selected.Count == 0) return;
            if (_isZipMode && _currentZipPath != null)
            {
                MessageBox.Show("Delete inside ZIP not implemented in this version.");
                return;
            }
            if (MessageBox.Show($"Send {selected.Count} item(s) to Recycle Bin?", "Confirm Delete", MessageBoxButton.YesNo, MessageBoxImage.Question) == MessageBoxResult.Yes)
            {
                FileOperationService.DeleteToRecycleBin(selected.Select(i => i.FullPath));
                await LoadDirectoryAsync(_currentPath);
            }
        }

        private async void Rename_Click(object sender, RoutedEventArgs e)
        {
            if (FileList.SelectedItem is not FileItem item) return;
            if (_isZipMode)
            {
                MessageBox.Show("Rename inside ZIP not implemented in this version.");
                return;
            }
            var input = Microsoft.VisualBasic.Interaction.InputBox("New name:", "Rename", item.Name);
            if (string.IsNullOrWhiteSpace(input)) return;
            FileOperationService.Rename(item.FullPath, input);
            await LoadDirectoryAsync(_currentPath);
        }

        private async void Duplicate_Click(object sender, RoutedEventArgs e)
        {
            if (FileList.SelectedItem is not FileItem item) return;
            if (_isZipMode)
            {
                MessageBox.Show("Duplicate inside ZIP not implemented in this version.");
                return;
            }
            FileOperationService.Duplicate(item.FullPath);
            await LoadDirectoryAsync(_currentPath);
        }

        private void ToggleSearch_Click(object sender, RoutedEventArgs e)
        {
            SearchExpander.IsExpanded = !SearchExpander.IsExpanded;
        }

        private void Settings_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Settings saved in %APPDATA%/AAAFileManager/settings.json", "Settings");
        }

        private void About_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("AAA File Manager\nFast, modern, developer-friendly.", "About");
        }

        private void Exit_Click(object sender, RoutedEventArgs e)
        {
            Close();
        }

        private void NewWindow_Click(object sender, RoutedEventArgs e)
        {
            var w = new MainWindow();
            w.Show();
        }

        private void FileList_PreviewMouseMove(object sender, MouseEventArgs e)
        {
            if (e.LeftButton == MouseButtonState.Pressed)
            {
                var selectedItems = FileList.SelectedItems.Cast<FileItem>().ToList();
                if (selectedItems.Count > 0)
                {
                    var paths = new List<string>();
                    foreach (var it in selectedItems)
                    {
                        if (it.IsFromZip && !it.IsDirectory && it.ZipArchivePath != null && it.ZipInnerPath != null)
                        {
                            try { paths.Add(ZipFileSystem.ExtractEntryToTemp(it.ZipArchivePath, it.ZipInnerPath)); } catch { }
                        }
                        else
                        {
                            paths.Add(it.FullPath);
                        }
                    }
                    if (paths.Count > 0)
                    {
                        var data = new DataObject(DataFormats.FileDrop, paths.ToArray());
                        DragDrop.DoDragDrop(FileList, data, DragDropEffects.Copy | DragDropEffects.Move);
                    }
                }
            }
        }

        private async void FileList_Drop(object sender, DragEventArgs e)
        {
            if (!e.Data.GetDataPresent(DataFormats.FileDrop)) return;
            var files = (string[])e.Data.GetData(DataFormats.FileDrop);

            // Quick replace if a single target file is selected and a single source file is dropped
            if (!_isZipMode && FileList.SelectedItem is FileItem target && !target.IsDirectory && files.Length == 1)
            {
                try
                {
                    FileOperationService.CreateBackup(target.FullPath);
                    File.Copy(files[0], target.FullPath, overwrite: true);
                    await LoadDirectoryAsync(_currentPath);
                    StatusText.Text = $"Replaced {target.Name}";
                    return;
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message, "Replace Error", MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }

            if (_isZipMode && _currentZipPath != null)
            {
                foreach (var f in files) ZipFileSystem.AddExternalFile(_currentZipPath, _zipInnerDir, f);
                await LoadZipDirectoryAsync(_currentZipPath, _zipInnerDir);
            }
            else
            {
                var progress = new Progress<double>(v => OperationProgress.Value = v);
                await FileOperationService.CopyAsync(files, _currentPath, progress);
                await LoadDirectoryAsync(_currentPath);
            }
        }

        private async void FolderTree_Drop(object sender, DragEventArgs e)
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop) && FolderTree.SelectedItem is TreeViewItem tvi)
            {
                string? target = tvi.Tag as string;
                if (string.IsNullOrEmpty(target)) return;
                var files = (string[])e.Data.GetData(DataFormats.FileDrop);
                var progress = new Progress<double>(v => OperationProgress.Value = v);
                await FileOperationService.CopyAsync(files, target, progress);
                if (PathUtils.PathsEqual(target, _currentPath)) await LoadDirectoryAsync(_currentPath);
            }
        }

        private async void OpenFolder_Click(object sender, RoutedEventArgs e)
        {
            var dlg = new System.Windows.Forms.FolderBrowserDialog();
            if (dlg.ShowDialog() == System.Windows.Forms.DialogResult.OK)
            {
                await LoadDirectoryAsync(dlg.SelectedPath);
            }
        }

        private async void OpenZip_Click(object sender, RoutedEventArgs e)
        {
            var dlg = new OpenFileDialog { Filter = "ZIP files (*.zip)|*.zip|All files (*.*)|*.*" };
            if (dlg.ShowDialog() == true)
            {
                await LoadZipDirectoryAsync(dlg.FileName, string.Empty);
            }
        }

        private async void SearchPaneControl_SearchRequested(object sender, SearchRequestedEventArgs e)
        {
            OperationProgress.Value = 0;
            var results = await SearchAsync(
                _isZipMode && _currentZipPath != null ? _currentZipPath : _currentPath,
                e.NameQuery,
                e.ContentQuery,
                new Progress<double>(v => OperationProgress.Value = v),
                e.CancellationToken);
            FileList.ItemsSource = results;
        }

        private Task<List<FileItem>> SearchAsync(string root, string? nameQuery, string? contentQuery, IProgress<double>? progress, System.Threading.CancellationToken ct)
        {
            return Task.Run(() =>
            {
                var matches = new List<FileItem>();
                try
                {
                    if (_isZipMode && _currentZipPath != null)
                    {
                        var entries = ZipFileSystem.List(_currentZipPath, _zipInnerDir).Where(i => !i.IsDirectory).ToList();
                        int total = entries.Count;
                        int processed = 0;
                        foreach (var entry in entries)
                        {
                            ct.ThrowIfCancellationRequested();
                            processed++;
                            if (!string.IsNullOrWhiteSpace(nameQuery) && !entry.Name.Contains(nameQuery, StringComparison.OrdinalIgnoreCase))
                            {
                                progress?.Report(processed * 100.0 / total);
                                continue;
                            }
                            if (!string.IsNullOrWhiteSpace(contentQuery) && entry.ZipInnerPath != null)
                            {
                                try
                                {
                                    var temp = ZipFileSystem.ExtractEntryToTemp(_currentZipPath, entry.ZipInnerPath);
                                    var text = File.ReadAllText(temp);
                                    if (text.IndexOf(contentQuery, StringComparison.OrdinalIgnoreCase) < 0)
                                    {
                                        progress?.Report(processed * 100.0 / total);
                                        continue;
                                    }
                                }
                                catch { }
                            }
                            matches.Add(entry);
                            progress?.Report(processed * 100.0 / total);
                        }
                    }
                    else
                    {
                        var allFiles = PathUtils.EnumerateFilesSafe(root).ToList();
                        int total = allFiles.Count;
                        int processed = 0;
                        foreach (var file in allFiles)
                        {
                            ct.ThrowIfCancellationRequested();
                            processed++;
                            if (!string.IsNullOrWhiteSpace(nameQuery) && !System.IO.Path.GetFileName(file).Contains(nameQuery, StringComparison.OrdinalIgnoreCase))
                            {
                                progress?.Report(processed * 100.0 / total);
                                continue;
                            }
                            if (!string.IsNullOrWhiteSpace(contentQuery))
                            {
                                try
                                {
                                    var text = File.ReadAllText(file);
                                    if (text.IndexOf(contentQuery, StringComparison.OrdinalIgnoreCase) < 0)
                                    {
                                        progress?.Report(processed * 100.0 / total);
                                        continue;
                                    }
                                }
                                catch { }
                            }
                            var fi = new FileInfo(file);
                            matches.Add(new FileItem
                            {
                                Name = fi.Name,
                                FullPath = fi.FullName,
                                IsDirectory = false,
                                SizeBytes = fi.Length,
                                ModifiedUtc = fi.LastWriteTimeUtc,
                                Type = PathUtils.GetTypeDisplay(fi.FullName, false)
                            });
                            progress?.Report(processed * 100.0 / total);
                        }
                    }
                }
                catch { }
                return matches;
            }, ct);
        }

        private void SetupInboxWatcher()
        {
            try { _inboxWatcher?.Dispose(); } catch { }
            _inboxItems.Clear();
            var path = SettingsService.Instance.Settings.MonitoredFolder;
            if (!Directory.Exists(path)) return;
            _inboxWatcher = new FileSystemWatcher(path)
            {
                Filter = "*.*",
                IncludeSubdirectories = false,
                NotifyFilter = NotifyFilters.FileName | NotifyFilters.LastWrite
            };
            _inboxWatcher.Created += (_, e) => Dispatcher.Invoke(() => AddInboxItem(e.FullPath));
            _inboxWatcher.Changed += (_, e) => Dispatcher.Invoke(() => AddInboxItem(e.FullPath));
            _inboxWatcher.EnableRaisingEvents = true;

            // Seed with last 10 files by write time
            try
            {
                var last = Directory.EnumerateFiles(path)
                    .Select(p => new FileInfo(p))
                    .OrderByDescending(fi => fi.LastWriteTimeUtc)
                    .Take(10)
                    .Select(fi => fi.FullName);
                foreach (var f in last) AddInboxItem(f);
            }
            catch { }
        }

        private void AddInboxItem(string filePath)
        {
            if (!File.Exists(filePath)) return;
            if (_inboxItems.Contains(filePath, StringComparer.OrdinalIgnoreCase)) return;
            _inboxItems.Insert(0, filePath);
            while (_inboxItems.Count > 50) _inboxItems.RemoveAt(_inboxItems.Count - 1);
        }

        private void InboxList_PreviewMouseMove(object? sender, MouseEventArgs e)
        {
            if (e.LeftButton != MouseButtonState.Pressed) return;
            var pos = e.GetPosition(null);
            if (Math.Abs(pos.X - _inboxDragStart.X) < SystemParameters.MinimumHorizontalDragDistance &&
                Math.Abs(pos.Y - _inboxDragStart.Y) < SystemParameters.MinimumVerticalDragDistance) return;

            var selected = InboxList.SelectedItems.Cast<string>().ToArray();
            if (selected.Length == 0) return;
            var data = new DataObject(DataFormats.FileDrop, selected);
            DragDrop.DoDragDrop(InboxList, data, DragDropEffects.Copy | DragDropEffects.Move);
        }

        private async void InboxList_Drop(object sender, DragEventArgs e)
        {
            if (!e.Data.GetDataPresent(DataFormats.FileDrop)) return;
            var files = (string[])e.Data.GetData(DataFormats.FileDrop);
            var target = SettingsService.Instance.Settings.MonitoredFolder;
            Directory.CreateDirectory(target);
            var progress = new Progress<double>(v => OperationProgress.Value = v);
            await FileOperationService.CopyAsync(files, target, progress);
        }

        private void SetInbox_Click(object sender, RoutedEventArgs e)
        {
            var dlg = new System.Windows.Forms.FolderBrowserDialog();
            if (dlg.ShowDialog() == System.Windows.Forms.DialogResult.OK)
            {
                SettingsService.Instance.Settings.MonitoredFolder = dlg.SelectedPath;
                SettingsService.Instance.Save();
                InboxPath.Text = dlg.SelectedPath;
                SetupInboxWatcher();
            }
        }
    }

    internal sealed class ZipEditContext
    {
        public string ZipPath { get; }
        public string InnerPath { get; }
        public string TempFilePath { get; }
        public ZipEditContext(string zipPath, string innerPath, string tempPath)
        {
            ZipPath = zipPath; InnerPath = innerPath; TempFilePath = tempPath;
        }
    }
}