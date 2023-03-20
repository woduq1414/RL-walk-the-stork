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
import csv

import pyformulas as pf
import matplotlib.pyplot as plt


class BirdEnv(gym.Env):
    meta_data = {'render.modes': ['human']}

    def __init__(self):
        config = Config()
        # define hparams

        # self.fig, self.ax1 = plt.subplots()
        # self.ax2 = self.ax1.twinx()
        #
        # plt.tight_layout()
        # canvas = np.zeros((480, 640))
        # self.screen = pf.screen(canvas, 'Plot')

        self.episode = 1
        self.score = 0

        self.start_time = None

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

        self.head_pos_buffer = deque(maxlen=4)

        self.left_end = 0.03
        self.right_end = 0.93
        self.center = 0.6117

        self.right_coef = 3 / ((self.right_end - self.center) ** 2)
        self.left_coef = 3 / ((self.center - self.left_end) ** 2)

        self.csv_field_names = ["Episode", "Time", "Reward Sum"]
        self.csv_file_name = f"./result_csv/result_{int(datetime.now().timestamp())}.csv"
        self.csv_writer = None

        self.result_dict = {
            "Episode": [],
            "Time": [],
            "Reward Sum": []
        }

        self.make_csv()

    def make_csv(self):
        self.csv_file = open(self.csv_file_name, "a", newline='')
        self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=self.csv_field_names)
        self.csv_writer.writeheader()
        self.csv_file.close()

    def write_csv(self, episode, survived_time, reward_sum):

        with open(self.csv_file_name, "a", newline='') as self.csv_file:
            self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=self.csv_field_names)
            self.csv_writer.writerow({"Episode": episode, "Time": survived_time, "Reward Sum": reward_sum})

    def plot_result(self, episode, survived_time, reward_sum):

        plt.cla()

        self.ax1.plot(self.result_dict["Episode"], self.result_dict["Time"], label="Time", color='green',
                      markersize=2, linewidth=1, linestyle='-')

        self.ax2.plot(self.result_dict["Episode"], self.result_dict["Reward Sum"], label="Reward Sum",
                      color='red', markersize=2, linewidth=1, linestyle='-')
        # plt.plot(episode, reward_sum, label = "Reward")

        self.fig.canvas.draw()
        image = np.fromstring(self.fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
        image = image.reshape(self.fig.canvas.get_width_height()[::-1] + (3,))

        self.screen.update(image)

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
            self.start_time = time.time()

        self.action.send_key(key_num)

        observation = self.state.get_state()

        is_over = self.state.is_over()

        if is_over:
            # print(self.score, self.reward_sum)
            end_time = time.time()
            survived_time = end_time - self.start_time

            self.result_dict["Episode"].append(self.episode)
            self.result_dict["Time"].append(survived_time)
            self.result_dict["Reward Sum"].append(self.reward_sum)

            if self.max_score < self.score:
                self.max_score = self.score

                if self.max_score >= 100:
                    print(
                        f"New Record !! Episode {self.episode} : Time - {int(survived_time * 1000)}ms / Reward - {self.reward_sum}")
                    time.sleep(2)
                    file_name = f'./screenshots/{self.episode}_{int(survived_time * 1000)}_{int(self.reward_sum)}.png'
                    print(f"Saving to {file_name} ...")
                    cv2.imwrite(file_name, cv2.cvtColor(self.state.screenshot(), cv2.COLOR_RGB2BGR))

                    time.sleep(1)
                else:
                    print(f"Episode {self.episode} : Time - {int(survived_time * 1000)}ms / Reward - {self.reward_sum}")
            else:
                if self.episode % 1 == 0:
                    print(f"Episode {self.episode} : Time - {int(survived_time * 1000)}ms / Reward - {self.reward_sum}")

            observation = self.prev_observation
            reward = 0
            self.episode += 1

            self.write_csv(self.episode, survived_time, self.reward_sum)
            # self.plot_result(self.episode, survived_time, self.reward_sum)

        else:
            self.score += 1

            # 0.03 0.6117 0.93

            if observation[0] > self.center:
                if observation[0] < self.center + (self.right_end - self.center) * 0.25:
                    reward = 4
                else:
                    reward = 3 - ((observation[0] - self.center) ** 2) * self.right_coef
            else:

                if observation[0] > self.center - (self.center - self.left_end) * 0.25:
                    reward = 4
                else:
                    reward = 3 - ((self.center - observation[0]) ** 2) * self.left_coef

            # print(reward)
            self.head_pos_buffer.append(observation[0])

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
            observation = [observation[0], 0, min(self.score / 2000, 1)]
        else:
            observation = [observation[0], observation[0] - self.head_pos_buffer[0], min(self.score / 2000, 1)]
            # print([observation[0], observation[0] - self.head_pos_buffer[0], min(self.score / 2000, 1)])

        self.prev_observation = observation
        return observation, reward, is_over, {"info": ""}

    def close(self):
        if self.viewer is not None:
            self.viewer.close()
            self.viewer = None

    def reset_game(self):
        self.score = 0
        self.reward_sum = 0

        self.prev_observation = None
        self.action.reset_game()
        self.head_pos_buffer.clear()

    def start_game(self):
        self.action.start_game()

    def render(self):
        pass
