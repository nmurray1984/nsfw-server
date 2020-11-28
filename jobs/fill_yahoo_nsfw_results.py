import psycopg2
import json
import os
from nsfw import classify
import requests

DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()
query = "SELECT id, image_bytes FROM nsfw_server.contributed_image where azure_content_moderator_result is null limit 10"
cursor.execute(query)
query_results = cursor.fetchall()

for (image_id, image_bytes) in query_results:
    try:
        print(image_id)
        sfw, nsfw = classify(image_bytes)
        print(sfw, nsfw)
        cursor2 = conn.cursor()
        update_sql = 'update nsfw_server.contributed_image set yahoo_nsfw_result = %(data)s where id = %(id)s'
        cursor2.execute(update_sql, {'data': json.dumps({'sfwScore': sfw, 'nsfwScore': nsfw}), 'id': image_id})
        conn.commit()
        cursor2.close()
        print('Complete')
    except Exception as e:
        print("Error: {0}".format(e))


cursor.close()
conn.close()