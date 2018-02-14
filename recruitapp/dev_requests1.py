import gitmeet_user
import collections
import re
class SimpleProject:
    def __init__(self, *args):
        self.__dict__ = dict(zip(['projectname', 'owner', 'tags'], args))
    @property
    def is_tags(self):
        return 1 if self.tags else 0
    def __repr__(self):
        return "/{owner}/{projectname}".format(**self.__dict__)

    def __iter__(self):
        if not self.tags:
            raise StopIteration("No tags, need to check")
        for tag in self.tags:
            yield tag
class Experience:
    def __init__(self, experience):
        self.experience = experience
    @property
    def length(self):
        return len(self.experience)
    def __len__(self):
        return len(self.experience)

    def __bool__(self):
        return len(self.experience) > 0

    def __iter__(self):
        for [a, b], i in self.experience:
            print "final experience project data", [a, b, i]
            yield SimpleProject(a, b, i)

class JobRequest:
    def __init__(self, project, user_data, the_job, experience):
        job = collections.namedtuple('job', ['title', 'description', 'id', 'tags'])
        self.project = project
        self.user = gitmeet_user.User(user_data)
        print "checking 'the_job' here", the_job
        self.potential_job = job(*[the_job[i] for i in [u'job_title', u'job_description', u'id', u'job_tags']])
        self.user_experience = Experience(experience)
        #self.joined_projects = [[a, b] for a, b, h in self.project_db_instance.get_projectname_owner_team('projects') if any(c == self.current_user for c, d, e in h)]

    @property
    def div_id(self):
        return re.sub('\s+', '', "{}JobRequestId{}".format(self.user.username, self.potential_job.title))

    @property
    def decline_request(self):
        return "/decline_request/{}/{}/{}".format(self.project, self.user.username, self.potential_job.id)

    def __repr__(self):
        return "/confirm_request/{}/{}/{}".format(self.project, self.user.username, self.potential_job.id)

class Requests:
    def __init__(self, current_user, *instances):

        self.__dict__ = dict(zip(['request_db_instance', 'user_db_instance', 'project_db_instance'], instances))
        #(projectname text, owner text, requestlist text)')
        self.current_user = current_user


        if self.current_user:
            self.all_requests = filter(lambda (name, owner, requests):owner == current_user, self.request_db_instance.get_projectname_owner_requestlist('join_requests'))
            self.all_requests = map(lambda (name, owner, requests):[name, requests], self.all_requests)
        else:
            self.all_requests = []

        print "in __init__, self.all_requests", self.all_requests
    @property
    def length(self):
        return sum([len(b) for a, b in self.all_requests])

    def __bool__(self):
        return len(self.all_requests) > 0

    def __iter__(self):
        if not self.all_requests:
            raise StopIteration('need to check if list is empty instead')
        for target_project, requests in self.all_requests:
            for request in requests:
                user_data = [i for i in self.user_db_instance.get_username_name_avatar_email_summary_id_extra('users') if i[0] == request['name']][0]
                the_job = filter(lambda x:x['id'] == request['for_job'], [c for a, b, c in self.project_db_instance.get_projectname_owner_teamneeded('projects') if a == target_project][0])[0]
                self.experience = [[a, b] for a, b, c in self.project_db_instance.get_projectname_owner_team('projects') if c and any(i[0] == request['name'] for i in c)]
                self.tags = self.project_db_instance.get_projectname_team_extra('projects')
                self.final_tags = map(lambda x:None if not x or (len(x) ==1 and not x[0]) else x, [c if not c else re.split(',\s*', c.get('project_tags')) for a, b, c in self.tags if b and any(i[0] == request['name'] for i in b)])
                print "()"*10
                print "self.final_tags", self.final_tags
                print "()"*10
                yield JobRequest(target_project, user_data, the_job, zip(self.experience, self.final_tags))
