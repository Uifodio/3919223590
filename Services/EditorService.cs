using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using WindowsFileManagerPro.Models;

namespace WindowsFileManagerPro.Services
{
    public class EditorService : IEditorService
    {
        private readonly Dictionary<string, string> _languageExtensions = new()
        {
            { ".cs", "C#" },
            { ".js", "JavaScript" },
            { ".ts", "TypeScript" },
            { ".py", "Python" },
            { ".java", "Java" },
            { ".cpp", "C++" },
            { ".c", "C" },
            { ".h", "C++" },
            { ".hpp", "C++" },
            { ".html", "HTML" },
            { ".htm", "HTML" },
            { ".css", "CSS" },
            { ".scss", "SCSS" },
            { ".sass", "Sass" },
            { ".less", "Less" },
            { ".xml", "XML" },
            { ".xaml", "XAML" },
            { ".json", "JSON" },
            { ".yaml", "YAML" },
            { ".yml", "YAML" },
            { ".sql", "SQL" },
            { ".php", "PHP" },
            { ".rb", "Ruby" },
            { ".go", "Go" },
            { ".rs", "Rust" },
            { ".swift", "Swift" },
            { ".kt", "Kotlin" },
            { ".scala", "Scala" },
            { ".pl", "Perl" },
            { ".sh", "Shell" },
            { ".bat", "Batch" },
            { ".cmd", "Batch" },
            { ".ps1", "PowerShell" },
            { ".vbs", "VBScript" },
            { ".lua", "Lua" },
            { ".r", "R" },
            { ".matlab", "MATLAB" },
            { ".tex", "LaTeX" },
            { ".md", "Markdown" },
            { ".txt", "Plain Text" },
            { ".log", "Log" },
            { ".ini", "INI" },
            { ".cfg", "Configuration" },
            { ".conf", "Configuration" },
            { ".config", "Configuration" }
        };

        private readonly Dictionary<string, string> _fileContents = new();
        private readonly Dictionary<string, string> _originalContents = new();
        private readonly Dictionary<string, DateTime> _lastModified = new();

