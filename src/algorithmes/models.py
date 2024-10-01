import torch
import torch.nn as nn


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
        if hidden_layer_sizes is None:
            hidden_layer_sizes = (64, 64)
        self.input_layer = nn.Linear(num_states_description, hidden_layer_sizes[0])

        self.hidden_layers = nn.ModuleList()
        for i in range(len(hidden_layer_sizes) - 1):
            self.hidden_layers.append(nn.Linear(hidden_layer_sizes[i], hidden_layer_sizes[i + 1]))

        self.output_layer = nn.Linear(hidden_layer_sizes[-1], num_actions)
        self.criterion = criterion
        self.optimizer = optimizer(self.parameters(), lr=alpha)
        self.loss = None

    def forward(self, x):
        x = torch.relu(self.input_layer(x))
        for layer in self.hidden_layers:
            x = torch.relu(layer(x))
        x = self.output_layer(x)
        return x

    def backward(self, q_value, q_target):
        self.loss = self.criterion(q_value, torch.tensor(q_target, dtype=torch.float32))
        self.optimizer.zero_grad()
        self.loss.backward()
        self.optimizer.step()