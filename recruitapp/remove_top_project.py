import click
import tigerSqlite

@click.command()
@click.option('--projectname')
@click.option('--username')
def remove_top_project(projectname, username):
    if not any(a == projectname and b == username for a, b in tigerSqlite.Sqlite('top_projects.db').get_projectname_owner('best')):
        raise ValueError('project "{}" with creator @{} not found'.format(projectname, username))
    tigerSqlite.Sqlite('top_projects.db').delete('best', ('projectname', projectname))
    click.echo('project removed')

if __name__ == '__main__':
    remove_top_project()
