import random



def utc(env,nb_rollout_per_action):
    best_a = 0
    best_q_s_z = -1000
    for a in range(0,env.num_actions()):
        if a in env.available_actions_ids():
            q_s_a = 0
            for nb in range(nb_rollout_per_action):
                env_copy = env.copy()
                env_copy.step(a)
                while not env_copy.is_game_over():
                    random_a = random.choice(env_copy.available_actions_ids())
                    env_copy.step(random_a)
                q_s_a += env_copy.score()
            q_s_a /= nb_rollout_per_action
            if q_s_a > best_q_s_z:
                best_q_s_z = q_s_a
                best_a = a

    return best_a