import requests
import os
from bs4 import BeautifulSoup, NavigableString
import re

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
            file['size'] = re.match(r"\s+(\d+)\s+$", re.split('[AP]M', e)[1])[1]
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
            return {'value': float(value), 'unit': unit}
    raise Exception("Demo size failed to get parsed")


def index_matches():
    matches = []
    dir = 'cache/ChallengeTV/demos/view'
    for file in os.listdir(dir):
        file_path = os.path.join(dir, file)
        with open(file_path, 'r') as f:
            size = parse_demo_size_from_match_page(f.read())
        matches.append({'size': size})
    return matches


def size_match(byte_size, megabyte_size):
    return round(byte_size / 1024 / 1024, 2) == megabyte_size


# parse_demo_list()
# download_match_pages()