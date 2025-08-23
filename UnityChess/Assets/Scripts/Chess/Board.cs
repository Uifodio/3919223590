using System;
using System.Collections.Generic;

namespace Chess
{
	[Flags]
	public enum CastlingRights
	{
		None = 0,
		WhiteKingSide = 1 << 0,
		WhiteQueenSide = 1 << 1,
		BlackKingSide = 1 << 2,
		BlackQueenSide = 1 << 3
	}

	[Serializable]
	public struct BoardState
	{
		public int FromSquare;
		public int ToSquare;
		public Piece MovedPiece;
		public Piece CapturedPiece;
		public int CapturedOnSquare;
		public PieceType Promotion;
		public CastlingRights PrevCastling;
		public int PrevEnPassant;
		public int PrevHalfmoveClock;
		public int PrevFullmoveNumber;
		public PlayerColor PrevSideToMove;
	}

	public class Board
	{
		private readonly Piece[] squares = new Piece[64];
		public PlayerColor SideToMove { get; set; } = PlayerColor.White;
		public CastlingRights Castling { get; set; } = CastlingRights.WhiteKingSide | CastlingRights.WhiteQueenSide | CastlingRights.BlackKingSide | CastlingRights.BlackQueenSide;
		public int EnPassantSquare { get; set; } = -1; // -1 if none
		public int HalfmoveClock { get; set; } = 0;
		public int FullmoveNumber { get; set; } = 1;

		private readonly Stack<BoardState> undoStack = new Stack<BoardState>(128);

		public void Clear()
		{
			for (int i = 0; i < 64; i++) squares[i] = Piece.None;
			SideToMove = PlayerColor.White;
			Castling = CastlingRights.None;
			EnPassantSquare = -1;
			HalfmoveClock = 0;
			FullmoveNumber = 1;
			undoStack.Clear();
		}

		public void SetPieceAt(int square, Piece piece)
		{
			squares[square] = piece;
		}

		public Piece GetPieceAt(int square)
		{
			return squares[square];
		}

		public IEnumerable<int> Squares()
		{
			for (int i = 0; i < 64; i++) yield return i;
		}

		public int GetKingSquare(PlayerColor color)
		{
			for (int i = 0; i < 64; i++)
			{
				Piece p = squares[i];
				if (!p.IsNone && p.Type == PieceType.King && p.Color == color)
				{
					return i;
				}
			}
			return -1;
		}

		public bool IsSquareAttackedBy(int targetSquare, PlayerColor attackerColor)
		{
			// Pawns
			int dir = attackerColor == PlayerColor.White ? 1 : -1;
			int targetRank = targetSquare / 8;
			int targetFile = targetSquare % 8;
			int pawnRank = targetRank - dir;
			if (pawnRank >= 0 && pawnRank < 8)
			{
				for (int df = -1; df <= 1; df += 2)
				{
					int file = targetFile + df;
					if (file >= 0 && file < 8)
					{
						int sq = pawnRank * 8 + file;
						Piece p = squares[sq];
						if (!p.IsNone && p.Color == attackerColor && p.Type == PieceType.Pawn)
							return true;
					}
				}
			}

			// Knights
			int[] knightOffsets = { 17, 15, -17, -15, 10, -10, 6, -6 };
			foreach (int off in knightOffsets)
			{
				int sq = targetSquare + off;
				if (IsKnightMoveOnBoard(targetSquare, sq) && InBounds(sq))
				{
					Piece p = squares[sq];
					if (!p.IsNone && p.Color == attackerColor && p.Type == PieceType.Knight)
						return true;
				}
			}

			// Bishops/Queens (diagonals)
			if (ScanRaysForAttack(targetSquare, attackerColor, new int[] { 9, 7, -9, -7 }, PieceType.Bishop, PieceType.Queen)) return true;
			// Rooks/Queens (orthogonals)
			if (ScanRaysForAttack(targetSquare, attackerColor, new int[] { 8, -8, 1, -1 }, PieceType.Rook, PieceType.Queen)) return true;

			// King
			for (int dr = -1; dr <= 1; dr++)
			{
				for (int df = -1; df <= 1; df++)
				{
					if (dr == 0 && df == 0) continue;
					int r = targetRank + dr;
					int f = targetFile + df;
					if (r >= 0 && r < 8 && f >= 0 && f < 8)
					{
						int sq = r * 8 + f;
						Piece p = squares[sq];
						if (!p.IsNone && p.Color == attackerColor && p.Type == PieceType.King)
							return true;
					}
				}
			}

			return false;
		}

