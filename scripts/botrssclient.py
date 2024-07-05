import logging
import os
import re
import sys
import feedparser
import requests
from bs4 import BeautifulSoup
from meta_ai_api import MetaAI
import pprint, objprint
import time, json


class NewsClient:
    title = ""
    summary = ""
    description = ""
    url = ""
    status = ""
    ai_prompt = ""
    ai_response = ""
    ai_questions_prompt = ""
    ai_questions_response = ""
    tags = []
    properties = []
    location = []
    created_by = ""
    published_at = ""

    def __init__(self, url, created_by, title, published_at, status):
        self.url = url
        self.created_by = created_by
        self.title = title
        self.published_at = published_at
        self.status = status

    def tojson(self):
        vals = {
            'title': self.title,
            'summary': self.summary,
            'description': self.description,
            'url': self.url,
            'status': self.status,
            'ai_prompt': self.ai_prompt,
            'ai_response': self.ai_response,
            'ai_questions_prompt': self.ai_questions_prompt,
            'ai_questions_response': self.ai_questions_response,
            'tags': self.tags,
            'properties': self.properties,
            'location': self.location,
            'created_by': self.created_by,
            'published_at': self.published_at
        }
        return vals


def _get_content(news: NewsClient):
    content = ""
    if news.url.startswith("https://www.sciencedaily.com"):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0'}
        response = requests.get(news.url, headers=headers)
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        content = soup.find('div', {'id': 'text'}).text
    return content


def _extract_regex(pattern, text):
    strmatch = re.search(pattern, text)
    if strmatch:
        return strmatch.group(1)


def _parse_ai_response(news: NewsClient):
    news.summary = news.ai_response
    if "Paragraph two" in news.ai_questions_response:  # format regex
        is_climate_change = _extract_regex(r'Paragraph two:(.*)', news.ai_questions_response)
        climate_change_mitigation = _extract_regex(r'Paragraph three:(.*)', news.ai_questions_response)
        climate_change_damage = _extract_regex(r'Paragraph four:(.*)', news.ai_questions_response)
        tags_raw = _extract_regex(r'Question five:(.*)', news.ai_questions_response)
        location_raw = _extract_regex(r'Question six:(.*)', news.ai_questions_response)
    else:  # split method
        parts = news.ai_questions_response.split("\n")
        is_climate_change = parts[0]
        climate_change_mitigation = parts[1]
        climate_change_damage = parts[2]
        tags_raw = parts[3]
        location_raw = parts[4]

    if is_climate_change and "Yes" in is_climate_change:
        news.status = "NEW"
    else:
        news.status = "DISCARDED"

    properties = []
    if climate_change_mitigation and "Yes" in climate_change_mitigation:
        properties.append("Mitigation")
    if climate_change_damage and "Yes" in climate_change_damage:
        properties.append("Impact")
    news.properties = properties
    if location_raw:
        news.location = [s.strip() for s in location_raw.split(",")]
    if tags_raw:
        news.tags = [s.strip() for s in tags_raw.split(",")]
        # sometimes locations are added in the tags
        news.tags = [element for element in news.tags if element not in news.location]

    return news


def _is_within_hours(time_to_compare, hours: int):
    return time.mktime(time_to_compare) >= time.time() - hours * 60 * 60


def save(news: NewsClient):
    url = "http://localhost:8000/api/v1/news/"
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, data=json.dumps(news.tojson()), headers=headers)
    if response.status_code == 201:
        print('News added successfully!')
    else:
        print('Error adding news:', response.text)


def _proces_rss_feed(url):
    # user = User.objects.get(username="ClimateBot")
    user = 1 # ClimateBot
    feed = feedparser.parse(url)
    total_news = []
    ai = MetaAI()
    for entry in feed.entries:
        logging.info(">> Processing entry '%s'" % entry.title)
        # , published_at=entry.published_parsed,
        new_news = NewsClient(url=entry.link, created_by=user, title=entry.title,
                              published_at=time.strftime('%Y-%m-%dT%H:%M:%S', entry.published_parsed),
                              status="DRAFT")
        if False:  # News.objects.filter(url=new_news.url).exists(): TODO IMPLEMENT
            logging.warning("Url %s already exists" % rss_url)
        else:
            logging.warning("New news found: %s" % rss_url)
            if not _is_within_hours(entry.published_parsed, 48):
                logging.warning("Url %s published at %s is older than 48 hours" % (new_news.url, new_news.published_at))
                continue

            # new_news.save() TODO SAVE ?

            content = _get_content(new_news)

            prompt = ("Read the following article:\n\n"
                      "%s\n\n"
                      "End of article.\n\n"
                      "Can you provide a summary using data points in one paragraph narrative (no bullet points) and no more than 50 words?") % content
            new_news.ai_prompt = prompt
            # new_news.save()
            logging.debug("Prompt %s " % prompt)

            ai_response_raw = ai.prompt(message=prompt)
            new_news.ai_response = ai_response_raw["message"]
            # new_news.save()
            logging.debug("Response: %s" % new_news.ai_response)
            # ai_response_raw = {
            #     "message": "It is related\nBrief summary:\nThe article discusses a new study that reveals how ocean currents play a crucial role in the global carbon cycle, which is essential for understanding climate change. The research shows that ocean currents transport carbon from the surface to the deep ocean, where it can be stored for centuries, and highlights the importance of considering these currents in climate models.\nSummary:\nThe article explores the connection between ocean currents and the global carbon cycle, which is critical for understanding climate change. The study reveals that ocean currents transport carbon from the surface to the deep ocean, where it can be stored for centuries, and emphasizes the need to incorporate these currents into climate models to accurately predict carbon sequestration and mitigate climate change.\n",
            #     "sources": [],
            #     "media": []
            # }
            is_climate_change_prompt = ("Read the following article:\n\n"
                                        "%s\n\n"
                                        "End of article.\n\n"
                                        "Answer the following questions.\n\n"
                                        "Paragraph two: Is this article related with climate change? Start the answer with 'Yes' or 'No'\n"
                                        "Paragraph three: Does this article help to mitigate climate change ? Start the answer with 'Yes' or 'No'\n"
                                        "Paragraph four: Does this article describe damage created by climate change ? Start the answer with 'Yes' or 'No'\n"
                                        "question five: Tell me 5 tags that describes the article, only the tags separated by comma.\n"
                                        "question six: Is this article specific to a country or region in the world ? If Yes, just say the location, the locations separated by comma, or 'World' if global scope.\n") % content
            print(is_climate_change_prompt)
            new_news.ai_questions_prompt = is_climate_change_prompt
            # new_news.save()
            ai_response_raw = ai.prompt(message=is_climate_change_prompt)
            new_news.ai_questions_response = ai_response_raw["message"]
            print(ai_response_raw["message"])
            # new_news.save()
            new_news = _parse_ai_response(new_news)
            # new_news.save()
            save(new_news)
            if new_news.status != "NEW":
                logging.warning("This article is not climate change.")
                continue

            total_news.append(new_news)

            print("------RESULT------")
            # objprint.op(new_news)
            print(new_news.tojson())
            print("//------END------")
            exit(1)
    return total_news


rss_feeds = [
    "https://www.sciencedaily.com/rss/earth_climate.xml"
]

# find climate change articles
entries = []
# add them into a database

for rss_url in rss_feeds:
    logging.info("Processing rss feed %s" % rss_url)
    all_news = _proces_rss_feed(rss_url)
    logging.info("Number of entries: %s" % len(all_news))
    # entries.extend(climate_entries)
    logging.info("Total entries: %s" % len(entries))
