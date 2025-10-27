using System;
using System.IO;
using UnityEngine;
using Chess.Engine;

namespace Chess.Economy
{
	[Serializable]
	public class EconomyState
	{
		public int playerBalance = 0;
		public int aiBalance = 0;
		public int playerRating = 1200;
		public int aiRating = 1200;
	}

	public class GameEconomy : MonoBehaviour
	{
		[Header("Economy Settings")]
		public int winReward = 100;
		public int lossPenalty = 50;
		public int drawReward = 10;
		public float kFactor = 20f; // ELO update K

		private ChessGameController controller;
		private EconomyState state = new EconomyState();
		private string savePath;

		public int PlayerBalance => state.playerBalance;
		public int AIRating => state.aiRating;
		public int PlayerRating => state.playerRating;

		private void Awake()
		{
			savePath = Path.Combine(Application.persistentDataPath, "economy.json");
			Load();
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
			Save();
		}

		private void HandleGameOver(GameResult result, PieceColor winner)
		{
			bool aiEnabled = controller.AiEnabled;
			PieceColor humanColor = controller.AiPlaysBlack ? PieceColor.White : PieceColor.Black;
			if (!aiEnabled) humanColor = PieceColor.White;

			// Balance
			switch (result)
			{
				case GameResult.WhiteWin:
					if (humanColor == PieceColor.White) state.playerBalance += winReward; else state.playerBalance -= lossPenalty;
					break;
				case GameResult.BlackWin:
					if (humanColor == PieceColor.Black) state.playerBalance += winReward; else state.playerBalance -= lossPenalty;
					break;
				default:
					state.playerBalance += drawReward;
					break;
			}

			// ELO ratings
			float scorePlayer = (result == GameResult.WhiteWin && humanColor == PieceColor.White) || (result == GameResult.BlackWin && humanColor == PieceColor.Black) ? 1f : (result == GameResult.Stalemate || result == GameResult.Draw50Move ? 0.5f : 0f);
			UpdateRatings(scorePlayer);
			Save();
		}

		private void UpdateRatings(float scorePlayer)
		{
			float rp = state.playerRating;
			float ra = state.aiRating;
			float expectedP = 1f / (1f + Mathf.Pow(10f, (ra - rp) / 400f));
			float expectedA = 1f - expectedP;
			state.playerRating = Mathf.RoundToInt(rp + kFactor * (scorePlayer - expectedP));
			state.aiRating = Mathf.RoundToInt(ra + kFactor * ((1f - scorePlayer) - expectedA));
		}

		private void Load()
		{
			try
			{
				if (File.Exists(savePath))
				{
					var json = File.ReadAllText(savePath);
					state = JsonUtility.FromJson<EconomyState>(json);
				}
			}
			catch { state = new EconomyState(); }
		}

		private void Save()
		{
			try
			{
				var json = JsonUtility.ToJson(state);
				File.WriteAllText(savePath, json);
			}
			catch { }
		}
	}
}