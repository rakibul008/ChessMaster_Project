import random
from ai.strategy_interface import AIStrategy

class RandomBot(AIStrategy):
    def get_move(self, board):
        moves = list(board.legal_moves)
        if not moves:
            return None
        return random.choice(moves)