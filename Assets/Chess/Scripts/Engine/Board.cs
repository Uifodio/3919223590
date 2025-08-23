using System;
using System.Collections.Generic;

namespace Chess.Engine
{
	public class Board
	{
		public Piece[] squares = new Piece[64];
		public PieceColor sideToMove = PieceColor.White;
		public bool whiteCastleKingSide = true;
		public bool whiteCastleQueenSide = true;
		public bool blackCastleKingSide = true;
		public bool blackCastleQueenSide = true;
		public int enPassantSquare = -1; // target square behind pawn that moved two
		public int halfmoveClock = 0;
		public int fullmoveNumber = 1;

		public int whiteKingSquare = 60; // e1
		public int blackKingSquare = 4;  // e8

		public struct UndoState
		{
			public Piece captured;
			public bool wK, wQ, bK, bQ;
			public int ep;
			public int half;
			public int full;
			public int whiteKingSquare;
			public int blackKingSquare;
		}

		private readonly Stack<UndoState> undoStack = new Stack<UndoState>(128);
		private readonly Stack<Move> moveStack = new Stack<Move>(128);
		private readonly Dictionary<ulong, int> repetitionTable = new Dictionary<ulong, int>();
		private readonly Stack<ulong> positionHistory = new Stack<ulong>(256);

		public IEnumerable<Move> MoveHistory => moveStack;

		public void SetupStartingPosition()
		{
			Array.Fill(squares, new Piece(PieceType.None, PieceColor.White));
			// Black back rank
			squares[0] = new Piece(PieceType.Rook, PieceColor.Black);
			squares[1] = new Piece(PieceType.Knight, PieceColor.Black);
			squares[2] = new Piece(PieceType.Bishop, PieceColor.Black);
			squares[3] = new Piece(PieceType.Queen, PieceColor.Black);
			squares[4] = new Piece(PieceType.King, PieceColor.Black);
			blackKingSquare = 4;
			squares[5] = new Piece(PieceType.Bishop, PieceColor.Black);
			squares[6] = new Piece(PieceType.Knight, PieceColor.Black);
			squares[7] = new Piece(PieceType.Rook, PieceColor.Black);
			for (int i = 8; i < 16; i++) squares[i] = new Piece(PieceType.Pawn, PieceColor.Black);
			// Empty middle
			for (int i = 16; i < 48; i++) squares[i] = new Piece(PieceType.None, PieceColor.White);
			// White pawns
			for (int i = 48; i < 56; i++) squares[i] = new Piece(PieceType.Pawn, PieceColor.White);
			// White back rank
			squares[56] = new Piece(PieceType.Rook, PieceColor.White);
			squares[57] = new Piece(PieceType.Knight, PieceColor.White);
			squares[58] = new Piece(PieceType.Bishop, PieceColor.White);
			squares[59] = new Piece(PieceType.Queen, PieceColor.White);
			squares[60] = new Piece(PieceType.King, PieceColor.White);
			whiteKingSquare = 60;
			squares[61] = new Piece(PieceType.Bishop, PieceColor.White);
			squares[62] = new Piece(PieceType.Knight, PieceColor.White);
			squares[63] = new Piece(PieceType.Rook, PieceColor.White);

			sideToMove = PieceColor.White;
			whiteCastleKingSide = whiteCastleQueenSide = blackCastleKingSide = blackCastleQueenSide = true;
			enPassantSquare = -1;
			halfmoveClock = 0;
			fullmoveNumber = 1;
			undoStack.Clear();
			moveStack.Clear();
			repetitionTable.Clear();
			positionHistory.Clear();
			IncrementRepetition();
		}

		public Board Clone()
		{
			var b = new Board();
			Array.Copy(squares, b.squares, 64);
			b.sideToMove = sideToMove;
			b.whiteCastleKingSide = whiteCastleKingSide;
			b.whiteCastleQueenSide = whiteCastleQueenSide;
			b.blackCastleKingSide = blackCastleKingSide;
			b.blackCastleQueenSide = blackCastleQueenSide;
			b.enPassantSquare = enPassantSquare;
			b.halfmoveClock = halfmoveClock;
			b.fullmoveNumber = fullmoveNumber;
			b.whiteKingSquare = whiteKingSquare;
			b.blackKingSquare = blackKingSquare;
			return b;
		}

