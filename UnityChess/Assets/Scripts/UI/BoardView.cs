using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;

namespace Chess
{
	public class BoardView : MonoBehaviour
	{
		[SerializeField] private GameManager gameManager;
		[SerializeField] private GridLayoutGroup grid;
		[SerializeField] private Button squarePrefab;
		[SerializeField] private Sprite whiteSquareSprite;
		[SerializeField] private Sprite blackSquareSprite;
		[SerializeField] private Sprite highlightSprite;
		[SerializeField] private Sprite[] pieceSprites; // 0..11 order: WP, WN, WB, WR, WQ, WK, BP, BN, BB, BR, BQ, BK
		[SerializeField] private PromotionUI promotionUI;

		private Button[] squareButtons = new Button[64];
		private Image[] squareImages = new Image[64];
		private Image[] pieceImages = new Image[64];
		private Text[] pieceLabels = new Text[64];
		private int? selectedSquare;
		private List<int> legalTargets = new List<int>(32);

		private Color lightColor = new Color(0.9f, 0.9f, 0.9f, 1f);
		private Color darkColor = new Color(0.2f, 0.3f, 0.4f, 1f);
		private Color highlightColor = new Color(0.3f, 0.8f, 0.3f, 1f);

		private void Start()
		{
			BuildBoard();
			gameManager.OnBoardChanged += Refresh;
			Refresh();
		}

		private void OnDestroy()
		{
			if (gameManager != null) gameManager.OnBoardChanged -= Refresh;
		}

		private void BuildBoard()
		{
			for (int i = 0; i < 64; i++)
			{
				var btn = Instantiate(squarePrefab, grid.transform);
				int sq = i;
				btn.onClick.AddListener(() => OnSquareClicked(sq));
				squareButtons[i] = btn;
				squareImages[i] = btn.GetComponent<Image>();
				var pieceGo = new GameObject("Piece", typeof(RectTransform), typeof(CanvasRenderer), typeof(Image));
				pieceGo.transform.SetParent(btn.transform, false);
				var img = pieceGo.GetComponent<Image>();
				img.raycastTarget = false;
				pieceImages[i] = img;

				var labelGo = new GameObject("Label", typeof(RectTransform), typeof(CanvasRenderer), typeof(Text));
				labelGo.transform.SetParent(btn.transform, false);
				var lab = labelGo.GetComponent<Text>();
				lab.alignment = TextAnchor.MiddleCenter;
				lab.fontSize = 42;
				lab.color = Color.black;
				lab.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
				pieceLabels[i] = lab;
			}
		}

		private void Refresh()
		{
			for (int i = 0; i < 64; i++)
			{
				bool isLight = ((i / 8) + (i % 8)) % 2 == 0;
				if (whiteSquareSprite != null && blackSquareSprite != null)
				{
					squareImages[i].sprite = isLight ? whiteSquareSprite : blackSquareSprite;
					squareImages[i].color = Color.white;
				}
				else
				{
					squareImages[i].sprite = null;
					squareImages[i].color = isLight ? lightColor : darkColor;
				}

				var p = gameManager.Board.GetPieceAt(i);
				Sprite s = GetSpriteForPiece(p);
				if (s != null)
				{
					pieceImages[i].sprite = s;
					pieceImages[i].enabled = true;
					pieceLabels[i].text = string.Empty;
					pieceLabels[i].enabled = false;
				}
				else
				{
					pieceImages[i].sprite = null;
					pieceImages[i].enabled = false;
					pieceLabels[i].text = GetPieceLetter(p);
					pieceLabels[i].enabled = !p.IsNone;
				}
			}
			if (selectedSquare.HasValue)
			{
				foreach (var t in legalTargets)
				{
					if (highlightSprite != null)
					{
						squareImages[t].sprite = highlightSprite;
						squareImages[t].color = Color.white;
					}
					else
					{
						squareImages[t].color = highlightColor;
					}
				}
			}
		}

		private Sprite GetSpriteForPiece(Piece p)
		{
			if (p.IsNone || pieceSprites == null || pieceSprites.Length < 12) return null;
			int idxBase = p.Color == PlayerColor.White ? 0 : 6;
			int offset = p.Type switch
			{
				PieceType.Pawn => 0,
				PieceType.Knight => 1,
				PieceType.Bishop => 2,
				PieceType.Rook => 3,
				PieceType.Queen => 4,
				PieceType.King => 5,
				_ => 0
			};
			return pieceSprites[idxBase + offset];
		}

		private string GetPieceLetter(Piece p)
		{
			if (p.IsNone) return string.Empty;
			char c = p.Type switch
			{
				PieceType.Pawn => 'P',
				PieceType.Knight => 'N',
				PieceType.Bishop => 'B',
				PieceType.Rook => 'R',
				PieceType.Queen => 'Q',
				PieceType.King => 'K',
				_ => ' '
			};
			return p.Color == PlayerColor.White ? c.ToString() : c.ToString().ToLowerInvariant();
		}

		private void OnSquareClicked(int sq)
		{
			var piece = gameManager.Board.GetPieceAt(sq);
			if (!selectedSquare.HasValue)
			{
				// select only if piece is player's to move and it's human's turn
				if (!piece.IsNone && piece.Color == gameManager.Board.SideToMove && gameManager.IsHumanTurn())
				{
					selectedSquare = sq;
					ComputeLegalTargets();
					Refresh();
				}
			}
			else
			{
				int from = selectedSquare.Value;
				int to = sq;
				if (from == to)
				{
					selectedSquare = null;
					legalTargets.Clear();
					Refresh();
					return;
				}
				if (legalTargets.Contains(to))
				{
					// If promotion required, show UI and wait for choice
					bool needsPromotion = false;
					foreach (var m in gameManager.Board.GenerateLegalMoves())
					{
						if (m.FromSquare == from && m.ToSquare == to && (m.Flags & MoveFlag.Promotion) != 0)
						{
							needsPromotion = true;
							break;
						}
					}
					if (needsPromotion && promotionUI != null)
					{
						promotionUI.Show(pt =>
						{
							gameManager.TryMakeHumanMove(from, to, pt);
							selectedSquare = null;
							legalTargets.Clear();
							Refresh();
						});
					}
					else
					{
						gameManager.TryMakeHumanMove(from, to, PieceType.Queen);
						selectedSquare = null;
						legalTargets.Clear();
						Refresh();
					}
				}
				else
				{
					selectedSquare = null;
					legalTargets.Clear();
					Refresh();
				}
			}
		}

		private void ComputeLegalTargets()
		{
			legalTargets.Clear();
			if (!selectedSquare.HasValue) return;
			int from = selectedSquare.Value;
			foreach (var m in gameManager.Board.GenerateLegalMoves())
			{
				if (m.FromSquare == from) legalTargets.Add(m.ToSquare);
			}
		}
	}
}