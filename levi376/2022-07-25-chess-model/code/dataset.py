"""
Original file is located at
https://colab.research.google.com/drive/1d9oBD1JE3hI3TeIYlYJIycrsxOL6Tljs
"""

import numpy as np
# machine learning libraries
from sklearn.model_selection import train_test_split
# deep learning libraries
import torch
from torch.utils.data import Dataset, DataLoader

# this variable will help using gpu if it's available
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
# print('device:', device)

"""Define new class for Chess dataset"""

class ChessDataset(Dataset):
    def __init__(self, X, y, debug=False):
        self.debug = debug
        self.X = torch.tensor(X)
        self.y = torch.tensor(y, dtype=torch.int64)
    
    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

# Load chess dataset from numpy file
npz_path = 'data.npz'
data = np.load(npz_path)
X = data['X']
y = data['y']
# print('[X]', X.shape, X.dtype)
# print('[y]', y.shape, y.dtype)

# split dataset into train/val/test sets with ratios 0.8/0.1/0.1 (approximately).
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=0)
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.1, random_state=0)

# create ChessDataset instances for train/val/test sets
train_dataset = ChessDataset(X_train, y_train)
val_dataset = ChessDataset(X_val, y_val)
test_dataset = ChessDataset(X_test, y_test)

# create DataLoader instances for train/val/test sets
BATCH_SIZE = 64
train_dataloader = DataLoader(train_dataset, batch_size=BATCH_SIZE)
val_dataloader = DataLoader(val_dataset, batch_size=BATCH_SIZE)
test_dataloader = DataLoader(test_dataset, batch_size=BATCH_SIZE)

if __name__ == '__main__':
    print('[X_train, y_train]', X_train.shape, y_train.shape)
    print('[X_val, y_val]', X_val.shape, y_val.shape)
    print('[X_test, y_test]', X_test.shape, y_test.shape)
    print(len(X_train) + len(X_val) + len(X_test), len(X))

    print('[train_dataset]', len(train_dataset))
    print('[val_dataset]', len(val_dataset))
    print('[test_dataset]', len(test_dataset))

    print('[train_dataloader]', len(train_dataloader))
    print('[val_dataloader]', len(val_dataloader))
    print('[test_dataloader]', len(test_dataloader))
