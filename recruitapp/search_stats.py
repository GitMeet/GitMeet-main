import tigerSqlite
import collections
import re
import gitmeet_user
import project as project_object
import itertools
class Job:
    def __init__(self, job_listing):
        self.job_listing = job_listing
        self.__dict__.update(job_listing[0])
    def __repr__(self):
        return "/{}/{}".format(*self.job_listing[-2:][::-1])
class SearchBlock:
    def __init__(self, query, block_type):
        self.block_type = block_type
        self.query = query
        self.users = [i for i in tigerSqlite.Sqlite('/home/jamespetullo/gitmeet/userprofiles.db').get_username_name_avatar_email_summary_id_extra('users') if str(self.query).lower() in str(i[0]).lower()]
        self.projects = [i for i in tigerSqlite.Sqlite('/home/jamespetullo/gitmeet/projects.db').get_projectname_description_owner_id_team_teamneeded_requests_extra('projects') if str(self.query).lower() in str(i[0]).lower() or str(self.query).lower() in str(i[1]).lower()]
        self.jobs = list(itertools.chain(*[[[job]+[i[0], i[1]] for job in filter(None, i[-1]) if str(self.query).lower() in (' ' if not job['job_description'] else str(job['job_description']).lower()) or str(self.query).lower() in (' ' if not job['job_title'] else str(job['job_title']).lower())] for i in tigerSqlite.Sqlite('/home/jamespetullo/gitmeet/projects.db').get_projectname_owner_teamneeded('projects') if i[-1]]))
        #self.jobs = [[job for job in i[-1]] for i in tigerSqlite.Sqlite('/home/jamespetullo/gitmeet/projects.db').get_projectname_owner_teamneeded('projects') if i[-1]]
class UserSearch(SearchBlock):

    @property
    def length(self):
        return len(self.users)

    def __iter__(self):
        if not self.users:
            raise StopIteration('no users found')
        for user in self.users:
            yield gitmeet_user.User(user)
class ProjectSearch(SearchBlock):
    @property
    def length(self):
        return len(self.projects)


    def __iter__(self):
        if not self.projects:
            raise StopIteration('no projects')
        for p in self.projects:
            yield project_object.Project(p)

class JobSearch(SearchBlock):
    @property
    def length(self):
        return len(self.jobs)
    def __iter__(self):
        for job in self.jobs:
            yield Job(job)