		public bool IsSquareAttackedByColor(int square, PieceColor attacker)
		{
			// Pawns
			int rank = Move.RankOf(square);
			int file = Move.FileOf(square);
			if (attacker == PieceColor.White)
			{
				if (rank > 0)
				{
					int s1 = Move.FromFileRank(file - 1, rank - 1);
					int s2 = Move.FromFileRank(file + 1, rank - 1);
					if (file > 0 && squares[s1].type == PieceType.Pawn && squares[s1].color == PieceColor.White) return true;
					if (file < 7 && squares[s2].type == PieceType.Pawn && squares[s2].color == PieceColor.White) return true;
				}
			}
			else
			{
				if (rank < 7)
				{
					int s1 = Move.FromFileRank(file - 1, rank + 1);
					int s2 = Move.FromFileRank(file + 1, rank + 1);
					if (file > 0 && squares[s1].type == PieceType.Pawn && squares[s1].color == PieceColor.Black) return true;
					if (file < 7 && squares[s2].type == PieceType.Pawn && squares[s2].color == PieceColor.Black) return true;
				}
			}
			// Knights
			int[] kdx = { -2,-1,1,2, 2,1,-1,-2 };
			int[] kdy = { 1,2,2,1, -1,-2,-2,-1 };
			for (int i = 0; i < 8; i++)
			{
				int nf = file + kdx[i];
				int nr = rank + kdy[i];
				if (nf < 0 || nf > 7 || nr < 0 || nr > 7) continue;
				int s = Move.FromFileRank(nf, nr);
				if (squares[s].type == PieceType.Knight && squares[s].color == attacker) return true;
			}
			// Sliding: bishops/queens (diagonals)
			int[] dfx = { 1,1,-1,-1 };
			int[] dfy = { 1,-1,1,-1 };
			for (int d = 0; d < 4; d++)
			{
				int nf = file + dfx[d];
				int nr = rank + dfy[d];
				while (nf >= 0 && nf < 8 && nr >= 0 && nr < 8)
				{
					int s = Move.FromFileRank(nf, nr);
					if (!squares[s].IsEmpty)
					{
						if (squares[s].color == attacker && (squares[s].type == PieceType.Bishop || squares[s].type == PieceType.Queen)) return true;
						break;
					}
					nf += dfx[d]; nr += dfy[d];
				}
			}
			// Sliding: rooks/queens (orthogonals)
			int[] ofx = { 1,-1,0,0 };
			int[] ofy = { 0,0,1,-1 };
			for (int d = 0; d < 4; d++)
			{
				int nf = file + ofx[d];
				int nr = rank + ofy[d];
				while (nf >= 0 && nf < 8 && nr >= 0 && nr < 8)
				{
					int s = Move.FromFileRank(nf, nr);
					if (!squares[s].IsEmpty)
					{
						if (squares[s].color == attacker && (squares[s].type == PieceType.Rook || squares[s].type == PieceType.Queen)) return true;
						break;
					}
					nf += ofx[d]; nr += ofy[d];
				}
			}
			// King
			for (int df = -1; df <= 1; df++)
			{
				for (int dr = -1; dr <= 1; dr++)
				{
					if (df == 0 && dr == 0) continue;
					int nf = file + df; int nr = rank + dr;
					if (nf < 0 || nf > 7 || nr < 0 || nr > 7) continue;
					int s = Move.FromFileRank(nf, nr);
					if (squares[s].type == PieceType.King && squares[s].color == attacker) return true;
				}
			}
			return false;
		}

		public bool InCheck(PieceColor color)
		{
			int kingSq = color == PieceColor.White ? whiteKingSquare : blackKingSquare;
			return IsSquareAttackedByColor(kingSq, color == PieceColor.White ? PieceColor.Black : PieceColor.White);
		}

