using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace Chess
{
	public class GameManager : MonoBehaviour
	{
		[SerializeField] private int aiDepth = 3;
		[SerializeField] private bool humanPlaysWhite = true;
		[SerializeField] private bool humanPlaysBlack = false;
		[SerializeField] private bool autosaveEnabled = true;
		[SerializeField] private TextAsset initialFen;

		public Board Board { get; private set; }
		public ChessAI Ai { get; private set; }
		public Wallet Wallet { get; private set; }

		public event Action<GameResult> OnGameEnded;
		public event Action OnBoardChanged;

		private float autosaveInterval = 5f;
		private float autosaveTimer = 0f;
		private bool isAiThinking = false;

		private readonly List<string> positionHistory = new List<string>(256);
		private readonly Dictionary<string, int> repetitionCounts = new Dictionary<string, int>(256);

		private void Awake()
		{
			Board = new Board();
			Ai = new ChessAI { MaxDepth = aiDepth };
			Wallet = new Wallet();

			bool loaded = false;
			if (autosaveEnabled && SaveSystem.TryLoad(out var data))
			{
				FenUtility.LoadPositionFromFen(Board, data.Fen);
				humanPlaysWhite = data.HumanPlaysWhite;
				humanPlaysBlack = data.HumanPlaysBlack;
				aiDepth = data.AiDepth;
				Ai.MaxDepth = aiDepth;
				Wallet.Set(data.WalletBalance);
				loaded = true;
			}

			if (!loaded)
			{
				Board.Clear();
				FenUtility.LoadPositionFromFen(Board, initialFen != null ? initialFen.text : FenUtility.StandardStartPosition);
			}

			ResetHistory();
		}

		private void Update()
		{
			if (autosaveEnabled)
			{
				autosaveTimer += Time.deltaTime;
				if (autosaveTimer >= autosaveInterval)
				{
					Autosave();
					autosaveTimer = 0f;
				}
			}

			// AI move when it's AI's turn
			if (IsAITurn() && !isAiThinking)
			{
				StartCoroutine(DoAIMoveCoroutine());
			}
		}

		private void OnApplicationQuit()
		{
			if (autosaveEnabled) Autosave();
		}

		private IEnumerator DoAIMoveCoroutine()
		{
			isAiThinking = true;
			yield return null;
			if (!IsAITurn()) { isAiThinking = false; yield break; }
			Move best = Ai.FindBestMove(Board);
			Board.ApplyMove(best);
			RecordPositionKey();
			OnBoardChanged?.Invoke();
			CheckEndState();
			isAiThinking = false;
		}

		public bool TryMakeHumanMove(int fromSquare, int toSquare, PieceType promotion = PieceType.None)
		{
			if (!IsHumanTurn()) return false;
			foreach (var move in Board.GenerateLegalMoves())
			{
				if (move.FromSquare == fromSquare && move.ToSquare == toSquare)
				{
					Move finalMove = move;
					if ((move.Flags & MoveFlag.Promotion) != 0 && promotion != PieceType.None)
					{
						finalMove.Promotion = promotion;
					}
					Board.ApplyMove(finalMove);
					RecordPositionKey();
					OnBoardChanged?.Invoke();
					CheckEndState();
					return true;
				}
			}
			return false;
		}

		public void Undo()
		{
			if (positionHistory.Count > 0)
			{
				UnrecordPositionKey();
			}
			Board.UndoLastMove();
			OnBoardChanged?.Invoke();
		}

		public void NewGame()
		{
			Board.Clear();
			FenUtility.LoadPositionFromFen(Board, FenUtility.StandardStartPosition);
			ResetHistory();
			OnBoardChanged?.Invoke();
		}

		private void ResetHistory()
		{
			positionHistory.Clear();
			repetitionCounts.Clear();
			RecordPositionKey();
		}

		private void RecordPositionKey()
		{
			string key = FenUtility.ToFenKey(Board);
			positionHistory.Add(key);
			if (repetitionCounts.ContainsKey(key)) repetitionCounts[key] = repetitionCounts[key] + 1; else repetitionCounts[key] = 1;
		}

		private void UnrecordPositionKey()
		{
			if (positionHistory.Count == 0) return;
			string key = positionHistory[positionHistory.Count - 1];
			positionHistory.RemoveAt(positionHistory.Count - 1);
			if (repetitionCounts.ContainsKey(key))
			{
				repetitionCounts[key] = Mathf.Max(0, repetitionCounts[key] - 1);
			}
		}

		private void CheckEndState()
		{
			// Repetition
			string key = FenUtility.ToFenKey(Board);
			if (repetitionCounts.TryGetValue(key, out int count) && count >= 3)
			{
				OnGameEnded?.Invoke(GameResult.Draw(GameEndReason.Repetition));
				return;
			}

			// Insufficient material
			if (Board.HasInsufficientMaterial())
			{
				OnGameEnded?.Invoke(GameResult.Draw(GameEndReason.InsufficientMaterial));
				return;
			}

			// No legal moves => checkmate or stalemate
			var legal = Board.GenerateLegalMoves();
			bool any = false;
			foreach (var _ in legal) { any = true; break; }
			if (!any)
			{
				PlayerColor us = Board.SideToMove;
				int kingSq = Board.GetKingSquare(us);
				bool inCheck = Board.IsSquareAttackedBy(kingSq, us == PlayerColor.White ? PlayerColor.Black : PlayerColor.White);
				if (inCheck)
				{
					PlayerColor winner = us == PlayerColor.White ? PlayerColor.Black : PlayerColor.White;
					OnGameEnded?.Invoke(GameResult.Mate(winner));
					RewardOutcome(winner);
				}
				else
				{
					OnGameEnded?.Invoke(GameResult.Draw(GameEndReason.Stalemate));
				}
				return;
			}

			// Fifty-move rule
			if (Board.HalfmoveClock >= 100)
			{
				OnGameEnded?.Invoke(GameResult.Draw(GameEndReason.FiftyMoveRule));
			}
		}

		private void RewardOutcome(PlayerColor winner)
		{
			// Simple hooks; amount can be tuned in inspector or elsewhere
			int winReward = 100;
			int lossPenalty = 50;
			bool humanWon = (winner == PlayerColor.White && humanPlaysWhite) || (winner == PlayerColor.Black && humanPlaysBlack);
			if (humanWon) Wallet.Add(winReward); else Wallet.Subtract(lossPenalty);
		}

		private void Autosave()
		{
			SaveSystem.Save(Board, humanPlaysWhite, humanPlaysBlack, aiDepth, Wallet);
		}

		public bool IsHumanTurn()
		{
			return (Board.SideToMove == PlayerColor.White && humanPlaysWhite) || (Board.SideToMove == PlayerColor.Black && humanPlaysBlack);
		}

		public bool IsAITurn()
		{
			return (Board.SideToMove == PlayerColor.White && !humanPlaysWhite) || (Board.SideToMove == PlayerColor.Black && !humanPlaysBlack);
		}
	}
}