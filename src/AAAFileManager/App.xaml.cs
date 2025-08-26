using System;
using System.IO;
using System.Text;
using System.Windows;

namespace AAAFileManager
{
    public partial class App : Application
    {
        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);
            Services.SettingsService.Instance.Load();
            Services.ThemeService.ApplyTheme(Services.SettingsService.Instance.Settings.Theme);

            AppDomain.CurrentDomain.UnhandledException += (_, args) =>
            {
                try
                {
                    string dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "AAAFileManager");
                    Directory.CreateDirectory(dir);
                    string log = Path.Combine(dir, "crash.log");
                    var ex = args.ExceptionObject as Exception;
                    File.AppendAllText(log, $"=== {DateTime.Now} ===\n{ex}\n\n", Encoding.UTF8);
                }
                catch { }
            };
        }

        protected override void OnExit(ExitEventArgs e)
        {
            Services.SettingsService.Instance.Save();
            base.OnExit(e);
        }
    }
}