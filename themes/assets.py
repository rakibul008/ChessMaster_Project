from themes.theme_factory import AbstractThemeFactory


class ClassicTheme(AbstractThemeFactory):
    def get_light_square_color(self):
        return (238, 238, 210)

    def get_dark_square_color(self):
        return (118, 150, 86)

    def get_highlight_color(self):
        return (186, 202, 68)

    def get_piece_style(self):
        return {
            'P': '♟', 'R': '♜', 'N': '♞', 'B': '♝', 'Q': '♛', 'K': '♚',
            'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚'
        }


class HighContrastTheme(AbstractThemeFactory):
    def get_light_square_color(self):
        return (240, 240, 240)

    def get_dark_square_color(self):
        return (70, 130, 180)

    def get_highlight_color(self):
        return (100, 255, 218)

    def get_piece_style(self):
        return {
            'P': '♟', 'R': '♜', 'N': '♞', 'B': '♝', 'Q': '♛', 'K': '♚',
            'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚'
        }
