import collections
import re
import gitmeet_user
import project as project_object
from itertools import chain
class JobResult:
    def __init__(self, data):
        self.projectname, self.owner, self.job_data = data
        if self.job_data[0]:
            self.__dict__.update(self.job_data[0])
            self.flag = True
        else:
            self.flag = False

class ResultsPannel:
    def __init__(self, *args):

        self.__dict__ = {a:len(b) for a, b in zip(['users', 'projects', 'jobs'], args)}

    def __iter__(self):
        for a, b in self.__dict__.items():
            yield '{}\n{}'.format(a, b)
class SearchResults:
    def __init__(self, *args):
        self.__dict__ = dict(zip(['query', 'userdb', 'projectdb'], args))
        self.user_data = self.userdb.get_username_name_avatar_email_summary_id_extra('users')
        self.project_data = self.projectdb.get_projectname_description_owner_id_team_teamneeded_requests_extra('projects')
        self.filtered_users = [i for i in self.user_data if self.query in i[0].lower()]
        self.projects = [i for i in self.project_data if self.query in i[0].lower() or self.query in i[1].lower() or self.query in i[2].lower()]

        self.jobs = [[a, d, [c for c in b if self.query in c['job_title'].lower() or self.query in c['job_description'].lower()]] for a, d, b in self.projectdb.get_projectname_owner_teamneeded('projects') if b]
        self.stats = ResultsPannel(self.filtered_users, self.projects, filter(None, self.found_jobs()))
        print "self.jobs in search results", self.jobs
    def found_jobs(self):
        return [i[-1] for i in self.jobs if i[-1]]
    @property
    def github_repos(self):
        return len(self.projects)
    @property
    def gitlab_projects(self):
        return sum('gitlab_link' in i[-1] for i in self.projects if i[-1])
    @property
    def gitter_rooms(self):
        return sum('gitter_link' in i[-1] for i in self.projects if i[-1])
    def __len__(self):
        return len(self.filtered_users)+len(self.projects) + len(self.found_jobs())

    def __bool__(self):
        return len(self) > 0

    @property
    def number_of_results(self):
        return len(self)

    def __repr__(self):
        return '{}(users found:{}, projects found:{}, jobs found:{})'.format(self.__class__.__name__, len(self.filtered_users), len(self.projects), len(self.jobs))

    def __iter__(self):
        if not len(self):
            raise StopIteration('no results')
        if self.filtered_users:
            for user in self.filtered_users:
                yield ['user', gitmeet_user.User(user)]
        if self.projects:
            for project in self.projects:
                yield ['project', project_object.Project(project)]
        if any(i[-1] for i in self.jobs):
            for job in self.jobs:
                if job[-1]:
                    yield ['job', JobResult(job)]
