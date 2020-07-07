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
    for i, e in enumerate(list(parsed_page.body.pre.children)):
        if i < 3:
            continue
        if i < 20:
            if isinstance(e, NavigableString):
                match_demo['size'] = re.match(r"\s+(\d+)\s+$", re.split('[AP]M', e)[1])[1]
                print(i, e)
            elif e.name == 'a':
                # CHTV_!hero-USA_21-USA_!hero_Map01_ZDaemon_1v1.zip
                #      teamA-flg_??-flg_teamB_map  _mode?
                m = re.match(r"CHTV_", e.contents[0])
                # match_demo['teamA'] =
                print(match_demo)
                match_demo = {}
        else:
            break


parse_demo_list()
