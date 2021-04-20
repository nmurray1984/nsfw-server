from tensorflow import keras
import tensorflow as tf
from datetime import datetime
import os
import pandas as pd
import logging

batch_size = 32
img_height = 224
img_width = 224
epochs = 10

IMAGE_FILE_PATH = '/tmp/training_images'
DATASET_NAME = 'test-set'

TRAINING_RUN_NAME = 'test-run'
HISTORY_FILE_PATH = '/tmp/training_run_history'
save_dir = os.path.join(HISTORY_FILE_PATH, TRAINING_RUN_NAME, '{}'.format(datetime.now().strftime("%Y-%b-%d-%H-%M-%S")) )
os.makedirs(save_dir, exist_ok=True)

#check that dataset folder exists and assume that it contains all the files necessary
dataset_folder = os.path.join(IMAGE_FILE_PATH, DATASET_NAME)
if not os.path.isdir(dataset_folder):
    raise Exception('Dataset does not exist. Run load_images_to_disk job')

train_ds = tf.keras.preprocessing.image_dataset_from_directory(
  dataset_folder,
  validation_split=0.2,
  subset="training",
  seed=123,
  image_size=(img_height, img_width),
  batch_size=batch_size)

val_ds = tf.keras.preprocessing.image_dataset_from_directory(
  dataset_folder,
  validation_split=0.2,
  subset="validation",
  seed=123,
  image_size=(img_height, img_width),
  batch_size=batch_size)

AUTOTUNE = tf.data.AUTOTUNE

train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

IMG_SHAPE = (img_height, img_width, 3)

base_model = tf.keras.applications.MobileNetV2(
    input_shape=IMG_SHAPE,
    include_top=False, 
    weights='imagenet')

base_model.trainable = False

model = tf.keras.Sequential([
  base_model,
  tf.keras.layers.Conv2D(32, 3, activation='relu'),
  tf.keras.layers.Dropout(0.2),
  tf.keras.layers.GlobalAveragePooling2D(),
  tf.keras.layers.Dense(1)
])

model.compile(optimizer=tf.keras.optimizers.Adam(), #TODO check if this is correct
              loss='mean_absolute_error', 
              metrics=['accuracy'])

print(model.summary())

print('Number of trainable variables = {}'.format(len(model.trainable_variables)))

history = model.fit(train_ds, epochs=epochs, validation_data=val_ds)



model.save(os.path.join(save_dir, 'model.h5'))

# convert the history.history dict to a pandas DataFrame:     
hist_df = pd.DataFrame(history.history) 

# save to json:  
hist_json_file = os.path.join(save_dir, 'history.json')
with open(hist_json_file, mode='w') as f:
    hist_df.to_json(f)

# or save to csv: 
hist_csv_file = os.path.join(save_dir, 'history.csv')
with open(hist_csv_file, mode='w') as f:
    hist_df.to_csv(f)
