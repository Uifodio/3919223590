using System.Threading.Tasks;

namespace WindowsFileManagerPro.Services
{
    public interface IEditorService
    {
        Task<string> LoadFileAsync(string filePath);
        Task<bool> SaveFileAsync(string filePath, string content);
        Task<bool> SaveFileAsAsync(string originalPath, string newPath, string content);
        Task<string> GetFileContentAsync(string filePath);
        Task<bool> IsFileModifiedAsync(string filePath);
        Task<string> GetSyntaxLanguageAsync(string filePath);
        Task<bool> ValidateSyntaxAsync(string content, string language);
        Task<string> FormatCodeAsync(string content, string language);
        Task<string[]> GetSupportedLanguagesAsync();
        Task<string> GetLanguageExtensionAsync(string language);
        Task<bool> HasUnsavedChangesAsync(string filePath);
        Task<string> GetAutoSavePathAsync(string originalPath);
        Task<bool> RestoreFromBackupAsync(string filePath);
    }
}