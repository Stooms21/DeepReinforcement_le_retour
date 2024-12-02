import torch
import torch.nn as nn
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, Model, optimizers, losses


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


class PolicyNetworkReinforce(tf.keras.Model):
    def __init__(
            self,
            state_dim,
            action_dim,
            nb_hidden_layers=2,
            hidden_layer_size=64,
            alpha=0.0001,
            **kwargs
    ):
        """
        Initialise le réseau de neurones pour la politique.

        :param state_dim: Dimension de l'état (taille du vecteur d'entrée)
        :param action_dim: Nombre d'actions (taille de la sortie)
        """
        super(PolicyNetworkReinforce, self).__init__()
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.nb_hidden_layers = nb_hidden_layers
        self.hidden_layer_size = hidden_layer_size
        self.optimizer = optimizers.Adam(learning_rate=alpha)


        # Créez les couches comme des attributs
        self.hidden_layers = [
            layers.Dense(hidden_layer_size, activation='tanh')
            for _ in range(nb_hidden_layers - 1)
        ]
        self.output_layer = layers.Dense(action_dim, activation='softmax')

    def call(self, inputs, predict=True):
        x = tf.convert_to_tensor(inputs, dtype=tf.float32)
        if len(x.shape) == 1:
            x = tf.expand_dims(x, axis=0)  # Ajouter une dimension batch

        for layer in self.hidden_layers:
            x = layer(x)

        logits = self.output_layer(x)
        if predict:
            probs = tf.squeeze(logits) / tf.reduce_sum(logits)
            return probs.numpy()
        else:
            return logits

    def train_step(self, state, action, G_t):
        """
        Met à jour les paramètres avec REINFORCE.
        """
        with tf.GradientTape() as tape:
            logits = self.call(state, predict=False)
            action_prob = tf.nn.softmax(logits)[0, action]  # Probabilité de l'action prise
            loss = -tf.math.log(action_prob) * G_t  # REINFORCE loss
        gradients = tape.gradient(loss, self.trainable_variables)
        self.optimizer.apply_gradients(zip(gradients, self.trainable_variables))

    def get_config(self):
        """
        Retourne la configuration de l'objet pour la sérialisation.
        """
        config = super().get_config()
        config.update({
            "state_dim": self.state_dim,
            "action_dim": self.action_dim,
            "nb_hidden_layers": self.nb_hidden_layers,
            "hidden_layer_size": self.hidden_layer_size,
            "alpha": self.optimizer.learning_rate.numpy(),
        })
        return config

    @classmethod
    def from_config(cls, config):
        """
        Reconstruit le modèle à partir de la configuration.
        """
        # Crée une instance en passant les arguments directement
        return cls(
            state_dim=config["state_dim"],
            action_dim=config["action_dim"],
            nb_hidden_layers=config["nb_hidden_layers"],
            hidden_layer_size=config["hidden_layer_size"],
            alpha=config["alpha"]
        )


class ValueNetwork(tf.keras.Model):
    """
    Réseau de neurones pour approximer la fonction de valeur d'état V(s).
    """
    def __init__(self, state_dim, hidden_layer_size=64, alpha=0.001):
        super(ValueNetwork, self).__init__()
        self.state_dim = state_dim
        self.hidden_layer_size = hidden_layer_size
        self.optimizer = tf.keras.optimizers.Adam(learning_rate=alpha)

        # Couches
        self.hidden_layer = tf.keras.layers.Dense(hidden_layer_size, activation='relu')
        self.output_layer = tf.keras.layers.Dense(1)

    def call(self, inputs):
        x = tf.convert_to_tensor(inputs, dtype=tf.float32)
        if len(x.shape) == 1:  # Si l'entrée est un vecteur, ajouter une dimension batch
            x = tf.expand_dims(x, axis=0)
        x = self.hidden_layer(x)
        return self.output_layer(x)

    def train_step(self, state, target):
        """
        Met à jour les paramètres du réseau de valeur pour approximer V(s).
        """
        with tf.GradientTape() as tape:
            value = self.call(state)
            loss = tf.keras.losses.MSE(target, value)
        gradients = tape.gradient(loss, self.trainable_variables)
        self.optimizer.apply_gradients(zip(gradients, self.trainable_variables))
        return loss


