using WindowsFileManagerPro.Models;

namespace WindowsFileManagerPro.Services
{
    public interface IConfigurationService
    {
        AppSettings? GetSettings();
        bool SaveSettings(AppSettings settings);
        AppSettings GetDefaultSettings();
        bool ResetToDefaults();
        bool ExportSettings(string filePath);
        bool ImportSettings(string filePath);
        bool ValidateSettings(AppSettings settings);
        string GetSettingsFilePath();
    }
}