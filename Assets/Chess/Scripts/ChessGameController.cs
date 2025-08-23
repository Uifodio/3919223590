using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;
using Chess.Engine;

namespace Chess
{
	public enum GameResult
	{
		InProgress,
		WhiteWin,
		BlackWin,
		Stalemate,
		Draw50Move
	}

	public class ChessGameController : MonoBehaviour
	{
		[Serializable]
		public struct Config
		{
			public bool aiEnabled;
			public bool aiPlaysBlack;
			public int aiSearchDepth;
			public int aiTimeBudgetMs;
			public bool autoSaveEnabled;
			public bool loadAutoSaveOnStart;
			public bool highlightLegalMoves;
			public bool allowUndo;
			public AI.AIStyle aiStyle;
		}

		public event Action<GameResult, PieceColor> OnGameOver;

		private Config config;
		public bool AiEnabled => config.aiEnabled;
		public bool AiPlaysBlack => config.aiPlaysBlack;
		private Board board;
		private UI.ChessUI ui;
		private AI.ChessAI ai;
		private List<Move> legalMoves = new List<Move>(128);
		private List<Move> scratch = new List<Move>(128);
		private int selectedSquare = -1;
		private string autosavePath;
		private bool isAiThinking = false;

		[Serializable]
		private struct SaveData
		{
			public string fen;
		}

		public void Configure(Config config)
		{
			this.config = config;
		}

		private void Start()
		{
			autosavePath = Path.Combine(Application.persistentDataPath, "chess_autosave.json");
			ui = gameObject.AddComponent<UI.ChessUI>();
			ui.Initialize(this, config.highlightLegalMoves, OnSquareClicked, OnUndo, OnNewGame, OnDepthChanged, OnOfferDraw);
			ai = new AI.ChessAI();
			ai.SetLimits(config.aiSearchDepth, config.aiTimeBudgetMs);
			ai.SetStyle(config.aiStyle);
			NewGame();
			if (config.autoSaveEnabled && config.loadAutoSaveOnStart && File.Exists(autosavePath))
			{
				TryLoad();
			}
			UpdateUIFull();
		}

		private void UpdateUIFull()
		{
			ui.RenderBoard(board);
			ui.SetTurn(board.sideToMove);
			ui.SetCanUndo(config.allowUndo && CanUndo());
			ui.SetGameOver(GameResult.InProgress, PieceColor.White); // reset indicator
			ui.SetDrawEnabled(true);
		}

		public void NewGame()
		{
			board = new Board();
			board.SetupStartingPosition();
			Chess.AI.SanUtil.Clear();
			selectedSquare = -1;
			GenerateLegalMoves();
			SaveIfEnabled();
		}

		private void GenerateLegalMoves()
		{
			MoveGenerator.GenerateLegalMoves(board, legalMoves);
			ui.ShowLegalMoves(selectedSquare, legalMoves);
		}

		private bool CanUndo()
		{
			return true; // stack can be empty; UI will disable if none
		}

		private void OnSquareClicked(int square)
		{
			if (isAiThinking) return;
			if (board.sideToMove == (config.aiPlaysBlack ? PieceColor.Black : PieceColor.White) && config.aiEnabled)
			{
				return; // wait AI turn
			}

			if (selectedSquare == -1)
			{
				// select own piece
				if (!board.squares[square].IsEmpty && board.squares[square].color == board.sideToMove)
				{
					selectedSquare = square;
					GenerateLegalMoves();
				}
			}
			else
			{
				// attempt move
				Move? chosen = null;
				for (int i = 0; i < legalMoves.Count; i++)
				{
					var m = legalMoves[i];
					if (m.from == selectedSquare && m.to == square) { chosen = m; break; }
				}
				if (chosen.HasValue)
				{
					// Handle promotion UI if needed
					var move = chosen.Value;
					if (move.IsPromotion && move.promotion == PieceType.Queen) // placeholder to trigger UI
					{
						ui.ShowPromotionDialog(board.sideToMove, (prom) =>
						{
							ExecuteMove(new Move(move.from, move.to, move.flags, prom));
						});
						return;
					}
					ExecuteMove(move);
				}
				else
				{
					// reselect if clicked own piece
					if (!board.squares[square].IsEmpty && board.squares[square].color == board.sideToMove)
					{
						selectedSquare = square;
						GenerateLegalMoves();
					}
					else
					{
						selectedSquare = -1;
						GenerateLegalMoves();
					}
				}
			}
		}

