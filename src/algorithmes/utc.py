import random
import math as m
import tqdm

def utc(env,nb_action_play,c):
    tree = {}
    root = env.state_id()
    state_id = env.state_id()
    for a in env.available_actions_ids():
        if state_id not in tree:
            tree[state_id] = {}
            edge_a = (0, 0, 0)
            tree[state_id][a] = edge_a
        else:
            node = tree[state_id]
            if a not in node:
                edge_a = (0, 0, 0)
                tree[state_id][a] = edge_a

    for nb_move in tqdm.tqdm(range(nb_action_play)):
        action_select = 0
        best_ucb = -1000
        root_node = tree[root]
        choose = False
        for action, triplet in root_node.items():
            score = 0
            if triplet[1] != 0:
                score = triplet[0] / triplet[1]
            else:
                score = triplet[0]
            nb_select = triplet[1]
            nb_considered = triplet[2]
            if nb_considered == 0:
                ucb = 0
            elif nb_select == 0:
                action_select = action
                choose = True
            else:
                ucb = score + c * (m.sqrt(m.log(nb_considered) / nb_select))
            if ucb > best_ucb and not choose:
                best_ucb = ucb
                action_select = action

            env_copy = env.copy()
            env_copy.step(action_select)
            while not env_copy.is_game_over():
                random_a = random.choice(env_copy.available_actions_ids())
                env_copy.step(random_a)
            score_final = env_copy.score()
            for action,triplet in root_node.items():
                score = triplet[0]
                nb_select = triplet[1]
                if action == action_select:
                    score += score_final
                    nb_select = triplet[1] + 1

                nb_considered = triplet[2] + 1
                nouveau_triplet = (score , nb_select , nb_considered)
                root_node[action] = nouveau_triplet

    max_nb_select = 0
    best_a = 0
    print(root_node)
    print(tree)
    for action, triplet in root_node.items():
        nb_select = triplet[1]
        if nb_select > max_nb_select:
            max_nb_select = nb_select
            best_a = action
    return best_a