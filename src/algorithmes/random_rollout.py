import random
import math as m

import tqdm

from config.algos_config import CONFIG_FILE, DDQN_HIDDEN_LAYER_SIZE, ENV_MODULE_MAPPING
from src.utils import utils as ut

def random_rollout(env,num_rollouts_per_action):

    best_a = 0

    best_q_s_z = -1000
    for a in env.available_actions():
        q_s_a = 0.0
        for i in tqdm.tqdm(range(num_rollouts_per_action)):
            env_copy = env.copy()
            env_copy.step(a)
            while not env_copy.is_game_over():
                aa = env_copy.available_actions()
                action = random.choice(aa)
                env_copy.step(action)

            q_s_a += env_copy.score()

        q_s_a /= num_rollouts_per_action

        if q_s_a > best_q_s_z:
            best_q_s_z = q_s_a
            best_a = a


    return best_a

if __name__ == '__main__':
    env_name = "GridWorld"
    # Charger la configuration de l'environnement
    config = ut.load_config(CONFIG_FILE, env_name)
    # Obtenir le module de l'environnement
    env_module = ENV_MODULE_MAPPING[env_name]
    # Obtenir la classe de l'environnement
    env_class = getattr(env_module, env_name)
    # Initialiser l'environnement avec la configuration
    env = env_class(config)
    while(not env.is_game_over()):
        a = random_rollout(env,1000)
        env.step(a)
        env.display()