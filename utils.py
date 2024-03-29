import os
import json
import random

from datetime import datetime


def read_json_file(path):
    with open(path) as json_file:
        data = json.load(json_file)

    return data


def get_news(lang='sk', items=None):
    news = []
    counter = 0

    for item in read_json_file(os.path.join('data', 'news.json')):
        counter += 1
        data = {
            "date": datetime.strptime(item['date'], '%Y-%m-%d').date(),
            "categories": item['categories']
        }

        if lang == "sk":
            data["title"] = item['title_sk']
            data["meta"] = item['meta_sk']

        if lang == "en":
            data["title"] = item['title_en']
            data["meta"] = item['meta_en']

        if 'url' in item.keys():
            data['url'] = item['url']

        news.append(data)

        if items and counter >= items:
            break

    return news


def get_jobs():
    print(read_json_file(os.path.join('data', 'jobs.json')))
    return read_json_file(os.path.join('data', 'jobs.json'))


def encode_name(name):
    return name.lower().replace('-', '--').replace(' ', '-')


def decode_name(encoded_name):
    return encoded_name.lower().replace('-', ' ').replace('  ', '-')


def get_speakers():
    return read_json_file(os.path.join('data', 'speakers.json'))


def get_talks():
    return read_json_file(os.path.join('data', 'talks.json'))


def get_sponsors():
    all_sponsors = read_json_file(os.path.join('data', 'sponsors.json'))
    categories = {}
    for _sponsor in all_sponsors:
        name = _sponsor.get('name', '')
        ctg = _sponsor.get('category', 'Partners')
        sponsor = {
            'name': name,
            'category': ctg,
            'class': ctg.lower(),
            'link': _sponsor.get('link', ''),
            'logo': _sponsor.get('logo', ''),
            'alt': _sponsor.get('alt', name + ' logo')
        }
        categories.setdefault(ctg, []).append(sponsor)
    return categories


def get_edu_speakers():
    return read_json_file(os.path.join('data', 'edusummit_speakers.json'))


def get_edu_talks():
    return read_json_file(os.path.join('data', 'edusummit_talks.json'))
