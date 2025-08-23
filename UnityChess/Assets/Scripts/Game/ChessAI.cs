using System;
using System.Collections.Generic;

namespace Chess
{
	public class ChessAI
	{
		public int MaxDepth { get; set; } = 3;
		public int NodesSearched { get; private set; }

		private readonly Dictionary<ulong, (int depth, int score, Move move)> transposition = new Dictionary<ulong, (int, int, Move)>();

		public Move FindBestMove(Board board)
		{
			NodesSearched = 0;
			int alpha = int.MinValue + 1;
			int beta = int.MaxValue;
			Move best = default;
			int bestScore = board.SideToMove == PlayerColor.White ? int.MinValue : int.MaxValue;
			foreach (var move in board.GenerateLegalMoves())
			{
				board.ApplyMove(move);
				int score = Search(board, MaxDepth - 1, alpha, beta);
				board.UndoLastMove();
				if (board.SideToMove == PlayerColor.White)
				{
					if (score > bestScore)
					{
						bestScore = score;
						best = move;
						alpha = Math.Max(alpha, score);
					}
				}
				else
				{
					if (score < bestScore)
					{
						bestScore = score;
						best = move;
						beta = Math.Min(beta, score);
					}
				}
			}
			return best;
		}

		private int Search(Board board, int depth, int alpha, int beta)
		{
			NodesSearched++;
			GameResult result = EvaluateEndConditions(board);
			if (result.IsGameOver)
			{
				if (result.IsDraw) return 0;
				return result.Winner == PlayerColor.White ? 100000 : -100000;
			}
			if (depth == 0)
			{
				return Evaluate(board);
			}

			if (board.SideToMove == PlayerColor.White)
			{
				int best = int.MinValue + 1;
				foreach (var move in board.GenerateLegalMoves())
				{
					board.ApplyMove(move);
					int score = Search(board, depth - 1, alpha, beta);
					board.UndoLastMove();
					if (score > best) best = score;
					if (best > alpha) alpha = best;
					if (alpha >= beta) break; // beta cutoff
				}
				return best;
			}
			else
			{
				int best = int.MaxValue;
				foreach (var move in board.GenerateLegalMoves())
				{
					board.ApplyMove(move);
					int score = Search(board, depth - 1, alpha, beta);
					board.UndoLastMove();
					if (score < best) best = score;
					if (best < beta) beta = best;
					if (alpha >= beta) break; // alpha cutoff
				}
				return best;
			}
		}

		private static readonly Dictionary<PieceType, int> pieceValues = new Dictionary<PieceType, int>
		{
			{ PieceType.Pawn, 100 },
			{ PieceType.Knight, 320 },
			{ PieceType.Bishop, 330 },
			{ PieceType.Rook, 500 },
			{ PieceType.Queen, 900 },
			{ PieceType.King, 20000 }
		};

		private int Evaluate(Board board)
		{
			int score = 0;
			for (int sq = 0; sq < 64; sq++)
			{
				Piece p = board.GetPieceAt(sq);
				if (p.IsNone) continue;
				int val = pieceValues[p.Type];
				score += p.Color == PlayerColor.White ? val : -val;
			}
			// mobility
			int mobility = 0;
			var side = board.SideToMove;
			foreach (var m in board.GenerateLegalMoves()) mobility++;
			score += side == PlayerColor.White ? mobility : -mobility;
			return score;
		}

		private GameResult EvaluateEndConditions(Board board)
		{
			var legal = board.GenerateLegalMoves();
			bool any = false;
			foreach (var _ in legal) { any = true; break; }
			if (!any)
			{
				// No legal moves: check or stalemate
				PlayerColor us = board.SideToMove;
				int kingSq = board.GetKingSquare(us);
				bool inCheck = board.IsSquareAttackedBy(kingSq, us == PlayerColor.White ? PlayerColor.Black : PlayerColor.White);
				if (inCheck)
				{
					return GameResult.Mate(us == PlayerColor.White ? PlayerColor.Black : PlayerColor.White);
				}
				else
				{
					return GameResult.Draw(GameEndReason.Stalemate);
				}
			}
			if (board.HalfmoveClock >= 100) return GameResult.Draw(GameEndReason.FiftyMoveRule);
			return GameResult.Ongoing;
		}
	}
}