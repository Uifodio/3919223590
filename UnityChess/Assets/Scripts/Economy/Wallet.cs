using System;

namespace Chess
{
	public class Wallet
	{
		public int Balance { get; private set; }
		public event Action<int> OnBalanceChanged;

		public void Set(int amount)
		{
			Balance = amount;
			OnBalanceChanged?.Invoke(Balance);
		}

		public void Add(int amount)
		{
			Balance += amount;
			OnBalanceChanged?.Invoke(Balance);
		}

		public void Subtract(int amount)
		{
			Balance -= amount;
			OnBalanceChanged?.Invoke(Balance);
		}
	}
}