		private bool ScanRaysForAttack(int targetSquare, PlayerColor attackerColor, int[] directions, PieceType a, PieceType b)
		{
			int tsRank = targetSquare / 8;
			int tsFile = targetSquare % 8;
			foreach (int dir in directions)
			{
				int sq = targetSquare + dir;
				while (InBounds(sq) && AreSquaresRayConnected(targetSquare, sq, dir))
				{
					Piece p = squares[sq];
					if (!p.IsNone)
					{
						if (p.Color == attackerColor && (p.Type == a || p.Type == b)) return true;
						break;
					}
					sq += dir;
				}
			}
			return false;
		}

		private static bool InBounds(int sq) => sq >= 0 && sq < 64;

		private static bool AreSquaresRayConnected(int from, int to, int dir)
		{
			// Ensure we don't wrap around files when moving horizontally/diagonally
			int fromFile = from % 8;
			int toFile = to % 8;
			if (dir == 1 || dir == -1 || dir == 9 || dir == -9 || dir == 7 || dir == -7)
			{
				int df = Math.Abs(toFile - fromFile);
				int steps = Math.Abs((to - from) / dir);
				return df == steps || dir == 1 || dir == -1; // for 1/-1, steps==df anyway
			}
			return true;
		}

		private static bool IsKnightMoveOnBoard(int from, int to)
		{
			if (!InBounds(to)) return false;
			int fromRank = from / 8, fromFile = from % 8;
			int toRank = to / 8, toFile = to % 8;
			int dr = Math.Abs(toRank - fromRank);
			int df = Math.Abs(toFile - fromFile);
			return dr * df == 2;
		}

		public IEnumerable<Move> GenerateLegalMoves()
		{
			// Generate pseudo-legal and filter by king safety
			List<Move> pseudo = new List<Move>(128);
			GeneratePseudoLegalMoves(pseudo);
			List<Move> legal = new List<Move>(pseudo.Count);
			foreach (var m in pseudo)
			{
				BoardState st = ApplyMove(m);
				bool kingInCheck = IsSquareAttackedBy(GetKingSquare(SideToMove == PlayerColor.White ? PlayerColor.Black : PlayerColor.White), SideToMove);
				// After ApplyMove we flipped side to move, so check if current side's king (after flip) is attacked
				if (!kingInCheck)
				{
					legal.Add(m);
				}
				UndoLastMove();
			}
			return legal;
		}

		private void GeneratePseudoLegalMoves(List<Move> moves)
		{
			moves.Clear();
			PlayerColor us = SideToMove;
			for (int sq = 0; sq < 64; sq++)
			{
				Piece p = squares[sq];
				if (p.IsNone || p.Color != us) continue;
				switch (p.Type)
				{
					case PieceType.Pawn:
						GeneratePawnMoves(sq, moves);
						break;
					case PieceType.Knight:
						GenerateKnightMoves(sq, moves);
						break;
					case PieceType.Bishop:
						GenerateSlidingMoves(sq, moves, new int[] { 9, 7, -9, -7 });
						break;
					case PieceType.Rook:
						GenerateSlidingMoves(sq, moves, new int[] { 8, -8, 1, -1 });
						break;
					case PieceType.Queen:
						GenerateSlidingMoves(sq, moves, new int[] { 9, 7, -9, -7, 8, -8, 1, -1 });
						break;
					case PieceType.King:
						GenerateKingMoves(sq, moves);
						break;
				}
			}
		}

		private void GeneratePawnMoves(int from, List<Move> moves)
		{
			Piece pawn = squares[from];
			int dir = pawn.Color == PlayerColor.White ? 1 : -1;
			int rank = from / 8;
			int file = from % 8;
			int oneAhead = from + dir * 8;
			if (InBounds(oneAhead) && squares[oneAhead].IsNone)
			{
				AddPawnAdvanceOrPromotion(from, oneAhead, pawn.Color, moves);
				bool isStartRank = (pawn.Color == PlayerColor.White && rank == 1) || (pawn.Color == PlayerColor.Black && rank == 6);
				int twoAhead = from + dir * 16;
				if (isStartRank && squares[twoAhead].IsNone)
				{
					moves.Add(new Move(from, twoAhead, PieceType.None, MoveFlag.DoublePawnPush));
				}
			}
			for (int df = -1; df <= 1; df += 2)
			{
				int toFile = file + df;
				if (toFile < 0 || toFile > 7) continue;
				int to = from + dir * 8 + df;
				if (!InBounds(to)) continue;
				Piece target = squares[to];
				if (!target.IsNone && target.Color != pawn.Color)
				{
					AddPawnCaptureOrPromotion(from, to, pawn.Color, moves);
				}
				// En passant
				if (EnPassantSquare == to)
				{
					moves.Add(new Move(from, to, PieceType.None, MoveFlag.EnPassant | MoveFlag.Capture));
				}
			}
		}

