using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace Chess
{
	public class MoveListUI : MonoBehaviour
	{
		[SerializeField] private Text movesText;

		private readonly List<string> moves = new List<string>(256);

		public void Clear()
		{
			moves.Clear();
			Refresh();
		}

		public void AddMove(Move move)
		{
			string s = Move.SquareToString(move.FromSquare) + Move.SquareToString(move.ToSquare);
			if (move.Promotion != PieceType.None)
			{
				s += "=" + move.Promotion.ToString()[0];
			}
			moves.Add(s);
			Refresh();
		}

		private void Refresh()
		{
			movesText.text = string.Join(" ", moves);
		}
	}
}