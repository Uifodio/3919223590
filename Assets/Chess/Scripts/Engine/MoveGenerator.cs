using System.Collections.Generic;

namespace Chess.Engine
{
	public static class MoveGenerator
	{
		public static void GenerateLegalMoves(Board board, List<Move> movesOut)
		{
			movesOut.Clear();
			var pseudo = new List<Move>(128);
			GeneratePseudoLegal(board, pseudo);
			for (int i = 0; i < pseudo.Count; i++)
			{
				var m = pseudo[i];
				board.MakeMove(m);
				bool illegal = board.InCheck(board.sideToMove == PieceColor.White ? PieceColor.Black : PieceColor.White);
				board.UnmakeMove();
				if (!illegal) movesOut.Add(m);
			}
		}

		public static void GeneratePseudoLegal(Board board, List<Move> movesOut)
		{
			movesOut.Clear();
			PieceColor us = board.sideToMove;
			for (int sq = 0; sq < 64; sq++)
			{
				var p = board.squares[sq];
				if (p.IsEmpty || p.color != us) continue;
				switch (p.type)
				{
					case PieceType.Pawn: GeneratePawn(board, sq, movesOut); break;
					case PieceType.Knight: GenerateKnight(board, sq, movesOut); break;
					case PieceType.Bishop: GenerateSliding(board, sq, movesOut, diag: true, ortho: false); break;
					case PieceType.Rook: GenerateSliding(board, sq, movesOut, diag: false, ortho: true); break;
					case PieceType.Queen: GenerateSliding(board, sq, movesOut, diag: true, ortho: true); break;
					case PieceType.King: GenerateKing(board, sq, movesOut); break;
				}
			}
		}

		private static void GeneratePawn(Board b, int from, List<Move> outMoves)
		{
			var p = b.squares[from];
			int dir = p.color == PieceColor.White ? -1 : 1;
			int rank = Move.RankOf(from);
			int file = Move.FileOf(from);
			int one = from + (dir << 3);
			if (one >= 0 && one < 64 && b.squares[one].IsEmpty)
			{
				AddPawnMoveOrPromotion(p.color, from, one, false, outMoves);
				bool onStart = (p.color == PieceColor.White && rank == 6) || (p.color == PieceColor.Black && rank == 1);
				if (onStart)
				{
					int two = from + (dir << 4);
					if (b.squares[two].IsEmpty) outMoves.Add(new Move(from, two, MoveFlags.DoublePawnPush));
				}
			}
			// Captures
			for (int df = -1; df <= 1; df += 2)
			{
				int nf = file + df;
				int nr = rank + dir;
				if (nf < 0 || nf > 7 || nr < 0 || nr > 7) continue;
				int to = Move.FromFileRank(nf, nr);
				if (!b.squares[to].IsEmpty && b.squares[to].color != p.color)
				{
					AddPawnMoveOrPromotion(p.color, from, to, true, outMoves);
				}
				// En passant
				if (b.enPassantSquare == to)
				{
					outMoves.Add(new Move(from, to, MoveFlags.Capture | MoveFlags.EnPassant));
				}
			}
		}

		private static void AddPawnMoveOrPromotion(PieceColor color, int from, int to, bool capture, List<Move> outMoves)
		{
			int targetRank = Move.RankOf(to);
			bool promote = (color == PieceColor.White && targetRank == 0) || (color == PieceColor.Black && targetRank == 7);
			if (promote)
			{
				var flags = MoveFlags.Promotion | (capture ? MoveFlags.Capture : MoveFlags.None);
				outMoves.Add(new Move(from, to, flags, PieceType.Queen));
				outMoves.Add(new Move(from, to, flags, PieceType.Rook));
				outMoves.Add(new Move(from, to, flags, PieceType.Bishop));
				outMoves.Add(new Move(from, to, flags, PieceType.Knight));
			}
			else
			{
				var flags = capture ? MoveFlags.Capture : MoveFlags.None;
				outMoves.Add(new Move(from, to, flags));
			}
		}

		private static void GenerateKnight(Board b, int from, List<Move> outMoves)
		{
			int f = Move.FileOf(from), r = Move.RankOf(from);
			int[] dx = { -2,-1,1,2, 2,1,-1,-2 };
			int[] dy = { 1,2,2,1, -1,-2,-2,-1 };
			for (int i = 0; i < 8; i++)
			{
				int nf = f + dx[i]; int nr = r + dy[i];
				if (nf < 0 || nf > 7 || nr < 0 || nr > 7) continue;
				int to = Move.FromFileRank(nf, nr);
				if (b.squares[to].IsEmpty || b.squares[to].color != b.squares[from].color)
				{
					var flags = b.squares[to].IsEmpty ? MoveFlags.None : MoveFlags.Capture;
					outMoves.Add(new Move(from, to, flags));
				}
			}
		}

