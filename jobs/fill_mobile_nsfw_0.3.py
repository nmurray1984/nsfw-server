import tensorflow as tf
import psycopg2
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import os
import sys
import json

DATABASE_URL = os.environ['DATABASE_URL']
MODEL_FILE_PATH = 'jobs/nsfw_v0.3.h5'
IMAGE_SIZE = 224
IMG_SHAPE = (IMAGE_SIZE, IMAGE_SIZE, 3)

model = load_model(MODEL_FILE_PATH, compile=False)
model.compile(loss='binary_crossentropy',
            optimizer='rmsprop',
            metrics=['accuracy'])

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()
query = '''SELECT id, image_bytes FROM nsfw_server.contributed_image where nsfwv03_result is null and image_bytes is not null limit 1000'''
cursor.execute(query)
query_results = cursor.fetchall()
cursor.close()

for id, image_bytes in query_results:
    full_size_image = tf.io.decode_image(bytes(image_bytes), channels=3)
    offset = tf.constant(255, dtype=tf.float32)
    resized = tf.image.resize(full_size_image, [IMAGE_SIZE, IMAGE_SIZE], tf.image.ResizeMethod.BILINEAR)
    normalized = tf.math.divide(resized, offset)
    batched = tf.reshape(normalized, [1, IMAGE_SIZE, IMAGE_SIZE, 3])

    #inference
    prediction_result = model.predict(batched)[0]
    result = {
        "sfwScore": prediction_result[0].item(),
        "racyScore": prediction_result[1].item(),
        "nsfwScore": prediction_result[2].item()
    }  
    #except :
    #    e = sys.exc_info()[0]
    #    result = {
    #        "error" : type(e).__name__
    #        ,"message" : str(e)
    #    }

    cursor2 = conn.cursor()
    update_sql = 'update nsfw_server.contributed_image set nsfwv03_result = %(data)s where id = %(id)s'
    cursor2.execute(update_sql, {'data': json.dumps(result), 'id': id})
    conn.commit()
    cursor2.close()
    print('Completed Image: %s' % id)


conn.close()
