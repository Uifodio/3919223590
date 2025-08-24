#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

namespace Chess.EditorTools
{
	public static class ChessSetupEditor
	{
		private const string PiecesFolder = "Assets/Chess/Resources/CBurnett";
		private const string BoardFolder = "Assets/Chess/Resources/Board";

		[MenuItem("Tools/Chess/Setup Project", priority = 1)]
		public static void SetupProject()
		{
			DownloadCbPngAssets();
			CreateChessScene();
		}

		[MenuItem("Tools/Chess/Download CBurnett Assets (PNG)", priority = 3)]
		public static void DownloadCbPngAssets()
		{
			Directory.CreateDirectory(PiecesFolder);
			Directory.CreateDirectory(BoardFolder);
			var files = new Dictionary<string, string>
			{
				{"Chess_klt45.png", "https://upload.wikimedia.org/wikipedia/commons/4/42/Chess_klt45.svg"},
				{"Chess_qlt45.png", "https://upload.wikimedia.org/wikipedia/commons/1/15/Chess_qlt45.svg"},
				{"Chess_rlt45.png", "https://upload.wikimedia.org/wikipedia/commons/7/72/Chess_rlt45.svg"},
				{"Chess_blt45.png", "https://upload.wikimedia.org/wikipedia/commons/b/b1/Chess_blt45.svg"},
				{"Chess_nlt45.png", "https://upload.wikimedia.org/wikipedia/commons/7/70/Chess_nlt45.svg"},
				{"Chess_plt45.png", "https://upload.wikimedia.org/wikipedia/commons/4/45/Chess_plt45.svg"},
				{"Chess_kdt45.png", "https://upload.wikimedia.org/wikipedia/commons/f/f0/Chess_kdt45.svg"},
				{"Chess_qdt45.png", "https://upload.wikimedia.org/wikipedia/commons/4/47/Chess_qdt45.svg"},
				{"Chess_rdt45.png", "https://upload.wikimedia.org/wikipedia/commons/f/ff/Chess_rdt45.svg"},
				{"Chess_bdt45.png", "https://upload.wikimedia.org/wikipedia/commons/9/98/Chess_bdt45.svg"},
				{"Chess_ndt45.png", "https://upload.wikimedia.org/wikipedia/commons/e/ef/Chess_ndt45.svg"},
				{"Chess_pdt45.png", "https://upload.wikimedia.org/wikipedia/commons/c/c7/Chess_pdt45.svg"},
				{"Board_wood.png", "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Chess_board_opening_staunton.jpg/1024px-Chess_board_opening_staunton.jpg"}
			};

			using (var client = new WebClient())
			{
				foreach (var kv in files)
				{
					var targetDir = kv.Key.StartsWith("Board_") ? BoardFolder : PiecesFolder;
					var path = Path.Combine(targetDir, kv.Key);
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
			var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

			// Camera
			var camGo = new GameObject("Main Camera", typeof(Camera));
			var cam = camGo.GetComponent<Camera>();
			cam.clearFlags = CameraClearFlags.SolidColor;
			cam.backgroundColor = new Color(0.08f, 0.08f, 0.1f);
			cam.orthographic = false;
			camGo.tag = "MainCamera";

			// Canvas (Screen Space - Camera)
			var canvasGo = new GameObject("Canvas", typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
			var canvas = canvasGo.GetComponent<Canvas>();
			canvas.renderMode = RenderMode.ScreenSpaceCamera;
			canvas.worldCamera = cam;
			var scaler = canvasGo.GetComponent<CanvasScaler>();
			scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
			scaler.referenceResolution = new Vector2(1920, 1080);

			// Bootstrap
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