using System;
using System.Windows;

namespace AAAFileManager.Services
{
    public static class ThemeService
    {
        public static void ApplyTheme(string theme)
        {
            var app = Application.Current;
            if (app == null) return;
            var dictionaries = app.Resources.MergedDictionaries;
            dictionaries.Clear();
            if (string.Equals(theme, "Light", StringComparison.OrdinalIgnoreCase))
            {
                dictionaries.Add(new ResourceDictionary { Source = new Uri("Themes/Light.xaml", UriKind.Relative) });
            }
            else
            {
                dictionaries.Add(new ResourceDictionary { Source = new Uri("Themes/Dark.xaml", UriKind.Relative) });
            }
        }
    }
}