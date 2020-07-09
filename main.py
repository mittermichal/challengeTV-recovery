import time

import requests
import os
from bs4 import BeautifulSoup, NavigableString
import re
from db import db_session, MatchPage, Demo, DemoMatch, DemoMatchAssocType
from sqlalchemy.orm.exc import NoResultFound
import re

# def parse_view(id):
#     root=html.fromstring(requests.get('http://demos.igmdb.org/ChallengeTV/demos/view/'+str(id)).text)
#     print(root.xpath('//div[@class="matchlineup"]/div/text()'))
# parse_view(10)


# CHTV_!hero-USA_21-USA_!hero_Map01_ZDaemon_1v1.zip
#      teamA-flg_??-flg_teamB_map  _mode?
# m = re.match(r"CHTV_", e.contents[0])
# match_demo['teamA'] =


def index_demo_list():
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

    for file in file_list_generator(content):
        demo = Demo(
            size=file['size'],
            path=file['path']
        )
        db_session.add(demo)
        db_session.commit()


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
    # 22000+ pages
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
    e = parsed_page.find("table", attrs={'bgcolor': '#3B434C'})
    for h6 in e.find_all('h6'):
        if h6.contents[0].contents[0] == 'Demo Size: ':
            value, unit = h6.contents[1].split(' ')
            del parsed_page
            return {'value': float(value), 'unit': unit}
    raise Exception("Demo size failed to get parsed")


def parse_match_info(content):
    parsed_page = BeautifulSoup(content, "html.parser")
    e = parsed_page.find("div", attrs={'id': 'main_content'})
    h3s = e.find_all('h3')
    teamA, teamB = h3s[0].text.strip().split(' vs ')
    if h3s[1].contents[0] == 'in a ':
        game_mode = h3s[1].contents[1].text.strip()
    else:
        raise Exception("Failed to parse game mode")
    game = h3s[2].contents[0].contents[0].strip()
    map = h3s[2].contents[0].contents[2].text.strip()
    return {'teamA': teamA, 'teamB': teamB, 'game_mode': game_mode, 'game': game, 'map': map}


def parse_demo_info_from_path(path):
    name = os.path.splitext(os.path.split(path)[-1])[0]
    underscore_splits = name.split('_')
    if re.match(r'^\d+$', underscore_splits[-1]):
        del underscore_splits[-1]
    if underscore_splits[-3] == 'Enemy' and underscore_splits[-2] == 'Territory':
        game = 'ET'
        demo_map = underscore_splits[-4]
    else:
        game = underscore_splits[-2]
        demo_map = underscore_splits[-3]

    teamA, teamB = map(lambda x: x.split('-')[0], underscore_splits[1:3])
    game_mode = underscore_splits[-1]

    return {'teamA': teamA, 'teamB': teamB, 'game_mode': game_mode, 'game': game, 'map': demo_map}


def index_demo_info():
    for i, demo in enumerate(Demo.query.order_by(Demo.id).all()):
        try:
            info = parse_demo_info_from_path(demo.path)
        except Exception as e:
            print('error in demo {} {} \n {}'.format(demo.id, demo.path, str(e)))
        else:
            demo.teamA = info['teamA']
            demo.teamB = info['teamB']
            demo.game = info['game']
            demo.game_mode = info['game_mode']
            demo.map = info['map']
            db_session.commit()
        if i % 50 == 0:
            print('demo i', i)


def index_matches():
    directory = 'cache/ChallengeTV/demos/view'
    start_time = time.time()
    time_spent = 0
    count = len(os.listdir(directory))
    for i, file in enumerate(os.listdir(directory)):
        file_path = os.path.join(directory, file)
        with open(file_path, 'r', errors='replace') as f:
            try:
                match = MatchPage.query.filter(MatchPage.id == int(file)).one()
            except NoResultFound:
                try:
                    size = parse_demo_size_from_match_page(f.read())
                except ValueError:
                    size = None
                if size is not None:
                    match = MatchPage(
                        id=int(file),
                        size=size['value'],
                        unit=size['unit']
                    )
                else:
                    match = MatchPage(id=int(file))
                db_session.add(match)
                db_session.commit()
            else:
                try:
                    info = parse_match_info(f.read())
                except Exception as e:
                    print('error in {} \n {}'.format(file, str(e)))
                else:
                    match.teamA = info['teamA']
                    match.teamB = info['teamB']
                    match.game = info['game']
                    match.game_mode = info['game_mode']
                    match.map = info['map']
                    db_session.commit()

        match_i = i + 1
        if match_i % 50 == 0:
            end_time = time.time()
            diff = end_time - start_time
            time_spent += diff
            avg_time_per_file = time_spent / match_i
            time_left = avg_time_per_file * (count - match_i)
            print('parsed: {} ETA: {}s SPENT: {}s'.format(match_i, time_left, time_spent))
            start_time = end_time
        match_i += 1


