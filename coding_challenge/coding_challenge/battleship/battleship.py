import gym
from gym import spaces
import numpy as np


class BattleshipEnv(gym.Env):
    def __init__(self, max_steps=100):
        self.max_steps = max_steps
        self.action_space = spaces.Box(0.0, 1.0, (2,))
        self.observation_space = spaces.Box(0.0, 1.0, (10, 10, 1))

    def _outside(self, x_idx, y_idx):
        return x_idx < 0 or x_idx >= 10 or y_idx < 0 or y_idx >= 10

    def _check_space(self, vertical, start_x, start_y, size):
        for x_idx_delta in range(3):
            for y_idx in range(start_y - 1, start_y + size + 1):
                x_idx = start_x - 1 + x_idx_delta
                if self._outside(x_idx, y_idx):
                    continue
                elif vertical and self._ships[x_idx][y_idx] > 0.0:
                    return False
                elif not vertical and self._ships[y_idx][x_idx] > 0.0:
                    return False
        return True

    def _place_ship(self, size):
        space = False
        while not space:
            vertical = (np.random.rand() > 0.5)
            x_idx = np.random.randint(10)
            y_idx_start = np.random.randint(11 - size)
            space = self._check_space(vertical, x_idx, y_idx_start, size)
        for y_idx in range(y_idx_start, y_idx_start + size):
            if vertical:
                self._ships[x_idx][y_idx] = 1.0
            else:
                self._ships[y_idx][x_idx] = 1.0

    def _check_ship_sunk(self, x_idx, y_idx):
        places_to_update = [(x_idx, y_idx)]
        for delta_x in range(1, 4):
            if self._outside(x_idx + delta_x, y_idx) or self._ships[x_idx + delta_x][y_idx] == 0.0:
                break
            elif self._ships[x_idx + delta_x][y_idx] == 1.0:
                return False
            places_to_update.append((x_idx + delta_x, y_idx))
        for delta_x in range(1, 4):
            if self._outside(x_idx - delta_x, y_idx) or self._ships[x_idx - delta_x][y_idx] == 0.0:
                break
            elif self._ships[x_idx - delta_x][y_idx] == 1.0:
                return False
            places_to_update.append((x_idx - delta_x, y_idx))
        for delta_y in range(1, 4):
            if self._outside(x_idx, y_idx + delta_y) or self._ships[x_idx][y_idx + delta_y] == 0.0:
                break
            elif self._ships[x_idx][y_idx + delta_y] == 1.0:
                return False
            places_to_update.append((x_idx, y_idx + delta_y))
        for delta_y in range(1, 4):
            if self._outside(x_idx, y_idx - delta_y) or self._ships[x_idx][y_idx - delta_y] == 0.0:
                break
            elif self._ships[x_idx][y_idx - delta_y] == 1.0:
                return False
            places_to_update.append((x_idx, y_idx - delta_y))
        for x_y in places_to_update:
            self._board[x_y[0]][x_y[1]] = 1.0
        return True

    def _place_ships(self):
        self._ships = np.zeros(shape=(10, 10, 1))
        for air_plane_carrier in range(1):
            self._place_ship(4)
        for battlecruiser in range(2):
            self._place_ship(3)
        for frigate in range(3):
            self._place_ship(2)
        for submarine in range(4):
            self._place_ship(1)

    def reset(self):
        self._step = 0
        self._board = np.zeros(shape=(10, 10, 1))
        self._place_ships()
        return self._board

    def step(self, action):
        x_idx = int(action[0] * 10)
        y_idx = int(action[1] * 10)
        terminal = False
        self._step += 1
        if self._step >= self.max_steps:
            info = {'game_message': 'You loose!'}
            reward = 0.0
            terminal = True
        elif x_idx < 0 or x_idx >= 10 or y_idx < 0 or y_idx >= 10:
            info = {'game_message': 'Invalid action!'}
            reward = -1.0
        elif self._ships[x_idx][y_idx] > 0.0:
            info = {'game_message': 'Hit'}
            self._board[x_idx][y_idx] = 0.6
            self._ships[x_idx][y_idx] = -1.0
            if self._check_ship_sunk(x_idx, y_idx):
                info = {'game_message': 'Ship sunk!'}
                if np.sum(self._ships) == -(1*4.0 + 2*3.0 + 3*2.0 + 4*1.0):
                    info = {'game_message': 'You win!'}
                    terminal = True
            reward = 1.0
        else:
            info = {'game_message': 'Miss'}
            reward = -0.1
            if self._board[x_idx][y_idx] == 0.0:
                self._board[x_idx][y_idx] = 0.3
        return self._board, reward, terminal, info
