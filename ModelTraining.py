#final code, differential privacy, federated learning, f1score: 0.90
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split



class DataPreprocessor:
    def __init__(self, filepath):
        self.data = pd.read_csv(filepath)
        self.X = None
        self.y = None

    def preprocess(self):
        self.X = np.asarray(self.data.drop(self.data.columns[:2], axis=1))
        self.y = np.asarray(self.data['pii_exist'])
        scaler = StandardScaler()
        self.X = scaler.fit_transform(self.X)
    
    def disable_gpu():
        # Disable GPU usage by TensorFlow
        tf.config.set_visible_devices([], 'GPU')

class ModelTrainer:
    def __init__(self, epsilon, delta, data_preprocessor):
        self.data_preprocessor = data_preprocessor
        self.test_size=0.2
        self.random_state=42
        self.num_classes = len(np.unique(data_preprocessor.y))    
        self.epsilon = epsilon
        self.delta = delta
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.data_preprocessor.X, self.data_preprocessor.y, train_size=self.test_size, random_state=self.random_state
            )
        self.model = tf.keras.Sequential([
            tf.keras.layers.Dense(self.num_classes, activation='softmax')
        ])
        self.global_model = tf.keras.models.clone_model(self.model)

    def preprocess(self):
        self.y_train_one_hot = y_train_one_hot = tf.one_hot(self.y_train, depth=self.num_classes).numpy()

    def train_on_client_dp(self, X, y):
        delta_prime = self.delta / (2 * len(X) / 32)  # Assuming batch size of 32
        c = np.sqrt(2 * np.log(1.25 / delta_prime))
        sensitivity = 2 * c
        sigma = c * sensitivity / self.epsilon

        self.model.compile(optimizer='adam',
                           loss='binary_crossentropy',
                           metrics=['accuracy'])
        self.model.fit(X, y, epochs=10, batch_size=32, verbose=0)

        for layer in self.model.layers:
            if isinstance(layer, tf.keras.layers.Dense):
                for weight in layer.trainable_variables:
                    noise = tf.random.normal(shape=weight.shape, stddev=sigma)
                    weight.assign_add(noise)

        return self.model
