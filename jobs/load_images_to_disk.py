import tensorflow as tf
import psycopg2
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import os
import sys
import json
import os
import shutil

DATABASE_URL = os.environ['DATABASE_URL']
IMAGE_FILE_PATH = '/tmp/training_images'
DATASET_NAME = 'test-set'

cache_folder_path = os.path.join(IMAGE_FILE_PATH, 'cache')
os.makedirs(cache_folder_path, exist_ok=True)

dataset_folder_path = os.path.join(IMAGE_FILE_PATH, DATASET_NAME)
if os.path.isdir(dataset_folder_path):
   shutil.rmtree(dataset_folder_path)

query = '''
SELECT
   c.id,
   c.image_bytes,
   di.classification
FROM
   nsfw_server.dataset_image di
   inner join nsfw_server.contributed_image c on di.image_id = c.id
   inner join nsfw_server.dataset d on di.dataset_id = d.id
WHERE
   d.name = 'test-set'
'''

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()
cursor.execute(query)

for row in cursor:
   image_id, image_bytes, image_classification = row

   image_file_name = str(image_id) + '.jpg'
   cache_file_path = os.path.join(cache_folder_path, image_file_name)
   sym_folder_path = os.path.join(IMAGE_FILE_PATH, DATASET_NAME, image_classification)
   sym_file_path = os.path.join(sym_folder_path, image_file_name)
   
   #check if file exists, and if so, don't write it again
   with open(cache_file_path, 'wb') as file:
      file.write(image_bytes)

   os.makedirs(sym_folder_path, exist_ok=True)
   os.symlink(cache_file_path, sym_file_path)

conn.close()





