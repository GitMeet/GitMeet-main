import collections
class Alert:
    def __init__(self, *args):
        self.__dict__ = dict(zip(['to', 'owner', 'projectname'], args))
    def __repr__(self):
        return "/{}/{}".format(self.owner, self.projectname)

class Messages:
    """simple wrapper for misc. user notifications"""
    def __init__(self, *args):
        self.__dict__ = dict(zip(['user', 'db_instance'], args))
        self.messages = filter(lambda (owner, message):owner == self.user, self.db_instance.get_owner_message('confirmations'))
    @property
    def length(self):
        return len(self.messages)

    def __bool__(self):
        return len(self.messages) > 0
    def __len__(self):
        return len(self.messages)

    def __iter__(self):
        if not self.messages:
            raise StopIteration('no messages')

        for target, [owner, projectname] in self.messages:
            yield Alert(target, owner, projectname)
