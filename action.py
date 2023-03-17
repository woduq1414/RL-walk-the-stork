import win32con
import win32api
import win32gui
import time
import win32com.client as client
import pyautogui
import os

class Action:
    def __init__(self, window_name, monitor):
        self.window_name = window_name
        self.shell = client.Dispatch("WScript.Shell")
        self.key_map = {
            0: None,  # do nothing
            1: 0x25,  # left arrow
            2: 0x27,  # right arrow
            3: 0x20,  # space
        }
        self.x = monitor["left"]
        self.y = monitor["top"]

    def send_key(self, action):
        print(action[0])
        if -0.3 < action[0] < 0.3:
            pass
        else:
            self.shell.AppActivate(self.window_name)
            action_type = 1 if action[0] < 0 else 2
            win32api.keybd_event(self.key_map[action_type], 0, 0, 0)
            # time.sleep(0.02 if abs(action[0]) >= 0.6 else 0.01)
            # time.sleep(-(abs(action[0]) - 0.3) / 70 + 0.02)
            time.sleep((abs(action[0]) - 0.3) / 50 + 0.01)
            win32api.keybd_event(self.key_map[action_type], 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.01)

        # if key != 0:
        #     self.shell.AppActivate(self.window_name)
        #     #
        #     win32api.keybd_event(self.key_map[key], 0, 0, 0)
        #     time.sleep(0.02)
        #     win32api.keybd_event(self.key_map[key], 0, win32con.KEYEVENTF_KEYUP, 0)
        #     time.sleep(0.02)
        #
        # else:
        #     # time.sleep
        #     pass

    def start_game(self):
        # os.system("ruffle.exe ./emulator/bird.swf")

        self.reset_game()

    def reset_game(self):
        time.sleep(2.5)
        pyautogui.click(self.x + 400, self.y + 54)
        time.sleep(0.5)
        pyautogui.moveTo(self.x + 600, self.y + 54)


        print("Reset Game")


    def start_game(self):
        win32api.keybd_event(self.key_map[3], 0, 0, 0)
        # time.sleep(0.02 if abs(action[0]) >= 0.6 else 0.01)
        time.sleep(0.01)
        win32api.keybd_event(self.key_map[3], 0, win32con.KEYEVENTF_KEYUP, 0)

if __name__ == "__main__":
    action = Action()
    action.reset_game()
