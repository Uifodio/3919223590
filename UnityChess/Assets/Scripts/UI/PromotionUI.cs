using System;
using UnityEngine;
using UnityEngine.UI;

namespace Chess
{
	public class PromotionUI : MonoBehaviour
	{
		[SerializeField] private GameObject panel;
		[SerializeField] private Button queenButton;
		[SerializeField] private Button rookButton;
		[SerializeField] private Button bishopButton;
		[SerializeField] private Button knightButton;

		private Action<PieceType> onChosen;

		private void Awake()
		{
			Hide();
			queenButton.onClick.AddListener(() => Choose(PieceType.Queen));
			rookButton.onClick.AddListener(() => Choose(PieceType.Rook));
			bishopButton.onClick.AddListener(() => Choose(PieceType.Bishop));
			knightButton.onClick.AddListener(() => Choose(PieceType.Knight));
		}

		public void Show(Action<PieceType> callback)
		{
			onChosen = callback;
			panel.SetActive(true);
		}

		public void Hide()
		{
			panel.SetActive(false);
			onChosen = null;
		}

		private void Choose(PieceType type)
		{
			onChosen?.Invoke(type);
			Hide();
		}
	}
}