        public async Task<string> LoadFileAsync(string filePath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    if (File.Exists(filePath))
                    {
                        var content = File.ReadAllText(filePath);
                        _fileContents[filePath] = content;
                        _originalContents[filePath] = content;
                        _lastModified[filePath] = File.GetLastWriteTime(filePath);
                        return content;
                    }
                    return string.Empty;
                }
                catch (Exception)
                {
                    return string.Empty;
                }
            });
        }

        public async Task<bool> SaveFileAsync(string filePath, string content)
        {
            return await Task.Run(() =>
            {
                try
                {
                    var directory = Path.GetDirectoryName(filePath);
                    if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
                    {
                        Directory.CreateDirectory(directory);
                    }

                    // Create backup before saving
                    if (File.Exists(filePath) && _originalContents.ContainsKey(filePath))
                    {
                        var backupPath = GetBackupPath(filePath);
                        File.Copy(filePath, backupPath, true);
                    }

                    File.WriteAllText(filePath, content);
                    _fileContents[filePath] = content;
                    _originalContents[filePath] = content;
                    _lastModified[filePath] = DateTime.Now;
                    return true;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<bool> SaveFileAsAsync(string originalPath, string newPath, string content)
        {
            return await Task.Run(() =>
            {
                try
                {
                    var directory = Path.GetDirectoryName(newPath);
                    if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
                    {
                        Directory.CreateDirectory(directory);
                    }

                    File.WriteAllText(newPath, content);
                    _fileContents[newPath] = content;
                    _originalContents[newPath] = content;
                    _lastModified[newPath] = DateTime.Now;
                    return true;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        public async Task<string> GetFileContentAsync(string filePath)
        {
            return await Task.Run(() =>
            {
                if (_fileContents.ContainsKey(filePath))
                {
                    return _fileContents[filePath];
                }
                return LoadFileAsync(filePath).Result;
            });
        }

        public async Task<bool> IsFileModifiedAsync(string filePath)
        {
            return await Task.Run(() =>
            {
                if (_fileContents.ContainsKey(filePath) && _originalContents.ContainsKey(filePath))
                {
                    return _fileContents[filePath] != _originalContents[filePath];
                }
                return false;
            });
        }

        public async Task<string> GetSyntaxLanguageAsync(string filePath)
        {
            return await Task.Run(() =>
            {
                var extension = Path.GetExtension(filePath).ToLowerInvariant();
                return _languageExtensions.ContainsKey(extension) ? _languageExtensions[extension] : "Plain Text";
            });
        }

        public async Task<bool> ValidateSyntaxAsync(string content, string language)
        {
            return await Task.Run(() =>
            {
                // Basic syntax validation - in a real implementation, you'd use language-specific parsers
                try
                {
                    switch (language.ToLower())
                    {
                        case "json":
                            return ValidateJson(content);
                        case "xml":
                            return ValidateXml(content);
                        case "c#":
                        case "javascript":
                        case "python":
                        case "html":
                        case "css":
                            // Basic validation - check for balanced brackets, quotes, etc.
                            return ValidateBasicSyntax(content);
                        default:
                            return true; // Assume valid for unknown languages
                    }
                }
                catch
                {
                    return false;
                }
            });
        }

        public async Task<string> FormatCodeAsync(string content, string language)
        {
            return await Task.Run(() =>
            {
                // Basic code formatting - in a real implementation, you'd use language-specific formatters
                try
                {
                    switch (language.ToLower())
                    {
                        case "json":
                            return FormatJson(content);
                        case "xml":
                            return FormatXml(content);
                        case "html":
                            return FormatHtml(content);
                        case "css":
                            return FormatCss(content);
                        default:
                            return content; // Return as-is for unsupported languages
                    }
                }
                catch
                {
                    return content;
                }
            });
        }

        public async Task<string[]> GetSupportedLanguagesAsync()
        {
            return await Task.Run(() => _languageExtensions.Values.Distinct().ToArray());
        }

        public async Task<string> GetLanguageExtensionAsync(string language)
        {
            return await Task.Run(() =>
            {
                var extension = _languageExtensions.FirstOrDefault(x => x.Value.Equals(language, StringComparison.OrdinalIgnoreCase));
                return extension.Key ?? ".txt";
            });
        }

        public async Task<bool> HasUnsavedChangesAsync(string filePath)
        {
            return await Task.Run(() =>
            {
                if (_fileContents.ContainsKey(filePath) && _originalContents.ContainsKey(filePath))
                {
                    return _fileContents[filePath] != _originalContents[filePath];
                }
                return false;
            });
        }

        public async Task<string> GetAutoSavePathAsync(string originalPath)
        {
            return await Task.Run(() =>
            {
                var directory = Path.GetDirectoryName(originalPath);
                var fileName = Path.GetFileNameWithoutExtension(originalPath);
                var extension = Path.GetExtension(originalPath);
                var timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
                return Path.Combine(directory ?? "", $"{fileName}_{timestamp}{extension}.autosave");
            });
        }

        public async Task<bool> RestoreFromBackupAsync(string filePath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    var backupPath = GetBackupPath(filePath);
                    if (File.Exists(backupPath))
                    {
                        var backupContent = File.ReadAllText(backupPath);
                        _fileContents[filePath] = backupContent;
                        _originalContents[filePath] = backupContent;
                        return true;
                    }
                    return false;
                }
                catch (Exception)
                {
                    return false;
                }
            });
        }

        private string GetBackupPath(string filePath)
        {
            var directory = Path.GetDirectoryName(filePath);
            var fileName = Path.GetFileNameWithoutExtension(filePath);
            var extension = Path.GetExtension(filePath);
            var timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
            return Path.Combine(directory ?? "", $"{fileName}_{timestamp}{extension}.bak");
        }

        private bool ValidateJson(string content)
        {
            try
            {
                Newtonsoft.Json.JsonConvert.DeserializeObject(content);
                return true;
            }
            catch
            {
                return false;
            }
        }

        private bool ValidateXml(string content)
        {
            try
            {
                var doc = new System.Xml.XmlDocument();
                doc.LoadXml(content);
                return true;
            }
            catch
            {
                return false;
            }
        }

        private bool ValidateBasicSyntax(string content)
        {
            // Basic validation for balanced brackets, quotes, etc.
            var brackets = new Stack<char>();
            var inString = false;
            var escapeNext = false;

            foreach (var c in content)
            {
                if (escapeNext)
                {
                    escapeNext = false;
                    continue;
                }

                if (c == '\\')
                {
                    escapeNext = true;
                    continue;
                }

                if (c == '"' && !escapeNext)
                {
                    inString = !inString;
                    continue;
                }

                if (!inString)
                {
                    if (c == '{' || c == '[' || c == '(')
                    {
                        brackets.Push(c);
                    }
                    else if (c == '}' || c == ']' || c == ')')
                    {
                        if (brackets.Count == 0) return false;
                        var open = brackets.Pop();
                        if ((c == '}' && open != '{') || (c == ']' && open != '[') || (c == ')' && open != '('))
                        {
                            return false;
                        }
                    }
                }
            }

            return brackets.Count == 0 && !inString;
        }

        private string FormatJson(string content)
        {
            try
            {
                var obj = Newtonsoft.Json.JsonConvert.DeserializeObject(content);
                return Newtonsoft.Json.JsonConvert.SerializeObject(obj, Newtonsoft.Json.Formatting.Indented);
            }
            catch
            {
                return content;
            }
        }

        private string FormatXml(string content)
        {
            try
            {
                var doc = new System.Xml.XmlDocument();
                doc.LoadXml(content);
                var settings = new System.Xml.XmlWriterSettings
                {
                    Indent = true,
                    IndentChars = "  ",
                    NewLineChars = "\r\n"
                };
                using var stringWriter = new StringWriter();
                using var xmlWriter = System.Xml.XmlWriter.Create(stringWriter, settings);
                doc.Save(xmlWriter);
                return stringWriter.ToString();
            }
            catch
            {
                return content;
            }
        }

        private string FormatHtml(string content)
        {
            // Basic HTML formatting - in a real implementation, you'd use a proper HTML formatter
            return content.Replace("><", ">\n<")
                        .Replace("</", "\n</")
                        .Replace("<", "\n<")
                        .Replace(">", ">\n");
        }

        private string FormatCss(string content)
        {
            // Basic CSS formatting
            return content.Replace(";", ";\n")
                        .Replace("{", " {\n")
                        .Replace("}", "\n}\n")
                        .Replace(",", ", ");
        }
    }
}