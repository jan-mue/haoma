import tensorflow as tf

from tensorflow.keras.layers import Dense, Flatten, Conv2D
from tensorflow.keras import Model

from patient_data import load_data

features, waiting_times, procedure_times, punctuality_times = load_data("Sample_Dataset.xlsx")

train_ds = tf.data.Dataset.from_tensor_slices((features, procedure_times)).shuffle(100).batch(4)


class WaitingTimeModel(Model):
    def __init__(self):
        super(WaitingTimeModel, self).__init__()
        self.d1 = Dense(64, activation="relu")
        self.d2 = Dense(64, activation="relu")
        self.d3 = Dense(1)

    def call(self, x):
            x = self.d1(x)
            x = self.d2(x)
            return self.d3(x)


model = WaitingTimeModel()

loss_object = tf.keras.losses.MeanSquaredError()
optimizer = tf.keras.optimizers.Adam()

train_loss = tf.keras.metrics.Mean(name='train_loss')


@tf.function
def train_step(features, values):
    with tf.GradientTape() as tape:
        predictions = model(features)
        loss = loss_object(values, predictions)
    gradients = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(gradients, model.trainable_variables))

    train_loss(loss)


EPOCHS = 5

for epoch in range(EPOCHS):
    for features, values in train_ds:
        train_step(features, tf.reshape(values, [-1, 1]))

    template = 'Epoch {}, Loss: {}'
    print(template.format(epoch + 1, train_loss.result()))

    # Reset the metrics for the next epoch
    train_loss.reset_states()
