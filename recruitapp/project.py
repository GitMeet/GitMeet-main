import collections
import re
import abc
import random
class Requests:
    def __init__(self, data):
        request = collections.namedtuple('request', 'username email')
        self.data = [] if data is None else [request(i['username'], i['email']) for i in data]

    @property
    def length(self):
        return len(self.data)
    def __iter__(self):
        for request in self.data:
            yield request
    def __len__(self):
        return len(self.data)

    def __bool__(self):
        return len(self.data) > 0

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, ' '.join("{}={}".format(i.username, i.email) for i in self.data))

class Team:
    def __init__(self, data):
        #teammate = collections.namedtuple('teammate', ['username', 'name', 'email', 'skills'])
        #self.data = [] if data is None else [teammate(*[ for i in ['username', 'name', 'email', 'skills']]) for c in data]
        teammate = collections.namedtuple('teammate', 'username, job, id')
        self.data = [] if data is None else [teammate(*i) for i in data]
    @property
    def length(self):
        return len(self.data)

    def __bool__(self):
        return len(self.data) > 0

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for teammate in self.data:
            yield teammate
    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, ', '.join(i.username for i in self.data))
class Job:
    """class to store data for each """
    headers = [u'job_description', u'job_title', u'bugs', u'id', u'job_tags']
    def __init__(self, data):
        self.colors = ['green', '#E3C611', 'red', 'blue', 'yellow', 'orange', '#E10D87', '#11E3D3']
        random.shuffle(self.colors)
        self.colors = iter(self.colors)
        job = collections.namedtuple('job', ['description', 'title', 'bugs', 'id', 'tags'])
        self.jobs = [] if data is None else [job(*[[(a, next(self.colors, 'blue')) for a in c[i]] if i == 'job_tags' else c[i] for i in self.headers]) for c in data]
    @property
    def length(self):
        return len(self.jobs)

    def __bool__(self):
        return len(self.jobs) > 0

    def __iter__(self):
        for job in self.jobs:
            yield job

    @classmethod
    def job_format(cls, data):
        job = collections.namedtuple('job', ['description', 'title', 'bugs', 'id', 'tags'])
        return [job(*[[(a, next(self.colors, 'blue')) for a in c[i]] if i == 'job_tags' else c[i] for i in cls.headers]) for c in data]

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, " ".join(i.title for i in self.jobs))

class Options:
    headers = ['project_tags', 'gitlab_link', 'disable_join', 'gitter_link']
    new_headers = ['_tags', '_gitlab', '_join', '_gitter']
    def __init__(self, data):
        self.__dict__ = {} if data is None else {dict(zip(self.headers, self.new_headers))[a]:b for a, b in data.items()}

    def __bool__(self):
        return bool(self.__dict__)

    @property
    def tags(self):
        return [] if not self.__dict__ else filter(None, re.split(',\s*', self.__dict__['_tags']))

    @property
    def gitlab(self):
        return '' if not self.__dict__ else self.__dict__['_gitlab']

    @property
    def join(self):
        return False if not self.__dict__ else self.__dict__['_join']
    @property
    def gitter(self):
        return '' if not self.__dict__ else self.__dict__['_gitter']

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, ' '.join("{}:{}".format(a[1:], b) for a, b in self.__dict__.items()))

class Project:
    #['projectname', 'description', 'owner', 'id', 'team', 'teamneeded', 'requests', 'extra']
    headers = ['title', 'description', 'owner', 'id', 'team', 'jobs', 'requests', 'options']
    def __init__(self, data):

        self.__dict__ = {a:b if a not in ['jobs', 'options', 'team', 'requests'] else (lambda x:Job(x) if a == 'jobs' else Options(x) if a == 'options' else Team(x) if a == 'team' else Requests(x))(b) for a, b in zip(self.headers, data)}

    @classmethod
    def format_project(cls, data):
        return {a:b if a not in ['jobs', 'options', 'team', 'requests'] else (lambda x:Job(x) if a == 'jobs' else Options(x) if a == 'options' else Team(x) if a == 'team' else Requests(x))(b) for a, b in zip(cls.headers, data)}


    def __repr__(self):
        return "{}/{}".format(self.owner, self.title)
