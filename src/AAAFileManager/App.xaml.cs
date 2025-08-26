using System.Windows;

namespace AAAFileManager
{
    public partial class App : Application
    {
        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);
            Services.SettingsService.Instance.Load();
        }

        protected override void OnExit(ExitEventArgs e)
        {
            Services.SettingsService.Instance.Save();
            base.OnExit(e);
        }
    }
}