import os
import numpy as np
from stable_baselines3.common.callbacks import BaseCallback


class SaveOnBestTrainingRewardCallback(BaseCallback):
    """
    Callback for saving a model (the check is done every ``check_freq`` steps)
    based on the training reward (in practice, we recommend using ``EvalCallback``).

    :param check_freq: (int)
    :param log_dir: (str) Path to the folder where the model will be saved.
      It must contains the file created by the ``Monitor`` wrapper.
    :param verbose: (int)
    """

    def __init__(self, log_dir: str, verbose=1):
        super(SaveOnBestTrainingRewardCallback, self).__init__(verbose)

        self.log_dir = log_dir
        self.save_path = os.path.join(log_dir, 'best_model')
        self.best_reward = -np.inf
        self.episode = 1

    def _init_callback(self) -> None:
        # Create folder if needed
        if self.save_path is not None:
            os.makedirs(self.save_path, exist_ok=True)

    def _on_step(self) -> bool:

        return True

    def _on_rollout_end(self):

        reward = int(self.locals['infos'][0]['episode']['r'])
        if reward >= 100 and reward > self.best_reward:
            self.best_reward = reward
            self.model.save(os.path.join(self.log_dir, f'{self.episode}_{reward}_rl_model'))

        self.episode += 1




