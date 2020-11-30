import psycopg2
import json
import os
import requests

DATABASE_URL = os.environ['DATABASE_URL']
CONTENT_MODERATOR_ENDPOINT = os.environ['CONTENT_MODERATOR_ENDPOINT']
CONTENT_MODERATOR_SUBSCRIPTION_KEY = os.environ['CONTENT_MODERATOR_SUBSCRIPTION_KEY']
url = 'https://southcentralus.api.cognitive.microsoft.com/contentmoderator/moderate/v1.0/ProcessImage/Evaluate?CacheImage=false'

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()
query = "SELECT id, image_bytes FROM nsfw_server.contributed_image where azure_content_moderator_result is null and image_bytes is not null limit 1000"
cursor.execute(query)
query_results = cursor.fetchall()

for (image_id, image_bytes) in query_results:
    headers = {
        # Request headers
        'Content-Type': 'image/jpeg',
        'Ocp-Apim-Subscription-Key': CONTENT_MODERATOR_SUBSCRIPTION_KEY,
    }

    try:
        print(image_id, url)
        response = requests.post(url, headers=headers, data=image_bytes)
        cursor2 = conn.cursor()
        update_sql = 'update nsfw_server.contributed_image set azure_content_moderator_result = %(data)s where id = %(id)s'
        cursor2.execute(update_sql, {'data': response.text, 'id': image_id})
        conn.commit()
        cursor2.close()
        print('Complete')
    except Exception as e:
        print("Error: {0}".format(e))


cursor.close()
conn.close()