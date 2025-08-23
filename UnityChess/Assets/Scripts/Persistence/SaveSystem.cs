using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using UnityEngine;

namespace Chess
{
	[Serializable]
	public class SaveData
	{
		public string Fen;
		public bool HumanPlaysWhite;
		public bool HumanPlaysBlack;
		public int AiDepth;
		public int WalletBalance;
		public List<string> HistoryFen;
	}

	public static class SaveSystem
	{
		private static string SavePath => Path.Combine(Application.persistentDataPath, "chess_autosave.json");

		public static void Save(Board board, bool humanWhite, bool humanBlack, int aiDepth, Wallet wallet)
		{
			try
			{
				var data = new SaveData
				{
					Fen = FenUtility.ToFen(board),
					HumanPlaysWhite = humanWhite,
					HumanPlaysBlack = humanBlack,
					AiDepth = aiDepth,
					WalletBalance = wallet?.Balance ?? 0,
					HistoryFen = new List<string>()
				};
				File.WriteAllText(SavePath, JsonUtility.ToJson(data, true), Encoding.UTF8);
			}
			catch (Exception e)
			{
				Debug.LogError($"Save failed: {e}");
			}
		}

		public static bool TryLoad(out SaveData data)
		{
			data = null;
			try
			{
				if (!File.Exists(SavePath)) return false;
				string json = File.ReadAllText(SavePath, Encoding.UTF8);
				data = JsonUtility.FromJson<SaveData>(json);
				return data != null;
			}
			catch (Exception e)
			{
				Debug.LogError($"Load failed: {e}");
				return false;
			}
		}

		public static void Delete()
		{
			try
			{
				if (File.Exists(SavePath)) File.Delete(SavePath);
			}
			catch (Exception e)
			{
				Debug.LogError($"Delete save failed: {e}");
			}
		}
	}
}