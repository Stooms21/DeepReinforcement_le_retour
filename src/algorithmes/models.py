import torch
import torch.nn as nn
import numpy as np

class QNet(nn.Module):
    def __init__(
            self,
            num_states_description,
            num_actions,
            hidden_layer_sizes=(64, 64),
            criterion=nn.MSELoss(),
            optimizer=torch.optim.Adam,
            alpha=0.0001
    ):
        super(QNet, self).__init__()
        # Initialisation des paramètres du réseau de neurones
        if hidden_layer_sizes is None:
            hidden_layer_sizes = (64, 64)
        # Définition de la couche d'entrée
        self.input_layer = nn.Linear(num_states_description, hidden_layer_sizes[0])

        # Définition des couches cachées
        self.hidden_layers = nn.ModuleList()
        for i in range(len(hidden_layer_sizes) - 1):
            self.hidden_layers.append(nn.Linear(hidden_layer_sizes[i], hidden_layer_sizes[i + 1]))

        # Définition de la couche de sortie
        self.output_layer = nn.Linear(hidden_layer_sizes[-1], num_actions)
        # Définition de la fonction de perte
        self.criterion = criterion
        # Définition de l'optimiseur
        self.optimizer = optimizer(self.parameters(), lr=alpha)
        self.loss = None

    def forward(self, x):
        # Propagation avant à travers la couche d'entrée avec la fonction d'activation ReLU
        x = torch.relu(self.input_layer(x))
        # Propagation avant à travers les couches cachées avec la fonction d'activation ReLU
        for layer in self.hidden_layers:
            x = torch.relu(layer(x))
        # Propagation avant à travers la couche de sortie
        x = self.output_layer(x)
        return x

    def backward(self, q_value, q_target):
        # Calcul de la perte entre la valeur Q actuelle et la valeur Q cible
        self.loss = self.criterion(q_value, torch.tensor(q_target, dtype=torch.float32))
        # Remise à zéro des gradients de l'optimiseur
        self.optimizer.zero_grad()
        # Rétropropagation de la perte
        self.loss.backward()
        # Mise à jour des poids du réseau de neurones
        self.optimizer.step()