class GameState:
    def __init__(self, ):
          # stores the position of king when under check to change color
          self.reset()

    def reset(self):
        self.in_game = False
        self.start_new = False

        self.board_settings_button_pressed = False
        self.pop_up_on = False

        self.check_position = None


game_state = GameState()