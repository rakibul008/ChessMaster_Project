from abc import ABC, abstractmethod

class AIStrategy(ABC):
    @abstractmethod
    def get_move(self, board):
        pass