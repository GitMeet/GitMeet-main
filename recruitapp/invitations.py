import collections
import re
class Invite:
    def __init__(self, data):
        print "data in invite", data
        self.from_user = data['from']
        self.projectname = data['projectname']
        self.job_id = data['job_id']
    def __repr__(self):
        return "/accept_invite/{projectname}/{from_user}/{job_id}".format(**self.__dict__)

class Invitations:
    def __init__(self, *args):
        self.__dict__ = dict(zip(['user', 'invitedb'], args))
        try:
            self.user_invites = [] if not self.invitedb.get_for_messages('invites') else [b for a, b in self.invitedb.get_for_messages('invites') if a == self.user][0]
        except IndexError:
            self.user_invites = []
        print "self.user_invites here", self.user_invites
    @property
    def length(self):
        return len(self.user_invites)

    def __iter__(self):
        if not self.user_invites:
            raise StopIteration('no invites')
        for invite in self.user_invites:
            yield Invite(invite)
