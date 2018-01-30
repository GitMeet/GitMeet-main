import click
import tigerSqlite
import random
import functools
import os
import pickle
'''
top_projects.db
CREATE TABLE best (projectname text, owner text)
'''
class ProjectDoesNotExist(ValueError):
    def __init__(self, message):
        ValueError.__init__(self, message)

def verify_project_exists(f):
    @functools.wraps(f)
    def wrapper(**kwargs):
        if not any(a == kwargs.get('projectname') and b == kwargs.get('username') for a, b in tigerSqlite.Sqlite('projects.db').get_projectname_owner('projects')):
            raise ProjectDoesNotExist('project "{projectname}" with creator of @{username} does not exist'.format(**kwargs))
        return f(**kwargs)
    return wrapper

@click.command()
@click.option('--projectname', default=random.choice([a for a, b in tigerSqlite.Sqlite('projects.db').get_projectname_owner('projects')]))
@click.option('--username', default=random.choice([b for a, b in tigerSqlite.Sqlite('projects.db').get_projectname_owner('projects')]))
@verify_project_exists
def set_top_user(**args):
    t = tigerSqlite.Sqlite('top_projects.db')
    t.insert('best', ('projectname', args.get('projectname')), ('owner', args.get('username')))
    click.echo('project added')

if __name__ == '__main__':
    set_top_user()
