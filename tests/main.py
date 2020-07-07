import web


def test_parse_demo_size_from_match_page():
    with open('../cache/ChallengeTV/demos/view/10', 'r') as f:
        size = web.parse_demo_size_from_match_page(f.read())
    assert size['value'] == 1.25 and size['unit'] == 'MB'


def test_size_match():
    assert web.size_match(7727104, 7.37)
