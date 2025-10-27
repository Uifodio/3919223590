using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using TMPro;
using Chess.Engine;

namespace Chess.UI
{
	public class ChessUI : MonoBehaviour
	{
		private RectTransform root;
		private GridLayoutGroup grid;
		private RectTransform gridRect;
		private Button[] squareButtons = new Button[64];
		private Image[] squareImages = new Image[64];
		private TextMeshProUGUI[] squareLabels = new TextMeshProUGUI[64];
		private Image[] pieceImages = new Image[64];
		private TextMeshProUGUI[] pieceFallbackLabels = new TextMeshProUGUI[64];
		private Image[] highlightImages = new Image[64];
		private RectTransform sidebar;
		private Button undoButton;
		private Button newGameButton;
		private TMP_Dropdown depthDropdown;
		private TextMeshProUGUI turnLabel;
		private TextMeshProUGUI statusLabel;
		private GameObject promotionPanel;
		private Action<PieceType> onPromotionChosen;
		private bool highlightLegal = true;
		private Func<int, bool> isLegalDestCached;
		private Dictionary<string, Sprite> spriteCache = new Dictionary<string, Sprite>();
		private Action<int> onSquareClicked;
		private Action onUndo;
		private Action onNewGame;
		private Action<int> onDepthChanged;
		private Action onOfferDraw;
		private Button drawButton;
		private TextMeshProUGUI economyLabel;
		private ChessUILayout externalLayout;
		private Camera providedCamera;

		public void Initialize(MonoBehaviour host, bool highlightLegalMoves, Action<int> onSquareClicked, Action onUndo, Action onNewGame, Action<int> onDepthChanged, Action onOfferDraw = null, int boardWidth = 1080, int cellSize = 128, float spacing = 2f, bool flip = false, Camera uiCam = null)
		{
			this.onSquareClicked = onSquareClicked;
			this.onUndo = onUndo;
			this.onNewGame = onNewGame;
			this.onDepthChanged = onDepthChanged;
			this.onOfferDraw = onOfferDraw;
			highlightLegal = highlightLegalMoves;
			EnsureEventSystem();
			this.paramBoardWidth = boardWidth;
			this.paramCellSize = cellSize;
			this.paramSpacing = spacing;
			this.paramFlip = flip;
			providedCamera = uiCam;
			externalLayout = FindObjectOfType<ChessUILayout>();
			BuildUI();
		}

		private void EnsureEventSystem()
		{
			if (FindObjectOfType<EventSystem>() == null)
			{
				var es = new GameObject("EventSystem", typeof(EventSystem), typeof(StandaloneInputModule));
			}
		}

		private int paramBoardWidth;
		private int paramCellSize;
		private float paramSpacing;
		private bool paramFlip;

