using System;
using System.Globalization;
using System.Text;

namespace Chess.Engine
{
	public static class FEN
	{
		public static void LoadFromFen(Board board, string fen)
		{
			var parts = fen.Trim().Split(' ');
			if (parts.Length < 4) throw new ArgumentException("Invalid FEN");

			// Board
			int idx = 0;
			for (int r = 0; r < 8; r++)
			{
				int rank = 7 - r; // FEN ranks 8..1
				int file = 0;
				while (file < 8)
				{
					char c = parts[0][idx++];
					if (c == '/') continue;
					if (char.IsDigit(c))
					{
						int empty = c - '0';
						for (int e = 0; e < empty; e++) board.squares[Move.FromFileRank(file++, rank)] = new Piece(PieceType.None, PieceColor.White);
					}
					else
					{
						bool isWhite = char.IsUpper(c);
						PieceType type = CharToPieceType(char.ToLowerInvariant(c));
						board.squares[Move.FromFileRank(file++, rank)] = new Piece(type, isWhite ? PieceColor.White : PieceColor.Black);
					}
				}
			}

			// Side to move
			board.sideToMove = parts[1] == "w" ? PieceColor.White : PieceColor.Black;

			// Castling
			board.whiteCastleKingSide = parts[2].Contains("K");
			board.whiteCastleQueenSide = parts[2].Contains("Q");
			board.blackCastleKingSide = parts[2].Contains("k");
			board.blackCastleQueenSide = parts[2].Contains("q");

			// En passant
			board.enPassantSquare = parts[3] == "-" ? -1 : AlgebraicToSquare(parts[3]);

			// Halfmove and fullmove
			if (parts.Length > 4) board.halfmoveClock = int.Parse(parts[4], CultureInfo.InvariantCulture); else board.halfmoveClock = 0;
			if (parts.Length > 5) board.fullmoveNumber = int.Parse(parts[5], CultureInfo.InvariantCulture); else board.fullmoveNumber = 1;

			// King squares
			for (int i = 0; i < 64; i++)
			{
				if (board.squares[i].type == PieceType.King)
				{
					if (board.squares[i].color == PieceColor.White) board.whiteKingSquare = i; else board.blackKingSquare = i;
				}
			}
		}

		public static string ToFen(Board board)
		{
			var sb = new StringBuilder();
			for (int rank = 7; rank >= 0; rank--)
			{
				int empty = 0;
				for (int file = 0; file < 8; file++)
				{
					var p = board.squares[Move.FromFileRank(file, rank)];
					if (p.IsEmpty)
					{
						empty++;
					}
					else
					{
						if (empty > 0) { sb.Append(empty); empty = 0; }
						sb.Append(PieceToChar(p));
					}
				}
				if (empty > 0) sb.Append(empty);
				if (rank > 0) sb.Append('/');
			}
			sb.Append(' ');
			sb.Append(board.sideToMove == PieceColor.White ? 'w' : 'b');
			sb.Append(' ');
			string castling = string.Empty;
			if (board.whiteCastleKingSide) castling += "K";
			if (board.whiteCastleQueenSide) castling += "Q";
			if (board.blackCastleKingSide) castling += "k";
			if (board.blackCastleQueenSide) castling += "q";
			sb.Append(string.IsNullOrEmpty(castling) ? "-" : castling);
			sb.Append(' ');
			sb.Append(board.enPassantSquare == -1 ? "-" : Move.SquareToString(board.enPassantSquare));
			sb.Append(' ');
			sb.Append(board.halfmoveClock);
			sb.Append(' ');
			sb.Append(board.fullmoveNumber);
			return sb.ToString();
		}

		private static PieceType CharToPieceType(char c)
		{
			return c switch
			{
				'p' => PieceType.Pawn,
				'n' => PieceType.Knight,
				'b' => PieceType.Bishop,
				'r' => PieceType.Rook,
				'q' => PieceType.Queen,
				'k' => PieceType.King,
				_ => PieceType.None
			};
		}

		private static char PieceToChar(Piece p)
		{
			char c = p.type switch
			{
				PieceType.Pawn => 'p',
				PieceType.Knight => 'n',
				PieceType.Bishop => 'b',
				PieceType.Rook => 'r',
				PieceType.Queen => 'q',
				PieceType.King => 'k',
				_ => '1'
			};
			return p.color == PieceColor.White ? char.ToUpperInvariant(c) : c;
		}

		private static int AlgebraicToSquare(string sq)
		{
			int file = sq[0] - 'a';
			int rank = sq[1] - '1';
			return Move.FromFileRank(file, rank);
		}
	}
}