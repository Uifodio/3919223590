using AAAFileManager.Models;
using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Linq;

namespace AAAFileManager.Services
{
    public static class ZipFileSystem
    {
        public static IEnumerable<FileItem> List(string zipPath, string innerDir)
        {
            using var fs = new FileStream(zipPath, FileMode.Open, FileAccess.Read, FileShare.Read);
            using var za = new ZipArchive(fs, ZipArchiveMode.Read);
            string prefix = NormalizeInner(innerDir);
            var items = new Dictionary<string, FileItem>(StringComparer.OrdinalIgnoreCase);
            foreach (var entry in za.Entries)
            {
                if (!entry.FullName.StartsWith(prefix, StringComparison.OrdinalIgnoreCase)) continue;
                string remainder = entry.FullName.Substring(prefix.Length);
                if (string.IsNullOrEmpty(remainder)) continue;
                var parts = remainder.Split('/', '\\');
                string first = parts[0];
                bool isDir = parts.Length > 1 || entry.FullName.EndsWith("/");
                if (!items.ContainsKey(first))
                {
                    if (isDir)
                    {
                        items[first] = new FileItem
                        {
                            Name = first.TrimEnd('/'),
                            FullPath = Path.Combine(zipPath, first),
                            IsDirectory = true,
                            SizeBytes = 0,
                            ModifiedUtc = entry.LastWriteTime.UtcDateTime,
                            Type = "Folder",
                            IsFromZip = true,
                            ZipArchivePath = zipPath,
                            ZipInnerPath = CombineInner(innerDir, first.TrimEnd('/'))
                        };
                    }
                    else
                    {
                        items[first] = new FileItem
                        {
                            Name = first,
                            FullPath = Path.Combine(zipPath, first),
                            IsDirectory = false,
                            SizeBytes = entry.Length,
                            ModifiedUtc = entry.LastWriteTime.UtcDateTime,
                            Type = PathUtils.GetTypeDisplay(first, false),
                            IsFromZip = true,
                            ZipArchivePath = zipPath,
                            ZipInnerPath = CombineInner(innerDir, first)
                        };
                    }
                }
            }
            return items.Values.OrderByDescending(i => i.IsDirectory).ThenBy(i => i.Name, StringComparer.OrdinalIgnoreCase).ToList();
        }

        public static string ExtractEntryToTemp(string zipPath, string innerPath)
        {
            string tempDir = Path.Combine(Path.GetTempPath(), "AAAFileManager", Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(tempDir);
            string fileName = Path.GetFileName(innerPath.TrimEnd('/', '\\'));
            string dest = Path.Combine(tempDir, fileName);
            using var fs = new FileStream(zipPath, FileMode.Open, FileAccess.Read, FileShare.Read);
            using var za = new ZipArchive(fs, ZipArchiveMode.Read);
            var entry = za.GetEntry(innerPath.Replace('\\', '/'));
            if (entry == null) throw new FileNotFoundException("Entry not found", innerPath);
            using var s = entry.Open();
            using var output = new FileStream(dest, FileMode.Create, FileAccess.Write, FileShare.None);
            s.CopyTo(output);
            return dest;
        }

        public static void WriteEntryFromFile(string zipPath, string innerPath, string sourceFilePath)
        {
            CreateZipBackup(zipPath);
            using var fs = new FileStream(zipPath, FileMode.Open, FileAccess.ReadWrite, FileShare.None);
            using var za = new ZipArchive(fs, ZipArchiveMode.Update);
            string normalized = innerPath.Replace('\\', '/');
            var existing = za.GetEntry(normalized);
            existing?.Delete();
            var entry = za.CreateEntry(normalized, CompressionLevel.Optimal);
            using var entryStream = entry.Open();
            using var input = new FileStream(sourceFilePath, FileMode.Open, FileAccess.Read, FileShare.Read);
            input.CopyTo(entryStream);
        }

        public static void AddExternalFile(string zipPath, string innerDir, string externalFilePath)
        {
            CreateZipBackup(zipPath);
            using var fs = new FileStream(zipPath, FileMode.Open, FileAccess.ReadWrite, FileShare.None);
            using var za = new ZipArchive(fs, ZipArchiveMode.Update);
            string fileName = Path.GetFileName(externalFilePath);
            string normalized = CombineInner(innerDir, fileName).Replace('\\', '/');
            var existing = za.GetEntry(normalized);
            existing?.Delete();
            var entry = za.CreateEntry(normalized, CompressionLevel.Optimal);
            using var entryStream = entry.Open();
            using var input = new FileStream(externalFilePath, FileMode.Open, FileAccess.Read, FileShare.Read);
            input.CopyTo(entryStream);
        }

        public static IEnumerable<FileItem> NavigateInto(string zipPath, string innerDir, string folderName)
        {
            string combined = CombineInner(innerDir, folderName);
            return List(zipPath, combined);
        }

        public static string CombineInner(string innerDir, string name)
        {
            string prefix = NormalizeInner(innerDir);
            if (!prefix.EndsWith("/")) prefix += "/";
            return (prefix + name).Trim('/') + (name.EndsWith("/") ? string.Empty : string.Empty);
        }

        private static string NormalizeInner(string innerDir)
        {
            string s = (innerDir ?? string.Empty).Replace('\\', '/').Trim('/');
            return s.Length == 0 ? string.Empty : s + "/";
        }

        private static void CreateZipBackup(string zipPath)
        {
            try { File.Copy(zipPath, zipPath + ".bak", overwrite: true); } catch { }
        }
    }
}