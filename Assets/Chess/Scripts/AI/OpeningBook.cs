using System.Collections.Generic;

namespace Chess.AI
{
	public static class OpeningBook
	{
		// Simple book: map history prefix to next move in SAN
		private static readonly Dictionary<string, string[]> book = new Dictionary<string, string[]>
		{
			{ "", new[]{ "e4", "d4", "c4", "Nf3" } },
			{ "e4", new[]{ "e5", "c5", "e6", "c6" } },
			{ "d4", new[]{ "d5", "Nf6" } },
			{ "c4", new[]{ "e5", "Nf6" } },
			{ "Nf3", new[]{ "d5", "Nf6" } },
			// Italian: e4 e5 Nf3 Nc6 Bc4 Bc5
			{ "e4 e5", new[]{ "Nf3" } },
			{ "e4 e5 Nf3", new[]{ "Nc6" } },
			{ "e4 e5 Nf3 Nc6", new[]{ "Bc4" } },
			{ "e4 e5 Nf3 Nc6 Bc4", new[]{ "Bc5" } },
			// Sicilian: e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3 a6
			{ "e4 c5", new[]{ "Nf3" } },
			{ "e4 c5 Nf3", new[]{ "d6", "Nc6" } },
			// Queen's Gambit: d4 d5 c4 e6 Nc3 Nf6
			{ "d4 d5", new[]{ "c4" } },
			{ "d4 d5 c4", new[]{ "e6", "dxc4" } },
		};

		public static bool TryGetBookMoves(string historySan, out string[] sanMoves)
		{
			return book.TryGetValue(historySan.Trim(), out sanMoves);
		}
	}
}