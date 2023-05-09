import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Activation, Dropout,LeakyReLU

IMG_SIZE = (299, 299) # resolution
IMG_SHAPE = IMG_SIZE +(3,)


data_augmentation = tf.keras.Sequential([
  tf.keras.layers.RandomFlip("horizontal"),
  tf.keras.layers.RandomRotation(0.2),
  tf.keras.layers.RandomZoom(0.2),
  tf.keras.layers.RandomHeight(0.2),
  tf.keras.layers.RandomWidth(0.2),
])

preprocess_input = tf.keras.applications.inception_v3.preprocess_input

def make_model(image_shape=IMG_SIZE):
    ''' Define a tf.keras model for multi-class classification out of the InceptionV3 model '''
    image_shape = image_shape + (3,)

    resnet_model = tf.keras.applications.InceptionV3(input_shape=IMG_SHAPE, include_top=False, weights='imagenet')
    resnet_model.trainable = True
    for layer in resnet_model.layers[0 : -6]:
        layer.trainable = False

    inputs = tf.keras.Input(image_shape)
    x = data_augmentation(inputs)
    x = preprocess_input(x)
    x = resnet_model(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    num_classes = 4# jumlah kelas pada dataset Anda
    prediction_layer = tf.keras.layers.Dense(num_classes, activation="softmax")
    outputs = prediction_layer(x)
    model = tf.keras.Model(inputs, outputs)
    # model.summary()

    return model

# def make_model():
#     model = Sequential()
#     model.add(Conv2D(16, (3, 3), input_shape=(32, 32, 3), padding='same'))
#     model.add(LeakyReLU(0.1))
#     model.add(Conv2D(32, (3, 3), padding='same'))
#     model.add(LeakyReLU(0.1))
#     model.add(MaxPooling2D(pool_size=(2, 2)))
#     model.add(Dropout(0.25))
#     model.add(Conv2D(32, (3, 3), padding='same'))
#     model.add(LeakyReLU(0.1))
#     model.add(Conv2D(64, (3, 3), padding='same'))
#     model.add(LeakyReLU(0.1))
#     model.add(MaxPooling2D(pool_size=(2, 2)))
#     model.add(Dropout(0.25))
#     model.add(Flatten())
#     model.add(Dense(256))
#     model.add(LeakyReLU(0.1))
#     model.add(Dropout(0.5))
#     model.add(Dense(4, activation='softmax'))
    
#     return model
