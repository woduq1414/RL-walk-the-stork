from stable_baselines3 import DDPG
from stable_baselines3.common.env_util import make_vec_env

from callback import SaveOnBestTrainingRewardCallback
from env import BirdEnv

TRAIN_FROM_SCRATCH = True


bird_env = make_vec_env(BirdEnv, n_envs=1)
callback = SaveOnBestTrainingRewardCallback(log_dir="tmp/")
#

if TRAIN_FROM_SCRATCH:
    model = DDPG('MlpPolicy', bird_env, verbose=1, learning_rate= 0.0005, learning_starts=300, batch_size=200, seed=0
                )

else:

    model = DDPG.load("./model_checkpoints/rl_model_45000_steps.zip", env=bird_env, learning_starts = 0, learning_rate=0.0003)

model.learn(total_timesteps=(100000), progress_bar=True, callback=callback)
# model.save("birdai")