		private void ExecuteMove(Move move)
		{
			ui.AnimateMove(move.from, move.to, 0.15f);
			Chess.AI.SanUtil.Append(board, move);
			board.MakeMove(move);
			selectedSquare = -1;
			ui.RenderBoard(board);
			GenerateLegalMoves();
			SaveIfEnabled();
			var result = EvaluateGameEnd();
			if (result != GameResult.InProgress)
			{
				ui.SetGameOver(result, board.sideToMove == PieceColor.White ? PieceColor.Black : PieceColor.White);
				OnGameOver?.Invoke(result, board.sideToMove == PieceColor.White ? PieceColor.Black : PieceColor.White);
				return;
			}
			MaybeStartAi();
		}

		private GameResult EvaluateGameEnd()
		{
			MoveGenerator.GenerateLegalMoves(board, scratch);
			if (scratch.Count == 0)
			{
				if (board.InCheck(board.sideToMove))
				{
					return board.sideToMove == PieceColor.White ? GameResult.BlackWin : GameResult.WhiteWin;
				}
				return GameResult.Stalemate;
			}
			if (board.halfmoveClock >= 100) return GameResult.Draw50Move;
			if (board.IsThreefoldRepetition()) return GameResult.Draw50Move; // using existing enum for draw
			if (board.IsInsufficientMaterial()) return GameResult.Draw50Move;
			return GameResult.InProgress;
		}

		private void MaybeStartAi()
		{
			if (!config.aiEnabled) return;
			var aiColor = config.aiPlaysBlack ? PieceColor.Black : PieceColor.White;
			if (board.sideToMove != aiColor) return;
			if (isAiThinking) return;
			isAiThinking = true;
			ui.ShowThinking(true);
			var boardCopy = board.Clone();
			Task.Run(() => ai.FindBestMove(boardCopy))
				.ContinueWith(t =>
				{
					isAiThinking = false;
					ui.ShowThinking(false);
					if (t.IsCompletedSuccessfully)
					{
						var best = t.Result;
						if (best.HasValue)
						{
							ExecuteMove(best.Value);
						}
					}
				}, TaskScheduler.FromCurrentSynchronizationContext());
		}

		private void OnUndo()
		{
			if (!config.allowUndo) return;
			if (isAiThinking) return;
			try
			{
				board.UnmakeMove();
				ui.RenderBoard(board);
				GenerateLegalMoves();
				SaveIfEnabled();
			}
			catch
			{
				// no-op if no moves
			}
		}

		private void OnNewGame()
		{
			NewGame();
			UpdateUIFull();
		}

		private void OnDepthChanged(int depth)
		{
			config.aiSearchDepth = depth;
			ai.SetLimits(depth, config.aiTimeBudgetMs);
		}

		private void OnOfferDraw()
		{
			ui.SetGameOver(GameResult.Draw50Move, board.sideToMove); // generic draw enum reuse
			OnGameOver?.Invoke(GameResult.Draw50Move, PieceColor.White);
		}

		private void SaveIfEnabled()
		{
			if (!config.autoSaveEnabled) return;
			var data = new SaveData { fen = FEN.ToFen(board) };
			var json = JsonUtility.ToJson(data);
			File.WriteAllText(autosavePath, json, Encoding.UTF8);
		}

		private void TryLoad()
		{
			try
			{
				var json = File.ReadAllText(autosavePath, Encoding.UTF8);
				var data = JsonUtility.FromJson<SaveData>(json);
				board = new Board();
				FEN.LoadFromFen(board, data.fen);
			}
			catch (Exception ex)
			{
				Debug.LogWarning($"Failed to load autosave: {ex.Message}");
				board.SetupStartingPosition();
			}
		}
	}
}