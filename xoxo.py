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
        self.move_count = [0, 0]

    def move(self, player_id, point):
        line, column = point[0], point[1]
        if self.field[line][column] != '_':
            return print("клетка занята!")
        # elif self.move_count[1] == player_id:
        #     return print("сейчас очередь другого игрока!")
        elif player_id == self.player1_id:
            self.field[line][column] = 'X'
        elif player_id == self.player2_id:
            self.field[line][column] = 'O'
        self.move_count[0] += 1
        self.move_count[1] = player_id

        """then check win conditions (after 4 moves)"""
        if self.move_count[0] >= 1:
            pattern = Game.pattern1 if player_id == self.player1_id else Game.pattern2
            if all(np.take(self.field, line, axis=0) == pattern) or \
                    all(np.take(self.field, column, axis=1) == pattern) or \
                    all(np.diagonal(self.field) == pattern) or \
                    all(np.diagonal(np.fliplr(self.field)) == pattern):
                self.state = 1
                return self.field, f'player{player_id}wins!'
        #return 'next turn'

