from src.algorithmes.utc import utc
from src.environnements.gridworld import GridWorld
import math as m
from config.algos_config import CONFIG_FILE, DDQN_HIDDEN_LAYER_SIZE, ENV_MODULE_MAPPING
from src.utils import utils as ut
import src.utils.dqn_utils as dqu

env_name = "GridWorld"
# Charger la configuration de l'environnement
config = ut.load_config("../" + CONFIG_FILE, env_name)
# Obtenir le module de l'environnement
env_module = ENV_MODULE_MAPPING[env_name]
# Obtenir la classe de l'environnement
env_class = getattr(env_module, env_name)
# Initialiser l'environnement avec la configuration
env = env_class(config)

while(not env.is_game_over()):
    a = utc(env,1000,m.sqrt(2))
    env.step(a)
    env.display()


