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

class ModelTrainer:
    def __init__(self, num_classes, epsilon, delta):
        self.num_classes = num_classes
        self.epsilon = epsilon
        self.delta = delta
        self.model = tf.keras.Sequential([
            tf.keras.layers.Dense(num_classes, activation='softmax')
        ])
        self.global_model = tf.keras.models.clone_model(self.model)

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

    def global_aggregator(self, client_model):
        for global_layer, client_layer in zip(self.global_model.layers, client_model.layers):
            global_layer_weights = global_layer.get_weights()
            client_layer_weights = client_layer.get_weights()
            aggregated_weights = [(w1 + w2) / 2 for w1, w2 in zip(global_layer_weights, client_layer_weights)]
            global_layer.set_weights(aggregated_weights)

        return self.global_model

    def federated_learning(self, X_train, y_train_one_hot, X_test, yg_test):
        noclient = 10
        for i in range(noclient):
            start_index = int(i * len(X_train) / noclient)
            end_index = int((i + 1) * len(X_train) / noclient)
            X_client_train = X_train[start_index:end_index]
            y_client_train = y_train_one_hot[start_index:end_index]

            client_model = self.train_on_client_dp(X_client_train, y_client_train)
            self.global_model = self.global_aggregator(client_model)

            y_pred = np.argmax(client_model.predict(X_test), axis=1)
            yg_pred = np.argmax(self.global_model.predict(X_test), axis=1)
            f1 = f1_score(yg_test, y_pred, average='weighted')
            f1g = f1_score(yg_test, yg_pred, average='weighted')
            print("Client", i+1, "F1 Score:", f1, "F1 Global", f1g)

# Usage
data_preprocessor = DataPreprocessor('/media/jay/Windows/Users/jay/Downloads/nit_research/output/output_1.csv')
data_preprocessor.preprocess()

X_train, X_test, y_train, y_test = train_test_split(data_preprocessor.X, data_preprocessor.y, test_size=0.2, random_state=42)
num_classes = len(np.unique(data_preprocessor.y))
y_train_one_hot = tf.one_hot(y_train, depth=num_classes).numpy()

trainer = ModelTrainer(num_classes, epsilon=1000, delta=1e-2)
trainer.federated_learning(X_train, y_train_one_hot, X_test, y_test)