class PolicyNetworkActor(tf.keras.Model):
    """
    Réseau de neurones pour approximer la politique π(a|s, θ).
    """
    def __init__(self, state_dim, action_dim, nb_hidden_layers=2, hidden_layer_size=64, alpha=0.001):
        super(PolicyNetworkActor, self).__init__()
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.nb_hidden_layers = nb_hidden_layers
        self.hidden_layer_size = hidden_layer_size
        self.optimizer = optimizers.Adam(learning_rate=alpha)


        # Créez les couches comme des attributs
        self.hidden_layers = [
            layers.Dense(hidden_layer_size, activation='relu')
            for _ in range(nb_hidden_layers - 1)
        ]
        self.output_layer = layers.Dense(action_dim, activation='softmax')

    def call(self, inputs, predict=True):
        x = tf.convert_to_tensor(inputs, dtype=tf.float32)
        if len(x.shape) == 1:
            x = tf.expand_dims(x, axis=0)  # Ajouter une dimension batch

        for layer in self.hidden_layers:
            x = layer(x)

        logits = self.output_layer(x)
        if predict:
            probs = tf.squeeze(logits) / tf.reduce_sum(logits)
            return probs.numpy()
        else:
            return logits

    def train_step(self, state, action, delta):
        """
        Met à jour θ avec une politique basée sur l'avantage (δ).
        """
        with tf.GradientTape() as tape:
            probs = self.call(state, predict=False)
            log_prob = tf.math.log(probs[0, action])
            loss = -log_prob * delta  # Mise à jour Actor
        gradients = tape.gradient(loss, self.trainable_variables)
        self.optimizer.apply_gradients(zip(gradients, self.trainable_variables))


class ValueNetworkActor(tf.keras.Model):
    """
    Réseau de neurones pour approximer la valeur d'état V(s, w).
    """
    def __init__(self, state_dim, hidden_layer_size=64, alpha=0.001):
        super(ValueNetworkActor, self).__init__()
        self.hidden_layer = layers.Dense(hidden_layer_size, activation='relu')
        self.output_layer = layers.Dense(1)
        self.optimizer = optimizers.Adam(learning_rate=alpha)

    def call(self, inputs):
        x = tf.convert_to_tensor(inputs, dtype=tf.float32)
        if len(x.shape) == 1:  # Si entrée est un vecteur, ajouter une dimension batch
            x = tf.expand_dims(x, axis=0)
        x = self.hidden_layer(x)
        return self.output_layer(x)

    def train_step(self, state, target):
        """
        Met à jour w pour approximer V(s, w).
        """
        with tf.GradientTape() as tape:
            value = self.call(state)
            loss = tf.keras.losses.MSE(target, value)  # Erreur quadratique
        gradients = tape.gradient(loss, self.trainable_variables)
        self.optimizer.apply_gradients(zip(gradients, self.trainable_variables))
        return loss


class QNet(tf.keras.Model):
    def __init__(
            self,
            num_states_description,
            num_actions,
            hidden_layer_sizes=(64, 64),
            loss_fn=tf.keras.losses.MeanSquaredError(),
            optimizer=tf.keras.optimizers.Adam,
            alpha=0.0001
    ):
        super(QNet, self).__init__()
        # Initialisation des paramètres du réseau de neurones
        if hidden_layer_sizes is None:
            hidden_layer_sizes = (64, 64)
        self.hidden_layer_sizes = hidden_layer_sizes

        # Définition de la couche d'entrée
        self.input_layer = layers.Dense(hidden_layer_sizes[0], activation='relu', input_shape=(num_states_description,))

        # Définition des couches cachées
        self.hidden_layers = [
            layers.Dense(hidden_layer_sizes[i + 1], activation='relu')
            for i in range(len(hidden_layer_sizes) - 1)
        ]

        # Définition de la couche de sortie
        self.output_layer = layers.Dense(num_actions)

        # Définition de la fonction de perte et de l'optimiseur
        self.loss_fn = loss_fn
        self.optimizer = optimizer(learning_rate=alpha)


    def call(self, inputs):
        # Propagation avant à travers la couche d'entrée
        x = tf.convert_to_tensor(inputs, dtype=tf.float32)
        if len(x.shape) == 1:  # Si entrée est un vecteur, ajouter une dimension batch
            x = tf.expand_dims(x, axis=0)
        # Propagation avant à travers les couches cachées
        for layer in self.hidden_layers:
            x = layer(x)
        # Propagation avant à travers la couche de sortie
        x = self.output_layer(x)
        return x

    def train_step(self, q_value, q_target):
        """
        Entraîne le modèle pour un état, une action spécifique et une Q-target.
        :param state: L'état courant, tensor de forme (batch_size, num_states_description).
        :param action: Les indices des actions sélectionnées, tensor de forme (batch_size,).
        :param q_target: Les valeurs cibles, tensor de forme (batch_size,).
        """
        with tf.GradientTape() as tape:
            q_value = tf.expand_dims(q_value, axis=0)  # Ajoute une dimension
            q_target = tf.expand_dims(q_target, axis=0)  # Ajoute une dimension
            # Calcul de la perte entre la Q-value actuelle et la Q-target
            loss = self.loss_fn(q_target, q_value)

        # Calcul des gradients
        gradients = tape.gradient(loss, self.trainable_variables)
        # Application des gradients pour mettre à jour les poids
        self.optimizer.apply_gradients(zip(gradients, self.trainable_variables))

        return loss