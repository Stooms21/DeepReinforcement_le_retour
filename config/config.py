import src.environnements.lineworld as lw
import src.environnements.gridworld as gw


CONFIG_FILE = "../../config/env_config.yaml"
DQN_HIDDEN_LAYER_SIZE = (128, 128)

ENV_MODULE_MAPPING = {
    "LineWorld": lw,
    "GridWorld": gw
}