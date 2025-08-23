# Unity Chess (Professional)

A full chess project for Unity with adjustable AI (iterative deepening + alpha-beta + quiescence), complete rules (castling, en passant, promotion, check/checkmate/stalemate), undo, auto-save, opening book, and draw detection. Uses CBurnett piece set rendered to PNG (CC BY-SA 3.0).

## Features
- Adjustable AI difficulty (depth, time budget)
- Opening book (common lines) + smarter AI (iterative deepening, quiescence, move ordering)
- Complete chess rules and legal move validation (no king captures)
- Draw rules: stalemate, 50-move, threefold repetition, insufficient material
- Undo/redo stack and Offer Draw button
- Auto-save and resume
- One-click Editor setup: downloads CBurnett PNGs (offline-ready), creates the scene, camera canvas, and UI
- Fallback UI if assets are missing (letters)
- Events for win/loss hooks (virtual economy integration)

## Quick Start
1. Open this project in Unity 2021.3+ or 2022.3+.
2. Wait for packages to restore (Vector Graphics, UGUI, TextMeshPro).
3. In the menu, go to `Tools > Chess > Setup Project`:
   - Installs Vector Graphics (if missing)
   - Downloads CBurnett SVG pieces into `Assets/Chess/Resources/CBurnett/`
   - Creates `Assets/Chess/Scenes/Chess.unity` and opens it
4. Enter Play Mode. Click a piece then a destination square to move.

## Adjustable AI and Openings
- Open the `ChessGameBootstrap` component in the scene.
- Configure:
  - AI Enabled, AI Plays Black/White
  - AI Search Depth and Time Budget (ms)
- The AI uses a built-in opening book for early moves, then switches to search.

## Undo and Auto-save
- Use the `Undo` button to revert the last move (player or AI).
- The game auto-saves after each move to `Application.persistentDataPath/chess_autosave.json`.
- On startup, the game will resume from the last auto-save if present.

## Draws
- The game will automatically declare a draw in these cases:
  - Stalemate (no legal moves, not in check)
  - 50-move rule (100 half-moves without pawn move or capture)
  - Threefold repetition (same position at least 3 times)
  - Insufficient material (e.g., K vs K, K+B vs K, K+N vs K)
- You can also click the `Offer Draw` button in the sidebar to agree to a draw.

## Assets: CBurnett SVG Chess Pieces
- Source category: `https://commons.wikimedia.org/wiki/Category:SVG_chess_pieces`
- PNGs downloaded via `Special:FilePath` with resizing query (width=256), e.g. `https://commons.wikimedia.org/wiki/Special:FilePath/Chess_plt45.svg?width=256`
- Stored under `Assets/Chess/Resources/CBurnett/`
- License: CC BY-SA 3.0 (see `LICENSES/`), attribution below.

### Attribution
- Chess piece set by Cburnett — licensed under CC BY-SA 3.0
- Attribution: "CBurnett chess piece set (SVG) — CC BY-SA 3.0". Source: `https://commons.wikimedia.org/wiki/Category:SVG_chess_pieces`

## How it works
- Engine: Pure C# move generator with legal move filtering, FEN, repetition, and check detection.
- AI: Minimax with alpha-beta, transposition table, quiescence search (captures), and configurable depth.
- UI: Procedurally generated board, square highlights, promotion dialog. Vector SVGs imported as sprites.
- Saving: JSON snapshot of FEN + ancillary state and move history.

## Integrations: Win/Loss Events & Virtual Currency
Hook into `GameEvents` on `ChessGameController`:
- `OnGameOver(GameResult result, PieceColor winner)`
- Add listeners to adjust your currency balances when matches end.

## Editor Tools
- `Tools > Chess > Setup Project`: Installs packages, downloads assets, creates scene.
- `Tools > Chess > Download CBurnett Assets`: Redownload/refresh SVGs.
- `Tools > Chess > Create Chess Scene`: Rebuilds scene with default layout.

## Fallback UI
If SVGs are missing, the board renders with text-based piece labels. You can still play and test.

## Folder Structure
- `Assets/Chess/Scripts` — engine, AI, UI, save, editor
- `Assets/Chess/Editor` — setup and scene creation tools
- `Assets/Chess/Resources/CBurnett` — SVG pieces (downloaded)
- `Assets/Chess/Scenes` — generated scene
- `LICENSES/` — license texts and attribution

## License
- Code: MIT (see `LICENSES/CODE_LICENSE.txt`).
- CBurnett pieces: CC BY-SA 3.0. You must retain attribution and share-alike if you redistribute modified assets.

## Credits
- CBurnett for the SVG chess piece set.
- Unity Vector Graphics package team.