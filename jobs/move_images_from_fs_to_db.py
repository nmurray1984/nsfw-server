import glob
import os
import tensorflow as tf
import psycopg2
import base64
import json

file_pattern = "/data-drive/raw_data/*/*.original.jpg"
file_list = glob.glob(file_pattern)

print('Number of files:')
print(len(file_list))

#for testing
#file_list = file_list[0:9]


DATABASE_URL="postgres://nsfwadmin%40nsfw-server-db:%25%21bc%27H%7E7%3BGrR%3Cq5v@nsfw-server-db.postgres.database.azure.com:5432/postgres"
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
#cursor = conn.cursor()

for file in file_list:
        folder = os.path.dirname(file)
        classification = folder.split('/data-drive/raw_data/')[1]
        print('processing ' + file)
        with open(file, 'rb') as f:
                try:
                        full_size_image = tf.io.decode_image(f.read(), channels=3)
                        resized = tf.image.resize(full_size_image, [224,224], tf.image.ResizeMethod.BILINEAR)
                        converted = tf.cast(resized, tf.uint8)
                        jpeg = tf.io.encode_jpeg(converted)
                        byte_array = psycopg2.Binary(jpeg.numpy())
                        cursor = conn.cursor()
                        query = '''INSERT INTO nsfw_server.contributed_image (image_bytes,image_bytes_response,url,image_is_explicit) VALUES (%(image_bytes)s,%(results)s,%(file_name)s,true)'''
                        results = {"classification" : classification}
                        url_orig = 'azure-drive:/' + file
                        url = base64.b64encode((url_orig.encode('ascii'))).decode('ascii')
                        cursor.execute(query, {'image_bytes': byte_array, 'results': json.dumps(results), 'file_name':url})
                        conn.commit()
                except tf.python.framework.errors_impl.InvalidArgumentError:
                        print('unable to process image ' + file)
                        continue
conn.commit()
#       cursor.close()
conn.close()