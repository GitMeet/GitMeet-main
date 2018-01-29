import collections
class Job:
    def __init__(self, pontial_worker, *args):

        self.for_project = args[0]
        self.owner = args[1]
        self.name = args[2]
        self.id = args[3]
        self.potential_worker = pontial_worker
    def __repr__(self):
        return "/invite_user/{owner}/{for_project}/{potential_worker}/{id}".format(**self.__dict__)

class SimpleProject:
    def __init__(self, potential_worker, iter_id,  *data):
        print "!"*10
        print "data here", data
        print "!"*10
        self.potential_worker = potential_worker

        self.title = data[0]
        self.owner = data[1]
        self.description = data[2]
        self.current_team = 0 if not data[3] else len(data[3])
        self.jobs = data[4]
        self.iter_id = iter_id

        self.full_jobs = [Job(potential_worker, self.title, self.owner, i['job_title'], i['id']) for i in self.jobs] if self.jobs else []

    @property
    def job_length(self):
        return len(self.full_jobs)

    def __iter__(self):
        if not self.full_jobs:
            raise StopIteration('No jobs')
        for job in self.full_jobs:
            yield job
class Invites:
    def __init__(self, *args):
        self.__dict__ = dict(zip(['user', 'potential_user', 'projectdb'], args))
        self.final_projects = filter(lambda (pro_name, owner, description, team, teamneeded):owner == self.user, self.projectdb.get_projectname_owner_description_team_teamneeded('projects'))
        print "()"*10
        print "self.final_projects", self.final_projects
        print "()"*10
    @property
    def length(self):
        return len(self.final_projects)

    def __len__(self):
        return len(self.final_projects)

    def __bool__(self):
        return len(self.final_projects) > 0

    def __iter__(self):
        if not self.final_projects:
            raise StopIteration('no projects found')
        for i, project in enumerate(self.final_projects, start=1):
            yield SimpleProject(self.potential_user, i,  *project)
