import chess


class BoardBuilder:
    def __init__(self):
        self._board = chess.Board(None)
        self._board.turn = chess.WHITE

    def clear(self):
        self._board.clear()

    def set_turn(self, color):
        self._board.turn = color

    def add_piece(self, piece_type, square_index, color):
        self._board.remove_piece_at(square_index)
        piece = chess.Piece(piece_type, color)
        self._board.set_piece_at(square_index, piece)

    def remove_piece(self, square_index):
        self._board.remove_piece_at(square_index)

    def get_preview(self):
        return self._board

    def build(self):
        if not self._board.king(chess.WHITE) or not self._board.king(chess.BLACK):
            print("BUILDER ERROR: Cannot build. Board must have a White King and a Black King.")
            return None
        return self._board.copy()
