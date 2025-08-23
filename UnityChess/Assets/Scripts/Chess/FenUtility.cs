using System;
using System.Text;

namespace Chess
{
	public static class FenUtility
	{
		public const string StandardStartPosition = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

		public static void LoadPositionFromFen(Board board, string fen)
		{
			string[] parts = fen.Trim().Split(' ');
			if (parts.Length < 4)
			{
				throw new System.ArgumentException("Invalid FEN");
			}

			// Board
			int sq = 56; // start from a8
			for (int i = 0; i < parts[0].Length; i++)
			{
				char c = parts[0][i];
				if (c == '/')
				{
					sq -= 16; // move to next rank
					continue;
				}
				if (char.IsDigit(c))
				{
					sq += (c - '0');
					continue;
				}
				board.SetPieceAt(sq, PieceUtility.FromFenChar(c));
				sq++;
			}

			board.SideToMove = parts[1] == "w" ? PlayerColor.White : PlayerColor.Black;

			// Castling
			board.Castling = CastlingRights.None;
			if (parts[2].Contains("K")) board.Castling |= CastlingRights.WhiteKingSide;
			if (parts[2].Contains("Q")) board.Castling |= CastlingRights.WhiteQueenSide;
			if (parts[2].Contains("k")) board.Castling |= CastlingRights.BlackKingSide;
			if (parts[2].Contains("q")) board.Castling |= CastlingRights.BlackQueenSide;

			// En passant
			board.EnPassantSquare = parts[3] == "-" ? -1 : AlgebraicToSquare(parts[3]);

			// Optional: halfmove/fullmove
			if (parts.Length >= 6)
			{
				board.HalfmoveClock = int.Parse(parts[4]);
				board.FullmoveNumber = int.Parse(parts[5]);
			}
			else
			{
				board.HalfmoveClock = 0;
				board.FullmoveNumber = 1;
			}
		}

		public static string ToFen(Board board)
		{
			StringBuilder sb = new StringBuilder();
			for (int rank = 7; rank >= 0; rank--)
			{
				int emptyCount = 0;
				for (int file = 0; file < 8; file++)
				{
					int sq = rank * 8 + file;
					Piece p = board.GetPieceAt(sq);
					if (p.IsNone)
					{
						emptyCount++;
					}
					else
					{
						if (emptyCount > 0)
						{
							sb.Append(emptyCount);
							emptyCount = 0;
						}
						sb.Append(PieceUtility.ToFenChar(p));
					}
				}
				if (emptyCount > 0) sb.Append(emptyCount);
				if (rank > 0) sb.Append('/');
			}

			sb.Append(' ');
			sb.Append(board.SideToMove == PlayerColor.White ? 'w' : 'b');
			sb.Append(' ');

			string castling = "";
			if ((board.Castling & CastlingRights.WhiteKingSide) != 0) castling += "K";
			if ((board.Castling & CastlingRights.WhiteQueenSide) != 0) castling += "Q";
			if ((board.Castling & CastlingRights.BlackKingSide) != 0) castling += "k";
			if ((board.Castling & CastlingRights.BlackQueenSide) != 0) castling += "q";
			sb.Append(string.IsNullOrEmpty(castling) ? "-" : castling);
			sb.Append(' ');

			sb.Append(board.EnPassantSquare >= 0 ? SquareToAlgebraic(board.EnPassantSquare) : "-");
			sb.Append(' ');
			sb.Append(board.HalfmoveClock);
			sb.Append(' ');
			sb.Append(board.FullmoveNumber);

			return sb.ToString();
		}

		public static string ToFenKey(Board board)
		{
			string fen = ToFen(board);
			var parts = fen.Split(' ');
			if (parts.Length < 4) return fen;
			return string.Concat(parts[0], " ", parts[1], " ", parts[2], " ", parts[3]);
		}

		public static int AlgebraicToSquare(string coord)
		{
			int file = coord[0] - 'a';
			int rank = coord[1] - '1';
			return rank * 8 + file;
		}

		public static string SquareToAlgebraic(int square)
		{
			int file = square % 8;
			int rank = square / 8;
			return $"{(char)('a' + file)}{(char)('1' + rank)}";
		}
	}
}