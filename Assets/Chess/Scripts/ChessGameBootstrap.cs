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

		[Header("Gameplay")]
		public bool autoSaveEnabled = true;
		public bool loadAutoSaveOnStart = true;
		public bool highlightLegalMoves = true;
		public bool allowUndo = true;

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
				allowUndo = allowUndo
			});
		}
	}
}