using System;
using UnityEngine;
using Chess.Engine;

namespace Chess.Economy
{
	public class GameEconomy : MonoBehaviour
	{
		[Header("Economy Settings")]
		public int playerBalance = 0;
		public int aiBalance = 0;
		public int winReward = 100;
		public int lossPenalty = 50;
		public int drawReward = 10;

		private ChessGameController controller;

		private void Awake()
		{
			controller = GetComponent<ChessGameController>();
			if (controller != null)
			{
				controller.OnGameOver += HandleGameOver;
			}
		}

		private void OnDestroy()
		{
			if (controller != null)
			{
				controller.OnGameOver -= HandleGameOver;
			}
		}

		private void HandleGameOver(GameResult result, PieceColor winner)
		{
			bool aiEnabled = controller.AiEnabled;
			PieceColor humanColor = controller.AiPlaysBlack ? PieceColor.White : PieceColor.Black;
			if (!aiEnabled)
			{
				// If AI is disabled, treat White as player for rewards
				humanColor = PieceColor.White;
			}
			switch (result)
			{
				case GameResult.WhiteWin:
					if (humanColor == PieceColor.White) { playerBalance += winReward; aiBalance -= lossPenalty; }
					else { playerBalance -= lossPenalty; aiBalance += winReward; }
					break;
				case GameResult.BlackWin:
					if (humanColor == PieceColor.Black) { playerBalance += winReward; aiBalance -= lossPenalty; }
					else { playerBalance -= lossPenalty; aiBalance += winReward; }
					break;
				case GameResult.Stalemate:
				case GameResult.Draw50Move:
					playerBalance += drawReward;
					aiBalance += drawReward;
					break;
			}
		}
	}
}