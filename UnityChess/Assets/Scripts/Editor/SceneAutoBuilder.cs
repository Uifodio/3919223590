#if UNITY_EDITOR
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;

namespace Chess.Editor
{
	public static class SceneAutoBuilder
	{
		[MenuItem("Tools/Chess/Create Sample Scene", priority = 0)]
		public static void CreateScene()
		{
			var newScene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);

			var root = new GameObject("GameRoot");
			var gm = root.AddComponent<GameManager>();

			var es = Object.FindObjectOfType<EventSystem>();
			if (es == null)
			{
				new GameObject("EventSystem", typeof(EventSystem), typeof(StandaloneInputModule));
			}

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
			boardRect.anchoredPosition = new Vector2(0, 100);

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

			// Assign piece sprites if available (Cburnett SVGs)
			var ps = new Sprite[12];
			ps[0] = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Chess/Pieces/white_pawn.svg");
			ps[1] = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Chess/Pieces/white_knight.svg");
			ps[2] = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Chess/Pieces/white_bishop.svg");
			ps[3] = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Chess/Pieces/white_rook.svg");
			ps[4] = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Chess/Pieces/white_queen.svg");
			ps[5] = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Chess/Pieces/white_king.svg");
			ps[6] = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Chess/Pieces/black_pawn.svg");
			ps[7] = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Chess/Pieces/black_knight.svg");
			ps[8] = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Chess/Pieces/black_bishop.svg");
			ps[9] = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Chess/Pieces/black_rook.svg");
			ps[10] = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Chess/Pieces/black_queen.svg");
			ps[11] = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Chess/Pieces/black_king.svg");
			bool anySprite = false;
			for (int i = 0; i < ps.Length; i++) if (ps[i] != null) { anySprite = true; break; }
			if (anySprite)
			{
				boardView.GetType().GetField("pieceSprites", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(boardView, ps);
			}

			// Promotion UI panel
			var promoPanel = new GameObject("PromotionPanel", typeof(RectTransform), typeof(Image));
			promoPanel.transform.SetParent(canvasGo.transform, false);
			var promoRect = promoPanel.GetComponent<RectTransform>();
			promoRect.anchorMin = new Vector2(0.5f, 0.5f);
			promoRect.anchorMax = new Vector2(0.5f, 0.5f);
			promoRect.sizeDelta = new Vector2(500, 200);
			promoRect.anchoredPosition = Vector2.zero;
			var promo = promoPanel.AddComponent<PromotionUI>();
			var panelField = typeof(PromotionUI).GetField("panel", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
			panelField.SetValue(promo, promoPanel);
			var q = CreateButton(promoPanel.transform, new Vector2(110, 60), new Vector2(-165, 0), "Queen");
			var r = CreateButton(promoPanel.transform, new Vector2(110, 60), new Vector2(-55, 0), "Rook");
			var b = CreateButton(promoPanel.transform, new Vector2(110, 60), new Vector2(55, 0), "Bishop");
			var n = CreateButton(promoPanel.transform, new Vector2(110, 60), new Vector2(165, 0), "Knight");
			typeof(PromotionUI).GetField("queenButton", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(promo, q);
			typeof(PromotionUI).GetField("rookButton", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(promo, r);
			typeof(PromotionUI).GetField("bishopButton", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(promo, b);
			typeof(PromotionUI).GetField("knightButton", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(promo, n);
			boardView.GetType().GetField("promotionUI", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(boardView, promo);

			// HUD
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

			// Settings Panel button
			var settingsBtn = CreateButton(canvasGo.transform, new Vector2(150, 60), new Vector2(490, -80), "Settings");
			var settingsGo = new GameObject("SettingsPanel", typeof(SettingsPanel));
			settingsGo.transform.SetParent(canvasGo.transform, false);
			var sp = settingsGo.GetComponent<SettingsPanel>();
			var spPanel = new GameObject("Panel", typeof(RectTransform), typeof(Image));
			spPanel.transform.SetParent(settingsGo.transform, false);
			var spRect = spPanel.GetComponent<RectTransform>();
			spRect.anchorMin = new Vector2(0.5f, 0.5f);
			spRect.anchorMax = new Vector2(0.5f, 0.5f);
			spRect.sizeDelta = new Vector2(600, 300);
			spRect.anchoredPosition = Vector2.zero;
		
typeof(SettingsPanel).GetField("gameManager", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(sp, gm);
		
typeof(SettingsPanel).GetField("panel", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(sp, spPanel);
			var whiteToggle = CreateToggle(spPanel.transform, new Vector2(-180, 60), "Human White");
			var blackToggle = CreateToggle(spPanel.transform, new Vector2(-180, 20), "Human Black");
			typeof(SettingsPanel).GetField("humanWhiteToggle", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(sp, whiteToggle);
			typeof(SettingsPanel).GetField("humanBlackToggle", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(sp, blackToggle);
			var depthLabel = CreateText(spPanel.transform, new Vector2(200, 40), new Vector2(-180, -20), "AI Depth: 3", TextAnchor.MiddleLeft);
			typeof(SettingsPanel).GetField("aiDepthLabel", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(sp, depthLabel);
			var depthSlider = CreateSlider(spPanel.transform, new Vector2(300, 20), new Vector2(0, -20));
			typeof(SettingsPanel).GetField("aiDepthSlider", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(sp, depthSlider);
			var closeBtn = CreateButton(spPanel.transform, new Vector2(120, 50), new Vector2(200, -100), "Close");
			typeof(SettingsPanel).GetField("closeButton", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(sp, closeBtn);
			settingsBtn.onClick.AddListener(() => sp.Show());

			// Move List
			var moveListGo = new GameObject("MoveList", typeof(MoveListUI));
			moveListGo.transform.SetParent(canvasGo.transform, false);
			var moveText = CreateText(moveListGo.transform, new Vector2(900, 100), new Vector2(0, -980), "", TextAnchor.MiddleCenter);
			var ml = moveListGo.GetComponent<MoveListUI>();
			typeof(MoveListUI).GetField("movesText", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(ml, moveText);
			gm.GetType().GetField("moveList", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(gm, ml);

			EditorSceneManager.MarkAllScenesDirty();
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
			rt.anchorMin = new Vector2(0.5f, 0.5f);
			rt.anchorMax = new Vector2(0.5f, 0.5f);
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

		private static Toggle CreateToggle(Transform parent, Vector2 anchoredPos, string label)
		{
			var go = new GameObject("Toggle", typeof(RectTransform), typeof(Toggle));
			go.transform.SetParent(parent, false);
			var rt = go.GetComponent<RectTransform>();
			rt.anchorMin = new Vector2(0.5f, 0.5f);
			rt.anchorMax = new Vector2(0.5f, 0.5f);
			rt.sizeDelta = new Vector2(200, 30);
			rt.anchoredPosition = anchoredPos;
			var bg = new GameObject("Background", typeof(RectTransform), typeof(Image));
			bg.transform.SetParent(go.transform, false);
			var bgImg = bg.GetComponent<Image>();
			bgImg.color = Color.gray;
			var check = new GameObject("Checkmark", typeof(RectTransform), typeof(Image));
			check.transform.SetParent(bg.transform, false);
			var ckImg = check.GetComponent<Image>();
			ckImg.color = Color.green;
			var lbl = CreateText(go.transform, new Vector2(140, 30), new Vector2(50, 0), label, TextAnchor.MiddleLeft);
			var toggle = go.GetComponent<Toggle>();
			toggle.targetGraphic = bgImg;
			toggle.graphic = ckImg;
			return toggle;
		}

		private static Slider CreateSlider(Transform parent, Vector2 size, Vector2 anchoredPos)
		{
			var go = new GameObject("Slider", typeof(RectTransform), typeof(Slider));
			go.transform.SetParent(parent, false);
			var rt = go.GetComponent<RectTransform>();
			rt.anchorMin = new Vector2(0.5f, 0.5f);
			rt.anchorMax = new Vector2(0.5f, 0.5f);
			rt.sizeDelta = size;
			rt.anchoredPosition = anchoredPos;
			var bg = new GameObject("Background", typeof(RectTransform), typeof(Image));
			bg.transform.SetParent(go.transform, false);
			var fillArea = new GameObject("Fill Area", typeof(RectTransform));
			fillArea.transform.SetParent(go.transform, false);
			var fill = new GameObject("Fill", typeof(RectTransform), typeof(Image));
			fill.transform.SetParent(fillArea.transform, false);
			var handle = new GameObject("Handle", typeof(RectTransform), typeof(Image));
			handle.transform.SetParent(go.transform, false);
			var slider = go.GetComponent<Slider>();
			slider.fillRect = fill.GetComponent<RectTransform>();
			slider.handleRect = handle.GetComponent<RectTransform>();
			return slider;
		}
	}
}
#endif