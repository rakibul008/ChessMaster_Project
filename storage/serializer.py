import json
import chess
import os

SAVE_FILE = "savegame.json"


class GameSerializer:
    @staticmethod
    def save_game(game_state):
        data = {
            "fen": game_state.board.fen(),
            "theme": game_state.theme_mode,
            "turn": "White" if game_state.board.turn == chess.WHITE else "Black",
            "history_count": len(game_state.history)
        }

        try:
            with open(SAVE_FILE, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Game Saved Successfully to {SAVE_FILE}")
            return True
        except Exception as e:
            print(f"ERROR: Could not save game. {e}")
            return False

    @staticmethod
    def load_game(game_state):
        if not os.path.exists(SAVE_FILE):
            print("No save file found.")
            return False

        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)

            game_state.board.set_fen(data["fen"])

            if data["theme"] == "High Contrast":
                if game_state.theme_mode != "High Contrast":
                    game_state.toggle_theme()
            elif data["theme"] == "Classic":
                if game_state.theme_mode != "Classic":
                    game_state.toggle_theme()

            print(f"Game Loaded! Turn: {data['turn']}")
            return True

        except json.JSONDecodeError:
            print("ERROR: Save file is corrupted.")
            return False
        except Exception as e:
            print(f"ERROR: Could not load game. {e}")
            return False
