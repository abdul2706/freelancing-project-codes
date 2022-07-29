"""
Original file is located at
https://colab.research.google.com/drive/1d9oBD1JE3hI3TeIYlYJIycrsxOL6Tljs
"""

import os
import numpy as np

"""This function converts text dataset to compressed numpy array format for fast use in the future."""

def convert_text_to_npz(text_path, npz_path):
    with open(text_path) as infile:
        print('processing', text_path)
        X = []
        y = []
        
        for i, line in enumerate(infile):
            line = line.strip()
            if len(line) > 0:
                _x = eval(line[line.index('['):])
                _y = eval(line[:line.index('[')-1])
                if -9000 <= _y <= 9000:
                    X.append(_x)
                    y.append(_y)
        
        X = np.array(X, np.int8)
        y = np.array(y, np.int32)
        print('[X]', X.shape, X)
        print('[y]', y.shape, y)

    np.savez_compressed(npz_path, X=X, y=y)
    print('saved file', text_path)

convert_text_to_npz('data.txt', 'data.npz')
