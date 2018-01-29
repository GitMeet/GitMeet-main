import collections
import re

class Teammate:
    def __init__(self, *args):
        self.__dict__ = dict(zip(['projectname', 'name', 'job_title', 'job_id'], args))
    @property
    def award_bonus(self):
        return "/award_bonus/{projectname}/{name}/{job_id}".format(**self.__dict__)

    def __repr__(self):
        return "/remove_teammate/{projectname}/{name}/{job_id}".format(**self.__dict__)

class Team:
    def __init__(self, *args):
        self.__dict__ = dict(zip(['projectname', 'db_instance'], args))
        self.projects = filter(lambda (pro_name, team):pro_name == self.projectname, self.db_instance.get_projectname_team('projects'))[0][-1]

    @property
    def length(self):
        return 0 if not self.projects else len(self.projects)

    def __iter__(self):
        if not self.projects:
            raise StopIteration('no team members')

        for i in self.projects:
            yield Teammate(*([self.projectname]+i))
