import random
import math as m
import tqdm

def utc(env,nb_action_play,c,color = 1):
    tree = {}
    root = env.state_id()
    tree = update_tree(env,tree,root)
    i =0
    for nb_move in tqdm.tqdm(range(nb_action_play)):
        #selection
        root_node = tree[root]
        action_select = select_action(root_node, c)
        env_copy = env.copy()
        env_copy.step(action_select)
        state_id = env_copy.state_id()
        all_action = [action_select]
        state = [state_id]
        chose_random = False
        while state_id in tree and not env_copy.is_game_over():
            current_node = tree[state_id]
            action_select = select_action(current_node, c)
            env_copy.step(action_select)
            state_id = env_copy.state_id()
            all_action.append(action_select)
            if not state_id in state:
                state.append(state_id)
            else:
                current_node = tree[state_id]
                action_select = select_action(current_node, c)
                env_copy.step(action_select)
                aa = env_copy.available_actions()
                action_select = random.choice(aa)
                env_copy.step(action_select)
                state_id = env_copy.state_id()
                all_action.append(action_select)
                i += 1
        # expansion
        update_tree(env_copy,tree,state_id)
        #simulation
        score_final = rollout(env_copy,color)
        #backpropagation
        for state,node in tree.items():
            for action,triplet in node.items():
                if action in all_action:
                    score = triplet[0]
                    nb_visited = triplet[1]
                    score += score_final
                    nb_visited += 1
                    nouveau_triplet = (score , nb_visited)
                    tree[state][action] = nouveau_triplet

    max_nb_select = 0
    best_a = 0
    print(i)
    root_node = tree[root]
    print(root_node)
    for action, triplet in root_node.items():
        nb_select = triplet[1]
        if nb_select > max_nb_select:
            max_nb_select = nb_select
            best_a = action
    print(best_a)
    return best_a


def select_action(node,c):
    choose = False
    action_select = 0
    best_ucb = -1000

    nb_visited_total = 0
    for action, triplet in node.items():
        nb_visited_total += triplet[1]
    for action, triplet in node.items():
        ucb = 0
        if triplet[1] != 0:
            score = triplet[0] / triplet[1]
        else:
            score = triplet[0]
        nb_visited = triplet[1]

        if nb_visited == 0:
            action_select = action
            choose = True
        else:
            ucb = score + c * (m.sqrt(m.log(nb_visited_total) / nb_visited))
        if ucb > best_ucb and not choose:
            best_ucb = ucb
            action_select = action
    return action_select

def update_tree(env,tree,state_id):
    for a in env.available_actions():
        if state_id not in tree:
            tree[state_id] = {}
            edge_a = (0, 0)
            tree[state_id][a] = edge_a
        else:
            node = tree[state_id]
            if a not in node:
                edge_a = (0, 0)
                tree[state_id][a] = edge_a
    return tree

def rollout(env_copy,color):
    while not env_copy.is_game_over():
        random_a = random.choice(env_copy.available_actions())
        env_copy.step(random_a)
    score = (env_copy.score() * color)
    return score