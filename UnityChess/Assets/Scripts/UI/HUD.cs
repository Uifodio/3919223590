using UnityEngine;
using UnityEngine.UI;

namespace Chess
{
	public class HUD : MonoBehaviour
	{
		[SerializeField] private GameManager gameManager;
		[SerializeField] private Button undoButton;
		[SerializeField] private Button newGameButton;
		[SerializeField] private Text balanceText;

		private void Start()
		{
			undoButton.onClick.AddListener(() => gameManager.Undo());
			newGameButton.onClick.AddListener(() => gameManager.NewGame());
			if (gameManager.Wallet != null)
			{
				gameManager.Wallet.OnBalanceChanged += OnBalanceChanged;
				OnBalanceChanged(gameManager.Wallet.Balance);
			}
		}

		private void OnDestroy()
		{
			if (gameManager != null && gameManager.Wallet != null)
			{
				gameManager.Wallet.OnBalanceChanged -= OnBalanceChanged;
			}
		}

		private void OnBalanceChanged(int amount)
		{
			balanceText.text = $"$ {amount}";
		}
	}
}