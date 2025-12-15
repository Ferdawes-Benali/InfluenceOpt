from core.data_models import User, Edge, Campaign


def test_user_dataclass():
    u = User('id', 'name', 'IG', 1000, 100.0, 0.05, 0.02)
    assert u.id == 'id'
    assert u.followers == 1000


def test_campaign():
    c = Campaign('c', 10000, 0.1, 0.8, 1.0)
    assert c.budget == 10000
