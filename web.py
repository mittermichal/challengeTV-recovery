import requests
import os
from bs4 import BeautifulSoup, NavigableString
import re

# def parse_view(id):
#     root=html.fromstring(requests.get('http://demos.igmdb.org/ChallengeTV/demos/view/'+str(id)).text)
#     print(root.xpath('//div[@class="matchlineup"]/div/text()'))
# parse_view(10)


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
    parsed_page = BeautifulSoup(content, "html.parser")
    match_demo = {}
    demo_list = []
    for i, e in enumerate(list(parsed_page.body.pre.children)):
        if i < 3:
            continue
        if i < 10:
            if isinstance(e, NavigableString):
                match_demo['size'] = re.match(r"\s+(\d+)\s+$", re.split('[AP]M', e)[1])[1]
                # print(i, e)
            elif e.name == 'a':
                match_demo['path'] = e.attrs['href']
                # CHTV_!hero-USA_21-USA_!hero_Map01_ZDaemon_1v1.zip
                #      teamA-flg_??-flg_teamB_map  _mode?
                # m = re.match(r"CHTV_", e.contents[0])
                # match_demo['teamA'] =
                print(match_demo)
                demo_list.append(match_demo)
                match_demo = {}
        else:
            break


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
