import pygame
import chess
from core.settings import SQUARE_SIZE


class PieceRenderer:
    def __init__(self, theme=None):
        self.font_large = pygame.font.SysFont("segoe ui symbol", int(SQUARE_SIZE * 0.85))
        self.font_small = pygame.font.SysFont("segoe ui symbol", 35)

        self.unicode_map = {
            chess.PAWN: "♟",
            chess.KNIGHT: "♞",
            chess.BISHOP: "♝",
            chess.ROOK: "♜",
            chess.QUEEN: "♛",
            chess.KING: "♚"
        }

    def get_image(self, piece):
        if piece is None:
            return None

        symbol = self.unicode_map.get(piece.piece_type, "?")

        if piece.color == chess.WHITE:
            color = (255, 255, 255)
            outline = (0, 0, 0)
        else:
            color = (0, 0, 0)
            outline = (255, 255, 255)

        return self._render_text_with_outline(symbol, self.font_large, color, outline)

    def get_small_image_by_type(self, piece_type, color):
        symbol = self.unicode_map.get(piece_type, "?")

        if color == chess.WHITE:
            color = (255, 255, 255)
            outline = (0, 0, 0)
        else:
            color = (0, 0, 0)
            outline = (150, 150, 150)

        return self._render_text_with_outline(symbol, self.font_small, color, outline)

    def _render_text_with_outline(self, text, font, color, outline_color):
        base = font.render(text, True, color)
        w, h = base.get_size()
        s = pygame.Surface((w + 4, h + 4), pygame.SRCALPHA)

        outline = font.render(text, True, outline_color)
        s.blit(outline, (0, 2))
        s.blit(outline, (4, 2))
        s.blit(outline, (2, 0))
        s.blit(outline, (2, 4))

        s.blit(base, (2, 2))
        return s
