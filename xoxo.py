import numpy as np


class Game:
    pattern1 = ['X'] * 3
    pattern2 = ['O'] * 3
    state = 0

    def __init__(self, game_id, player1_id, player2_id):
        self.game_id = game_id
        self.field = np.full((3, 3), '_')
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.move_count = 0
        self.first_player = player1_id
        self.second_player = player2_id

    def move(self, player_id, point):
        line, column = point[0], point[1]
        if self.field[line][column] != '_':
            return False  # "клетка занята!"
        elif player_id == self.player1_id:
            self.field[line][column] = 'X'
        elif player_id == self.player2_id:
            self.field[line][column] = 'O'
        self.move_count += 1
        self.first_player, self.second_player = self.second_player, self.first_player

        """then check win/draw conditions (after 4 moves)"""
        if self.move_count >= 4:
            pattern = Game.pattern1 if player_id == self.player1_id else Game.pattern2
            if all(np.take(self.field, line, axis=0) == pattern) or \
                    all(np.take(self.field, column, axis=1) == pattern) or \
                    all(np.diagonal(self.field) == pattern) or \
                    all(np.diagonal(np.fliplr(self.field)) == pattern):
                self.state = 1
                return {'winner':player_id}
            elif self.move_count == 9:
                self.state = 1
                return 'ничейка!'
            else:
                return True
        return True
