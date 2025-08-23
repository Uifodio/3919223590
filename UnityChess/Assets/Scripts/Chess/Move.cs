using System;

namespace Chess
{
	[Flags]
	public enum MoveFlag
	{
		None = 0,
		Capture = 1 << 0,
		EnPassant = 1 << 1,
		CastleKingSide = 1 << 2,
		CastleQueenSide = 1 << 3,
		Promotion = 1 << 4,
		DoublePawnPush = 1 << 5
	}

	[Serializable]
	public struct Move
	{
		public int FromSquare; // 0..63
		public int ToSquare;   // 0..63
		public PieceType Promotion; // None or piece type
		public MoveFlag Flags;

		public Move(int from, int to, PieceType promotion = PieceType.None, MoveFlag flags = MoveFlag.None)
		{
			FromSquare = from;
			ToSquare = to;
			Promotion = promotion;
			Flags = flags;
		}

		public override string ToString()
		{
			return $"{SquareToString(FromSquare)}{SquareToString(ToSquare)}" + (Promotion != PieceType.None ? PromotionToChar(Promotion).ToString() : string.Empty);
		}

		public static string SquareToString(int square)
		{
			int file = square % 8;
			int rank = square / 8;
			return $"{(char)('a' + file)}{(char)('1' + rank)}";
		}

		public static char PromotionToChar(PieceType type)
		{
			return type switch
			{
				PieceType.Queen => 'q',
				PieceType.Rook => 'r',
				PieceType.Bishop => 'b',
				PieceType.Knight => 'n',
				_ => ' '
			};
		}
	}
}