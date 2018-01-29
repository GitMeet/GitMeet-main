import pickle
import tigerSqlite
import re
from sklearn import svm
import functools
import contextlib
import abc
import random
import collections
repdb = tigerSqlite.Sqlite('user_rep.db')
'''
tablename: users
username text, name text, avatar text, email text, summary text, id int, extra text
'''
def check_users(list_of_users):
    @functools.wraps(list_of_users)
    def select_user(flag = False, avoid = ''):
        if flag:
            return list_of_users()

        return {a:b for a, b in list_of_users().items() if any(i[1] == a for i in tigerSqlite.Sqlite('projects.db').get_projectname_owner('projects')) and a != avoid}
    return select_user


@check_users
def user_listing():
    return {a:b for a, b in tigerSqlite.Sqlite('userprofiles.db').get_username_id('users')}

@contextlib.contextmanager
def so_tags():
    f = open('full_so_tags.txt')
    yield pickle.load(f)
    f.close()


class DevRecommendations:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def user_corpus(self):
        '''
        returns concatenated string of all text that the user is associated with the user
        '''
        return

    @abc.abstractmethod
    def user_tag_listing(self, corpus):
        '''
        returns list of counts of all tags found
        '''
        return

class Recommendation(DevRecommendations):
    def __init__(self, current_user, project):
        self.current_user = current_user
        self.project = project

    def project_corpus(self):
        full_user_project_data = [[c, d, e] for a, b, c, d, e in tigerSqlite.Sqlite('projects.db').get_projectname_owner_description_teamneeded_extra('projects') if a == self.project]
        final_user_project_data = ' '.join(' '.join([str(b), ' '.join(j['job_description'] for j in c)+' '.join(' '.join(g['job_tags']) for g in c) if c else '', '' if not d else re.sub(',\s*', ' ', d['project_tags'])]) for b, c, d in full_user_project_data)
        return final_user_project_data

    def user_corpus(self, user):
        full_user_data = [i for i in tigerSqlite.Sqlite('userprofiles.db').get_username_summary_extra('users') if i[0] == user]
        if not full_user_data:
            raise ValueError('user @{current_user} not found'.format(current_user=user))
        full_user_data = full_user_data[0]
        full_user_project_data = [[c, d, e] for a, b, c, d, e in tigerSqlite.Sqlite('projects.db').get_projectname_owner_description_team_extra('projects') if b == user or (any(h[0] == user for h in d) if d else False)]
        final_user_project_data = ' '.join(' '.join([str(b), ' '.join(j[1] for j in c) if c else '', '' if not d else re.sub(',\s*', ' ', d['project_tags'])]) for b, c, d in full_user_project_data)
        return full_user_data[1] + ' '.join(full_user_data[-1]['tags'] if full_user_data[-1] else [])+final_user_project_data

    def user_tag_listing(self, corpus):
        with so_tags() as tags:
            pass
        full_tag_listing = map(lambda x:str(x).lower(), filter(None, re.findall(open('output_results_from_tags.txt').read(), corpus, flags=re.IGNORECASE)))
        return [full_tag_listing.count(i.lower()) for i in tags]
    def __enter__(self):
        training_matrix = [self.user_tag_listing(self.user_corpus(i))+[i] for i, _ in user_listing(avoid = self.current_user).items()]
        new_array = self.user_tag_listing(self.project_corpus())
        clf = svm.SVC(gamma=0.001, C=100.)
        clf.fit([i[:-1] for i in training_matrix], [i[-1] for i in training_matrix])
        self.result = list(clf.predict([new_array]))[0]
        return self

    def __exit__(self, *args):
        t = tigerSqlite.Sqlite('recommendations.db')
        if not t.get_touser_messages('dev_recs') or not any(a == self.current_user for a, b in t.get_touser_messages('dev_recs')):
            t.insert('dev_recs', ('touser', self.current_user), ('messages', [{'suggested':self.result, 'for_project':self.project}]))
            return False
        new_data = t.get_touser_messages('dev_recs')
        final_data = [b for a, b in new_data if a == self.current_user][0]
        t.update('dev_recs', [('messages', final_data+[{'suggested':self.result, 'for_project':self.project}])], [('touser', self.current_user)])
        return False



for a, b in user_listing().items():
    with Recommendation(a, random.choice([i[0] for i in tigerSqlite.Sqlite('projects.db').get_projectname_owner('projects') if i[1] == a])) as r:
        pass
