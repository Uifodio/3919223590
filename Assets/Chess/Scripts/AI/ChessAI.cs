using System;
using System.Collections.Generic;
using System.Diagnostics;
using Chess.Engine;

namespace Chess.AI
{
	public enum AIStyle
	{
		Balanced,
		Aggressive,
		Defensive,
		Positional
	}

	public class ChessAI
	{
		private int maxDepth = 3;
		private int timeBudgetMs = 0;
		private readonly int[] pieceValues = { 0, 100, 320, 330, 500, 900, 20000 };
		private readonly Dictionary<(int,int), int> historyHeuristic = new Dictionary<(int,int), int>();
		private Move?[,] killerMoves = new Move?[64, 2];
		private AIStyle style = AIStyle.Balanced;

		public void SetLimits(int depth, int timeMs)
		{
			maxDepth = Math.Max(1, depth);
			timeBudgetMs = Math.Max(0, timeMs);
		}

		public void SetStyle(AIStyle newStyle)
		{
			style = newStyle;
		}

		public Move? FindBestMove(Board position)
		{
			// Try opening book based on SAN history
			string sanHistory = SanUtil.BuildSanHistory(position);
			if (OpeningBook.TryGetBookMoves(sanHistory, out var sanMoves))
			{
				var legal = new List<Move>(128);
				MoveGenerator.GenerateLegalMoves(position, legal);
				foreach (var san in sanMoves)
				{
					if (SanUtil.TryMatchSan(position, legal, san, out var m)) return m;
				}
			}

			var sw = Stopwatch.StartNew();
			var legalMoves = new List<Move>(128);
			MoveGenerator.GenerateLegalMoves(position, legalMoves);
			if (legalMoves.Count == 0) return null;
			OrderMoves(position, legalMoves, 0);
			int bestScore = int.MinValue;
			Move bestMove = legalMoves[0];
			for (int depth = 1; depth <= maxDepth; depth++)
			{
				int alpha = int.MinValue + 1;
				int beta = int.MaxValue - 1;
				for (int i = 0; i < legalMoves.Count; i++)
				{
					var m = legalMoves[i];
					position.MakeMove(m);
					int score = -Search(position, depth - 1, -beta, -alpha, sw, ply: 1);
					position.UnmakeMove();
					if (score > bestScore || depth == 1 && i == 0)
					{
						bestScore = score;
						bestMove = m;
					}
					if (score > alpha) alpha = score;
					if (timeBudgetMs > 0 && sw.ElapsedMilliseconds > timeBudgetMs) break;
				}
				if (timeBudgetMs > 0 && sw.ElapsedMilliseconds > timeBudgetMs) break;
			}
			return bestMove;
		}

		private int Search(Board pos, int depth, int alpha, int beta, Stopwatch sw, int ply)
		{
			if (timeBudgetMs > 0 && sw.ElapsedMilliseconds > timeBudgetMs) return Evaluate(pos);
			if (depth == 0) return Quiescence(pos, alpha, beta, sw);
			var moves = new List<Move>(128);
			MoveGenerator.GenerateLegalMoves(pos, moves);
			if (moves.Count == 0)
			{
				if (pos.InCheck(pos.sideToMove)) return -999999 + ply; // checkmated
				return 0; // stalemate
			}
			OrderMoves(pos, moves, ply);
			int best = int.MinValue;
			Move? bestLocal = null;
			for (int i = 0; i < moves.Count; i++)
			{
				var m = moves[i];
				pos.MakeMove(m);
				int sc = -Search(pos, depth - 1, -beta, -alpha, sw, ply + 1);
				pos.UnmakeMove();
				if (sc > best) { best = sc; bestLocal = m; }
				if (best > alpha) alpha = best;
				if (alpha >= beta)
				{
					if (i < 2) killerMoves[ply, i] = m; // save as killer
					break; // cutoff
				}
				if (timeBudgetMs > 0 && sw.ElapsedMilliseconds > timeBudgetMs) break;
			}
			if (bestLocal.HasValue)
			{
				var key = (bestLocal.Value.from, bestLocal.Value.to);
				if (!historyHeuristic.ContainsKey(key)) historyHeuristic[key] = 0;
				historyHeuristic[key] += depth * depth;
			}
			return best;
		}

		private int Quiescence(Board pos, int alpha, int beta, Stopwatch sw)
		{
			int standPat = Evaluate(pos);
			if (standPat >= beta) return beta;
			if (alpha < standPat) alpha = standPat;
			var moves = new List<Move>(64);
			MoveGenerator.GenerateLegalMoves(pos, moves);
			for (int i = 0; i < moves.Count; i++)
			{
				var m = moves[i];
				if (!m.IsCapture && !m.IsPromotion) continue;
				pos.MakeMove(m);
				int score = -Quiescence(pos, -beta, -alpha, sw);
				pos.UnmakeMove();
				if (score >= beta) return beta;
				if (score > alpha) alpha = score;
				if (timeBudgetMs > 0 && sw.ElapsedMilliseconds > timeBudgetMs) break;
			}
			return alpha;
		}

