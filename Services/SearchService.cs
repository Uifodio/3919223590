using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using WindowsFileManagerPro.Models;

namespace WindowsFileManagerPro.Services
{
    public class SearchService : ISearchService
    {
        private readonly List<SearchResult> _recentSearches = new();
        private readonly string[] _searchableExtensions = {
            ".txt", ".cs", ".js", ".ts", ".py", ".java", ".cpp", ".c", ".h", ".hpp",
            ".html", ".htm", ".css", ".scss", ".sass", ".less", ".xml", ".xaml",
            ".json", ".yaml", ".yml", ".sql", ".php", ".rb", ".go", ".rs", ".swift",
            ".kt", ".scala", ".pl", ".sh", ".bat", ".cmd", ".ps1", ".vbs", ".lua",
            ".r", ".matlab", ".tex", ".md", ".log", ".ini", ".cfg", ".conf", ".config"
        };

        public async Task<IEnumerable<FileItem>> SearchFilesByNameAsync(string searchPath, string searchPattern, bool recursive = false)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (!Directory.Exists(searchPath))
                        return Enumerable.Empty<FileItem>();

                    var searchOption = recursive ? SearchOption.AllDirectories : SearchOption.TopDirectoryOnly;
                    var files = Directory.GetFiles(searchPath, searchPattern, searchOption);
                    
                    return files.Select(f => new FileItem(f));
                }
                catch (Exception)
                {
                    return Enumerable.Empty<FileItem>();
                }
            });
        }

        public async Task<IEnumerable<SearchResult>> SearchInFileContentAsync(string filePath, string searchText, bool caseSensitive = false, bool useRegex = false)
        {
            return await Task.Run(() =>
            {
                var results = new List<SearchResult>();

                try
                {
                    if (!File.Exists(filePath) || !IsSearchableFileAsync(filePath).Result)
                        return results;

                    var content = File.ReadAllText(filePath);
                    var lines = content.Split('\n');
                    var comparison = caseSensitive ? StringComparison.Ordinal : StringComparison.OrdinalIgnoreCase;

                    for (int i = 0; i < lines.Length; i++)
                    {
                        var line = lines[i];
                        var lineNumber = i + 1;
                        bool found = false;

                        if (useRegex)
                        {
                            try
                            {
                                var regex = new Regex(searchText, caseSensitive ? RegexOptions.None : RegexOptions.IgnoreCase);
                                if (regex.IsMatch(line))
                                {
                                    found = true;
                                }
                            }
                            catch
                            {
                                // Invalid regex, skip
                                continue;
                            }
                        }
                        else
                        {
                            found = line.IndexOf(searchText, comparison) >= 0;
                        }

                        if (found)
                        {
                            var result = new SearchResult
                            {
                                FilePath = filePath,
                                FileName = Path.GetFileName(filePath),
                                SearchText = searchText,
                                LineNumber = lineNumber,
                                ColumnNumber = line.IndexOf(searchText, comparison) + 1,
                                LineContent = line.Trim(),
                                Context = GetContext(lines, i, 2),
                                Type = SearchResultType.Content,
                                FoundAt = DateTime.Now
                            };

                            results.Add(result);
                        }
                    }
                }
                catch (Exception)
                {
                    // Return empty results if file can't be read
                }

                return results;
            });
        }

        public async Task<IEnumerable<SearchResult>> SearchInDirectoryAsync(string searchPath, string searchText, bool recursive = false, bool caseSensitive = false, bool useRegex = false)
        {
            return await Task.Run(async () =>
            {
                var allResults = new List<SearchResult>();

                try
                {
                    if (!Directory.Exists(searchPath))
                        return allResults;

                    var searchOption = recursive ? SearchOption.AllDirectories : SearchOption.TopDirectoryOnly;
                    var files = Directory.GetFiles(searchPath, "*.*", searchOption)
                        .Where(f => IsSearchableFileAsync(f).Result)
                        .ToList();

                    foreach (var file in files)
                    {
                        try
                        {
                            var fileResults = await SearchInFileContentAsync(file, searchText, caseSensitive, useRegex);
                            allResults.AddRange(fileResults);
                        }
                        catch
                        {
                            // Skip files that can't be searched
                            continue;
                        }
                    }
                }
                catch (Exception)
                {
                    // Return empty results if search fails
                }

                return allResults;
            });
        }

        public async Task<IEnumerable<SearchResult>> SearchInZipAsync(string zipPath, string searchText, bool caseSensitive = false, bool useRegex = false)
        {
            return await Task.Run(async () =>
            {
                var results = new List<SearchResult>();

                try
                {
                    // This would require ZIP service integration
                    // For now, return empty results
                    // In a full implementation, you'd extract and search ZIP contents
                }
                catch (Exception)
                {
                    // Return empty results if ZIP search fails
                }

                return results;
            });
        }

        public async Task<bool> IsSearchableFileAsync(string filePath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (!File.Exists(filePath))
                        return false;

                    var extension = Path.GetExtension(filePath).ToLowerInvariant();
                    return _searchableExtensions.Contains(extension);
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<string[]> GetSearchableExtensionsAsync()
        {
            return await Task.Run(() => _searchableExtensions);
        }

        public async Task<long> GetSearchableFileCountAsync(string searchPath, bool recursive = false)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (!Directory.Exists(searchPath))
                        return 0;

                    var searchOption = recursive ? SearchOption.AllDirectories : SearchOption.TopDirectoryOnly;
                    var files = Directory.GetFiles(searchPath, "*.*", searchOption);
                    
                    return files.Count(f => IsSearchableFileAsync(f).Result);
                }
                catch (Exception)
                {
                    return 0;
                }
            });
        }

        public Task<IProgress<int>> GetSearchProgressAsync()
        {
            return Task.FromResult<IProgress<int>>(new Progress<int>(value => { }));
        }

        public async Task CancelSearchAsync()
        {
            await Task.Run(() =>
            {
                // Implementation would require cancellation token support
            });
        }

        public async Task<IEnumerable<SearchResult>> GetRecentSearchesAsync()
        {
            return await Task.Run(() => _recentSearches.AsEnumerable());
        }

        public async Task SaveSearchResultAsync(SearchResult result)
        {
            await Task.Run(() =>
            {
                try
                {
                    _recentSearches.Add(result);
                    
                    // Keep only last 100 searches
                    if (_recentSearches.Count > 100)
                    {
                        _recentSearches.RemoveRange(0, _recentSearches.Count - 100);
                    }
                }
                catch (Exception)
                {
                    // Ignore errors when saving search results
                }
            });
        }

        public async Task ClearSearchHistoryAsync()
        {
            await Task.Run(() =>
            {
                _recentSearches.Clear();
            });
        }

        private string GetContext(string[] lines, int currentLine, int contextLines)
        {
            try
            {
                var start = Math.Max(0, currentLine - contextLines);
                var end = Math.Min(lines.Length - 1, currentLine + contextLines);
                var contextLinesList = new List<string>();

                for (int i = start; i <= end; i++)
                {
                    var prefix = i == currentLine ? ">>> " : "    ";
                    contextLinesList.Add($"{prefix}{lines[i].Trim()}");
                }

                return string.Join("\n", contextLinesList);
            }
            catch (Exception)
            {
                return "";
            }
        }
    }
}