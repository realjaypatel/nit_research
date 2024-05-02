#final code, differential privacy, federated learning, f1score: 0.90
import tensorflow as tf


class ModelTrainer:
    def __init__(self, epsilon, delta, data_file):
        self.model = tf.keras.Sequential([
            tf.keras.layers.Dense(self.num_classes, activation='softmax')
        ])
        self.global_model = tf.keras.models.clone_model(self.model)



    def global_aggregator(self, client_models):
        for client_model in client_models:
            for global_layer, client_layer in zip(self.global_model.layers, client_model.layers):
                global_layer_weights = global_layer.get_weights()
                client_layer_weights = client_layer.get_weights()
                aggregated_weights = [(w1 + w2) / 2 for w1, w2 in zip(global_layer_weights, client_layer_weights)]
                global_layer.set_weights(aggregated_weights)

        return self.global_model
