import tensorflow as tf
tf.enable_v2_behavior()

from tensorflow.keras import layers

from patient_data import load_data

features, waiting_times, procedure_times, punctuality_times = load_data("data_dependent.csv")
features_test, waiting_times_test, procedure_times_test, punctuality_times_test = load_data("Sample_Dataset.xlsx")

train_ds = tf.data.Dataset.from_tensor_slices((features, procedure_times)).shuffle(1000).batch(32)
test_ds = tf.data.Dataset.from_tensor_slices((features_test, procedure_times_test)).batch(32)

model = tf.keras.models.Sequential([
    layers.BatchNormalization(input_shape=features[0].shape),
    layers.Dense(64, activation="relu"),
    layers.Dropout(0.2),
    layers.Dense(128, activation="relu"),
    layers.Dropout(0.2),
    layers.Dense(256, activation="relu"),
    layers.Dropout(0.2),
    layers.Dense(512, activation="relu"),
    layers.BatchNormalization(),
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


EPOCHS = 1400

for epoch in range(EPOCHS):
    for features, values in train_ds:
        train_step(features, tf.reshape(values, [-1, 1]))

    for test_features, test_values in test_ds:
        test_step(test_features, test_values)

    template = 'Epoch {}, Loss: {}, Test Loss: {}'
    print(template.format(epoch + 1,
                          train_loss.result(),
                          test_loss.result()))

    # Reset the metrics for the next epoch
    train_loss.reset_states()
    test_loss.reset_states()

print(model(features))

model.summary()
model.save('ge_procedure_time_model.h5')
