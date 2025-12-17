import pygame
import sys
import chess
import time

from core.settings import *
from core.game_state import GameState
from pieces.piece_factory import PieceRenderer
from ai.random_bot import RandomBot
from ai.minimax_bot import MinimaxBot
from editor.board_builder import BoardBuilder
from storage.serializer import GameSerializer
from ui.components import Button

STATE_MENU = "MENU"
STATE_DIFFICULTY = "DIFFICULTY"
STATE_GAME = "GAME"
STATE_EDITOR = "EDITOR"

SIDEBAR_X = WIDTH
SIDEBAR_WIDTH = 350
GAME_WIDTH = WIDTH + SIDEBAR_WIDTH
GAME_HEIGHT = HEIGHT


class ChessApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT), pygame.RESIZABLE)

        self.canvas = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

        self.offsets = (0, 0)

        pygame.display.set_caption("Smart Chess Game")
        self.clock = pygame.time.Clock()

        try:
            bg_img = pygame.image.load("assets/background.jpg")
            self.background = pygame.transform.smoothscale(bg_img, (GAME_WIDTH, GAME_HEIGHT))
            self.using_bg_image = True
        except Exception:
            self.background = (30, 30, 30)
            self.using_bg_image = False

        self.game = GameState()
        self.builder = BoardBuilder()
        self.piece_renderer = PieceRenderer()

        self.running = True
        self.current_state = STATE_MENU
        self.is_flipped = False

        self.bot_easy = RandomBot()
        self.bot_hard = MinimaxBot(depth=3)

        self.ui_font = pygame.font.SysFont("Arial", 20)
        self.clock_font = pygame.font.SysFont("Consolas", 34, bold=True)
        self.menu_font = pygame.font.SysFont("Arial", 40, bold=True)
        self.large_font = pygame.font.SysFont("Arial", 60, bold=True)

        self.editor_brush = {'type': chess.PAWN, 'color': chess.WHITE}
        self.create_menus()

    def create_menus(self):
        center_x = GAME_WIDTH // 2 - 100
        self.btn_pvp = Button(center_x, 300, 200, 60, "Human vs Human", self.ui_font, (50, 50, 50), HIGHLIGHT,
                              self.set_mode_pvp)
        self.btn_ai = Button(center_x, 400, 200, 60, "Human vs AI", self.ui_font, (50, 50, 50), HIGHLIGHT,
                             self.set_mode_ai_select)
        self.btn_editor = Button(center_x, 500, 200, 60, "Puzzle Editor", self.ui_font, (50, 50, 50), HIGHLIGHT,
                                 self.set_mode_editor)
        self.btn_exit = Button(center_x, 600, 200, 60, "Exit", self.ui_font, (180, 50, 50), (255, 80, 80),
                               self.quit_game)
        self.btn_easy = Button(center_x, 350, 200, 60, "Easy Mode", self.ui_font, (50, 150, 50), HIGHLIGHT,
                               lambda: self.start_ai_game("Easy"))
        self.btn_hard = Button(center_x, 450, 200, 60, "Hard Mode", self.ui_font, (150, 50, 50), HIGHLIGHT,
                               lambda: self.start_ai_game("Hard"))

    def set_mode_pvp(self):
        self.game.mode = "PVP"
        self.game.reset()
        self.current_state = STATE_GAME

    def set_mode_ai_select(self):
        self.current_state = STATE_DIFFICULTY

    def set_mode_editor(self):
        self.builder.clear()
        self.current_state = STATE_EDITOR

    def start_ai_game(self, difficulty):
        self.game.mode = "AI"
        self.game.ai_difficulty = difficulty
        self.game.reset()
        self.current_state = STATE_GAME

    def quit_game(self):
        self.running = False

    def return_to_menu(self):
        self.current_state = STATE_MENU

    def handle_ai_turn(self):
        if self.game.board.is_game_over(): return
        if self.game.mode == "AI" and self.game.board.turn == chess.BLACK:
            pygame.display.set_caption("Smart Chess Game - AI Thinking...")
            pygame.event.pump()
            time.sleep(0.5)
            if self.game.ai_difficulty == "Easy":
                move = self.bot_easy.get_move(self.game.board)
            else:
                move = self.bot_hard.get_move(self.game.board)
            if move: self.game.make_move(move)
            pygame.display.set_caption("Smart Chess Game")

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            if self.using_bg_image:
                self.canvas.blit(self.background, (0, 0))
            else:
                self.canvas.fill((30, 30, 30))

            real_mx, real_my = pygame.mouse.get_pos()
            current_w, current_h = self.screen.get_size()

            offset_x = (current_w - GAME_WIDTH) // 2
            offset_y = (current_h - GAME_HEIGHT) // 2
            self.offsets = (offset_x, offset_y)

            mouse_pos = (real_mx - offset_x, real_my - offset_y)

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT: self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f: pygame.display.toggle_fullscreen()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    event.pos = (event.pos[0] - offset_x, event.pos[1] - offset_y)

            if self.current_state == STATE_MENU:
                self.draw_menu(events, mouse_pos)
            elif self.current_state == STATE_DIFFICULTY:
                self.draw_difficulty(events, mouse_pos)
            elif self.current_state == STATE_GAME:
                self.game.update_timer(dt)
                self.handle_game_input(events, mouse_pos)
                self.draw_game_screen()
                self.handle_ai_turn()
            elif self.current_state == STATE_EDITOR:
                self.handle_editor_input(events, mouse_pos)
                self.draw_editor_screen()

            self.screen.fill((0, 0, 0))
            self.screen.blit(self.canvas, (offset_x, offset_y))

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def draw_menu(self, events, mouse_pos):
        title = self.menu_font.render("SMART CHESS GAME", True, WHITE)
        self.canvas.blit(title, title.get_rect(center=(GAME_WIDTH // 2, 150)))
        for btn in [self.btn_pvp, self.btn_ai, self.btn_editor, self.btn_exit]:
            btn.update(mouse_pos)
            btn.draw(self.canvas)
            for e in events: btn.check_click(e)

    def draw_difficulty(self, events, mouse_pos):
        title = self.menu_font.render("SELECT DIFFICULTY", True, WHITE)
        self.canvas.blit(title, title.get_rect(center=(GAME_WIDTH // 2, 150)))
        for btn in [self.btn_easy, self.btn_hard]:
            btn.update(mouse_pos)
            btn.draw(self.canvas)
            for e in events: btn.check_click(e)

    def handle_game_input(self, events, mouse_pos):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.return_to_menu()
                if event.key == pygame.K_t: self.game.toggle_theme()
                if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL): GameSerializer.save_game(
                    self.game)
                if event.key == pygame.K_l and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    if GameSerializer.load_game(self.game): self.game.selected_square = None
                if event.key == pygame.K_o: self.is_flipped = not self.is_flipped

                if event.key == pygame.K_r:
                    self.game.reset()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.game.mode == "AI" and self.game.board.turn == chess.BLACK: return
                if not self.game.board.is_game_over() and self.game.game_active:
                    x, y = mouse_pos
                    if x < WIDTH:
                        c_visual = x // SQUARE_SIZE
                        r_visual = y // SQUARE_SIZE
                        if self.is_flipped:
                            c, r = 7 - c_visual, r_visual
                        else:
                            c, r = c_visual, 7 - r_visual
                        clicked_sq = chess.square(c, r)

                        if self.game.selected_square is None:
                            p = self.game.board.piece_at(clicked_sq)
                            if p and p.color == self.game.board.turn: self.game.selected_square = clicked_sq
                        else:
                            move = chess.Move(self.game.selected_square, clicked_sq)
                            if chess.square_rank(clicked_sq) in [0, 7] and \
                                    self.game.board.piece_at(self.game.selected_square).piece_type == chess.PAWN:
                                move = chess.Move(self.game.selected_square, clicked_sq, promotion=chess.QUEEN)
                            if self.game.make_move(move):
                                self.game.selected_square = None
                            else:
                                p = self.game.board.piece_at(clicked_sq)
                                if p and p.color == self.game.board.turn:
                                    self.game.selected_square = clicked_sq
                                else:
                                    self.game.selected_square = None

    def format_time(self, seconds):
        mins = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{mins:02}:{secs:02}"

    def draw_sidebar_logic(self, is_editor):
        panel = pygame.Surface((SIDEBAR_WIDTH, GAME_HEIGHT))
        panel.set_alpha(250)
        panel.fill((235, 235, 235))
        self.canvas.blit(panel, (WIDTH, 0))

        x_start = WIDTH + 20
        content_width = SIDEBAR_WIDTH - 40
        y_cursor = 30

        TEXT_COLOR = (20, 20, 20)
        SUB_TEXT_COLOR = (60, 60, 60)

        if is_editor:
            lines = ["EDITOR MODE", "L-Click: Place", "R-Click: Delete", "T: Theme", "Enter: Play", "Esc: Menu"]
            for i, line in enumerate(lines):
                t = self.ui_font.render(line, True, TEXT_COLOR)
                self.canvas.blit(t, (x_start, 50 + i * 40))
            return

        pygame.draw.rect(self.canvas, (255, 255, 255), (x_start, y_cursor, content_width, 50), border_radius=8)
        pygame.draw.rect(self.canvas, (100, 100, 100), (x_start, y_cursor, content_width, 50), 2, border_radius=8)
        w_time = self.format_time(self.game.white_time)
        w_surf = self.clock_font.render(f"White: {w_time}", True, BLACK)
        self.canvas.blit(w_surf, (x_start + 15, y_cursor + 8))
        y_cursor += 60

        pygame.draw.rect(self.canvas, (40, 40, 40), (x_start, y_cursor, content_width, 50), border_radius=8)
        b_time = self.format_time(self.game.black_time)
        b_surf = self.clock_font.render(f"Black: {b_time}", True, WHITE)
        self.canvas.blit(b_surf, (x_start + 15, y_cursor + 7))
        y_cursor += 70

        if self.game.board.is_check():
            warn_surf = self.large_font.render("CHECK!", True, (200, 0, 0))
            warn_rect = warn_surf.get_rect(center=(x_start + content_width // 2, y_cursor + 35))
            self.canvas.blit(warn_surf, warn_rect)
            y_cursor += 70
        else:
            y_cursor += 10

        board_pieces = self.game.board.piece_map().values()
        full_set = {chess.PAWN: 8, chess.KNIGHT: 2, chess.BISHOP: 2, chess.ROOK: 2, chess.QUEEN: 1}

        missing_w = []
        missing_b = []
        for p_type, count in full_set.items():
            curr_w = sum(1 for p in board_pieces if p.piece_type == p_type and p.color == chess.WHITE)
            for _ in range(count - curr_w): missing_w.append(p_type)
            curr_b = sum(1 for p in board_pieces if p.piece_type == p_type and p.color == chess.BLACK)
            for _ in range(count - curr_b): missing_b.append(p_type)

        if missing_b:
            header = self.ui_font.render("Black Lost:", True, SUB_TEXT_COLOR)
            self.canvas.blit(header, (x_start, y_cursor))
            y_cursor += 50
            for i, p_type in enumerate(missing_b):
                cx, cy = x_start + 20 + (i % 8) * 40, y_cursor + (i // 8) * 40
                img = self.piece_renderer.get_small_image_by_type(p_type, chess.BLACK)
                if img: self.canvas.blit(img, img.get_rect(center=(cx, cy)))
            y_cursor += ((len(missing_b) - 1) // 8 + 1) * 40 + 20

        if missing_w:
            header = self.ui_font.render("White Lost:", True, SUB_TEXT_COLOR)
            self.canvas.blit(header, (x_start, y_cursor))
            y_cursor += 50
            for i, p_type in enumerate(missing_w):
                cx, cy = x_start + 20 + (i % 8) * 40, y_cursor + (i // 8) * 40
                img = self.piece_renderer.get_small_image_by_type(p_type, chess.WHITE)
                if img: self.canvas.blit(img, img.get_rect(center=(cx, cy)))
            y_cursor += ((len(missing_w) - 1) // 8 + 1) * 40 + 20

        y_cursor += 10
        hist_header = self.ui_font.render("Last Moves:", True, (0, 50, 150))
        self.canvas.blit(hist_header, (x_start, y_cursor))
        y_cursor += 30
        recent_history = self.game.history[-8:]
        for i in range(0, len(recent_history), 2):
            turn_num = (len(self.game.history) - len(recent_history) + i) // 2 + 1
            w_move = recent_history[i]
            b_move = recent_history[i + 1] if i + 1 < len(recent_history) else ""
            t = self.ui_font.render(f"{turn_num}. {w_move}   {b_move}", True, TEXT_COLOR)
            self.canvas.blit(t, (x_start + 10, y_cursor))
            y_cursor += 25

    def draw_game_screen(self):
        self.draw_board_logic(self.game.board, self.game.theme, self.game.selected_square, self.piece_renderer)
        self.draw_sidebar_logic(False)
        if not self.game.game_active: self.draw_game_over_popup()

    def draw_game_over_popup(self):
        overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.canvas.blit(overlay, (0, 0))
        if self.game.white_time <= 0:
            msg, color = "BLACK WINS (Time)", (100, 100, 255)
        elif self.game.black_time <= 0:
            msg, color = "WHITE WINS (Time)", (255, 255, 255)
        else:
            outcome = self.game.board.outcome()
            if outcome and outcome.winner == chess.WHITE:
                msg, color = "WHITE WINS!", (255, 255, 255)
            elif outcome and outcome.winner == chess.BLACK:
                msg, color = "BLACK WINS!", (100, 100, 255)
            else:
                msg, color = "DRAW", (200, 200, 200)

        box_rect = pygame.Rect(0, 0, 500, 250)
        box_rect.center = (GAME_WIDTH // 2, GAME_HEIGHT // 2)
        pygame.draw.rect(self.canvas, (40, 40, 40), box_rect, border_radius=20)
        pygame.draw.rect(self.canvas, HIGHLIGHT, box_rect, 4, border_radius=20)
        text_surf = self.large_font.render(msg, True, color)
        self.canvas.blit(text_surf, text_surf.get_rect(center=(box_rect.centerx, box_rect.centery - 40)))
        sub_surf = self.ui_font.render("Press 'R' to Restart or 'Esc' for Menu", True, (180, 180, 180))
        self.canvas.blit(sub_surf, sub_surf.get_rect(center=(box_rect.centerx, box_rect.centery + 50)))

    def handle_editor_input(self, events, mouse_pos):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.return_to_menu()
                if event.key == pygame.K_t: self.game.toggle_theme()
                if event.key == pygame.K_1: self.editor_brush['type'] = chess.PAWN
                if event.key == pygame.K_2: self.editor_brush['type'] = chess.KNIGHT
                if event.key == pygame.K_3: self.editor_brush['type'] = chess.BISHOP
                if event.key == pygame.K_4: self.editor_brush['type'] = chess.ROOK
                if event.key == pygame.K_5: self.editor_brush['type'] = chess.QUEEN
                if event.key == pygame.K_6: self.editor_brush['type'] = chess.KING
                if event.key == pygame.K_c: self.editor_brush['color'] = not self.editor_brush['color']
                if event.key == pygame.K_RETURN:
                    new_board = self.builder.build()
                    if new_board:
                        self.game.board = new_board
                        self.current_state = STATE_GAME
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = mouse_pos
                if x < WIDTH:
                    c, r = x // SQUARE_SIZE, y // SQUARE_SIZE
                    clicked_sq = chess.square(c, 7 - r)
                    if event.button == 1:
                        self.builder.add_piece(self.editor_brush['type'], clicked_sq, self.editor_brush['color'])
                    elif event.button == 3:
                        self.builder.remove_piece(clicked_sq)

    def draw_editor_screen(self):
        self.draw_board_logic(self.builder.get_preview(), self.game.theme, None, self.piece_renderer)
        self.draw_sidebar_logic(True)

    def draw_board_logic(self, board, theme, selection, renderer):
        coord_font = pygame.font.SysFont("Arial", 14, bold=True)
        legal_destinations = []
        if selection is not None:
            for move in board.legal_moves:
                if move.from_square == selection: legal_destinations.append(move.to_square)
        last_move = board.peek() if board.move_stack else None

        for r in range(8):
            for c in range(8):
                color = theme.get_light_square_color() if (r + c) % 2 == 0 else theme.get_dark_square_color()
                if self.is_flipped:
                    sq_idx, file_label, rank_label = chess.square(7 - c, r), chess.FILE_NAMES[7 - c], str(r + 1)
                else:
                    sq_idx, file_label, rank_label = chess.square(c, 7 - r), chess.FILE_NAMES[c], str(8 - r)
                if selection == sq_idx: color = theme.get_highlight_color()

                pygame.draw.rect(self.canvas, color, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

                if last_move and (sq_idx == last_move.from_square or sq_idx == last_move.to_square):
                    s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                    s.set_alpha(100)
                    s.fill((255, 255, 0))
                    self.canvas.blit(s, (c * SQUARE_SIZE, r * SQUARE_SIZE))

                if sq_idx in legal_destinations:
                    pygame.draw.circle(self.canvas, (100, 100, 100, 100),
                                       (c * SQUARE_SIZE + SQUARE_SIZE // 2, r * SQUARE_SIZE + SQUARE_SIZE // 2),
                                       SQUARE_SIZE // 6)

                if r == 7:
                    tc = theme.get_dark_square_color() if (r + c) % 2 == 0 else theme.get_light_square_color()
                    self.canvas.blit(coord_font.render(file_label, True, tc),
                                     (c * SQUARE_SIZE + SQUARE_SIZE - 15, r * SQUARE_SIZE + SQUARE_SIZE - 18))
                if c == 0:
                    tc = theme.get_dark_square_color() if (r + c) % 2 == 0 else theme.get_light_square_color()
                    self.canvas.blit(coord_font.render(rank_label, True, tc),
                                     (c * SQUARE_SIZE + 3, r * SQUARE_SIZE + 3))

                piece = board.piece_at(sq_idx)
                img = renderer.get_image(piece)
                if img:
                    center_x, center_y = c * SQUARE_SIZE + SQUARE_SIZE // 2, r * SQUARE_SIZE + SQUARE_SIZE // 2
                    self.canvas.blit(img, img.get_rect(center=(center_x, center_y)))


if __name__ == "__main__":
    ChessApp().run()