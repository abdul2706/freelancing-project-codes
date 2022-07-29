"""
Original file is located at
https://colab.research.google.com/drive/1d9oBD1JE3hI3TeIYlYJIycrsxOL6Tljs
"""

from dataset import train_dataloader
import numpy as np

# deep learning libraries
import torch
import torch.nn as nn
import torch.nn.init as init
import torch.nn.functional as F

# this variable will help using gpu if it's available
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
# print('device:', device)

"""# Define Model

## Regression Model
"""

class ChessNetRegression(nn.Module):
    def __init__(self, num_hidden_layers=1, use_reduction=False, debug=False):
        super(ChessNetRegression, self).__init__()
        self.TAG = '[ChessNetRegression]'
        self.debug = debug

        in_neurons = 770
        out_neurons = 512
        self.r = int(0.9 * 512 / num_hidden_layers) if use_reduction else 0
        
        # define network layers
        self.num_hidden_layers = num_hidden_layers
        self.nn_layers = nn.ModuleList()
        self.nn_layers.append(nn.Linear(in_neurons, out_neurons, bias=True))
        for i in range(num_hidden_layers):
            in_neurons = out_neurons
            out_neurons = int(in_neurons - self.r)
            self.nn_layers.append(nn.Linear(in_neurons, out_neurons, bias=True))
        self.nn_layers.append(nn.Linear(out_neurons, 1, bias=True))
        # define activation layer
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.1)

        self.init_params()

    def init_params(net):
        for m in net.modules():
            if isinstance(m, nn.Linear):
                init.xavier_normal_(m.weight)
                # init.normal_(m.weight, std=0.2)
                if hasattr(m, 'bias') and m.bias is not None:
                    init.constant_(m.bias, 0)

    def forward(self, x):
        if self.debug: print(self.TAG, '[x]', x.shape)
        for layer in self.nn_layers[:-1]:
            x = self.dropout(self.relu(layer(x)))
            if self.debug: print(self.TAG, '[x]', x.shape)
        x = self.nn_layers[-1](x)
        if self.debug: print(self.TAG, '[x]', x.shape)
        return x


"""## Test Model Forward Pass"""

def get_model_size(model):
    return sum([np.prod(params.shape) for params in model.parameters()])

if __name__ == '__main__':
    model_reg = ChessNetRegression(num_hidden_layers=3, debug=True).to(device)
    print(model_reg)
    print('[model_reg]', get_model_size(model_reg))
    x, y_true = next(iter(train_dataloader))
    x, y_true = x.to(dtype=torch.float32, device=device), y_true.unsqueeze(1).to(device=device)
    print('[x]', x.shape)
    print('[y_true]', y_true.shape, '\n', y_true[:10].flatten())
    y_pred = model_reg(x)
    print('[y_pred]', y_pred.detach().shape, '\n', y_pred.detach()[:10].flatten())
