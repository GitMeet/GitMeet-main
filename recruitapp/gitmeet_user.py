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
        self.colors = ['green', 'red', 'blue', '#EFE630', '#E10D87', '#11E3D3', '#E49434']
        self.colors = iter(self.colors)
        options = collections.namedtuple('options', ['tags', 'receive_invites', 'display_email', 'reputation'])

        self.__dict__ = {a:b if a != 'extra' else options(*[[[tag, next(self.colors, 'blue')] for tag in b[i]] if i == 'tags' else b.get(i, 0) for i in ['tags', 'receive_invites', 'display_email', 'rep']]) if b is not None else options(*[[], ["I wish to receive developer invitations"], ["Show email on profile"]]) for a, b in zip(self.headers, data)}

    @property
    def tag_length(self):
        return len([i for i in self.extra.tags if i and i[0]])

    @property
    def score(self):
        score_sheet = {'summary':12, 'email':5, 'is_visible':6, 'tags':8}

        return (sum(score_sheet[a] if a in ['summary', 'email'] and b else (14 if a == 'extra' and b.tags and b.display_email and b.display_email[0] == 'Show email on profile' else 6 if a == 'extra' and b.display_email and b.display_email[0] == 'Show email on profile' and not b.tags else (8 if a == 'extra' and b.tags and not b.display_email else 0)) for a, b in self.__dict__.items())/float(31))*100



    @classmethod
    def get_headers(cls):
        return cls.headers

#user = User([u'Ajax12345', u'James Petullo', u'https://avatars1.githubusercontent.com/u/22758857?v=4', u'pentester18@gmail.com', u'I am high school student passionate about turning ideas into functional products via code.', 2, None])
