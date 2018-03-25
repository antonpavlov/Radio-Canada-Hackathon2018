# The lineup_crawler is a script for news extraction from Radio-Canada API.
# It works in a following way:
# For each region_id script makes a request to Radio-Canada API and process returned JSON.
# Next, each extracted news summary is submitted to Microsoft text analytics API, that results in
# text sentiment rate and some key words. All that data is uploaded to MySQL DB afterwards.
#
# This script is a part of a final submission of the Radio-Canada Hackathon 2018.
# Team GWAM. Its proud members are Irina Kim, Nikita Ponamaryov, Steve Gagné, Alexander Kim and Anton Pavlov.

import requests
import math
import urllib.request
from bs4 import BeautifulSoup
import mysql.connector

region_id = [475289, 7040, 6106, 5765, 5775, 5779, 35019, 6102, 4201, 36711, 5769, 5763, 7591, 6108, 35004, 36518,
4175, 35015, 36509, 5777, 7589, 6104, 1001046, 5717, 5767, 7039, 604312, 1000999, 7576, 7585, 21906, 7582, 36869,
6118, 1000595, 21880, 6126, 7590, 26047, 36706, 36705, 6130, 1000901, 36709, 7592, 23961, 7568, 7042, 1001052, 604318,
7584, 7570, 528645, 26497, 1000956, 7578, 7575, 1000601, 1000973, 6132, 7586, 7587, 36708, 36710, 604321, 604310,

# Regions - RAW list - it might not work, because this list contains not so clear development data not always
# related to regions.
#region_id = [36715, 6112, 6134, 6122, 528642, 1000995, 1000955, 528644, 6657, 36713, 1000840, 1000837, 1000948,
#1000947, 1001059, 1001056, 604320, 529996, 1001005, 7583, 1000996, 36507, 1000802, 604311, 604255, 604305,
#604307, 604308, 1000974, 1000975, 1000971, 1000972, 1000988, 1000981, 1000542, 1001053, 1001002, 1001003, 1001001,
#528625, 1000597, 1000954, 6655, 36465, 1000600, 36506, 36505, 1001004, 1000969, 54943, 36463, 1000663, 1000994,
#1000993, 1000992, 1000991, 1000990, 1000989, 1000987, 1000986, 1000985, 1000984, 1000983, 1000982, 1000980,
#1000979, 1000978, 1000977, 1000976, 1000967, 1000968, 1000970, 1000810, 1000825, 1000953, 36481, 36482, 36483,
#25418, 1000599, 1000686, 54946, 36453, 55402, 36454, 36452, 1000596, 26503, 528637, 1000893, 23988, 1000598,
#1000685, 1000684, 1000892, 1000891, 1000890, 1000889, 1000888, 1000887, 1000886, 1000885, 1000884,1000883,
#1000882, 1000881, 1000880, 1000879, 1000878, 1000877, 1000876, 1000875, 1000874, 1000873, 1000870, 23954,
#1000844, 528632, 528623, 26051, 23100, 21910, 1000805, 1000828, 528646, 528641, 528640, 528639, 528638, 528636,
#528633, 528631, 528629, 528627, 528626, 528624, 1000795, 1000763, 1000664, 1000654, 1000678, 1000676, 1000672,
#1000671, 1000670, 1000807, 1000806, 1000808, 1000809, 1000811, 1000812, 1000804, 1000798, 1000675, 6635,
#1000674, 1000668, 604319, 604316, 604315, 604314, 604309, 604306, 604304, 604260, 604258, 604257, 604256,
#1000693, 1000680, 1000712, 1000732, 1000728, 1000667, 1000718, 1000719, 1000716, 1000715, 1000713, 1000714,
#1000493, 1000717, 1000669, 582528, 1000679, 1000677, 1000673, 1000559, 130211, 130212, 130213, 1000483, 55191,
#55190, 54950, 54940, 36529, 36464, 36436, 6637, 23977, 23966, 21736, 6661, 6659, 6651, 6649, 6647,
#6643, 6641, 6639]

# Update credentials
cnx = mysql.connector.connect(user='', password='', host='', database='')

DEBUG = False  # Debug flag that prints lots of information

if DEBUG is True:
    # Connection test
    y = cnx.cursor(buffered=True)
    query_test = ("select count(*) from articles;")
    y.execute(query_test)
    test_result = y.fetchone()[0]
    print("Query result: ", test_result)
    #key = input('Press any key to continue')

cursor_x = cnx.cursor(buffered=True)  # Cursor for db manipulations

# Text Analytics subscription
# Sentiment
subscription_key = ''  # Update subscription key
api_endpoint = 'https://eastus.api.cognitive.microsoft.com/text/analytics/v2.0/'
language_api_url = api_endpoint + "sentiment"
if DEBUG is True:
    print(language_api_url)
# Key phrases
subscription_key2 = ''  # Update subscription key
language_api_url_phrases = api_endpoint + "keyPhrases"
if DEBUG is True:
    print(language_api_url_phrases)


for region in region_id:
    print('Region: ', region)
    # JSON
    url = 'https://services.radio-canada.ca/hackathon/neuro/v1/future/lineups/'+str(region)+'?'
    page_Number = 1
    params = dict(
        pageNumber=str(page_Number),
        client_key=''  # Update API key
    )

    # API may fail, make requests until success
    request_success = False
    while request_success != True:
        resp = requests.get(url=url, params=params)
        if resp.status_code == 200:
            request_success = True
        data = resp.json()

    while True:  # For each result of search
        results = int(data['pagedList']['totalNumOfItems'])
        pageNumber = int(data['pagedList']['pageNumber'])
        pageSize = int(data['pagedList']['pageSize'])
        if DEBUG is True:
            print('Results', results)
            print('pageNumber', pageNumber)
            print('pageSize', pageSize)

        iterations = len(data['pagedList']['items'])
        loops = math.ceil(results/pageSize)
        if DEBUG is True:
            print('Loops: ', loops)
        i = 0
        for i in range(iterations):
            # Parsing article ID
            article_id = int(data['pagedList']['items'][i]['id'])
            if DEBUG is True:
                print('INT article_id:', article_id)

            # Parsing article's title
            title = str(data['pagedList']['items'][i]['title'])
            if DEBUG is True:
                print('TEXT title:', title)

            # Parsing article's link
            link = str(data['pagedList']['items'][i]['canonicalWebLink'].get('href'))
            if DEBUG is True:
                print('TEXT link:', link)

            # Parsing article's summary
            summary = str(data['pagedList']['items'][i]['summary'])
            if DEBUG is True:
                print('TEXT Summary:', summary)


            # Getting article's body
            raw_body = []
            body = []
            body_result = []
            page = urllib.request.urlopen(link)
            soup = BeautifulSoup(page, 'html.parser')
            raw_body = soup.find_all('p')
            for g in range(len(raw_body)):
                a = b'<p> '
                b = b'<p><'
                if raw_body[i].find(a[0] & b[0]) != -1:
                    body.append(str(raw_body[g]))

            for f in range(len(body)):
                body_result = ' '.join(body)

            if DEBUG is True:
                print("TEXT Body: ", body_result)

            # Parsing article's images
            try:
                images = str(data['pagedList']['items'][i]['summaryMultimediaItem']['summaryImage']['concreteImages'][4]['mediaLink']['href'])
            except:
                images = '0'
            if DEBUG is True:
                print('TEXT Image:', images)


            # Parsing article's content type
            try:
                region = str(data['name'])
            except:
                region = '0'
            if DEBUG is True:
                print('TEXT Region:', region)

            # Key phrases
            # Getting sentiment float value (0-bad 1-good)
            documents_phrases = {'documents': [
                {'id': '1', 'language': 'fr',
                 'text': summary}
            ]}
            headers_phrases = {'Ocp-Apim-Subscription-Key': subscription_key2}
            req = requests.post(language_api_url_phrases, headers=headers_phrases, json=documents_phrases)
            phrases = req.json()
            phrases_extracted = str(phrases['documents'][0]['keyPhrases'])
            phrase = []
            for i in range(len(phrases['documents'][0]['keyPhrases'])):
                phrase.append(phrases['documents'][0]['keyPhrases'][i])
            phrases_result = ','.join(phrase)

            if DEBUG is True:
                print("TEXT phrases: ", phrases_result)

            # Getting sentiment float value (0-bad 1-good)
            documents = {'documents': [
                {'id': '1', 'language': 'fr',
                 'text': summary}
            ]}
            headers = {'Ocp-Apim-Subscription-Key': subscription_key}
            req = requests.post(language_api_url, headers=headers, json=documents)
            sentiments = req.json()
            sentiment = float(sentiments['documents'][0]['score'])
            if DEBUG is True:
                print("FLOAT sentiment: ", sentiment)

            # Upload data into database
            # id INT UNSIGNED AUTO_INCREMENT NOT NULL PRIMARY KEY,
            # article_id INT NOT NULL,
            # title VARCHAR(255) NOT NULL,
            # link VARCHAR(255) NOT NULL,
            # summary TEXT,
            # body TEXT,
            # images VARCHAR(255),
            # region VARCHAR(255),
            # keyphrases TEXT,
            # sentiment FLOAT,

            insert_query = ("INSERT INTO articles (article_id, title, link, summary, body, images, region, keyphrases, sentiment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);")

            insert_data = [article_id, title, link, summary, body_result, images, region, phrases_result, sentiment ]

            cursor_x.execute(insert_query, insert_data)
            cnx.commit()

        # Polling the next page of news line-up
        if pageNumber < loops:
            page_Number += 1
            params = dict(
                pageNumber=str(page_Number),
                client_key=''  # Update API key
            )

            request_success = False

            while request_success != True:
                resp = requests.get(url=url, params=params)
                if resp.status_code == 200:
                    request_success = True
                data = resp.json()
        else:
            break
cnx.close()
