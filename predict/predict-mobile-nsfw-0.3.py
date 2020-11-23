import tensorflow as tf
from dotenv import load_dotenv
import psycopg2
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import os
import requests
import sys
import json

load_dotenv(verbose=True)
DATABASE_URL = os.environ.get('DATABASE_URL')
MODEL_FILE_PATH = os.environ.get('MODEL_FILE_PATH')
IMAGE_SIZE = 224
IMG_SHAPE = (IMAGE_SIZE, IMAGE_SIZE, 3)

model = load_model(MODEL_FILE_PATH, compile=False)
model.compile(loss='binary_crossentropy',
            optimizer='rmsprop',
            metrics=['accuracy'])

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()
query = '''SELECT id, convert_from(decode(url, 'base64'), 'UTF-8') as url FROM nsfw_server.contributed_image where nsfwv03_result is null '''
cursor.execute(query)
query_results = cursor.fetchall()
cursor.close()

for id, url in query_results:
    #download image
    result = None
    response = None
    try:
        response = requests.get(url)
        #convert to resized, formatted tensor
        full_size_image = tf.io.decode_image(response.content, channels=3)
        resized = tf.image.resize(full_size_image, [IMAGE_SIZE, IMAGE_SIZE], tf.image.ResizeMethod.BILINEAR)
        offset = tf.constant(255, dtype=tf.float32)
        normalized = tf.math.divide(resized, offset)
        batched = tf.reshape(normalized, [1, IMAGE_SIZE, IMAGE_SIZE, 3])

        #inference
        prediction_result = model.predict(batched)[0]
        result = {
            "sfwScore": prediction_result[0].item(),
            "racyScore": prediction_result[1].item(),
            "nsfwScore": prediction_result[2].item()
        }  
    except :
        e = sys.exc_info()[0]
        result = {
            "error" : type(e).__name__
            #,"message" : e.message
        }

    cursor2 = conn.cursor()
    update_sql = 'update nsfw_server.contributed_image set nsfwv03_result = %(data)s where id = %(id)s'
    cursor2.execute(update_sql, {'data': json.dumps(result), 'id': id})
    conn.commit()
    cursor2.close()
    print('%s' % url)


conn.close()







