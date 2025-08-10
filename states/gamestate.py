class GameState:
    def __init__(self):
        # stores the position of king when under check to change color
        self.reset()

    def reset(self):
        self.in_game = False
        self.start_new = False
        self.board_settings_button_pressed = False
        self.pop_up_on = False
        self.check_position = None

        # Multiplayer state
        self.multiplayer = False
        self.room_code = None
        self.is_host = False
        self.net_socket = None  # active TCP socket for moves
        self.advertise_socket = None  # UDP broadcast socket (host only)
        self.my_color = None  # 'white' or 'black' when in multiplayer


game_state = GameState()