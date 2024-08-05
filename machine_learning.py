from sklearn.linear_model import LinearRegression
import numpy as np

def train_model():
    # Placeholder for training model
    X_train = np.array([[1], [2], [3], [4], [5]])
    y_train = np.array([12, 19, 3, 5, 2])
    model = LinearRegression().fit(X_train, y_train)
    return model

def predict_usage(model):
    future_data = np.array([[6]])
    prediction = model.predict(future_data)
    return prediction[0]
