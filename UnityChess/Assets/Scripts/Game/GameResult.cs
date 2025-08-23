using System;

namespace Chess
{
	public enum GameEndReason
	{
		None = 0,
		Checkmate = 1,
		Stalemate = 2,
		FiftyMoveRule = 3,
		Repetition = 4,
		InsufficientMaterial = 5
	}

	[Serializable]
	public struct GameResult
	{
		public bool IsGameOver;
		public PlayerColor Winner; // ignored if draw
		public bool IsDraw;
		public GameEndReason Reason;

		public static GameResult Ongoing => new GameResult { IsGameOver = false };
		public static GameResult Mate(PlayerColor winner) => new GameResult { IsGameOver = true, Winner = winner, IsDraw = false, Reason = GameEndReason.Checkmate };
		public static GameResult Draw(GameEndReason reason) => new GameResult { IsGameOver = true, IsDraw = true, Reason = reason };
	}
}