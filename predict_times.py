import tensorflow as tf
import pandas as pd

from tensorflow.keras.layers import Dense, Flatten, Conv2D
from tensorflow.keras import Model

df = pd.read_excel("Sample_Dataset.xlsx")
df = df[df["PROCEDURE_START"].notnull()]

waiting_time = (df["PROCEDURE_START"] - df["REGISTRATION_ARRIVAL"]).astype('timedelta64[m]')
df["PROCEDURE_CODE"] = df["PROCEDURE_CODE"].astype("category").cat.codes
features = df[["PROCEDURE_CODE", "PRIORITY_CODE"]]

train_ds = tf.data.Dataset.from_tensor_slices((features.values, waiting_time.values)).shuffle(100).batch(4)


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
train_accuracy = tf.keras.metrics.SparseCategoricalAccuracy(name='train_accuracy')


@tf.function
def train_step(features, values):
    with tf.GradientTape() as tape:
        predictions = model(features)
        loss = loss_object(values, predictions)
    gradients = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(gradients, model.trainable_variables))

    train_loss(loss)
    train_accuracy(values, predictions)


EPOCHS = 5

for epoch in range(EPOCHS):
    for features, values in train_ds:
        train_step(features, tf.reshape(values, [-1, 1]))

    template = 'Epoch {}, Loss: {}, Accuracy: {}'
    print(template.format(epoch + 1,
                          train_loss.result(),
                          train_accuracy.result() * 100))

    # Reset the metrics for the next epoch
    train_loss.reset_states()
    train_accuracy.reset_states()