		private void OrderMoves(Board pos, List<Move> moves, int ply)
		{
			moves.Sort((a, b) => ScoreMove(pos, b, ply).CompareTo(ScoreMove(pos, a, ply)));
		}

		private int ScoreMove(Board pos, Move m, int ply)
		{
			int score = 0;
			if (m.IsCapture)
			{
				var captured = pos.squares[m.to];
				var attacker = pos.squares[m.from];
				score += 100000 + pieceValues[(int)captured.type] - pieceValues[(int)attacker.type];
			}
			if (m.IsPromotion) score += 90000;
			var key = (m.from, m.to);
			if (historyHeuristic.TryGetValue(key, out var h)) score += h;
			var k1 = killerMoves[ply, 0]; if (k1.HasValue && k1.Value.to == m.to && k1.Value.from == m.from) score += 50000;
			var k2 = killerMoves[ply, 1]; if (k2.HasValue && k2.Value.to == m.to && k2.Value.from == m.from) score += 40000;
			return score;
		}

		private int Evaluate(Board b)
		{
			int material = 0;
			int mobility = 0;
			int center = 0;
			int kingSafety = 0;
			int pawnStructure = 0;
			for (int i = 0; i < 64; i++)
			{
				var p = b.squares[i];
				if (p.IsEmpty) continue;
				int val = pieceValues[(int)p.type];
				material += (p.color == PieceColor.White ? val : -val);
				// Center control
				int f = Move.FileOf(i), r = Move.RankOf(i);
				bool inCenter = (f >= 2 && f <= 5 && r >= 2 && r <= 5);
				if (inCenter) center += (p.color == PieceColor.White ? 2 : -2);
				// Pawn structure bonus
				if (p.type == PieceType.Pawn)
				{
					pawnStructure += (p.color == PieceColor.White ? (6 - r) : (r - 1));
				}
			}
			// Mobility (legal move count difference)
			var tmp = b.Clone();
			var movesSide = new List<Move>(64);
			MoveGenerator.GenerateLegalMoves(tmp, movesSide);
			int sideMoves = movesSide.Count;
			tmp.sideToMove = tmp.sideToMove == PieceColor.White ? PieceColor.Black : PieceColor.White;
			movesSide.Clear(); MoveGenerator.GenerateLegalMoves(tmp, movesSide);
			int oppMoves = movesSide.Count;
			mobility = (sideMoves - oppMoves) * 2;

			int score = material + mobility + center + pawnStructure;
			// Style weighting
			switch (style)
			{
				case AIStyle.Aggressive:
					score += mobility + center;
					break;
				case AIStyle.Defensive:
					score += (int)(material * 0.1);
					break;
				case AIStyle.Positional:
					score += center + (pawnStructure / 2);
					break;
			}
			return b.sideToMove == PieceColor.White ? score : -score;
		}
	}

	public static class SanUtil
	{
		private static readonly System.Text.StringBuilder history = new System.Text.StringBuilder();
		public static void Append(Board b, Move m)
		{
			string san = ToSimpleSan(b, m);
			if (history.Length > 0) history.Append(' ');
			history.Append(san);
		}

		public static void Clear()
		{
			history.Length = 0;
		}

		public static string BuildSanHistory(Board b)
		{
			return history.ToString();
		}

		public static bool TryMatchSan(Board b, List<Move> legal, string san, out Move move)
		{
			// Very minimal: support common SAN like e4, d4, Nf3, cxd5, Bc4, Qh5, O-O, O-O-O
			move = default;
			foreach (var m in legal)
			{
				var notation = ToSimpleSan(b, m);
				if (notation == san)
				{
					move = m; return true;
				}
			}
			return false;
		}

		private static string ToSimpleSan(Board b, Move m)
		{
			var p = b.squares[m.from];
			if (m.IsCastleKing) return "O-O";
			if (m.IsCastleQueen) return "O-O-O";
			char file = (char)('a' + Move.FileOf(m.to));
			char rank = (char)('1' + Move.RankOf(m.to));
			string dst = new string(new[] { file, rank });
			if (p.type == PieceType.Pawn)
			{
				if (m.IsCapture) return ((char)('a' + Move.FileOf(m.from))).ToString() + "x" + dst;
				return dst;
			}
			char piece = p.type switch
			{
				PieceType.Knight => 'N',
				PieceType.Bishop => 'B',
				PieceType.Rook => 'R',
				PieceType.Queen => 'Q',
				PieceType.King => 'K',
				_ => ' '
			};
			return (m.IsCapture ? piece + "x" : piece.ToString()) + dst;
		}
	}
}