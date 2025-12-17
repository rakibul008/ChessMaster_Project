from abc import ABC, abstractmethod


class AbstractThemeFactory(ABC):
    @abstractmethod
    def get_light_square_color(self):
        pass

    @abstractmethod
    def get_dark_square_color(self):
        pass

    @abstractmethod
    def get_piece_style(self):
        pass

    @abstractmethod
    def get_highlight_color(self):
        pass
