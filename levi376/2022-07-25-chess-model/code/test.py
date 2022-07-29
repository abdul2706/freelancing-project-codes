"""
Original file is located at
https://colab.research.google.com/drive/1d9oBD1JE3hI3TeIYlYJIycrsxOL6Tljs
"""

import numpy as np
import torch
from model import ChessNetRegression

# this variable will help using gpu if it's available
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print('device:', device)

"""# Example: Use trained model later"""

# Create same model
model = ChessNetRegression(3, True)
# Load trained weights
model.load_state_dict(torch.load('regression_model/models/ChessNet-02.pth', map_location=device), strict=False)
# load in device
model = model.to(device)

# Define input here
x = np.random.randint(low=0, high=2, size=(1, 770))
print('[x]', x.tolist())
x = torch.tensor(x)
x = x.to(device=device, dtype=torch.float32)

# Inference model
with torch.no_grad():
    y_hat = model(x)
print('[y_hat]', y_hat.item())
