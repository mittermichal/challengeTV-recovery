import main


def test_parse_demo_size_from_match_page():
    with open('../cache/ChallengeTV/demos/view/10', 'r') as f:
        size = main.parse_demo_size_from_match_page(f.read())
    assert size['value'] == 1.25 and size['unit'] == 'MB'


def test_size_match():
    assert main.size_match({'value': 7727104, 'unit': 'B'}, {'value': 7.37, 'unit': 'MB'})


def test_parse_match_info():
    with open('../cache/ChallengeTV/demos/view/10', 'r') as f:
        info = main.parse_match_info(f.read())
    assert info['teamA'] == 'Flaming Fist'
    assert info['teamB'] == 'Four Knights'
    assert info['game_mode'] == '4v4'
    assert info['game'] == 'Quakeworld'
    assert info['map'] == 'DM3'


def test_parse_demo_info_from_path():
    info = main.parse_demo_info_from_path('/ChallengeTV/demostorage/Miscellaneous/CHTV_20id-USA_SB-USA_xerxes_Dustbowl_TF2_6v6.zip')
    assert info['teamA'] == '20id'
    assert info['teamB'] == 'SB'
    assert info['game_mode'] == '6v6'
    assert info['game'] == 'TF2'
    assert info['map'] == 'Dustbowl'


def test_parse_demo_info_from_path_file_dup():
    info = main.parse_demo_info_from_path('/ChallengeTV/demostorage/Miscellaneous/CHTV_{UNi}-Finland_Russianz-Finland_schw_etf_openfire_ETF_8v8_1.zip')
    assert info['teamA'] == '{UNi}'
    assert info['teamB'] == 'Russianz'
    assert info['game_mode'] == '8v8'
    assert info['game'] == 'ETF'
    assert info['map'] == 'openfire'
