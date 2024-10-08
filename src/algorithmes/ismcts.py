from src.utils import utils as ut
from config.config import CONFIG_FILE, ENV_MODULE_MAPPING


def mcts(env, num_iterations, c):
    best_a = None
    best_q_s_z = float('-inf')

    # Placeholder for MCTS algorithm implementation
    # This should include selection, expansion, simulation, and backpropagation steps.
    # Currently not implemented in Rust either.

    return best_a

def main():
    # Nom de l'environnement
    env_name = "LineWorld"
    # Charger la configuration de l'environnement
    config = ut.load_config(CONFIG_FILE, env_name)
    # Obtenir le module de l'environnement
    env_module = ENV_MODULE_MAPPING[env_name]
    # Obtenir la classe de l'environnement
    env_class = getattr(env_module, env_name)
    # Initialiser l'environnement avec la configuration
    env = env_class(config)

    NUM_GAMES = 10000

    for num_iterations in [1, 10, 100, 1000, 10000]:
        mean_score = 0.0
        for _ in range(NUM_GAMES):
            env.reset()
            while not env.is_game_over():
                action = mcts(env, num_iterations, 2 ** 0.5)
                env.step(action)
            mean_score += env.score()

        mean_score /= NUM_GAMES
        print(f"Mean score for {num_iterations} iterations: {mean_score}")

if __name__ == "__main__":
    main()