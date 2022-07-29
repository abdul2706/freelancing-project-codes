"""
Original file is located at
https://colab.research.google.com/drive/1d9oBD1JE3hI3TeIYlYJIycrsxOL6Tljs
"""

from dataset import train_dataset, val_dataset, test_dataset, train_dataloader, val_dataloader, test_dataloader
from model import ChessNetRegression
from runner import Runner

# general libraries
import gc
import numpy as np

# deep learning libraries
import torch
import torch.nn as nn
import torch.optim as optim

# this variable will help using gpu if it's available
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print('device:', device)

"""# Train"""

print('[train_dataset]', len(train_dataset))
print('[val_dataset]', len(val_dataset))
print('[test_dataset]', len(test_dataset))

print('[train_dataloader]', len(train_dataloader))
print('[val_dataloader]', len(val_dataloader))
print('[test_dataloader]', len(test_dataloader))

torch.cuda.empty_cache()
gc.collect()

regression_runner = Runner(runner_type='REG',
                           work_dir='./regression_model', 
                           model=ChessNetRegression(num_hidden_layers=3, use_reduction=True), 
                           criterion=nn.L1Loss(), 
                           optimizer=optim.Adam, lr=0.001, 
                           save_weight_file='ChessNet-02.pth', load_weight_file='ChessNet-01.pth')

print(regression_runner.model)

regression_runner.train(train_loader=train_dataloader, val_loader=val_dataloader, epochs=50, log_interval=1000)

"""## Tensorboard Plots"""

# run following line on command prompt to start tensorboard plots in browser
# %tensorboard --logdir 'regression_model/runs'

"""# Test"""

train_losses, train_y_true, train_y_pred = regression_runner.test(train_dataloader)
print('[train_loss]', np.mean(train_losses))

val_losses, val_y_true, val_y_pred = regression_runner.test(val_dataloader)
print('[val_loss]', np.mean(val_losses))

test_losses, test_y_true, test_y_pred = regression_runner.test(test_dataloader)
print('[test_loss]', np.mean(test_losses))

test_preds = regression_runner.inference(test_dataloader)
print(test_preds)
print(test_preds.shape)
