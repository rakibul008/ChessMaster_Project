import chess
from core.events import game_events
from themes.assets import ClassicTheme, HighContrastTheme


class GameState:
    _instance = None
    DEFAULT_TIME = 600

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameState, cls).__new__(cls)
            cls._instance.board = chess.Board()
            cls._instance.history = []
            cls._instance.selected_square = None
            cls._instance.white_time = cls.DEFAULT_TIME
            cls._instance.black_time = cls.DEFAULT_TIME
            cls._instance.game_active = True
            cls._instance.mode = "PVP"
            cls._instance.ai_difficulty = "Easy"
            cls._instance.theme_mode = "Classic"
            cls._instance.theme = ClassicTheme()
        return cls._instance

    def reset(self):
        self.board.reset()
        self.history = []
        self.selected_square = None
        self.white_time = self.DEFAULT_TIME
        self.black_time = self.DEFAULT_TIME
        self.game_active = True
        game_events.trigger("game_reset")

    def update_timer(self, dt):
        if not self.game_active or self.board.is_game_over():
            return

        if self.board.turn == chess.WHITE:
            self.white_time -= dt
            if self.white_time <= 0:
                self.white_time = 0
                self.game_active = False
                game_events.trigger("game_over", "0-1")
        else:
            self.black_time -= dt
            if self.black_time <= 0:
                self.black_time = 0
                self.game_active = False
                game_events.trigger("game_over", "1-0")

    def make_move(self, move):
        if move in self.board.legal_moves:
            mover_color = self.board.turn
            san_text = self.board.san(move)
            self.history.append(san_text)
            self.board.push(move)

            if mover_color == chess.WHITE:
                self.white_time = self.DEFAULT_TIME
            else:
                self.black_time = self.DEFAULT_TIME

            game_events.trigger("move_made", move)

            if self.board.is_game_over():
                self.game_active = False
                game_events.trigger("game_over", self.board.result())
            return True
        return False

    def toggle_theme(self):
        if self.theme_mode == "Classic":
            self.theme = HighContrastTheme()
            self.theme_mode = "High Contrast"
        else:
            self.theme = ClassicTheme()
            self.theme_mode = "Classic"
        game_events.trigger("theme_changed")