		private void AddPawnAdvanceOrPromotion(int from, int to, PlayerColor color, List<Move> moves)
		{
			int toRank = to / 8;
			if ((color == PlayerColor.White && toRank == 7) || (color == PlayerColor.Black && toRank == 0))
			{
				moves.Add(new Move(from, to, PieceType.Queen, MoveFlag.Promotion));
				moves.Add(new Move(from, to, PieceType.Rook, MoveFlag.Promotion));
				moves.Add(new Move(from, to, PieceType.Bishop, MoveFlag.Promotion));
				moves.Add(new Move(from, to, PieceType.Knight, MoveFlag.Promotion));
			}
			else
			{
				moves.Add(new Move(from, to));
			}
		}

		private void AddPawnCaptureOrPromotion(int from, int to, PlayerColor color, List<Move> moves)
		{
			int toRank = to / 8;
			if ((color == PlayerColor.White && toRank == 7) || (color == PlayerColor.Black && toRank == 0))
			{
				moves.Add(new Move(from, to, PieceType.Queen, MoveFlag.Promotion | MoveFlag.Capture));
				moves.Add(new Move(from, to, PieceType.Rook, MoveFlag.Promotion | MoveFlag.Capture));
				moves.Add(new Move(from, to, PieceType.Bishop, MoveFlag.Promotion | MoveFlag.Capture));
				moves.Add(new Move(from, to, PieceType.Knight, MoveFlag.Promotion | MoveFlag.Capture));
			}
			else
			{
				moves.Add(new Move(from, to, PieceType.None, MoveFlag.Capture));
			}
		}

		private void GenerateKnightMoves(int from, List<Move> moves)
		{
			int[] offs = { 17, 15, -17, -15, 10, -10, 6, -6 };
			int fromRank = from / 8, fromFile = from % 8;
			foreach (int off in offs)
			{
				int to = from + off;
				if (!InBounds(to)) continue;
				int toRank = to / 8, toFile = to % 8;
				if (Math.Abs(toRank - fromRank) * Math.Abs(toFile - fromFile) != 2) continue;
				Piece target = squares[to];
				if (target.IsNone)
					moves.Add(new Move(from, to));
				else if (target.Color != squares[from].Color)
					moves.Add(new Move(from, to, PieceType.None, MoveFlag.Capture));
			}
		}

		private void GenerateSlidingMoves(int from, List<Move> moves, int[] directions)
		{
			foreach (int dir in directions)
			{
				int to = from + dir;
				while (InBounds(to) && AreSquaresRayConnected(from, to, dir))
				{
					Piece target = squares[to];
					if (target.IsNone)
					{
						moves.Add(new Move(from, to));
					}
					else
					{
						if (target.Color != squares[from].Color)
							moves.Add(new Move(from, to, PieceType.None, MoveFlag.Capture));
						break;
					}
					to += dir;
				}
			}
		}

