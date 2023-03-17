from stable_baselines3 import DDPG
from stable_baselines3.common.env_util import make_vec_env
from env import BirdEnv

from stable_baselines3.common.noise import NormalActionNoise
import numpy as np
from stable_baselines3.common.callbacks import CheckpointCallback

checkpoint_callback = CheckpointCallback(save_freq=5000, save_path='./model_checkpoints/')
bird_env = make_vec_env(BirdEnv, n_envs=1)

action_noise = NormalActionNoise(mean=np.zeros(1), sigma=0.1 * np.ones(1))


model = DDPG('MlpPolicy', bird_env, verbose=1, learning_rate= 0.0005, learning_starts=200, batch_size=200, seed=0
            )

# model = PPO.load("birdai", env=bird_env)

model.learn(total_timesteps=(100000), progress_bar=True, callback=checkpoint_callback)
model.save("birdai")