		private void BuildUI()
		{
			Canvas canvas;
			var existingCanvas = FindObjectOfType<Canvas>();
			GameObject canvasGo;
			if (existingCanvas == null)
			{
				canvasGo = new GameObject("Canvas", typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
				canvas = canvasGo.GetComponent<Canvas>();
				if (providedCamera != null)
				{
					canvas.renderMode = RenderMode.ScreenSpaceCamera;
					canvas.worldCamera = providedCamera;
				}
				else
				{
					canvas.renderMode = RenderMode.ScreenSpaceOverlay;
				}
				var scaler = canvasGo.GetComponent<CanvasScaler>();
				scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
				scaler.referenceResolution = new Vector2(1920, 1080);
			}
			else
			{
				canvas = existingCanvas;
				canvasGo = existingCanvas.gameObject;
			}
			root = new GameObject("Root", typeof(RectTransform)).GetComponent<RectTransform>();
			root.SetParent(canvasGo.transform, false);
			root.anchorMin = Vector2.zero; root.anchorMax = Vector2.one; root.offsetMin = Vector2.zero; root.offsetMax = Vector2.zero;

			// Board background
			if (externalLayout?.boardRoot == null)
			{
				var boardBgGo = new GameObject("BoardBackground", typeof(RectTransform), typeof(Image));
				var boardBgRect = boardBgGo.GetComponent<RectTransform>();
				boardBgRect.SetParent(root, false);
				boardBgRect.anchorMin = new Vector2(0, 0);
				boardBgRect.anchorMax = new Vector2(0, 1);
				boardBgRect.pivot = new Vector2(0, 0.5f);
				boardBgRect.sizeDelta = new Vector2(paramBoardWidth > 0 ? paramBoardWidth : 1080, 0);
				boardBgRect.anchoredPosition = new Vector2(0, 0);
				var boardBgImg = boardBgGo.GetComponent<Image>();
				var boardSprite = Resources.Load<Sprite>("Board/Board_wood");
				if (boardSprite != null)
				{
					boardBgImg.sprite = boardSprite;
					boardBgImg.type = Image.Type.Sliced;
					boardBgImg.color = Color.white;
				}
				else
				{
					boardBgImg.color = new Color(0.1f, 0.1f, 0.1f, 1f);
				}
			}

			// Board area on top of background
			var boardHolder = new GameObject("Board", typeof(RectTransform), typeof(GridLayoutGroup), typeof(Image));
			gridRect = boardHolder.GetComponent<RectTransform>();
			gridRect.SetParent(externalLayout?.boardRoot != null ? externalLayout.boardRoot : root, false);
			if (externalLayout?.boardRoot == null)
			{
				gridRect.anchorMin = new Vector2(0, 0);
				gridRect.anchorMax = new Vector2(0, 1);
				gridRect.pivot = new Vector2(0, 0.5f);
				gridRect.sizeDelta = new Vector2(paramBoardWidth > 0 ? paramBoardWidth : 1080, 0);
				gridRect.anchoredPosition = new Vector2(0, 0);
			}
			grid = boardHolder.GetComponent<GridLayoutGroup>();
			grid.constraint = GridLayoutGroup.Constraint.FixedColumnCount;
			grid.constraintCount = 8;
			grid.cellSize = new Vector2(paramCellSize > 0 ? paramCellSize : 128, paramCellSize > 0 ? paramCellSize : 128);
			grid.spacing = new Vector2(paramSpacing, paramSpacing);
			var boardBg = boardHolder.GetComponent<Image>();
			boardBg.color = new Color(1f, 1f, 1f, 0f);

			// Sidebar
			sidebar = new GameObject("Sidebar", typeof(RectTransform), typeof(VerticalLayoutGroup)).GetComponent<RectTransform>();
			sidebar.SetParent(externalLayout?.sidebarRoot != null ? externalLayout.sidebarRoot : root, false);
			if (externalLayout?.sidebarRoot == null)
			{
				sidebar.anchorMin = new Vector2(0, 0);
				sidebar.anchorMax = new Vector2(1, 1);
				sidebar.offsetMin = new Vector2(paramBoardWidth + 20, 40);
				sidebar.offsetMax = new Vector2(-40, -40);
			}
			var v = sidebar.GetComponent<VerticalLayoutGroup>();
			v.childForceExpandHeight = false; v.childForceExpandWidth = true; v.spacing = 16;

			// Controls (attach to external slots if provided)
			turnLabel = CreateLabel(externalLayout?.turnLabelRoot ?? sidebar, "Turn: White", 36, FontStyles.Bold);
			statusLabel = CreateLabel(externalLayout?.statusLabelRoot ?? sidebar, "Status: Playing", 28, FontStyles.Normal);
			undoButton = CreateButton(externalLayout?.undoButtonRoot ?? sidebar, "Undo", () => onUndo?.Invoke());
			newGameButton = CreateButton(externalLayout?.newGameButtonRoot ?? sidebar, "New Game", () => onNewGame?.Invoke());
			depthDropdown = CreateDropdown(externalLayout?.depthDropdownRoot ?? sidebar, new[] { "Depth 1", "Depth 2", "Depth 3", "Depth 4", "Depth 5", "Depth 6" }, 2, (i) => onDepthChanged?.Invoke(i + 1));
			drawButton = CreateButton(externalLayout?.drawButtonRoot ?? sidebar, "Offer Draw", () => onOfferDraw?.Invoke());
			economyLabel = CreateLabel(externalLayout?.economyLabelRoot ?? sidebar, "Economy: $0 | Player ELO 1200 vs AI 1200", 24, FontStyles.Italic);

			// Create 64 squares
			for (int i = 0; i < 64; i++)
			{
				var cell = new GameObject($"Cell_{i}", typeof(RectTransform), typeof(Image), typeof(Button));
				cell.transform.SetParent(gridRect, false);
				var img = cell.GetComponent<Image>();
				squareImages[i] = img;
				img.color = ((i + (i / 8)) % 2 == 0) ? new Color(0.86f, 0.86f, 0.74f) : new Color(0.52f, 0.58f, 0.3f);
				var btn = cell.GetComponent<Button>();
				squareButtons[i] = btn;
				int dispIdx = i;
				btn.onClick.AddListener(() => onSquareClicked?.Invoke(DisplayToBoardIndex(dispIdx)));

				var pieceGo = new GameObject("Piece", typeof(RectTransform), typeof(Image));
				pieceGo.transform.SetParent(cell.transform, false);
				var pimg = pieceGo.GetComponent<Image>();
				pimg.raycastTarget = false;
				pieceImages[i] = pimg;

				var fallbackTextGo = new GameObject("PieceText", typeof(RectTransform), typeof(TextMeshProUGUI));
				fallbackTextGo.transform.SetParent(cell.transform, false);
				var label = fallbackTextGo.GetComponent<TextMeshProUGUI>();
							label.alignment = TextAlignmentOptions.Center;
			label.fontSize = 72;
			label.raycastTarget = false;
			label.color = new Color(0,0,0,0.85f);
			pieceFallbackLabels[i] = label;

				var highlightGo = new GameObject("Highlight", typeof(RectTransform), typeof(Image));
				highlightGo.transform.SetParent(cell.transform, false);
				var h = highlightGo.GetComponent<Image>();
				h.raycastTarget = false;
				h.color = new Color(0, 0.8f, 0, 0f);
				highlightImages[i] = h;
			}
		}

		private TextMeshProUGUI CreateLabel(RectTransform parent, string text, int size, FontStyles style)
		{
			var go = new GameObject("Label", typeof(RectTransform), typeof(TextMeshProUGUI));
			go.transform.SetParent(parent, false);
			var l = go.GetComponent<TextMeshProUGUI>();
			l.text = text;
			l.fontSize = size;
			l.fontStyle = style;
			return l;
		}

		private Button CreateButton(RectTransform parent, string text, Action onClick)
		{
			var go = new GameObject(text + "Button", typeof(RectTransform), typeof(Image), typeof(Button));
			go.transform.SetParent(parent, false);
			var img = go.GetComponent<Image>(); img.color = new Color(0.2f,0.2f,0.2f,1);
			var btn = go.GetComponent<Button>();
			btn.onClick.AddListener(() => onClick?.Invoke());
			var lbl = new GameObject("Text", typeof(RectTransform), typeof(TextMeshProUGUI));
			lbl.transform.SetParent(go.transform, false);
			var t = lbl.GetComponent<TextMeshProUGUI>(); t.text = text; t.alignment = TextAlignmentOptions.Center; t.fontSize = 28;
			return btn;
		}

		private TMP_Dropdown CreateDropdown(RectTransform parent, IEnumerable<string> options, int defaultIndex, Action<int> onChanged)
		{
			var go = new GameObject("Dropdown", typeof(RectTransform), typeof(TMP_Dropdown));
			go.transform.SetParent(parent, false);
			var dd = go.GetComponent<TMP_Dropdown>();
			dd.options = new List<TMP_Dropdown.OptionData>();
			foreach (var opt in options) dd.options.Add(new TMP_Dropdown.OptionData(opt));
			dd.value = defaultIndex;
			dd.onValueChanged.AddListener(i => onChanged?.Invoke(i));
			return dd;
		}

		public void RenderBoard(Board board)
		{
			for (int i = 0; i < 64; i++)
			{
				int idx = paramFlip ? (63 - i) : i;
				var p = board.squares[idx];
				RenderPiece(i, p);
			}
		}

		private void RenderPiece(int square, Piece p)
		{
			var img = pieceImages[square];
			var text = pieceFallbackLabels[square];
			Sprite sprite = null;
			if (!p.IsEmpty)
			{
				string key = GetSpriteKey(p);
				if (!spriteCache.TryGetValue(key, out sprite))
				{
					sprite = Resources.Load<Sprite>("CBurnett/" + key);
					if (sprite == null) sprite = Resources.Load<Sprite>("CBurnett/" + key.Replace(".png", ""));
					if (sprite != null) spriteCache[key] = sprite;
				}
			}
			img.sprite = sprite;
			img.enabled = sprite != null;
			text.text = SpriteFallbackText(p);
			text.enabled = sprite == null && !p.IsEmpty;
		}

		private int DisplayToBoardIndex(int displayIndex)
		{
			return paramFlip ? (63 - displayIndex) : displayIndex;
		}

		private int BoardToDisplayIndex(int boardIndex)
		{
			return paramFlip ? (63 - boardIndex) : boardIndex;
		}

		public void ShowLegalMoves(int selectedSquare, List<Move> legalMoves)
		{
			for (int i = 0; i < 64; i++)
			{
				var baseColor = ((i + (i / 8)) % 2 == 0) ? new Color(0.86f, 0.86f, 0.74f) : new Color(0.52f, 0.58f, 0.3f);
				squareImages[i].color = baseColor;
				highlightImages[i].color = new Color(0, 0.8f, 0, 0f);
			}
			if (!highlightLegal) return;
			if (selectedSquare < 0) return;
			foreach (var m in legalMoves)
			{
				if (m.from != selectedSquare) continue;
				int dispTo = BoardToDisplayIndex(m.to);
				var c = m.IsCapture ? new Color(0.9f, 0, 0, 0.35f) : new Color(0, 0.8f, 0, 0.35f);
				highlightImages[dispTo].color = c;
			}
			// highlight selected
			if (selectedSquare >= 0)
				highlightImages[BoardToDisplayIndex(selectedSquare)].color = new Color(0.9f, 0.85f, 0.2f, 0.4f);
		}

		public void SetTurn(PieceColor color)
		{
			turnLabel.text = "Turn: " + (color == PieceColor.White ? "White" : "Black");
		}

		public void SetCanUndo(bool canUndo)
		{
			undoButton.interactable = canUndo;
		}

		public void SetGameOver(GameResult result, PieceColor winner)
		{
			if (result == GameResult.InProgress) { statusLabel.text = "Status: Playing"; return; }
			switch (result)
			{
				case GameResult.WhiteWin: statusLabel.text = "Status: Checkmate — White wins"; break;
				case GameResult.BlackWin: statusLabel.text = "Status: Checkmate — Black wins"; break;
				case GameResult.Stalemate: statusLabel.text = "Status: Stalemate"; break;
				case GameResult.Draw50Move: statusLabel.text = "Status: Draw — 50-move rule"; break;
			}
		}

		public void ShowThinking(bool thinking)
		{
			statusLabel.text = thinking ? "Status: AI thinking..." : "Status: Playing";
		}

		public void ShowPromotionDialog(PieceColor color, Action<PieceType> onChosen)
		{
			onPromotionChosen = onChosen;
			if (promotionPanel != null) Destroy(promotionPanel);
			promotionPanel = new GameObject("PromotionDialog", typeof(RectTransform), typeof(Image));
			promotionPanel.transform.SetParent(root, false);
			var r = promotionPanel.GetComponent<RectTransform>();
			r.sizeDelta = new Vector2(360, 120);
			r.anchoredPosition = Vector2.zero;
			promotionPanel.GetComponent<Image>().color = new Color(0,0,0,0.8f);
			var row = new GameObject("Row", typeof(RectTransform), typeof(HorizontalLayoutGroup));
			row.transform.SetParent(promotionPanel.transform, false);
			var hl = row.GetComponent<HorizontalLayoutGroup>(); hl.childForceExpandWidth = true; hl.spacing = 8; hl.padding.left = 8; hl.padding.right = 8;
			void AddChoice(string label, PieceType t)
			{
				var btn = CreateButton(row.GetComponent<RectTransform>(), label, () => { onPromotionChosen?.Invoke(t); Destroy(promotionPanel); promotionPanel = null; });
			}
			AddChoice("Queen", PieceType.Queen);
			AddChoice("Rook", PieceType.Rook);
			AddChoice("Bishop", PieceType.Bishop);
			AddChoice("Knight", PieceType.Knight);
		}

		private string GetSpriteKey(Piece p)
		{
			if (p.IsEmpty) return string.Empty;
			char t = p.type switch
			{
				PieceType.Pawn => 'p',
				PieceType.Knight => 'n',
				PieceType.Bishop => 'b',
				PieceType.Rook => 'r',
				PieceType.Queen => 'q',
				PieceType.King => 'k',
				_ => 'p'
			};
			string side = p.color == PieceColor.White ? "l" : "d"; // light/dark
			return $"Chess_{t}{side}t45.png";
		}

		private string SpriteFallbackText(Piece p)
		{
			if (p.IsEmpty) return string.Empty;
			switch (p.type)
			{
				case PieceType.Pawn: return p.color == PieceColor.White ? "P" : "p";
				case PieceType.Knight: return p.color == PieceColor.White ? "N" : "n";
				case PieceType.Bishop: return p.color == PieceColor.White ? "B" : "b";
				case PieceType.Rook: return p.color == PieceColor.White ? "R" : "r";
				case PieceType.Queen: return p.color == PieceColor.White ? "Q" : "q";
				case PieceType.King: return p.color == PieceColor.White ? "K" : "k";
			}
			return string.Empty;
		}

		public void SetDrawEnabled(bool enabled)
		{
			if (drawButton != null) drawButton.interactable = enabled;
		}

		public void AnimateMove(int from, int to, float duration = 0.15f)
		{
			StartCoroutine(AnimatePieceCoroutine(from, to, duration));
		}

		private System.Collections.IEnumerator AnimatePieceCoroutine(int from, int to, float duration)
		{
			var fromCell = squareImages[from].transform as RectTransform;
			var toCell = squareImages[to].transform as RectTransform;
			var piece = pieceImages[from];
			if (!piece.enabled) yield break;
			var overlay = new GameObject("MovingPiece", typeof(RectTransform), typeof(Image));
			overlay.transform.SetParent(gridRect, false);
			var rt = overlay.GetComponent<RectTransform>();
			var img = overlay.GetComponent<Image>();
			img.sprite = piece.sprite;
			rt.sizeDelta = piece.rectTransform.sizeDelta;
			rt.position = fromCell.position;
			piece.enabled = false;
			float t = 0f;
			while (t < 1f)
			{
				t += Time.deltaTime / duration;
				rt.position = Vector3.Lerp(fromCell.position, toCell.position, Mathf.SmoothStep(0, 1, t));
				yield return null;
			}
			destroyAfterFrame = overlay;
			yield return null;
			if (destroyAfterFrame != null) GameObject.Destroy(destroyAfterFrame);
		}
		private GameObject destroyAfterFrame;

		public void UpdateEconomy(Chess.Economy.GameEconomy econ)
		{
			if (econ == null || economyLabel == null) return;
			economyLabel.text = $"Economy: ${econ.PlayerBalance} | Player ELO {econ.PlayerRating} vs AI {econ.AIRating}";
		}
	}
}