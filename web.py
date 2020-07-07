import time

import requests
import os
from bs4 import BeautifulSoup, NavigableString
import re
from db import db_session, Match
from sqlalchemy.orm.exc import NoResultFound

# def parse_view(id):
#     root=html.fromstring(requests.get('http://demos.igmdb.org/ChallengeTV/demos/view/'+str(id)).text)
#     print(root.xpath('//div[@class="matchlineup"]/div/text()'))
# parse_view(10)


# CHTV_!hero-USA_21-USA_!hero_Map01_ZDaemon_1v1.zip
#      teamA-flg_??-flg_teamB_map  _mode?
# m = re.match(r"CHTV_", e.contents[0])
# match_demo['teamA'] =


def parse_demo_list():
    demo_list_url = 'http://demos.igmdb.org/ChallengeTV/demostorage/Miscellaneous/'
    filename = 'cache/demo_list.html'
    if os.path.exists(filename):
        f = open(filename, "r")
        content = f.read()
        f.close()
    else:
        content = requests.get(demo_list_url).content
        f = open(filename, "wb")
        f.write(content)
        f.close()
    match_demo = {}
    demo_list = []
    return [
        {
            'size': {
                'value': file['size'],
                'unit': 'B'
            },
            'path': file['path']
        }
        for file in file_list_generator(content)]


def file_list_generator(content):
    parsed_page = BeautifulSoup(content, "html.parser")
    file = {}
    for i, e in enumerate(list(parsed_page.body.pre.children)):
        if i < 3:  # skip [To Parent Directory]
            continue
        if isinstance(e, NavigableString):
            try:
                file['size'] = re.match(r"\s+(\d+)\s+$", re.split('[AP]M', e)[1])[1]
            except TypeError:
                break  # <dir>
            # print(i, e)
        elif e.name == 'a':
            file['path'] = e.attrs['href']
            yield file
            file = {}


def download_match_pages():
    list_url = 'http://demos.igmdb.org/ChallengeTV/demos/view/'
    filename = 'cache/match_list.html'
    if os.path.exists(filename):
        f = open(filename, "r")
        content = f.read()
        f.close()
    else:
        content = requests.get(list_url).content
        f = open(filename, "wb")
        f.write(content)
        f.close()
    i = 1
    for file in file_list_generator(content):
        r = requests.get('http://demos.igmdb.org'+file['path'])
        if r.status_code == 200:
            with open('cache'+file['path'], "wb") as f:
                f.write(r.content)
            print(i)
            i += 1
        else:
            raise Exception


def parse_demo_size_from_match_page(content):
    parsed_page = BeautifulSoup(content, "html.parser")
    e = parsed_page.find_all("table", attrs={'bgcolor': '#3B434C'})
    for h6 in e[0].find_all('h6'):
        if h6.contents[0].contents[0] == 'Demo Size: ':
            value, unit = h6.contents[1].split(' ')
            del parsed_page
            return {'value': float(value), 'unit': unit}
    raise Exception("Demo size failed to get parsed")


def index_matches():
    directory = 'cache/ChallengeTV/demos/view'
    match_i = 1
    start_time = time.time()
    time_spent = 0
    count = len(os.listdir(directory))
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        with open(file_path, 'r') as f:
            try:
                Match.query.filter(Match.id == int(file)).one()
            except NoResultFound:
                try:
                    size = parse_demo_size_from_match_page(f.read())
                except ValueError:
                    size = None
                if size is not None:
                    match = Match(
                        id=int(file),
                        size=size['value'],
                        unit=size['unit']
                    )
                else:
                    match = Match(id=int(file))
                db_session.add(match)
                db_session.commit()

                if match_i % 50 == 0:
                    end_time = time.time()
                    diff = end_time - start_time
                    time_spent += diff
                    avg_time_per_file = time_spent / match_i
                    time_left = avg_time_per_file * (count - match_i)
                    print('parsed: {} ETA: {}s SPENT: {}s'.format(match_i, time_left, time_spent))
                    start_time = end_time
                match_i += 1


def size_match(byte_size, megabyte_size):
    if byte_size['unit'] != 'B' or megabyte_size['unit'] != 'MB':
        raise Exception('wrong units')
    return round(byte_size['value'] / 1024 / 1024, 2) == megabyte_size['value']


if __name__ == '__main__':
    index_matches()
    # with open('tmp/matches.txt', 'w') as log:
    #     demo_i = 1
    #     matches = get_matches()
    #     for demo in parse_demo_list():
    #         for match in matches:
    #             if size_match(demo['size'], match['size']):
    #                 msg = "{} ==> {}".format(demo['path'], match['file'])
    #                 print(msg)
    #                 log.write(msg)
    #                 break
    #         if demo_i % 50 == 0:
    #             print('demo_i', demo_i)
    #         demo_i += 1



# parse_demo_list()
# download_match_pages()
