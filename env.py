from collections import deque
from datetime import datetime

import numpy as np
import os
import time
import gym
from gym import error, spaces
from gym import utils
from gym.utils import seeding
from gym.envs.registration import register

from action import Action
from state import State

import win32con
import win32api
import win32gui
import time
import win32com.client as client
import pyautogui
from config import Config
import cv2


class BirdEnv(gym.Env):
    meta_data = {'render.modes': ['human']}

    def __init__(self):
        config = Config()
        # define hparams
        self.episode = 1
        self.score = 0
        self.reward_sum = 0

        self.frame_skip = (2, 5)
        self.repeat_action_prob = 0.
        self.image_size = config.image_size
        # 윈도우 이름과 handler 받아오기
        self.window_name = config.window_name

        self.hwnd, self.monitor, self.screen_x, self.screen_y = self.get_window_info(self.window_name)

        self.max_score = -1

        # state, action, memory_reader 정의
        self.state = State(self.monitor)
        self.state_buffer = deque()
        for _ in range(2):
            self.state_buffer.append(np.zeros(config.image_size))

        self.action = Action(self.window_name, self.monitor)
        self.actions = 3
        # rendering
        self.viewer = None

        # self.action_space = spaces.Discrete(self.actions)
        self.action_space = spaces.Box(low=-1, high=1, shape=(1,))

        self.observation_space = spaces.Box(low=0, high=1, shape=(3,), dtype=float)

        self.prev_observation = None

    def get_window_info(self, window_name="Ruffle - bird.swf"):

        hwnd = win32gui.FindWindow(None, window_name)
        if not hwnd:
            raise Exception('Window not found: ' + window_name)

        left, top, right, bot = win32gui.GetClientRect(hwnd)
        x, y = win32gui.ClientToScreen(hwnd, (left, top))

        t = win32gui.ClientToScreen(hwnd, (right - x, bot - y))
        monitor = {"left": x, "top": y, "width": t[0], "height": t[1]}

        return hwnd, monitor, x, y

    def reset(self):
        self.reset_game()
        time.sleep(0.1)
        return self.state.get_state()

    def seed(self, seed=None):
        self.np_random, seed1 = seeding.np_random(seed)
        # Derive a random seed. This gets passed as a uint, but gets
        # checked as an int elsewhere, so we need to keep it below
        # 2**31.
        seed2 = seeding.hash_seed(seed1 + 1) % 2 ** 31
        # Empirically, we need to seed before loading the ROM.
        # self.ale.setInt(b'random_seed', seed2)
        # self.ale.loadROM(self.game_path)
        return [seed1, seed2]

    # def get_states(self):
    #     observation = self.state.get_state()
    #
    #     previous_frames = np.array(self.state_buffer)
    #     s_t1 = np.zeros((3, self.image_size[0], self.image_size[1]))
    #     s_t1[:2, :] = previous_frames
    #     s_t1[2, :] = observation
    #     return np.moveaxis(s_t1, 0, -1)

    def step(self, key_num):

        if self.score == 0:
            self.action.start_game()



        self.action.send_key(key_num)

        observation = self.state.get_state()

        is_over = self.state.is_over()

        if is_over:
            # print(self.score, self.reward_sum)

            if self.max_score < self.score:
                self.max_score = self.score

                if self.max_score >= 100:
                    print(f"New Record !! Episode {self.episode} : Frame - {self.score} / Reward - {self.reward_sum}")
                    time.sleep(2)
                    file_name = f'./screenshots/{self.episode}_{self.score}_{int(self.reward_sum)}.png'
                    print(f"Saving to {file_name} ...")
                    cv2.imwrite(file_name, cv2.cvtColor(self.state.screenshot(), cv2.COLOR_RGB2BGR))

                    time.sleep(1)
            else:
                if self.episode % 1 == 0:
                    print(f"Episode {self.episode} : Frame - {self.score} / Reward - {self.reward_sum}")


            observation = self.prev_observation
            reward = 0
            self.episode += 1
        else:
            self.score += 1

            if observation[0] > 0.66666:
                reward = 3 - ((observation[0] - 0.666666) ** 2) * 27
            else:
                reward = 3 - ((0.66666 - observation[0]) ** 2) * 6.5

            # if 0.66666 - 0.12 < observation[0] < 0.66666 + 0.08:
            #     reward = 3
            #
            # elif 0.66666 - 0.30 < observation[0] < 0.66666 + 0.20:
            #     reward = 2
            #
            # else:
            #     reward = -1

            self.reward_sum += reward

        if self.prev_observation is None:
            observation = [observation[0], 0, max(self.score / 2000, 1)]
        else:
            observation = [observation[0], observation[0] - self.prev_observation[0], max(self.score / 2000, 1)]

        self.prev_observation = observation
        # print(observation, reward, self.state.is_over())
        return observation, reward, is_over, {"hello": "world"}

    def close(self):
        if self.viewer is not None:
            self.viewer.close()
            self.viewer = None

    def reset_game(self):
        self.score = 0
        self.reward_sum = 0
        # self.com_score = 0
        # self.my_score = 0
        self.action.reset_game()

    def start_game(self):
        self.action.start_game()

    def render(self):
        pass
