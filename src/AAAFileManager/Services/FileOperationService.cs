using Microsoft.VisualBasic.FileIO;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace AAAFileManager.Services
{
    public static class FileOperationService
    {
        public static async Task CopyAsync(IEnumerable<string> sources, string targetDirectory, IProgress<double>? progress = null, CancellationToken ct = default)
        {
            var allFiles = ExpandToFiles(sources).ToList();
            long totalBytes = allFiles.Sum(f => new FileInfo(f).Length);
            long copiedBytes = 0;
            const int BufferSize = 1024 * 128;
            Directory.CreateDirectory(targetDirectory);

            foreach (var source in allFiles)
            {
                ct.ThrowIfCancellationRequested();
                string relative = Path.GetRelativePath(GetCommonRoot(sources), source);
                string destination = Path.Combine(targetDirectory, relative);
                Directory.CreateDirectory(Path.GetDirectoryName(destination)!);

                if (File.Exists(destination))
                {
                    try { File.Copy(destination, destination + ".bak", overwrite: true); } catch { }
                }
                using (var input = new FileStream(source, FileMode.Open, FileAccess.Read, FileShare.Read, BufferSize, useAsync: true))
                using (var output = new FileStream(destination, FileMode.Create, FileAccess.Write, FileShare.None, BufferSize, useAsync: true))
                {
                    var buffer = new byte[BufferSize];
                    int read;
                    while ((read = await input.ReadAsync(buffer.AsMemory(0, buffer.Length), ct)) > 0)
                    {
                        await output.WriteAsync(buffer.AsMemory(0, read), ct);
                        copiedBytes += read;
                        progress?.Report(totalBytes == 0 ? 100 : (copiedBytes * 100.0 / totalBytes));
                    }
                }
            }
            progress?.Report(100);
        }

        public static async Task MoveAsync(IEnumerable<string> sources, string targetDirectory, IProgress<double>? progress = null, CancellationToken ct = default)
        {
            await CopyAsync(sources, targetDirectory, progress, ct);
            DeleteToRecycleBin(sources);
        }

        public static void DeleteToRecycleBin(IEnumerable<string> paths)
        {
            foreach (var path in paths)
            {
                if (Directory.Exists(path))
                {
                    FileSystem.DeleteDirectory(path, UIOption.OnlyErrorDialogs, RecycleOption.SendToRecycleBin);
                }
                else if (File.Exists(path))
                {
                    FileSystem.DeleteFile(path, UIOption.OnlyErrorDialogs, RecycleOption.SendToRecycleBin);
                }
            }
        }

        public static string Rename(string path, string newName)
        {
            string? dir = Path.GetDirectoryName(path);
            if (dir == null) throw new InvalidOperationException("Invalid path");
            string newPath = Path.Combine(dir, newName);
            if (Directory.Exists(path)) Directory.Move(path, newPath);
            else File.Move(path, newPath);
            return newPath;
        }

        public static string Duplicate(string path)
        {
            string? dir = Path.GetDirectoryName(path);
            string name = Path.GetFileNameWithoutExtension(path);
            string ext = Path.GetExtension(path);
            int i = 1;
            string candidate;
            do
            {
                candidate = Path.Combine(dir!, $"{name} - Copy{i}{ext}");
                i++;
            } while (File.Exists(candidate) || Directory.Exists(candidate));

            if (File.Exists(path)) File.Copy(path, candidate);
            else CopyDirectory(path, candidate);
            return candidate;
        }

        public static void CreateBackup(string filePath)
        {
            if (!File.Exists(filePath)) return;
            string bak = filePath + ".bak";
            try { File.Copy(filePath, bak, overwrite: true); } catch { }
        }

        private static IEnumerable<string> ExpandToFiles(IEnumerable<string> paths)
        {
            foreach (var p in paths)
            {
                if (File.Exists(p)) yield return p;
                else if (Directory.Exists(p))
                {
                    foreach (var f in Directory.EnumerateFiles(p, "*", SearchOption.AllDirectories))
                        yield return f;
                }
            }
        }

        private static void CopyDirectory(string sourceDir, string targetDir)
        {
            foreach (string dir in Directory.EnumerateDirectories(sourceDir, "*", SearchOption.AllDirectories))
            {
                string rel = Path.GetRelativePath(sourceDir, dir);
                Directory.CreateDirectory(Path.Combine(targetDir, rel));
            }
            foreach (string file in Directory.EnumerateFiles(sourceDir, "*", SearchOption.AllDirectories))
            {
                string rel = Path.GetRelativePath(sourceDir, file);
                string dest = Path.Combine(targetDir, rel);
                Directory.CreateDirectory(Path.GetDirectoryName(dest)!);
                File.Copy(file, dest, overwrite: true);
            }
        }

        private static string GetCommonRoot(IEnumerable<string> paths)
        {
            var list = paths.ToList();
            if (list.Count == 1)
            {
                var p = list[0];
                return Directory.Exists(p) ? p : Path.GetDirectoryName(p)!;
            }
            string first = Path.GetFullPath(list[0]);
            string common = Path.GetDirectoryName(first)!;
            foreach (var p in list.Skip(1))
            {
                string cur = Path.GetFullPath(p);
                while (!cur.StartsWith(common, StringComparison.OrdinalIgnoreCase) && common.Length > 3)
                {
                    common = Path.GetDirectoryName(common)!;
                }
            }
            return common;
        }
    }
}