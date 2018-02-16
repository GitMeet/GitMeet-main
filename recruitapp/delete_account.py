import tigerSqlite
import contextlib

@contextlib.contextmanager
def remove_user(username):
    '''this file is dangerous!! use carefully!!'''
    t = tigerSqlite.Sqlite('/home/jamespetullo/gitmeet/userprofiles.db')
    t.delete('users', ('username', username))
    t1 = tigerSqlite.Sqlite('/home/jamespetullo/gitmeet/projects.db')
    t1.delete('projects', ('owner', username.decode('utf-8')))

    t3 = tigerSqlite.Sqlite('/home/jamespetullo/gitmeet/projects.db')
    t4 = tigerSqlite.Sqlite('/home/jamespetullo/gitmeet/projects.db')
    for a, b in t3.get_projectname_team('projects'):
        if b:
            if any(i[0] == username for i in b):
                print('filtered team', [('team', [i for i in b if i[0] != username])])
                t4.update('projects', [('team', [i for i in b if i[0] != username])], [('projectname', a)])
    confirms = tigerSqlite.Sqlite('/home/jamespetullo/gitmeet/confirmation_db.db')
    confirms.delete('confirmations', ('owner', username))
    recommendations = tigerSqlite.Sqlite('/home/jamespetullo/gitmeet/recommendations.db')
    for a, b in tigerSqlite.Sqlite('/home/jamespetullo/gitmeet/recommendations.db').get_touser_messages('dev_recs'):
        recommendations.update('dev_recs', [('messages', [i for i in b if i['suggested'] != username])], [('touser', a)])

    yield