		private void GenerateKingMoves(int from, List<Move> moves)
		{
			int fromRank = from / 8, fromFile = from % 8;
			for (int dr = -1; dr <= 1; dr++)
			{
				for (int df = -1; df <= 1; df++)
				{
					if (dr == 0 && df == 0) continue;
					int r = fromRank + dr, f = fromFile + df;
					if (r < 0 || r > 7 || f < 0 || f > 7) continue;
					int to = r * 8 + f;
					Piece target = squares[to];
					if (target.IsNone)
						moves.Add(new Move(from, to));
					else if (target.Color != squares[from].Color)
						moves.Add(new Move(from, to, PieceType.None, MoveFlag.Capture));
				}
			}

			// Castling
			Piece king = squares[from];
			if (king.Color == PlayerColor.White)
			{
				if ((Castling & CastlingRights.WhiteKingSide) != 0 && squares[5].IsNone && squares[6].IsNone)
				{
					if (!IsSquareAttackedBy(4, PlayerColor.Black) && !IsSquareAttackedBy(5, PlayerColor.Black) && !IsSquareAttackedBy(6, PlayerColor.Black))
						moves.Add(new Move(from, 6, PieceType.None, MoveFlag.CastleKingSide));
				}
				if ((Castling & CastlingRights.WhiteQueenSide) != 0 && squares[1].IsNone && squares[2].IsNone && squares[3].IsNone)
				{
					if (!IsSquareAttackedBy(4, PlayerColor.Black) && !IsSquareAttackedBy(3, PlayerColor.Black) && !IsSquareAttackedBy(2, PlayerColor.Black))
						moves.Add(new Move(from, 2, PieceType.None, MoveFlag.CastleQueenSide));
				}
			}
			else
			{
				if ((Castling & CastlingRights.BlackKingSide) != 0 && squares[61].IsNone && squares[62].IsNone)
				{
					if (!IsSquareAttackedBy(60, PlayerColor.White) && !IsSquareAttackedBy(61, PlayerColor.White) && !IsSquareAttackedBy(62, PlayerColor.White))
						moves.Add(new Move(from, 62, PieceType.None, MoveFlag.CastleKingSide));
				}
				if ((Castling & CastlingRights.BlackQueenSide) != 0 && squares[57].IsNone && squares[58].IsNone && squares[59].IsNone)
				{
					if (!IsSquareAttackedBy(60, PlayerColor.White) && !IsSquareAttackedBy(59, PlayerColor.White) && !IsSquareAttackedBy(58, PlayerColor.White))
						moves.Add(new Move(from, 58, PieceType.None, MoveFlag.CastleQueenSide));
				}
			}
		}

		public BoardState ApplyMove(Move move)
		{
			BoardState prev = new BoardState
			{
				FromSquare = move.FromSquare,
				ToSquare = move.ToSquare,
				MovedPiece = squares[move.FromSquare],
				CapturedPiece = squares[move.ToSquare],
				CapturedOnSquare = move.ToSquare,
				Promotion = move.Promotion,
				PrevCastling = Castling,
				PrevEnPassant = EnPassantSquare,
				PrevHalfmoveClock = HalfmoveClock,
				PrevFullmoveNumber = FullmoveNumber,
				PrevSideToMove = SideToMove
			};

			undoStack.Push(prev);

			Piece moving = squares[move.FromSquare];
			Piece captured = squares[move.ToSquare];

			// Update halfmove clock
			if (moving.Type == PieceType.Pawn || !captured.IsNone) HalfmoveClock = 0; else HalfmoveClock++;

			// Handle en passant capture
			if ((move.Flags & MoveFlag.EnPassant) != 0)
			{
				int dir = moving.Color == PlayerColor.White ? -8 : 8;
				int capturedSq = move.ToSquare + dir;
				prev.CapturedPiece = squares[capturedSq];
				prev.CapturedOnSquare = capturedSq;
				squares[capturedSq] = Piece.None;
			}

			// Move piece
			squares[move.ToSquare] = moving;
			squares[move.FromSquare] = Piece.None;

			// Handle promotion
			if ((move.Flags & MoveFlag.Promotion) != 0 && move.Promotion != PieceType.None)
			{
				squares[move.ToSquare] = new Piece(move.Promotion, moving.Color);
			}

			// Handle castling rook move
			if ((move.Flags & MoveFlag.CastleKingSide) != 0)
			{
				if (moving.Color == PlayerColor.White)
				{
					// Move rook h1->f1 (7->5)
					squares[5] = squares[7];
					squares[7] = Piece.None;
				}
				else
				{
					// h8->f8 (63->61)
					squares[61] = squares[63];
					squares[63] = Piece.None;
				}
			}
			else if ((move.Flags & MoveFlag.CastleQueenSide) != 0)
			{
				if (moving.Color == PlayerColor.White)
				{
					// a1->d1 (0->3)
					squares[3] = squares[0];
					squares[0] = Piece.None;
				}
				else
				{
					// a8->d8 (56->59)
					squares[59] = squares[56];
					squares[56] = Piece.None;
				}
			}

			// Update castling rights
			UpdateCastlingRights(prev, move, moving);

			// Update en passant square
			if ((move.Flags & MoveFlag.DoublePawnPush) != 0)
			{
				EnPassantSquare = moving.Color == PlayerColor.White ? move.FromSquare + 8 : move.FromSquare - 8;
			}
			else
			{
				EnPassantSquare = -1;
			}

			// Flip side to move and move number
			SideToMove = SideToMove == PlayerColor.White ? PlayerColor.Black : PlayerColor.White;
			if (SideToMove == PlayerColor.White) FullmoveNumber++;

			return prev;
		}

