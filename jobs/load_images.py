import os
import psycopg2
import base64
import logging
import json
import requests
import tensorflow as tf

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()
query = '''SELECT id, convert_from(decode(url, 'base64'), 'UTF-8') as url FROM nsfw_server.contributed_image where image_bytes is null and image_bytes_response is null limit 10'''
cursor.execute(query)
query_results = cursor.fetchall()
cursor.close()

results = {}

for image_id, url in query_results:
    print('Processing image %s' % str(image_id))
    try:
        response = requests.get(url)
        full_size_image = tf.io.decode_image(response.content, channels=3)
        resized = tf.image.resize(full_size_image, [224,224], tf.image.ResizeMethod.BILINEAR)
        converted = tf.cast(resized, tf.uint8)
        jpeg = tf.io.encode_jpeg(converted)
        byte_array = psycopg2.Binary(jpeg.numpy())
        cursor = conn.cursor()
        query = '''UPDATE nsfw_server.contributed_image SET image_bytes = %(image_bytes)s, image_bytes_response = %(results)s where id = %(image_id)s '''
        cursor.execute(query, {'image_id': image_id, 'image_bytes': byte_array, 'results': json.dumps(results)})
        conn.commit()   
        cursor.close()
    except tf.python.framework.errors_impl.InvalidArgumentError:
        #bad image that is not able to be processed
        results = {"error": True, "message": "tf.python.framework.errors_impl.InvalidArgumentError"}
        cursor = conn.cursor()
        query = '''UPDATE nsfw_server.contributed_image SET image_bytes_response = %(results)s where id = %(image_id)s '''
        cursor.execute(query, {'image_id': image_id, 'results': json.dumps(results)})
        conn.commit()   
        cursor.close()
        continue
    except requests.exceptions.ConnectionError:
        results = {"error": True, "message": "requests.exceptions.ConnectionError"}
        cursor = conn.cursor()
        query = '''UPDATE nsfw_server.contributed_image SET image_bytes_response = %(results)s where id = %(image_id)s '''
        cursor.execute(query, {'image_id': image_id, 'results': json.dumps(results)})
        conn.commit()   
        cursor.close()
        continue

conn.close()




#base64str = str(base64.b64encode(numbytes), 'utf-8')
#img_string = 'data:image/jpeg;base64,' + base64str

