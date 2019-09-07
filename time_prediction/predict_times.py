import tensorflow as tf

from tensorflow.keras import layers

from patient_data import load_data

features, waiting_times, procedure_times, punctuality_times = load_data("data.csv")

ds = tf.data.Dataset.from_tensor_slices((features, waiting_times))
train_ds = ds.take(80_000).shuffle(1000).batch(16)
test_ds = ds.skip(80_000).batch(16)

model = tf.keras.models.Sequential([
    layers.Dense(12, activation="relu"),
    layers.Dense(1, activation="relu")
  ])

loss_object = tf.keras.losses.MeanSquaredError()
optimizer = tf.keras.optimizers.Adam()

train_loss = tf.keras.metrics.Mean(name='train_loss')
test_loss = tf.keras.metrics.Mean(name='test_loss')


@tf.function
def train_step(features, values):
    with tf.GradientTape() as tape:
        predictions = model(features)
        loss = loss_object(values, predictions)
    gradients = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(gradients, model.trainable_variables))

    train_loss(loss)


@tf.function
def test_step(images, labels):
  predictions = model(images)
  t_loss = loss_object(labels, predictions)

  test_loss(t_loss)


EPOCHS = 8

for epoch in range(EPOCHS):
    for features, values in train_ds:
        train_step(features, tf.reshape(values, [-1, 1]))

    for test_images, test_labels in test_ds:
        test_step(test_images, test_labels)

    template = 'Epoch {}, Loss: {}, Test Loss: {}'
    print(template.format(epoch + 1,
                          train_loss.result(),
                          test_loss.result()))

    # Reset the metrics for the next epoch
    train_loss.reset_states()
    test_loss.reset_states()

model.summary()
model.save('ge_waiting_time_model.h5')
