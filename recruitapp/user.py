import collections
import random
import functools

class User:
    """
    simple wrapper for user database listings
    username text, name text, avatar text, email text, summary text, id int, extra text
    """
    headers = ['username', 'name', 'avatar', 'email', 'summary', 'id', 'extra']
    def __init__(self, data):
        self.colors = ['green', '#E3C611', 'red', 'blue', 'yellow', 'orange', '#E10D87', '#11E3D3']
        random.shuffle(self.colors)
        self.colors = iter(self.colors)
        options = collections.namedtuple('options', ['tags', 'recieve_invites', 'display_email'])
        self.__dict__ = {a:b if a != 'extra' else options(*[[(tag, next(self.colors, 'blue')) for tag in a[i]] if i == 'tag' else a[i] for i in ['tags', 'recieve_invites', 'display_email']]) for a, b in zip(self.headers, data)}
    
