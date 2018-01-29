import tigerSqlite
import re
import collections
import gitmeet_user
#get_username_name_avatar_email_summary_id_extra('users')
class Recommendations:
    def __init__(self, user):
        self.user = user
        self.recog_db = tigerSqlite.Sqlite('recommendations.db')
        self.user_messages = [b for a, b in self.recog_db.get_touser_messages('dev_recs') if a == self.user]
        print "in constructor of dev_recogs.py", self.user_messages
    def __len__(self):
        return 0 if not self.user_messages else (0 if self.user_messages and not self.user_messages[0] else len(self.user_messages))

    @property
    def length(self):
        return len(self)

    def __iter__(self):
        if not self.user_messages:
            raise StopIteration('no messages')
        message = collections.namedtuple('message', ['recommending', 'projects', 'user'])
        for m in self.user_messages[0]:
            yield message(m['suggested'], m['for_project'], gitmeet_user.User([i for i in tigerSqlite.Sqlite('userprofiles.db').get_username_name_avatar_email_summary_id_extra('users') if i[0] == m['suggested']][0]))
