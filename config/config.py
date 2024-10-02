import src.environnements.lineworld as lw
import src.environnements.gridworld as gw


CONFIG_FILE = "../../config/env_config.yaml"
DQN_HIDDEN_LAYER_SIZE = (32, 32)
DDQN_HIDDEN_LAYER_SIZE = (32, 32)

ENV_MODULE_MAPPING = {
    "LineWorld": lw,
    "GridWorld": gw
}