		public void MakeMove(in Move move)
		{
			var state = new UndoState
			{
				captured = squares[move.to],
				wK = whiteCastleKingSide,
				wQ = whiteCastleQueenSide,
				bK = blackCastleKingSide,
				bQ = blackCastleQueenSide,
				ep = enPassantSquare,
				half = halfmoveClock,
				full = fullmoveNumber,
				whiteKingSquare = whiteKingSquare,
				blackKingSquare = blackKingSquare
			};
			undoStack.Push(state);
			moveStack.Push(move);

			Piece moving = squares[move.from];
			// Update halfmove clock
			if (moving.type == PieceType.Pawn || move.IsCapture) halfmoveClock = 0; else halfmoveClock++;

			// Clear en passant by default
			enPassantSquare = -1;

			// Move the piece
			squares[move.to] = moving;
			squares[move.from] = new Piece(PieceType.None, PieceColor.White);

			// Update king square
			if (moving.type == PieceType.King)
			{
				if (moving.color == PieceColor.White) whiteKingSquare = move.to; else blackKingSquare = move.to;
				// Castling: move rook
				if (move.IsCastleKing)
				{
					if (moving.color == PieceColor.White)
					{
						// e1g1, rook h1f1
						squares[Move.FromFileRank(5, 7)] = squares[Move.FromFileRank(7, 7)];
						squares[Move.FromFileRank(7, 7)] = new Piece(PieceType.None, PieceColor.White);
					}
					else
					{
						// e8g8, rook h8f8
						squares[Move.FromFileRank(5, 0)] = squares[Move.FromFileRank(7, 0)];
						squares[Move.FromFileRank(7, 0)] = new Piece(PieceType.None, PieceColor.White);
					}
				}
				else if (move.IsCastleQueen)
				{
					if (moving.color == PieceColor.White)
					{
						// e1c1, rook a1d1
						squares[Move.FromFileRank(3, 7)] = squares[Move.FromFileRank(0, 7)];
						squares[Move.FromFileRank(0, 7)] = new Piece(PieceType.None, PieceColor.White);
					}
					else
					{
						// e8c8, rook a8d8
						squares[Move.FromFileRank(3, 0)] = squares[Move.FromFileRank(0, 0)];
						squares[Move.FromFileRank(0, 0)] = new Piece(PieceType.None, PieceColor.White);
					}
				}
				// Any king move removes castling rights for that side
				if (moving.color == PieceColor.White)
				{
					whiteCastleKingSide = false; whiteCastleQueenSide = false;
				}
				else
				{
					blackCastleKingSide = false; blackCastleQueenSide = false;
				}
			}

			// Handle rook movement or capture affecting castling rights
			if (moving.type == PieceType.Rook)
			{
				if (move.from == Move.FromFileRank(0, 7)) whiteCastleQueenSide = false;
				if (move.from == Move.FromFileRank(7, 7)) whiteCastleKingSide = false;
				if (move.from == Move.FromFileRank(0, 0)) blackCastleQueenSide = false;
				if (move.from == Move.FromFileRank(7, 0)) blackCastleKingSide = false;
			}
			if (move.to == Move.FromFileRank(0, 7)) whiteCastleQueenSide = false;
			if (move.to == Move.FromFileRank(7, 7)) whiteCastleKingSide = false;
			if (move.to == Move.FromFileRank(0, 0)) blackCastleQueenSide = false;
			if (move.to == Move.FromFileRank(7, 0)) blackCastleKingSide = false;

			// En passant capture
			if (move.IsEnPassant)
			{
				int capSq = move.to + ((moving.color == PieceColor.White) ? (1 << 3) : -(1 << 3));
				state.captured = squares[capSq]; // captured pawn is behind target square
				squares[capSq] = new Piece(PieceType.None, PieceColor.White);
			}

			// Double pawn push sets en passant square
			if (moving.type == PieceType.Pawn && move.IsDoublePush)
			{
				int dir = moving.color == PieceColor.White ? -1 : 1; // to behind pawn
				enPassantSquare = move.from + (dir << 3);
			}

			// Promotion
			if (move.IsPromotion)
			{
				squares[move.to] = new Piece(move.promotion, moving.color);
			}

			// Switch side
			sideToMove = sideToMove == PieceColor.White ? PieceColor.Black : PieceColor.White;
			if (sideToMove == PieceColor.White) fullmoveNumber++;

			IncrementRepetition();
		}

