using System;
using System.Collections.Generic;
using System.Diagnostics;
using Chess.Engine;

namespace Chess.AI
{
	public class ChessAI
	{
		private int maxDepth = 3;
		private int timeBudgetMs = 0;

		public void SetLimits(int depth, int timeMs)
		{
			maxDepth = Math.Max(1, depth);
			timeBudgetMs = Math.Max(0, timeMs);
		}

		public Move? FindBestMove(Board position)
		{
			var moves = new List<Move>(128);
			MoveGenerator.GenerateLegalMoves(position, moves);
			if (moves.Count == 0) return null;
			var sw = Stopwatch.StartNew();
			int bestScore = int.MinValue;
			Move bestMove = moves[0];
			foreach (var m in moves)
			{
				position.MakeMove(m);
				int score = -Search(position, maxDepth - 1, int.MinValue + 1, int.MaxValue - 1, sw);
				position.UnmakeMove();
				if (score > bestScore)
				{
					bestScore = score;
					bestMove = m;
				}
				if (timeBudgetMs > 0 && sw.ElapsedMilliseconds > timeBudgetMs) break;
			}
			return bestMove;
		}

		private int Search(Board pos, int depth, int alpha, int beta, Stopwatch sw)
		{
			if (depth == 0 || (timeBudgetMs > 0 && sw.ElapsedMilliseconds > timeBudgetMs))
			{
				return Evaluate(pos);
			}
			var moves = new List<Move>(128);
			MoveGenerator.GenerateLegalMoves(pos, moves);
			if (moves.Count == 0)
			{
				if (pos.InCheck(pos.sideToMove)) return -999999 + (maxDepth - depth); // checkmated
				return 0; // stalemate
			}
			int best = int.MinValue;
			foreach (var m in moves)
			{
				pos.MakeMove(m);
				int sc = -Search(pos, depth - 1, -beta, -alpha, sw);
				pos.UnmakeMove();
				if (sc > best) best = sc;
				if (best > alpha) alpha = best;
				if (alpha >= beta) break; // cutoff
				if (timeBudgetMs > 0 && sw.ElapsedMilliseconds > timeBudgetMs) break;
			}
			return best;
		}

		private static readonly int[] pieceValues = { 0, 100, 320, 330, 500, 900, 20000 };

		private int Evaluate(Board b)
		{
			int score = 0;
			for (int i = 0; i < 64; i++)
			{
				var p = b.squares[i];
				if (p.IsEmpty) continue;
				int val = pieceValues[(int)p.type];
				score += (p.color == Chess.Engine.PieceColor.White ? val : -val);
			}
			return b.sideToMove == Chess.Engine.PieceColor.White ? score : -score;
		}
	}
}