using UnityEngine;

namespace Chess
{
	public class ChessGameBootstrap : MonoBehaviour
	{
		[Header("AI Settings")]
		public bool aiEnabled = true;
		public bool aiPlaysBlack = true;
		[Range(1, 6)] public int aiSearchDepth = 3;
		public int aiTimeBudgetMs = 0; // 0 = no time budget
		public Chess.AI.AIStyle aiStyle = Chess.AI.AIStyle.Balanced;

		[Header("Gameplay")]
		public bool autoSaveEnabled = true;
		public bool loadAutoSaveOnStart = true;
		public bool highlightLegalMoves = true;
		public bool allowUndo = true;
		[TextArea] public string startingFEN = "";

		[Header("Layout")]
		public bool flipBoard = false;
		public int boardWidthPx = 1080;
		public int cellSizePx = 128;
		public float spacingPx = 2f;

		private ChessGameController controller;

		private void Awake()
		{
			controller = gameObject.AddComponent<ChessGameController>();
			controller.Configure(new ChessGameController.Config
			{
				aiEnabled = aiEnabled,
				aiPlaysBlack = aiPlaysBlack,
				aiSearchDepth = aiSearchDepth,
				aiTimeBudgetMs = aiTimeBudgetMs,
				autoSaveEnabled = autoSaveEnabled,
				loadAutoSaveOnStart = loadAutoSaveOnStart,
				highlightLegalMoves = highlightLegalMoves,
				allowUndo = allowUndo,
				aiStyle = aiStyle,
				startingFEN = startingFEN,
				flipBoard = flipBoard,
				boardWidthPx = boardWidthPx,
				cellSizePx = cellSizePx,
				spacingPx = spacingPx
			});
			if (GetComponent<Economy.GameEconomy>() == null)
			{
				gameObject.AddComponent<Economy.GameEconomy>();
			}
		}
	}
}