		public Move UnmakeMove()
		{
			// Remove current position from repetition before state changes
			DecrementCurrentPosition();
			var move = moveStack.Pop();
			var state = undoStack.Pop();

			Piece moving = squares[move.to];
			// Switch side back first
			sideToMove = sideToMove == PieceColor.White ? PieceColor.Black : PieceColor.White;
			if (sideToMove == PieceColor.Black) fullmoveNumber--;

			// Undo promotion
			if (move.IsPromotion)
			{
				moving = new Piece(PieceType.Pawn, moving.color);
			}

			// Move piece back
			squares[move.from] = moving;
			squares[move.to] = state.captured;

			// Undo en passant capture
			if (move.IsEnPassant)
			{
				int capSq = move.to + ((moving.color == PieceColor.White) ? (1 << 3) : -(1 << 3));
				squares[move.to] = new Piece(PieceType.None, PieceColor.White);
				squares[capSq] = new Piece(PieceType.Pawn, sideToMove == PieceColor.White ? PieceColor.Black : PieceColor.White);
			}

			// Undo rook movement for castling
			if (move.IsCastleKing)
			{
				if (moving.color == PieceColor.White)
				{
					// e1g1 -> rook f1 to h1
					squares[Move.FromFileRank(7, 7)] = squares[Move.FromFileRank(5, 7)];
					squares[Move.FromFileRank(5, 7)] = new Piece(PieceType.None, PieceColor.White);
				}
				else
				{
					// e8g8 -> rook f8 to h8
					squares[Move.FromFileRank(7, 0)] = squares[Move.FromFileRank(5, 0)];
					squares[Move.FromFileRank(5, 0)] = new Piece(PieceType.None, PieceColor.White);
				}
			}
			else if (move.IsCastleQueen)
			{
				if (moving.color == PieceColor.White)
				{
					// e1c1 -> rook d1 to a1
					squares[Move.FromFileRank(0, 7)] = squares[Move.FromFileRank(3, 7)];
					squares[Move.FromFileRank(3, 7)] = new Piece(PieceType.None, PieceColor.White);
				}
				else
				{
					// e8c8 -> rook d8 to a8
					squares[Move.FromFileRank(0, 0)] = squares[Move.FromFileRank(3, 0)];
					squares[Move.FromFileRank(3, 0)] = new Piece(PieceType.None, PieceColor.White);
				}
			}

			// Restore state
			whiteCastleKingSide = state.wK;
			whiteCastleQueenSide = state.wQ;
			blackCastleKingSide = state.bK;
			blackCastleQueenSide = state.bQ;
			enPassantSquare = state.ep;
			halfmoveClock = state.half;
			fullmoveNumber = state.full;
			whiteKingSquare = state.whiteKingSquare;
			blackKingSquare = state.blackKingSquare;

			return move;
		}

		private void IncrementRepetition()
		{
			ulong h = ComputeHash();
			if (!repetitionTable.ContainsKey(h)) repetitionTable[h] = 0;
			repetitionTable[h]++;
			positionHistory.Push(h);
		}

		private void DecrementCurrentPosition()
		{
			ulong h = ComputeHash();
			if (repetitionTable.TryGetValue(h, out var c))
			{
				c--;
				if (c <= 0) repetitionTable.Remove(h); else repetitionTable[h] = c;
			}
			if (positionHistory.Count > 0 && positionHistory.Peek() == h) positionHistory.Pop();
		}

		public bool IsThreefoldRepetition()
		{
			ulong h = ComputeHash();
			return repetitionTable.TryGetValue(h, out var c) && c >= 3;
		}

		public bool IsInsufficientMaterial()
		{
			bool anyPawnsOrQueensOrRooks = false;
			int whiteBishops = 0, whiteKnights = 0, blackBishops = 0, blackKnights = 0;
			for (int i = 0; i < 64; i++)
			{
				var p = squares[i];
				if (p.IsEmpty) continue;
				if (p.type == PieceType.Pawn || p.type == PieceType.Queen || p.type == PieceType.Rook) anyPawnsOrQueensOrRooks = true;
				if (p.type == PieceType.Bishop)
				{
					if (p.color == PieceColor.White) whiteBishops++; else blackBishops++;
				}
				if (p.type == PieceType.Knight)
				{
					if (p.color == PieceColor.White) whiteKnights++; else blackKnights++;
				}
			}
			if (anyPawnsOrQueensOrRooks) return false;
			// King vs King, King+Bishop vs King, King+Knight vs King, King+B vs King+B (same color bishops case ignored for simplicity)
			int totalPieces = whiteBishops + whiteKnights + blackBishops + blackKnights;
			return totalPieces <= 1;
		}

		private ulong ComputeHash()
		{
			// Simple Zobrist-like hash substitute: combine piece, square, side, castling, ep
			unchecked
			{
				ulong h = 1469598103934665603UL; // FNV offset basis
				for (int i = 0; i < 64; i++)
				{
					var p = squares[i];
					ulong v = ((ulong)p.type * 1315423911UL) ^ ((ulong)p.color * 2654435761UL) ^ (ulong)i;
					h ^= v + 0x9e3779b97f4a7c15UL + (h << 6) + (h >> 2);
				}
				h ^= (ulong)(sideToMove == PieceColor.White ? 1 : 2);
				if (whiteCastleKingSide) h ^= 0xA4A4A4A4A4A4A4A4UL;
				if (whiteCastleQueenSide) h ^= 0xB5B5B5B5B5B5B5B5UL;
				if (blackCastleKingSide) h ^= 0xC6C6C6C6C6C6C6C6UL;
				if (blackCastleQueenSide) h ^= 0xD7D7D7D7D7D7D7D7UL;
				h ^= (ulong)(enPassantSquare + 1) * 0x123456789ABCDEFUL;
				return h;
			}
		}
	}
}