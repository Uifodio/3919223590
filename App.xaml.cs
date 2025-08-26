using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using System;
using System.Windows;
using WindowsFileManagerPro.Services;
using WindowsFileManagerPro.ViewModels;
using WindowsFileManagerPro.Views;

namespace WindowsFileManagerPro
{
    public partial class App : Application
    {
        private IHost? _host;

        protected override async void OnStartup(StartupEventArgs e)
        {
            try
            {
                _host = CreateHostBuilder(e.Args).Build();
                await _host.StartAsync();

                var mainWindow = _host.Services.GetRequiredService<MainWindow>();
                mainWindow.Show();

                base.OnStartup(e);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Failed to start application: {ex.Message}", "Startup Error", 
                    MessageBoxButton.OK, MessageBoxImage.Error);
                Shutdown();
            }
        }

        protected override async void OnExit(ExitEventArgs e)
        {
            if (_host != null)
            {
                await _host.StopAsync();
                _host.Dispose();
            }

            base.OnExit(e);
        }

        private static IHostBuilder CreateHostBuilder(string[] args) =>
            Host.CreateDefaultBuilder(args)
                .ConfigureServices((context, services) =>
                {
                    // Services
                    services.AddSingleton<IFileService, FileService>();
                    services.AddSingleton<IZipService, ZipService>();
                    services.AddSingleton<ISearchService, SearchService>();
                    services.AddSingleton<IConfigurationService, ConfigurationService>();
                    services.AddSingleton<IClipboardService, ClipboardService>();
                    services.AddSingleton<IBackupService, BackupService>();
                    services.AddSingleton<IEditorService, EditorService>();

                    // ViewModels
                    services.AddTransient<MainWindowViewModel>();
                    services.AddTransient<FileExplorerViewModel>();
                    services.AddTransient<EditorViewModel>();
                    services.AddTransient<SearchViewModel>();

                    // Views
                    services.AddTransient<MainWindow>();
                    services.AddTransient<FileExplorerView>();
                    services.AddTransient<EditorView>();
                    services.AddTransient<SearchView>();

                    // Logging
                    services.AddLogging(builder =>
                    {
                        builder.AddConsole();
                        builder.AddDebug();
                    });
                });
    }
}