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
    assert info['teamA'] == 'Flaming Fist' and \
        info['teamB'] == 'Four Knights' and \
        info['game_mode'] == '4v4' and \
        info['game'] == 'Quakeworld' and \
        info['map'] == 'DM3'


def test_parse_demo_info_from_path():
    info = main.parse_demo_info_from_path('/ChallengeTV/demostorage/Miscellaneous/CHTV_20id-USA_SB-USA_xerxes_Dustbowl_TF2_6v6.zip')
    assert info['teamA'] == '20id' and \
        info['teamB'] == 'SB' and \
        info['game_mode'] == '6v6' and \
        info['game'] == 'TF2' and \
        info['map'] == 'Dustbowl'
