import datetime
import collections
import random
import project
import tigerSqlite
import functools
def top_projects(huristics):
    '''ulimately, read from file created by "click" program to select top project'''
    @functools.wraps(huristics)
    def wrapper(cls):
        full_projects = huristics(cls)
        final_projects = []
        for i in range(4):
            while True:
                project = random.choice(full_projects)
                if project not in final_projects:
                    final_projects.append(project)
                    break
        return final_projects
    return wrapper



class TopProjects:
    def __init__(self):
        self.t = tigerSqlite.Sqlite('projects.db')
        self.projects = self.get_top_projects()

    @top_projects
    def get_top_projects(self):
        return self.t.get_projectname_description_owner_id_team_teamneeded_requests_extra('projects')

    @staticmethod
    def months_of_the_year():
        return [(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')]

    @property
    def time_now(self):
        data_now = datetime.datetime.now()
        return "{} {}, {}".format(*[dict(TopProjects.months_of_the_year())[data_now.month], data_now.day, data_now.year])
    @property
    def length(self):
        return len(self)

    def __len__(self):
        return len(self.projects)

    def __iter__(self):
        top_project = collections.namedtuple('top_project', 'owner, project')
        for pro in self.projects:
            yield top_project(pro[2], project.Project(pro))
