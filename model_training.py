import os
import numpy as np
from tensorflow.keras.utils import to_categorical
from keras.layers import Input, Dense
from keras.models import Model

X, y = None, []
expected_shape = None

for file in os.listdir():
    if file.endswith(".npy") and file != "labels.npy" and os.path.isfile(file):
        data = np.load(file)
        if expected_shape is None:
            if len(data.shape) == 1:
                print(f"Skipping '{file}': 1D array is not valid for training.")
                continue
            expected_shape = data.shape[1:]
            X = data
        else:
            if data.shape[1:] != expected_shape:
                print(f"Skipping '{file}': expected shape {expected_shape}, got {data.shape[1:]}")
                continue
            X = np.concatenate((X, data), axis=0)

        class_name = file.split('.')[0]
        y.extend([class_name] * len(data))

# Make sure we actually loaded valid data
if X is None or len(y) == 0:
    raise ValueError("No valid .npy data files found. Please check the directory.")

# Encode labels
label_set = sorted(set(y))
label_dict = {name: idx for idx, name in enumerate(label_set)}
y_encoded = np.array([label_dict[label] for label in y])
y_cat = to_categorical(y_encoded)

# Shuffle data
perm = np.random.permutation(len(X))
X, y_cat = X[perm], y_cat[perm]

# Build model
ip = Input(shape=(X.shape[1],))
m = Dense(512, activation="relu")(ip)
m = Dense(256, activation="relu")(m)
op = Dense(y_cat.shape[1], activation="softmax")(m)

model = Model(inputs=ip, outputs=op)
model.compile(optimizer='rmsprop', loss="categorical_crossentropy", metrics=['acc'])

# Train model
model.fit(X, y_cat, epochs=50)

# Save model and labels
model.save("model.keras",include_optimizer=False)
np.save("labels.npy", np.array(label_set))
