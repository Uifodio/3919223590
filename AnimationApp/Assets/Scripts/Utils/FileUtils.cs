using UnityEngine;
using System.IO;

namespace AnimationApp.Utils
{
    public static class FileUtils
    {
        public static string GetProjectPath()
        {
            return Application.persistentDataPath;
        }
        
        public static string GetExportsPath()
        {
            string path = Path.Combine(GetProjectPath(), "Exports");
            if (!Directory.Exists(path))
            {
                Directory.CreateDirectory(path);
            }
            return path;
        }
        
        public static string GetAudioPath()
        {
            string path = Path.Combine(GetProjectPath(), "Audio");
            if (!Directory.Exists(path))
            {
                Directory.CreateDirectory(path);
            }
            return path;
        }
        
        public static string GetBrushesPath()
        {
            string path = Path.Combine(GetProjectPath(), "Brushes");
            if (!Directory.Exists(path))
            {
                Directory.CreateDirectory(path);
            }
            return path;
        }
        
        public static bool IsValidImageFile(string path)
        {
            string extension = Path.GetExtension(path).ToLower();
            return extension == ".png" || extension == ".jpg" || extension == ".jpeg" || 
                   extension == ".bmp" || extension == ".tga" || extension == ".tiff";
        }
        
        public static bool IsValidAudioFile(string path)
        {
            string extension = Path.GetExtension(path).ToLower();
            return extension == ".wav" || extension == ".mp3" || extension == ".aiff" || 
                   extension == ".ogg" || extension == ".flac";
        }
        
        public static string GetUniqueFileName(string basePath, string extension)
        {
            string path = basePath + extension;
            int counter = 1;
            
            while (File.Exists(path))
            {
                path = basePath + "_" + counter + extension;
                counter++;
            }
            
            return path;
        }
        
        public static void SaveTextureAsPNG(Texture2D texture, string path)
        {
            byte[] bytes = texture.EncodeToPNG();
            File.WriteAllBytes(path, bytes);
        }
        
        public static void SaveTextureAsJPEG(Texture2D texture, string path, int quality = 80)
        {
            byte[] bytes = texture.EncodeToJPG(quality);
            File.WriteAllBytes(path, bytes);
        }
        
        public static Texture2D LoadTextureFromFile(string path)
        {
            if (!File.Exists(path))
                return null;
            
            byte[] fileData = File.ReadAllBytes(path);
            Texture2D texture = new Texture2D(2, 2);
            
            if (texture.LoadImage(fileData))
            {
                return texture;
            }
            
            return null;
        }
    }
}
