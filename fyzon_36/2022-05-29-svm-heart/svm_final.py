import numpy as np
import pandas as pd  
import matplotlib.pyplot as plt 

"""## Support Vector Machine"""

# Main class implementations
class SVM:

    # Constructor
    def __init__(self, C=1e-2 , n_iters=100, learning_rate=1e-5):
        self.c = C
        self.iterations = n_iters
        self.learning_rate = learning_rate
        self.w = None
        self.b = None

    # calculate loss value of SVC model
    def hinge_loss(self, x, y):
        regularize_term = self.c * self.w.ravel() @ self.w.ravel()
        hinge_loss_term = max(0, 1 - y * (self.w @ x + self.b))
        return regularize_term + hinge_loss_term
    
    # Training function
    def fit(self, x, y):
        # Make sure that y contains 1 for positive class and -1 for negative class
        y = np.where(y == 1, 1, -1)
        # Intitalizing the weights
        self.w = np.random.rand(1, x.shape[1])
        # Initializing biasness
        self.b = np.random.rand()
        # variable to track if loss is increasing, then stop training
        loss_increase_counter = 0
        current_loss = 0
        previous_loss = 0

        # starting the Training
        for e in range(self.iterations):
            epoch_loss = []
            # iterate over all dataset rows
            for i in range(len(x)):
                # calculate model output
                y_hat = x[i] @ self.w.T + self.b
                # calculate value of loss function
                epoch_loss.append(self.hinge_loss(x[i], y[i]))
                # calculate derivative of loss function with respect to weights and bias
                if y[i] * y_hat >= 1:
                    dw = 2 * self.c * self.w
                    db = 0
                else:
                    dw = 2 * self.c * self.w - y[i] * x[i]
                    db = y[i]
                # update weights and bias
                self.w = self.w - self.learning_rate * dw
                self.b = self.b - self.learning_rate * db

            # calculate value of loss function
            current_loss = np.mean(epoch_loss)[0]

            # print loss value
            if (e + 1) % 10 == 0:
                print("Epoch:", e + 1, "; Loss:", current_loss)

            # increment counter if loss is increasing
            if current_loss > previous_loss:
                loss_increase_counter += 1

            # save current loss in previous loss variable
            previous_loss = current_loss

            if loss_increase_counter >= 10:
                break

    # Prediction functions
    def predict(self, x_test):
        pred_y = []
        # Applying the weights and biasness on the test data
        svc = x_test @ self.w.T + self.b
        pred_y = np.where(svc >= 0, 1, 0).ravel()
        return pred_y

"""## Helping Functions"""

# Preprocessing function
def standardize(X):
    # Standrizing the features
    standarized = (X - X.mean(axis=0)) / X.std(axis=0)
    return standarized

# Function to shuffle the dataset
def shfl_data(X, y, seed=None):
    # Check if the SEED value is given
    if seed:
        # Shuffle according to the seed values
        np.random.seed(seed)
    # Getting the indexes according to the length of the data
    idx = np.arange(X.shape[0])
    # Applying the shuffling
    np.random.shuffle(idx)
    # Returning the Shuffled features
    return X[idx], y[idx]

# Function to split the dataset into train and test data
def trainTestSplit(X, y, test_size=0.2, shuffle=True, seed=None):
    # Check for the flag Shuffle
    if shuffle:
        # Applying shuffling
        X, y = shfl_data(X, y, seed)
    # seprate data into training through testing data in the ratio specified in size test
##    split_i = len(y) - int(len(y) // (1 / test_size))
    split_i = int(len(y) * (1 - test_size))
    # Seperating the Train and test
    x_trn, x_tst = X[:split_i], X[split_i:]
    y_trn, y_tst = y[:split_i], y[split_i:]

    return x_trn, x_tst, y_trn, y_tst

# Function for the Accuracy score calculation
def score(ytrue, y_predict):
    score = sum(ytrue == y_predict)
    return score / len(ytrue)

"""## Dataset Loading """

# loading data
heart = pd.read_csv("heart.csv")
print(heart.tail())

"""## Seperating the features and Target columns"""

# Seperating the features and Target columns
X = heart.iloc[:, :-1].values
y = heart.iloc[:, -1].values
y = y.reshape(len(y) , 1)
print("Features:", X.shape[1])
print("Total Records:", len(y))

"""## Applying preprocessing"""

# Applying the preprocecssing
X = standardize(X)
# Seperate data into training and testing part
x_trn, x_tst, y_trn, y_tst = trainTestSplit(X, y, seed=42)
y_tst = y_tst.ravel()
print("[x_trn, x_tst, y_trn, y_tst]", x_trn.shape, x_tst.shape, y_trn.shape, y_tst.shape)

"""## Training Starting"""

# Appyling the model
model = SVM(learning_rate=1e-4, C=0.01, n_iters=5000)
model.fit(x_trn, y_trn)

"""## Model Prediction"""

# Making predictions
y_predict = model.predict(x_tst)
print("Actual values:", y_tst[:20])
print("Pred   values:", y_predict[:20])

"""## Accuracy Score"""

# Displaying the accuracy scores
print("score: ", np.round(score(y_tst, y_predict), 2))

"""## Results Visualization"""

# Graphical comparisons between the actual and predicted values
plt.scatter(range(len(y_tst)), y_tst, alpha=0.5, marker='*')
plt.scatter(range(len(y_predict)), y_predict, color='red', alpha=0.5)
plt.show()
