using System.Collections.Generic;

namespace Chess.AI
{
	public static class OpeningBook
	{
		private static readonly Dictionary<string, string[]> book = new Dictionary<string, string[]>
		{
			// Starting choices
			{ "", new[]{ "e4", "d4", "c4", "Nf3" } },
			{ "e4", new[]{ "e5", "c5", "e6", "c6" } },
			{ "d4", new[]{ "d5", "Nf6" } },
			{ "c4", new[]{ "e5", "Nf6" } },
			{ "Nf3", new[]{ "d5", "Nf6" } },
			// Italian / Two Knights / Giuoco Piano
			{ "e4 e5", new[]{ "Nf3" } },
			{ "e4 e5 Nf3", new[]{ "Nc6" } },
			{ "e4 e5 Nf3 Nc6", new[]{ "Bc4", "Bb5" } },
			{ "e4 e5 Nf3 Nc6 Bc4", new[]{ "Bc5", "Nf6" } },
			{ "e4 e5 Nf3 Nc6 Bc4 Nf6", new[]{ "Ng5" } },
			// Ruy Lopez mainlines
			{ "e4 e5 Nf3 Nc6 Bb5", new[]{ "a6", "Nf6" } },
			{ "e4 e5 Nf3 Nc6 Bb5 a6", new[]{ "Ba4", "Bxc6" } },
			// Sicilian mainlines
			{ "e4 c5 Nf3", new[]{ "d6", "Nc6", "e6" } },
			{ "e4 c5 Nf3 d6", new[]{ "d4" } },
			{ "e4 c5 Nf3 d6 d4 cxd4 Nxd4", new[]{ "Nf6", "a6" } },
			{ "e4 c5 Nf3 Nc6", new[]{ "d4", "Bb5" } },
			// French
			{ "e4 e6 d4", new[]{ "d5" } },
			{ "e4 e6 d4 d5", new[]{ "Nc3", "Nd2", "exd5" } },
			// Caro-Kann
			{ "e4 c6 d4", new[]{ "d5" } },
			{ "e4 c6 d4 d5", new[]{ "Nc3", "Nd2" } },
			// Scandinavian
			{ "e4 d5", new[]{ "exd5" } },
			// Queen's Gambit
			{ "d4 d5", new[]{ "c4" } },
			{ "d4 d5 c4", new[]{ "e6", "dxc4" } },
			{ "d4 d5 c4 e6", new[]{ "Nc3", "Nf3" } },
			{ "d4 d5 c4 dxc4", new[]{ "Nf3", "e3" } },
			// King's Indian
			{ "d4 Nf6", new[]{ "c4", "Nf3" } },
			{ "d4 Nf6 c4 g6", new[]{ "Nc3" } },
			{ "d4 Nf6 c4 g6 Nc3 Bg7", new[]{ "e4", "Nf3" } },
			// Nimzo-Indian
			{ "d4 Nf6 c4 e6 Nc3", new[]{ "Bb4" } },
			// English (symmetric and reversed Sicilian ideas)
			{ "c4 e5", new[]{ "Nc3", "g3" } },
			{ "c4 Nf6", new[]{ "Nc3", "g3" } },
		};

		public static bool TryGetBookMoves(string historySan, out string[] sanMoves)
		{
			return book.TryGetValue(historySan.Trim(), out sanMoves);
		}
	}
}