		private static void GenerateSliding(Board b, int from, List<Move> outMoves, bool diag, bool ortho)
		{
			int f = Move.FileOf(from), r = Move.RankOf(from);
			int[] dfx = diag && ortho ? new int[] { 1,1,-1,-1, 1,-1,0,0 } : diag ? new int[] { 1,1,-1,-1 } : new int[] { 1,-1,0,0 };
			int[] dfy = diag && ortho ? new int[] { 1,-1,1,-1, 0,0,1,-1 } : diag ? new int[] { 1,-1,1,-1 } : new int[] { 0,0,1,-1 };
			for (int d = 0; d < dfx.Length; d++)
			{
				int nf = f + dfx[d], nr = r + dfy[d];
				while (nf >= 0 && nf < 8 && nr >= 0 && nr < 8)
				{
					int to = Move.FromFileRank(nf, nr);
					if (b.squares[to].IsEmpty)
					{
						outMoves.Add(new Move(from, to));
					}
					else
					{
						if (b.squares[to].color != b.squares[from].color) outMoves.Add(new Move(from, to, MoveFlags.Capture));
						break;
					}
					nf += dfx[d]; nr += dfy[d];
				}
			}
		}

		private static void GenerateKing(Board b, int from, List<Move> outMoves)
		{
			int f = Move.FileOf(from), r = Move.RankOf(from);
			for (int df = -1; df <= 1; df++)
			{
				for (int dr = -1; dr <= 1; dr++)
				{
					if (df == 0 && dr == 0) continue;
					int nf = f + df; int nr = r + dr;
					if (nf < 0 || nf > 7 || nr < 0 || nr > 7) continue;
					int to = Move.FromFileRank(nf, nr);
					if (b.squares[to].IsEmpty || b.squares[to].color != b.squares[from].color)
					{
						var flags = b.squares[to].IsEmpty ? MoveFlags.None : MoveFlags.Capture;
						outMoves.Add(new Move(from, to, flags));
					}
				}
			}

			// Castling
			var us = b.squares[from].color;
			if (us == PieceColor.White)
			{
				// King side: e1 to g1
				if (b.whiteCastleKingSide && b.squares[Move.FromFileRank(5,7)].IsEmpty && b.squares[Move.FromFileRank(6,7)].IsEmpty)
				{
					if (!b.IsSquareAttackedByColor(Move.FromFileRank(4,7), PieceColor.Black) && !b.IsSquareAttackedByColor(Move.FromFileRank(5,7), PieceColor.Black) && !b.IsSquareAttackedByColor(Move.FromFileRank(6,7), PieceColor.Black))
					{
						outMoves.Add(new Move(from, Move.FromFileRank(6,7), MoveFlags.CastleKingSide));
					}
				}
				// Queen side: e1 to c1
				if (b.whiteCastleQueenSide && b.squares[Move.FromFileRank(1,7)].IsEmpty && b.squares[Move.FromFileRank(2,7)].IsEmpty && b.squares[Move.FromFileRank(3,7)].IsEmpty)
				{
					if (!b.IsSquareAttackedByColor(Move.FromFileRank(4,7), PieceColor.Black) && !b.IsSquareAttackedByColor(Move.FromFileRank(3,7), PieceColor.Black) && !b.IsSquareAttackedByColor(Move.FromFileRank(2,7), PieceColor.Black))
					{
						outMoves.Add(new Move(from, Move.FromFileRank(2,7), MoveFlags.CastleQueenSide));
					}
				}
			}
			else
			{
				// King side: e8 to g8
				if (b.blackCastleKingSide && b.squares[Move.FromFileRank(5,0)].IsEmpty && b.squares[Move.FromFileRank(6,0)].IsEmpty)
				{
					if (!b.IsSquareAttackedByColor(Move.FromFileRank(4,0), PieceColor.White) && !b.IsSquareAttackedByColor(Move.FromFileRank(5,0), PieceColor.White) && !b.IsSquareAttackedByColor(Move.FromFileRank(6,0), PieceColor.White))
					{
						outMoves.Add(new Move(from, Move.FromFileRank(6,0), MoveFlags.CastleKingSide));
					}
				}
				// Queen side: e8 to c8
				if (b.blackCastleQueenSide && b.squares[Move.FromFileRank(1,0)].IsEmpty && b.squares[Move.FromFileRank(2,0)].IsEmpty && b.squares[Move.FromFileRank(3,0)].IsEmpty)
				{
					if (!b.IsSquareAttackedByColor(Move.FromFileRank(4,0), PieceColor.White) && !b.IsSquareAttackedByColor(Move.FromFileRank(3,0), PieceColor.White) && !b.IsSquareAttackedByColor(Move.FromFileRank(2,0), PieceColor.White))
					{
						outMoves.Add(new Move(from, Move.FromFileRank(2,0), MoveFlags.CastleQueenSide));
					}
				}
			}
		}
	}
}