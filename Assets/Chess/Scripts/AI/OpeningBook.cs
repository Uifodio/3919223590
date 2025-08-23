using System.Collections.Generic;

namespace Chess.AI
{
	public static class OpeningBook
	{
		private static readonly Dictionary<string, string[]> book = new Dictionary<string, string[]>
		{
			{ "", new[]{ "e4", "d4", "c4", "Nf3" } },
			{ "e4", new[]{ "e5", "c5", "e6", "c6" } },
			{ "d4", new[]{ "d5", "Nf6" } },
			{ "c4", new[]{ "e5", "Nf6" } },
			{ "Nf3", new[]{ "d5", "Nf6" } },
			// Italian
			{ "e4 e5", new[]{ "Nf3" } },
			{ "e4 e5 Nf3", new[]{ "Nc6" } },
			{ "e4 e5 Nf3 Nc6", new[]{ "Bc4" } },
			{ "e4 e5 Nf3 Nc6 Bc4", new[]{ "Bc5", "Nf6" } },
			// Ruy Lopez
			{ "e4 e5 Nf3 Nc6", new[]{ "Bb5" } },
			{ "e4 e5 Nf3 Nc6 Bb5", new[]{ "a6", "Nf6" } },
			// Sicilian Najdorf/Scheveningen
			{ "e4 c5 Nf3 d6", new[]{ "d4" } },
			{ "e4 c5 Nf3 d6 d4 cxd4 Nxd4", new[]{ "Nf6", "a6" } },
			// French
			{ "e4 e6", new[]{ "d4" } },
			{ "e4 e6 d4", new[]{ "d5" } },
			// Caro-Kann
			{ "e4 c6", new[]{ "d4" } },
			{ "e4 c6 d4", new[]{ "d5" } },
			// Scandinavian
			{ "e4 d5", new[]{ "exd5" } },
			// Queen's Gambit
			{ "d4 d5", new[]{ "c4" } },
			{ "d4 d5 c4", new[]{ "e6", "dxc4" } },
			{ "d4 d5 c4 e6", new[]{ "Nc3", "Nf3" } },
			// King's Indian
			{ "d4 Nf6", new[]{ "c4", "Nf3" } },
			{ "d4 Nf6 c4 g6", new[]{ "Nc3" } },
			// Nimzo-Indian
			{ "d4 Nf6 c4 e6", new[]{ "Nc3" } },
			{ "d4 Nf6 c4 e6 Nc3", new[]{ "Bb4" } },
			// English
			{ "c4 e5", new[]{ "Nc3", "g3" } },
			{ "c4 Nf6", new[]{ "Nc3", "g3" } },
		};

		public static bool TryGetBookMoves(string historySan, out string[] sanMoves)
		{
			return book.TryGetValue(historySan.Trim(), out sanMoves);
		}
	}
}