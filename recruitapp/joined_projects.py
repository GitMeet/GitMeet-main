import collections
import project
class Joined:
    def __init__(self, *args):
        self.__dict__ = dict(zip(['user', 'projectdb'], args))
        self.full_projects = [project.Project(i) for i in self.projectdb.get_projectname_description_owner_id_team_teamneeded_requests_extra('projects')]
        self.joined_projects = [i for i in self.full_projects if any(t.username == self.user for t in i.team)]
        print "in error logs testing self.joined_projects", self.joined_projects

    @property
    def length(self):
        count = 0
        for project in self.joined_projects:
            count += sum([len([b for b in project.jobs if b.id == i.id]) for i in project.team if i.username == self.user])
        return count

    def __iter__(self):
        if not self.joined_projects:
            raise StopIteration('no projects that {user} belongs to'.format(**self.__dict__))
        joined_project = collections.namedtuple('joined_project', ['project', 'user_jobs'])
        for project in self.joined_projects:

            specific_project = [[b for b in project.jobs if b.id == i.id][0] for i in project.team if i.username == self.user]

            print "specific_project", specific_project
            yield joined_project(project, specific_project)
