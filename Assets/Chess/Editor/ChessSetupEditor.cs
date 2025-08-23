#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEditor.PackageManager;
using UnityEditor.PackageManager.Requests;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Chess.EditorTools
{
	public static class ChessSetupEditor
	{
		private const string PiecesFolder = "Assets/Chess/Resources/CBurnett";

		[MenuItem("Tools/Chess/Setup Project", priority = 1)]
		public static void SetupProject()
		{
			InstallVectorGraphics();
			DownloadCbAssets();
			CreateChessScene();
		}

		[MenuItem("Tools/Chess/Install Vector Graphics", priority = 2)]
		public static void InstallVectorGraphics()
		{
			Client.Add("com.unity.vectorgraphics");
			Debug.Log("Requested install of com.unity.vectorgraphics via Package Manager.");
		}

		[MenuItem("Tools/Chess/Download CBurnett Assets", priority = 3)]
		public static void DownloadCbAssets()
		{
			Directory.CreateDirectory(PiecesFolder);
			var files = new Dictionary<string, string>
			{
				{"Chess_klt45.svg", "https://commons.wikimedia.org/wiki/Special:FilePath/Chess_klt45.svg"},
				{"Chess_qlt45.svg", "https://commons.wikimedia.org/wiki/Special:FilePath/Chess_qlt45.svg"},
				{"Chess_rlt45.svg", "https://commons.wikimedia.org/wiki/Special:FilePath/Chess_rlt45.svg"},
				{"Chess_blt45.svg", "https://commons.wikimedia.org/wiki/Special:FilePath/Chess_blt45.svg"},
				{"Chess_nlt45.svg", "https://commons.wikimedia.org/wiki/Special:FilePath/Chess_nlt45.svg"},
				{"Chess_plt45.svg", "https://commons.wikimedia.org/wiki/Special:FilePath/Chess_plt45.svg"},
				{"Chess_kdt45.svg", "https://commons.wikimedia.org/wiki/Special:FilePath/Chess_kdt45.svg"},
				{"Chess_qdt45.svg", "https://commons.wikimedia.org/wiki/Special:FilePath/Chess_qdt45.svg"},
				{"Chess_rdt45.svg", "https://commons.wikimedia.org/wiki/Special:FilePath/Chess_rdt45.svg"},
				{"Chess_bdt45.svg", "https://commons.wikimedia.org/wiki/Special:FilePath/Chess_bdt45.svg"},
				{"Chess_ndt45.svg", "https://commons.wikimedia.org/wiki/Special:FilePath/Chess_ndt45.svg"},
				{"Chess_pdt45.svg", "https://commons.wikimedia.org/wiki/Special:FilePath/Chess_pdt45.svg"}
			};

			using (var client = new WebClient())
			{
				foreach (var kv in files)
				{
					var path = Path.Combine(PiecesFolder, kv.Key);
					try
					{
						client.DownloadFile(kv.Value, path);
						Debug.Log($"Downloaded {kv.Key}");
					}
					catch (Exception ex)
					{
						Debug.LogWarning($"Failed to download {kv.Key}: {ex.Message}");
					}
				}
			}
			AssetDatabase.Refresh();
		}

		[MenuItem("Tools/Chess/Create Chess Scene", priority = 4)]
		public static void CreateChessScene()
		{
			var scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
			var bootstrap = new GameObject("ChessGame");
			bootstrap.AddComponent<Chess.ChessGameBootstrap>();
			EditorSceneManager.MarkSceneDirty(scene);

			Directory.CreateDirectory("Assets/Chess/Scenes");
			var scenePath = "Assets/Chess/Scenes/Chess.unity";
			EditorSceneManager.SaveScene(scene, scenePath);
			EditorSceneManager.OpenScene(scenePath, OpenSceneMode.Single);
			Debug.Log("Created and opened Chess scene at " + scenePath);
		}
	}
}
#endif