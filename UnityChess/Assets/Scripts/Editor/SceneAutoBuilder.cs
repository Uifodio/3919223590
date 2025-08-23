#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;

namespace Chess.Editor
{
	public static class SceneAutoBuilder
	{
		[MenuItem("Tools/Chess/Create Sample Scene")]
		public static void CreateScene()
		{
			var root = new GameObject("GameRoot");
			var gm = root.AddComponent<GameManager>();

			var camGo = new GameObject("Main Camera");
			var cam = camGo.AddComponent<Camera>();
			camGo.tag = "MainCamera";
			cam.orthographic = true;
			cam.transform.position = new Vector3(0, 0, -10);

			var es = new GameObject("EventSystem", typeof(EventSystem), typeof(StandaloneInputModule));

			var canvasGo = new GameObject("Canvas", typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
			var canvas = canvasGo.GetComponent<Canvas>();
			canvas.renderMode = RenderMode.ScreenSpaceOverlay;
			var scaler = canvasGo.GetComponent<CanvasScaler>();
			scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
			scaler.referenceResolution = new Vector2(1080, 1920);

			var boardGo = new GameObject("Board", typeof(RectTransform));
			boardGo.transform.SetParent(canvasGo.transform, false);
			var boardRect = boardGo.GetComponent<RectTransform>();
			boardRect.anchorMin = new Vector2(0.5f, 0.5f);
			boardRect.anchorMax = new Vector2(0.5f, 0.5f);
			boardRect.sizeDelta = new Vector2(900, 900);
			boardRect.anchoredPosition = Vector2.zero;

			var gridGo = new GameObject("Grid", typeof(GridLayoutGroup));
			gridGo.transform.SetParent(boardGo.transform, false);
			var grid = gridGo.GetComponent<GridLayoutGroup>();
			grid.constraint = GridLayoutGroup.Constraint.FixedColumnCount;
			grid.constraintCount = 8;
			grid.cellSize = new Vector2(100, 100);
			grid.spacing = new Vector2(2, 2);

			var squarePrefab = new GameObject("SquareButton", typeof(RectTransform), typeof(Image), typeof(Button));
			PrefabUtility.SaveAsPrefabAsset(squarePrefab, "Assets/SquareButton.prefab");
			GameObject.DestroyImmediate(squarePrefab);
			var squarePrefabAsset = AssetDatabase.LoadAssetAtPath<Button>("Assets/SquareButton.prefab");

			var boardViewGo = new GameObject("BoardView", typeof(BoardView));
			boardViewGo.transform.SetParent(boardGo.transform, false);
			var boardView = boardViewGo.GetComponent<BoardView>();
			boardView.GetType().GetField("gameManager", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(boardView, gm);
			boardView.GetType().GetField("grid", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(boardView, grid);
			boardView.GetType().GetField("squarePrefab", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(boardView, squarePrefabAsset);

			var hudGo = new GameObject("HUD", typeof(HUD));
			hudGo.transform.SetParent(canvasGo.transform, false);
			var undoBtn = CreateButton(canvasGo.transform, new Vector2(150, 60), new Vector2(150, -80), "Undo");
			var newBtn = CreateButton(canvasGo.transform, new Vector2(150, 60), new Vector2(320, -80), "New Game");
			var balanceText = CreateText(canvasGo.transform, new Vector2(300, 80), new Vector2(-160, -80), "$ 0", TextAnchor.MiddleRight);

			var hud = hudGo.GetComponent<HUD>();
			hud.GetType().GetField("gameManager", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(hud, gm);
			hud.GetType().GetField("undoButton", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(hud, undoBtn);
			hud.GetType().GetField("newGameButton", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(hud, newBtn);
			hud.GetType().GetField("balanceText", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(hud, balanceText);

			Selection.activeGameObject = root;
		}

		private static Button CreateButton(Transform parent, Vector2 size, Vector2 anchoredPos, string label)
		{
			var go = new GameObject("Button", typeof(RectTransform), typeof(Image), typeof(Button));
			go.transform.SetParent(parent, false);
			var rt = go.GetComponent<RectTransform>();
			rt.anchorMin = new Vector2(0, 1);
			rt.anchorMax = new Vector2(0, 1);
			rt.sizeDelta = size;
			rt.anchoredPosition = anchoredPos;
			var txt = CreateText(go.transform, size - new Vector2(10, 10), Vector2.zero, label, TextAnchor.MiddleCenter);
			return go.GetComponent<Button>();
		}

		private static Text CreateText(Transform parent, Vector2 size, Vector2 anchoredPos, string content, TextAnchor anchor)
		{
			var go = new GameObject("Text", typeof(RectTransform), typeof(Text));
			go.transform.SetParent(parent, false);
			var rt = go.GetComponent<RectTransform>();
			rt.anchorMin = new Vector2(1, 1);
			rt.anchorMax = new Vector2(1, 1);
			rt.sizeDelta = size;
			rt.anchoredPosition = anchoredPos;
			var text = go.GetComponent<Text>();
			text.text = content;
			text.alignment = anchor;
			text.fontSize = 28;
			text.color = Color.white;
			text.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
			return text;
		}
	}
}
#endif