# select unit from match group by unit; -> B,KB,MB
def size_match(byte_size, var_size):
    if byte_size['unit'] != 'B' or var_size['unit'] not in ['B', 'KB', 'MB']:
        raise Exception('wrong byte unit')
    if var_size['unit'] == 'B':
        return byte_size['value'] == var_size['value']
    elif var_size['unit'] == 'KB':
        return round(byte_size['value'] / 1024, 2) == var_size['value']
    elif var_size['unit'] == 'MB':
        return round(byte_size['value'] / 1024 / 1024, 2) == var_size['value']
    else:
        raise Exception('wrong var unit')


def demo_to_match_by_size():
    # too many connections and too slow
    # part of data saved in tmp/test-size.db or tmp/demo_match.sql
    matches = MatchPage.query.filter(MatchPage.size != None).all()
    for demo in Demo.query.order_by(Demo.id).all():
        start_time = time.time()
        print('demo:', demo.id)
        for match in matches:
            if size_match(
                    {'value': demo.size, 'unit': 'B'},
                    {'value': match.size, 'unit': match.unit}
            ):
                msg = "{} ==> {}".format(demo.path, match.id)
                print(msg)
                db_session.add(DemoMatch(
                        demo_id=demo.id,
                        match_id=match.id,
                        type=DemoMatchAssocType.size.value
                    ))
                db_session.commit()
        print("{}".format(time.time()-start_time))


def demo_to_match_by_game_game_mode():
    not_found_count = 0
    with open('tmp/game-game_mode.txt', 'w') as f:
        with open('tmp/game-game_mode-e.txt', 'w') as err:
            for i, demo in enumerate(Demo.query.order_by(Demo.id).all()):
                matches = MatchPage.query.\
                    filter(demo.game_mode == MatchPage.game_mode).\
                    filter(demo.game == MatchPage.game).\
                    count()
                log_line = "{} {}\n".format(demo.id, matches)
                f.write(log_line)
                if matches == 0:
                    not_found_count += 1
                    log_line = "no matches found for {}\n".format(os.path.splitext(os.path.split(demo.path)[-1])[0])
                    err.write(log_line)
                if i % 50 == 0:
                    print('demo i', i)
            err.write("count:" + str(not_found_count))


def demo_to_match_by_game_game_mode_size():
    with open('tmp/game-game_mode-size.txt', 'w') as f:
        with open('tmp/game-game_mode-size-e.txt', 'w') as err:
            for i, demo in enumerate(Demo.query.order_by(Demo.id).all()):
                matches = MatchPage.query.\
                    filter(MatchPage.size != None).\
                    filter(demo.game_mode == MatchPage.game_mode).\
                    filter(demo.game == MatchPage.game).\
                    all()
                found_count = 1
                for match in matches:
                    if size_match(
                            {'value': demo.size, 'unit': 'B'},
                            {'value': match.size, 'unit': match.unit}
                    ):
                        # msg = "{} ==> {}".format(demo.path, match.id)
                        # print(msg)
                        db_session.add(DemoMatch(
                            demo_id=demo.id,
                            match_id=match.id,
                            type=DemoMatchAssocType.gm_g_size.value
                        ))
                        db_session.commit()
                        found_count += 1

                log_line = "{} {}\n".format(demo.id, found_count)
                f.write(log_line)
                if len(matches) > 0 and found_count == 0:
                    log_line = "no matches found for {} {}\n".format(
                        os.path.splitext(os.path.split(demo.path)[-1])[0],
                        match.id
                    )
                    err.write(log_line)
                if i % 5 == 0:
                    print('demo i', i)


if __name__ == '__main__':
    # index_matches()
    demo_to_match_by_game_game_mode_size()
    # index_demo_list()
    # demo_to_match_by_size()
    pass


"""
to browse matches:
select * from demo_match left join demo on demo_match.demo_id=demo.id left join match on demo_match.match_id=match.id;


demo matches count stats:
select c, count(*) from (select count(*) as c from demo_match group by demo_id) group by c; 



match demos count stats:
select c, count(*) from (select count(*) as c from demo_match group by match_id) group by c; 
"""
