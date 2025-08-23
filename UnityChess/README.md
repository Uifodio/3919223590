# UnityChess: Professional Chess for Unity (AI, Undo, Autosave)

A production-ready chess game for Unity including:

- Adjustable AI (minimax + alpha-beta). Depth-driven strength.
- Complete rules: legal moves, check, checkmate, stalemate, castling, en passant, promotions.
- Undo stack, autosave/load, and save-on-quit.
- Basic but clean 2D UI (Unity UI) with highlight and input. Works without sprites via text fallback; you can plug in any free board/piece sprites.
- Economy hooks to grant/charge virtual currency on win/loss.
- Editor tool to auto-create a sample playable scene.

## Requirements
- Unity 2022.3 LTS or newer
- TextMeshPro (Install via Window > TextMeshPro > Import TMP Essential Resources)

## Quickstart
1) Open the project in Unity Hub (path: `UnityChess`).
2) From the menu, run: Tools > Chess > Create Sample Scene. Save the scene (e.g., `Assets/Scenes/Sample.unity`).
3) Press Play. Click a piece, then a highlighted square to move. Use Undo/New Game.
4) AI plays for the side not assigned to Human in `GameManager`.

## Project Structure
- `Assets/Scripts/Chess`
  - `Piece.cs`: piece and color enums, FEN conversion helpers
  - `Move.cs`: move struct and flags (capture, en passant, castling, promotion)
  - `Board.cs`: board state, legal move generation, apply/undo, attacks, insufficient material
  - `FenUtility.cs`: FEN load/save and repetition keys
- `Assets/Scripts/Game`
  - `GameManager.cs`: orchestration, AI turns, history, repetition/fifty-move, autosave, rewards
  - `ChessAI.cs`: minimax + alpha-beta, material + mobility evaluation, adjustable depth
  - `GameResult.cs`: end state types
- `Assets/Scripts/UI`
  - `BoardView.cs`: grid UI, input handling, highlights, piece rendering (sprites or text fallback)
  - `HUD.cs`: Undo/New Game buttons and wallet balance label
- `Assets/Scripts/Editor`
  - `SceneAutoBuilder.cs`: menu to build a complete sample scene with wiring and EventSystem
- `Assets/Scripts/Economy`
  - `Wallet.cs`: simple currency API with change event
- `Assets/Scripts/Persistence`
  - `SaveSystem.cs`: JSON autosave to `Application.persistentDataPath`

## Features and How To Use
- Castling and en passant: fully supported, including path safety checks and correct undo.
- Promotion: UI chooses queen by default. You can add a popup to select other pieces and pass the chosen `PieceType` to `GameManager.TryMakeHumanMove`.
- Undo: calls `GameManager.Undo()`; multiple undos supported.
- Autosave: every 5 seconds of play and on quit. Restored next launch.
- Economy: on checkmate, `RewardOutcome` updates `Wallet`. Hook into `Wallet.OnBalanceChanged` or read `Wallet.Balance`.

## Customization
- AI strength: set `GameManager.aiDepth`. Depth 1-2 is light, 3-4 casual, 5-6 stronger but slower. For production, consider iterative deepening and time controls.
- Who plays: toggle `humanPlaysWhite` / `humanPlaysBlack` on `GameManager`.
- Rewards: edit `RewardOutcome()` in `GameManager.cs`. Example: add XP, analytics, or difficulty-based payouts.
- UI/Art: assign your own sprites to `BoardView` (`pieceSprites` size 12: WP, WN, WB, WR, WQ, WK, BP, BN, BB, BR, BQ, BK). If not assigned, text letters render.
- Board assets: any free square/piece sprites can be used. Popular free options include CC0 chess piece sprite sheets. Import and drop into the inspector.

## Save Data
- Path: `Application.persistentDataPath/chess_autosave.json`
- Contents: FEN, side assignment, AI depth, wallet balance.

## Extending
- Time controls: add a clock and per-move time budget; link to AI search.
- Move list: track SAN/PGN; show a scrollable history UI.
- Opening book: add a lightweight book for early moves.
- Stronger engine: you can swap `ChessAI` for an external UCI engine (e.g., Stockfish) if desired.

## Notes
- The rules engine is independent of rendering and can be unit-tested headless.
- Repetition detection uses a FEN key without half/fullmove counters.
- Insufficient material: covers common cases (K vs K, K+minor vs K, bishops on same color).