		private void UpdateCastlingRights(BoardState prev, Move move, Piece moving)
		{
			// When king moves, lose both rights for that color
			if (moving.Type == PieceType.King)
			{
				if (moving.Color == PlayerColor.White)
				{
					Castling &= ~(CastlingRights.WhiteKingSide | CastlingRights.WhiteQueenSide);
				}
				else
				{
					Castling &= ~(CastlingRights.BlackKingSide | CastlingRights.BlackQueenSide);
				}
			}

			// When rook moves or is captured, lose that side's specific right
			if (move.FromSquare == 0 || move.ToSquare == 0) Castling &= ~CastlingRights.WhiteQueenSide;
			if (move.FromSquare == 7 || move.ToSquare == 7) Castling &= ~CastlingRights.WhiteKingSide;
			if (move.FromSquare == 56 || move.ToSquare == 56) Castling &= ~CastlingRights.BlackQueenSide;
			if (move.FromSquare == 63 || move.ToSquare == 63) Castling &= ~CastlingRights.BlackKingSide;
		}

		public void UndoLastMove()
		{
			if (undoStack.Count == 0) return;
			BoardState st = undoStack.Pop();

			// Restore side/move counters/state
			SideToMove = st.PrevSideToMove;
			Castling = st.PrevCastling;
			EnPassantSquare = st.PrevEnPassant;
			HalfmoveClock = st.PrevHalfmoveClock;
			FullmoveNumber = st.PrevFullmoveNumber;

			// Undo castling rook move
			Piece moving = st.MovedPiece;
			if ((st.ToSquare == 6 && moving.Type == PieceType.King && moving.Color == PlayerColor.White))
			{
				// undo rook f1->h1
				squares[7] = squares[5];
				squares[5] = Piece.None;
			}
			else if ((st.ToSquare == 2 && moving.Type == PieceType.King && moving.Color == PlayerColor.White))
			{
				// undo rook d1->a1
				squares[0] = squares[3];
				squares[3] = Piece.None;
			}
			else if ((st.ToSquare == 62 && moving.Type == PieceType.King && moving.Color == PlayerColor.Black))
			{
				// undo rook f8->h8
				squares[63] = squares[61];
				squares[61] = Piece.None;
			}
			else if ((st.ToSquare == 58 && moving.Type == PieceType.King && moving.Color == PlayerColor.Black))
			{
				// undo rook d8->a8
				squares[56] = squares[59];
				squares[59] = Piece.None;
			}

			// Undo promotion
			Piece restoredFrom = moving;
			if (st.Promotion != PieceType.None)
			{
				restoredFrom = new Piece(PieceType.Pawn, moving.Color);
			}

			// Clear destination and restore pieces
			squares[st.ToSquare] = Piece.None;
			squares[st.FromSquare] = restoredFrom;
			squares[st.CapturedOnSquare] = st.CapturedPiece;
		}

		public bool HasInsufficientMaterial()
		{
			bool anyPawn = false, anyRook = false, anyQueen = false;
			int whiteKnights = 0, blackKnights = 0;
			int lightBishops = 0, darkBishops = 0;
			for (int i = 0; i < 64; i++)
			{
				Piece p = squares[i];
				if (p.IsNone) continue;
				switch (p.Type)
				{
					case PieceType.Pawn:
						anyPawn = true; break;
					case PieceType.Rook:
						anyRook = true; break;
					case PieceType.Queen:
						anyQueen = true; break;
					case PieceType.Knight:
						if (p.Color == PlayerColor.White) whiteKnights++; else blackKnights++;
						break;
					case PieceType.Bishop:
						int file = i % 8; int rank = i / 8;
						bool isLight = ((file + rank) % 2) == 0;
						if (isLight) lightBishops++; else darkBishops++;
						break;
				}
			}
			if (anyPawn || anyRook || anyQueen) return false;
			int totalKnights = whiteKnights + blackKnights;
			int totalBishops = lightBishops + darkBishops;
			// K vs K
			if (totalKnights == 0 && totalBishops == 0) return true;
			// K+minor vs K (single knight or single bishop)
			if (totalKnights == 1 && totalBishops == 0) return true;
			if (totalKnights == 0 && totalBishops == 1) return true;
			// Only bishops and all bishops on same color squares
			if (totalKnights == 0 && totalBishops > 0 && (lightBishops == 0 || darkBishops == 0)) return true;
			return false;
		}
	}
}