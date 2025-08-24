using System;

namespace Chess.Engine
{
	public enum PieceColor
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

	[Flags]
	public enum MoveFlags
	{
		None = 0,
		Capture = 1 << 0,
		EnPassant = 1 << 1,
		CastleKingSide = 1 << 2,
		CastleQueenSide = 1 << 3,
		Promotion = 1 << 4,
		DoublePawnPush = 1 << 5
	}

	public struct Piece
	{
		public PieceType type;
		public PieceColor color;

		public bool IsEmpty => type == PieceType.None;

		public Piece(PieceType type, PieceColor color)
		{
			this.type = type;
			this.color = color;
		}

		public override string ToString()
		{
			if (IsEmpty) return ".";
			char c = type switch
			{
				PieceType.Pawn => 'P',
				PieceType.Knight => 'N',
				PieceType.Bishop => 'B',
				PieceType.Rook => 'R',
				PieceType.Queen => 'Q',
				PieceType.King => 'K',
				_ => '?' 
			};
			return color == PieceColor.White ? c.ToString() : char.ToLowerInvariant(c).ToString();
		}
	}

	public struct Move
	{
		public int from;
		public int to;
		public MoveFlags flags;
		public PieceType promotion;

		public Move(int from, int to, MoveFlags flags = MoveFlags.None, PieceType promotion = PieceType.None)
		{
			this.from = from;
			this.to = to;
			this.flags = flags;
			this.promotion = promotion;
		}

		public bool IsCapture => (flags & MoveFlags.Capture) != 0;
		public bool IsEnPassant => (flags & MoveFlags.EnPassant) != 0;
		public bool IsCastleKing => (flags & MoveFlags.CastleKingSide) != 0;
		public bool IsCastleQueen => (flags & MoveFlags.CastleQueenSide) != 0;
		public bool IsPromotion => (flags & MoveFlags.Promotion) != 0;
		public bool IsDoublePush => (flags & MoveFlags.DoublePawnPush) != 0;

		public override string ToString()
		{
			return $"{SquareToString(from)}-{SquareToString(to)}{(IsPromotion ? "=" + promotion : "")}";
		}

		public static int FileOf(int square) => square & 7; // 0..7
		public static int RankOf(int square) => square >> 3; // 0..7

		public static string SquareToString(int square)
		{
			char file = (char)('a' + FileOf(square));
			char rank = (char)('1' + RankOf(square));
			return new string(new[] { file, rank });
		}

		public static int FromFileRank(int file, int rank) => (rank << 3) | file;
	}
}