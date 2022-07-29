"""
Original file is located at
https://colab.research.google.com/drive/1d9oBD1JE3hI3TeIYlYJIycrsxOL6Tljs
"""

import numpy as np
import matplotlib.pyplot as plt

"""# Data Analysis

Load dataset as numpy array
"""
npz_path = 'data.npz'
data = np.load(npz_path)
X = data['X']
y = data['y']
print('[X]', X.dtype, X.shape, X.min(), X.max())
print('[y]', y.dtype, y.shape, y.min(), y.max())
print('[unique y values]', len(np.unique(y)))

"""Get count of each unique y value"""

y_counts = {}
y_unique = np.unique(y)
for val in y_unique:
    count = len(np.where(y == val)[0])
    y_counts[val] = count
# print(y_counts)
print(min(y_counts.values()), max(y_counts.values()))

"""Frequency plot of y values"""

plt.figure(figsize=(25, 5))
plt.hist(y, width=1, bins=18000)
plt.xlim([-9100, 9100])
plt.savefig('plot.jpg', dpi=150)
print('plot saved')
# plt.show()
