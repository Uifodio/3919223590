using System;

namespace Chess
{
	public enum PlayerColor
	{
		White = 0,
		Black = 1
	}

	public enum PieceType
	{
		None = 0,
		Pawn = 1,
		Knight = 2,
		Bishop = 3,
		Rook = 4,
		Queen = 5,
		King = 6
	}

	[Serializable]
	public struct Piece
	{
		public PieceType Type;
		public PlayerColor Color;

		public bool IsNone => Type == PieceType.None;

		public Piece(PieceType type, PlayerColor color)
		{
			Type = type;
			Color = color;
		}

		public static Piece None => new Piece(PieceType.None, PlayerColor.White);
	}

	public static class PieceUtility
	{
		public static char ToFenChar(Piece piece)
		{
			if (piece.IsNone) return '1';
			char c = piece.Type switch
			{
				PieceType.Pawn => 'p',
				PieceType.Knight => 'n',
				PieceType.Bishop => 'b',
				PieceType.Rook => 'r',
				PieceType.Queen => 'q',
				PieceType.King => 'k',
				_ => '1'
			};
			return piece.Color == PlayerColor.White ? char.ToUpperInvariant(c) : c;
		}

		public static Piece FromFenChar(char c)
		{
			bool isWhite = char.IsUpper(c);
			char lc = char.ToLowerInvariant(c);
			PieceType type = lc switch
			{
				'p' => PieceType.Pawn,
				'n' => PieceType.Knight,
				'b' => PieceType.Bishop,
				'r' => PieceType.Rook,
				'q' => PieceType.Queen,
				'k' => PieceType.King,
				_ => PieceType.None
			};
			if (type == PieceType.None) return Piece.None;
			return new Piece(type, isWhite ? PlayerColor.White : PlayerColor.Black);
		}
	}
}