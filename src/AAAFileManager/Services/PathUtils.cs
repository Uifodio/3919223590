using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace AAAFileManager.Services
{
    public static class PathUtils
    {
        private static readonly HashSet<string> TextExtensions = new(StringComparer.OrdinalIgnoreCase)
        {
            ".txt", ".md", ".log", ".json", ".xml", ".yml", ".yaml", ".ini", ".cfg", ".conf",
            ".cs", ".csx", ".vb", ".fs", ".fsx", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx",
            ".html", ".htm", ".css", ".scss", ".less",
            ".c", ".h", ".hpp", ".hh", ".hxx", ".cpp", ".cc", ".cxx",
            ".py", ".java", ".kt", ".kts", ".go", ".rs", ".swift", ".rb", ".php",
            ".sql", ".ps1", ".bat", ".sh", ".cmake",
            ".sln", ".csproj", ".fsproj", ".vbproj", ".proj", ".props", ".targets"
        };

        public static string FormatSize(long bytes)
        {
            if (bytes < 0) return string.Empty;
            string[] sizes = { "B", "KB", "MB", "GB", "TB" };
            double len = bytes;
            int order = 0;
            while (len >= 1024 && order < sizes.Length - 1)
            {
                order++;
                len /= 1024;
            }
            return string.Format(System.Globalization.CultureInfo.InvariantCulture, "{0:0.##} {1}", len, sizes[order]);
        }

        public static string GetTypeDisplay(string path, bool isDirectory)
        {
            if (isDirectory) return "Folder";
            string ext = Path.GetExtension(path);
            if (string.IsNullOrEmpty(ext)) return "File";
            return ext.TrimStart('.').ToUpperInvariant() + " File";
        }

        public static bool IsTextFileByExtension(string path)
        {
            string ext = Path.GetExtension(path);
            return TextExtensions.Contains(ext);
        }

        public static bool PathsEqual(string a, string b)
        {
            return string.Equals(Path.GetFullPath(a).TrimEnd(Path.DirectorySeparatorChar),
                                 Path.GetFullPath(b).TrimEnd(Path.DirectorySeparatorChar),
                                 StringComparison.OrdinalIgnoreCase);
        }

        public static IEnumerable<string> EnumerateFilesSafe(string root)
        {
            var stack = new Stack<string>();
            stack.Push(root);
            while (stack.Count > 0)
            {
                var dir = stack.Pop();
                IEnumerable<string> subdirs;
                IEnumerable<string> files;
                try
                {
                    subdirs = Directory.EnumerateDirectories(dir);
                }
                catch
                {
                    subdirs = Enumerable.Empty<string>();
                }
                try
                {
                    files = Directory.EnumerateFiles(dir);
                }
                catch
                {
                    files = Enumerable.Empty<string>();
                }

                foreach (var f in files) yield return f;
                foreach (var d in subdirs) stack.Push(d);
            }
        }
    }
}