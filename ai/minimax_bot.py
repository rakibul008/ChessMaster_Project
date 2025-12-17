import chess
import math
import random
from ai.strategy_interface import AIStrategy


class MinimaxBot(AIStrategy):
    def __init__(self, depth=3):
        self.depth = depth
        self.piece_values = {
            chess.PAWN: 10,
            chess.KNIGHT: 30,
            chess.BISHOP: 30,
            chess.ROOK: 50,
            chess.QUEEN: 90,
            chess.KING: 900
        }

    def get_move(self, board):
        best_move = None
        best_value = -math.inf
        alpha = -math.inf
        beta = math.inf

        legal_moves = list(board.legal_moves)
        random.shuffle(legal_moves)

        for move in legal_moves:
            board.push(move)
            board_value = -self.minimax(board, self.depth - 1, -beta, -alpha)
            board.pop()

            if board_value > best_value:
                best_value = board_value
                best_move = move

            alpha = max(alpha, board_value)

        return best_move

    def minimax(self, board, depth, alpha, beta):
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board)

        max_eval = -math.inf
        for move in board.legal_moves:
            board.push(move)
            eval = -self.minimax(board, depth - 1, -beta, -alpha)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval

    def evaluate_board(self, board):
        if board.is_checkmate():
            return -9999 if board.turn else 9999

        score = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = self.piece_values.get(piece.piece_type, 0)
                if piece.color == board.turn:
                    score += value
                else:
                    score -= value
        return score
