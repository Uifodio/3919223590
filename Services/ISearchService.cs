using System.Collections.Generic;
using System.Threading.Tasks;
using WindowsFileManagerPro.Models;

namespace WindowsFileManagerPro.Services
{
    public interface ISearchService
    {
        Task<IEnumerable<FileItem>> SearchFilesByNameAsync(string searchPath, string searchPattern, bool recursive = false);
        Task<IEnumerable<SearchResult>> SearchInFileContentAsync(string filePath, string searchText, bool caseSensitive = false, bool useRegex = false);
        Task<IEnumerable<SearchResult>> SearchInDirectoryAsync(string searchPath, string searchText, bool recursive = false, bool caseSensitive = false, bool useRegex = false);
        Task<IEnumerable<SearchResult>> SearchInZipAsync(string zipPath, string searchText, bool caseSensitive = false, bool useRegex = false);
        Task<bool> IsSearchableFileAsync(string filePath);
        Task<string[]> GetSearchableExtensionsAsync();
        Task<long> GetSearchableFileCountAsync(string searchPath, bool recursive = false);
        Task<IProgress<int>> GetSearchProgressAsync();
        Task CancelSearchAsync();
        Task<IEnumerable<SearchResult>> GetRecentSearchesAsync();
        Task SaveSearchResultAsync(SearchResult result);
        Task ClearSearchHistoryAsync();
    }

    public class SearchResult
    {
        public string FilePath { get; set; } = "";
        public string FileName { get; set; } = "";
        public string SearchText { get; set; } = "";
        public int LineNumber { get; set; } = 0;
        public int ColumnNumber { get; set; } = 0;
        public string LineContent { get; set; } = "";
        public string Context { get; set; } = "";
        public SearchResultType Type { get; set; } = SearchResultType.Content;
        public DateTime FoundAt { get; set; } = DateTime.Now;
    }

    public enum SearchResultType
    {
        FileName,
        Content,
        Metadata
    }
}