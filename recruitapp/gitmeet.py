import flask
from flask_github import GitHub
import requests
import json
import tigerSqlite
from github import Github
import re
import collections
import itertools
import pickle
import random
import project as project_object
import gitmeet_user
import functools
import datetime
import rep_info
import common_errors as error
import os
import dev_requests
import confirms
import project_team
import bonus_updates
import joined_projects
import invites
import invitations as messaged_invitations
import inspect
import search_results
import dev_recogs
import top_projects as top_project
#BUG:for bonus awards may have to update rep in repdb, and then display two messages: one for the rep increase (success), and another for the project name (info)
app = flask.Flask(__name__)
github = GitHub(app)
userdb = tigerSqlite.Sqlite('userprofiles.db')
repdb = tigerSqlite.Sqlite('user_rep.db')
'''
tablename: users
username text, name text, avatar text, email text, summary text, id int, extra text
'''
projectdb = tigerSqlite.Sqlite('projects.db')
#projectdb.create('projects', ('projectname', 'text'), ('description', 'text'), ('owner', 'text'), ('id', 'int'), ('team', 'text'), ('teamneeded', 'text'), ('requests', 'text'))
'''
tablename: projects
('projectname', 'text'), ('description', 'text'), ('owner', 'text'), ('id', 'int'), ('team', 'text'), ('teamneeded', 'text'), ('requests', 'text'), ('extra', 'text')
'''
'''


data = [i for i in g.get_user().get_repos()]
[[(b.title, b.url) for b in i.get_issues()] for i in data if i.name == 'chess_game']
if no issues found, will return an empty list of lists
'''
'''
rep (username text, reputation int)'
'''
'''
requests.db
tablename: join_requests
(projectname text, owner text, requestlist text)')
'''
'''
confirmation_db.db
tablename: confirmations
(owner text, message text)
'''
'''
bonuses.db
tablename:bonus
(user text, latest text, awardfor text)
'''
'''
invites.db
tablename: invites
(for text, messages text)
'''

'''
recommendations.db
tablename: dev_recs
touser text, messages text
'''
requestdb = tigerSqlite.Sqlite('requests.db')
confirmationdb = tigerSqlite.Sqlite('confirmation_db.db')
bonusdb = tigerSqlite.Sqlite('bonuses.db')
invitationdb = tigerSqlite.Sqlite('invites.db')
class User:
    def __init__(self):
        self._user = None

    @property
    def username(self):
        return self._user

    @username.setter
    def username(self, name):
        self._user = name

    def update_full(self, data):
        self.__dict__.update(data)

    def __getattr__(self, name):
        return self.__dict__[name] if name in self.__dict__ else None

    def __setattr__(self, name, val):
        self.__dict__[name] = val
class Methods:
    def __init__(self):
        pass
    def __getattr__(self, val):
        return val.upper()

class Jobs:
    def __init__(self, listing):
        self.__tags = list(itertools.chain.from_iterable(pickle.load(open('full_so_tags.txt'))))
        job = collections.namedtuple('job', ['title', 'description', 'tags', 'bugs', 'id'])
        self.__colors = ['#c2e0c6', '#ee0701', '#cccccc', '#84b6eb', '#7057ff', '#ff625f', '#128A0C', '#e6e6e6', '#fef2c0', '#cc317c', '#d4c5f9', '#ffffff', '41B6D9', 'D941A9']
        self.colors = iter(self.__colors)
        self.full_jobs = map(job._make, [[(lambda x:[x[c:c+3] for c in range(0, len(x), 3)])(filter(lambda x:x and len(x) < 13, i[b])) if b == 'job_tags' else i[b] for b in ['job_title', 'job_description', 'job_tags', 'bugs', 'id']] for i in listing]) if listing is not None else []
        print "self.full_jobs here 12333", self.full_jobs
    @property
    def length(self):
        return len(self.full_jobs)

    def __bool__(self):
        return len(self.full_jobs > 0)

    def __len__(self):
        return len(self.full_jobs)

    def __iter__(self):
        #three columns
        new_jobs = [self.full_jobs[i:i+3] for i in range(0, len(self.full_jobs), 3)]
        for job_row in new_jobs:
            yield job_row

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, "jobs:{}, {}".format(len(self.full_jobs)), ', '.join(i.title for i in self.full_jobs))


user = User()
method = Methods()
class Alert:
    def __init__(self, *args):

        self.__dict__ = dict(zip(['message', 'type'], args if args else ['', '']))

    @property
    def contains_message(self):
        return 1 if all(bool(b) for a, b in self.__dict__.items()) else 0

def scope_authorized(f):
    def wrapper(projectname):
        if user.username:
            return f(projectname)
        return flask.render_template('unauthorized.html')
    return wrapper

def check_authorized_user(f):
    @functools.wraps(f)
    def wrapper(**name):
        if not user.username:
            return flask.render_template('unauthorized.html')
        project_data = projectdb.get_projectname_owner('projects')
        if not any(projectname == name.get('projectname', '') and owner == user.username for projectname, owner in project_data):
            return flask.render_template('unauthorized.html')
        return f(name)
    return wrapper

def get_repo_issues(the_user = user.git_token, repo_name = None):

    g = Github(user.git_token)
    if not repo_name:
        return [[(i.name, b.title, b.url) for b in i.get_issues()] for i in g.get_user().get_repos()]

    data = [[(b.title, b.url) for b in i.get_issues()] for i in g.get_user().get_repos() if i.name == repo_name]


    return data
def change_authorized(f):
    def wrapper(projectname):
        if user.username:
            return f(projectname)
        return flask.render_template('unauthorized.html')
    return wrapper

def check_if_authorized(the_route):
    def route_wrapper():
        if user.username:
            return the_route()
        return flask.redirect('/')
    return route_wrapper
def get_repo_info(the_user = user.git_token, repo_name=None):

    if not repo_name:
        g = Github(user.git_token)
        return [[repo.name, repo.description] for repo in g.get_user().get_repos()]

    else:
        repos = [i for i in Github(user.git_token).get_user().get_repos()]
        return [i.description for i in repos if i.name == repo_name]

def add_rep(f):
    @functools.wraps(f)
    def wrapper(visitor, username=user.username):
        print "visitor", visitor, "username", username
        if username != visitor:
            return 0, []
        if username is None:
            print
            return 0, []
        return f(username=username)
    return wrapper
#10800
@add_rep
def check_rep(username=user.username):
    global repdb
    data = repdb.get_username_reputation('fullrep')
    print "rep data here", data
    rep_addition = [b for a, b in data if a == username][0]
    full_data = [i for i in userdb.get_username_name_avatar_email_summary_id_extra('users') if i[0] == username][0]
    new_extra = full_data[-1]
    print "rep_addition", rep_addition
    print "new_extra", new_extra
    #new_extra['rep'] = rep_addition['times'][-1][-1]
    new_extra['rep'] += rep_addition['rep']
    current_time = datetime.datetime.now()
    userdb.update('users', [('extra', new_extra)], [('username', user.username)])
    newest_addition = rep_addition['times']+[[current_time.month, current_time.day, new_extra['rep']]]
    final_addition = [a+[sum(set(f for d, e, f in list(b)))] for a, b in itertools.groupby(sorted(newest_addition, key=lambda x:x[:2]), key=lambda x:x[:2])]
    print "final_addition", final_addition
    repdb.update('fullrep', [('reputation', {'rep':0, 'times':final_addition})], [('username', user.username)])

    return rep_addition['rep'], final_addition

def tip(f):
    @functools.wraps(f)
    def wrapper(visitor, username=user.username):
        if visitor is None or visitor != username:
            return ''
        return f(username=user.username)
    return wrapper

@tip
def get_tips(username=user.username):
    tips = ["Tip: encourage frequent contributions by awarding bonuses to your team members", "Tip: updating your profile to include tags of your skills increases your changes of being invited to work on projects", ''][random.choice(([0]*12)+([1]*12)+([2]*80))]
    print "tips", tips
    return tips


@app.route('/terms_and_conditions')
def terms():
    return "thanks for visiting"
def valid_search(search_route):
    def search_wrapper(query, page_num):
        s = search_results.SearchResults(query, userdb, projectdb)
        print "search results", s
        return "searching for @{query}".format(**inspect.getcallargs(search_route, query, page_num))
    return search_wrapper
class PageResults:
    def __init__(self, *args):
        self.__dict__ = dict(zip(['page_number', 'results'], args))
        self.previous = self.page_number - 1
        self.next = self.page_number + 1

        self.page_results = [self.results[i:i+5] for i in range(0, len(self.results), 5)]
        if self.page_results:
            self.current_page = self.page_results[self.page_number] if self.page_number < len(self.page_results) else self.page_results[-1]
            self.page_range = map(lambda x:x+1, range(len(self.page_results)))
    @property
    def number_of_results(self):
        return len(self.page_results)


@app.route('/search/<query>/<page_num>', methods=['GET', 'POST'])
def search(query, page_num):
    if flask.request.method == 'POST':
        keyword = flask.request.form['search_gitmeet']
        return flask.redirect('/search/{}/{}'.format(keyword, 1))
    s = search_results.SearchResults(re.sub('\s+', '', query).lower(), userdb, projectdb)
    full_results = [i for i in s]
    return flask.render_template('search_results.html', engine = s, query = query, page = PageResults(int(page_num)-1, full_results))

@app.route('/', methods=['GET', 'POST'])
def home():
    if flask.request.method == 'POST':
        keyword = flask.request.form['search_gitmeet']
        return flask.redirect('/search/{}/{}'.format(keyword, 1))

    return flask.render_template('new_home.html', user=user.username)

@app.route('/disable_join/<projectname>', methods=['GET', 'POST'])
@scope_authorized
def disable_join(projectname):
    data = projectdb.get_projectname_extra('projects')
    final_extras = [b for a, b in data if a == projectname][0]
    final_extras['disable_join'] = True
    global projectdb
    projectdb.update('projects', [('extra', final_extras)], [('projectname', projectname)])
    return flask.redirect('{}/{}'.format(user.username, projectname))

@app.route('/enable_join/<projectname>')
def enable_join(projectname):
    data = projectdb.get_projectname_extra('projects')
    final_extras = [b for a, b in data if a == projectname][0]
    final_extras['disable_join'] = False
    global projectdb
    projectdb.update('projects', [('extra', final_extras)], [('projectname', projectname)])
    return flask.redirect('{}/{}'.format(user.username, projectname))

@app.route('/delete/<projectname>', methods=['GET', 'POST'])
@check_authorized_user
def delete(projectname):
    global projectdb
    projectdb.delete("projects", ('projectname', projectname.get('projectname', '')))
    return flask.redirect('/{}'.format(user.username))


@app.route('/update_projects/<projectname>')
def update_project(projectname):
    return "working on it"

def check_authorized_user_job(route_handler):
    @functools.wraps(route_handler)
    def route_wrapper(**params):
        project_data = projectdb.get_projectname_owner_teamneeded('projects')
        print "project data in validator", project_data
        if not user.username:
            return flask.render_template('unauthorized.html')
        project_data = projectdb.get_projectname_owner_teamneeded('projects')
        if not [a for a, b, c in project_data if str(a) == str(params.get('projectname', ''))]:
            return flask.render_template('404.html')
        if user.username != [b for a, b, c in project_data if a == params.get('projectname', '')][0]:
            return flask.render_template('unauthorized.html')

        print "job deletion in validator", [c for a, b, c in project_data if a == params.get('projectname', '')]

        return route_handler(**params)

    return route_wrapper



@app.route('/delete_job/<projectname>/<job_id>')
@check_authorized_user_job
def delete_job(projectname, job_id):
    projects = [c for a, b, c in projectdb.get_projectname_owner_teamneeded('projects') if a == projectname]
    if not projects:
        raise error.ProjectError('Error with validation decorator on line 243')
    print "projects in delete_jobs", projects
    print "type of job_id", type(job_id)
    final_jobs = filter(lambda x:x[u'id'] != int(job_id), projects[0])
    global projectdb

    projectdb.update('projects', [('teamneeded', final_jobs)], [('projectname', projectname)])
    return flask.redirect('/{}/{}'.format(user.username, projectname))
def verify_join_project(route_handler):
    def handler_wrapper(**data):
        possible_projects = [a for a, b in projectdb.get_projectname_owner('projects') if b == user.username]
        if data.get('projectname', '') in possible_projects:
            return flask.render_template('unauthorized.html')
        if not user.username:
            return flask.render_template('unauthorized.html')
        return route_handler(**data)
    return handler_wrapper
def flash_response(project, warning = 'you have already sent a request for this job', confirmation = 'request sent!'):
    print "warning", warning
    if user.username:
        user_data = [i for i in userdb.get_username_name_avatar_email_summary_id_extra('users') if i[0] == user.username][0]
        current_user_rep = user_data[-1]['rep']
    else:
        current_user_rep = ''
    the_new_rep, datetimes_rep = check_rep(user.username, username=user.username)

    project_data = projectdb.get_projectname_description_owner_extra('projects')
    username = [c for a, b, c, d in project_data if a == project][0]
    extras = [d for a, b, c, d in project_data if a == project][0]
    project_ids = projectdb.get_projectname_id('projects')
    current_projects = projectdb.get_projectname_teamneeded('projects')

    team_needed = [b for a, b in current_projects if a == project][0]
    team_needed = team_needed[0] if team_needed is not None and isinstance(team_needed[0], list) else team_needed

    return flask.render_template('project.html', view_avatar = '' if user.avatar is None else user.avatar, visitor = user.username, projectname = project, description = [b for a, b, c, d in project_data if a == project][0], owner = [c for a, b, c, d in project_data if a == project][0], id = [b for a, b in project_ids if a == project][0], project_tags = '' if extras is None else re.split(',\s*', extras['project_tags']), gitter_link = '' if extras is None else extras['gitter_link'], gitlab_link='' if extras is None else extras['gitlab_link'], jobs=Jobs(team_needed), disable_join=extras.get('disable_join', False) if extras else False, bugs=get_repo_issues(repo_name=project)[0] if user.username == username else None, new_rep = rep_info.Rep(the_new_rep, datetimes_rep), tips=get_tips(user.username, username=username), current_user_rep=current_user_rep, tag_values = '' if extras is None else extras['project_tags'], warning = warning, confirmation = confirmation, job_requests = dev_requests.Requests(user.username, requestdb, userdb, projectdb), messages = confirms.Messages(user.username, confirmationdb), team = project_team.Team(project, projectdb), invitation_messages = messaged_invitations.Invitations(user.username, invitationdb), developer_recommendations = dev_recogs.Recommendations(user.username))

join_failed = functools.partial(flash_response, confirmation = '')
join_confirmation = functools.partial(flash_response, warning = '')
already_joined_project = functools.partial(flash_response, warning = 'you are already working on that project', confirmation = '')

@app.route('/report_issues', methods=['GET', 'POST'])
def report_issue():
    class Message:
        def __init__(self, *args):
            self.__dict__ = dict(zip(['email', 'subject', 'name', 'message', 'date_sent'], args))
            self.date_sent = '{}/{}/{} at {}:{}:{}'.format(*[self.date_sent.month, self.date_sent.day, self.date_sent.year, self.date_sent.hour, self.date_sent.minute, self.date_sent.second])
        @property
        def plain_message(self):
            return "message from @{name}: email:{email}, subject:{subject}, send at:{date_sent}) message:{message}".format(**self.__dict__)
        @property
        def message_html(self):
            message_data = """
                    <html>
                        <head>
                        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
                      <meta name="viewport" content="width=device-width, initial-scale=1">
                      <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta.2/css/bootstrap.min.css">
                      <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
                      <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.6/umd/popper.min.js"></script>
                      <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta.2/js/bootstrap.min.js"></script>
                      <script defer src="https://use.fontawesome.com/releases/v5.0.2/js/all.js"></script>
                      <script src="http://code.jquery.com/jquery-1.10.1.min.js"></script>
                        </head>
                        <body>


                            <ul class="list-group">
                                <li class="list-group-item active">user info</li>
                                <li class="list-group-item">{email}</li>
                                <li class="list-group-item">{name}</li>
                                <li class="list-group-item">send at: {date_sent}</li>
                            </ul>

                            <div class="card w-75">
                                <div class="card-body">
                                <h5 class="card-title">{subject}</h5>
                                <p class="card-text">{message}</p>
                                <a href="mailto:{email}" target="_top" class="btn btn-primary">Respond</a>
                            </div>
                            </div>
                        </body>
                    </html>
                    """
            return message_data.format(**self.__dict__)
        def __repr__(self):
            return "Message(from @{name}, email:{email}, subject:{subject}, send at:{date_sent}) message:{message})".format(**self.__dict__)
    if flask.request.method == 'POST':
        email = flask.request.form['email']
        name = flask.request.form['name']
        subject = flask.request.form['subject']
        message = flask.request.form['message']
        new_message = Message(*[email, subject, name, message, datetime.datetime.now()])
        pickle.dump(pickle.load(open('user_messages.txt'))+[[new_message.plain_message, new_message.message_html]], open('user_messages.txt', 'w'))
        return flask.render_template('report_issues.html', confirmation_message = 'Message has been successfully sent.')
    return flask.render_template('report_issues.html', confirmation_message = '')

@app.route('/join_project/<projectname>/<jobid>', methods=['GET', 'POST'])
@verify_join_project
def join_project(projectname, jobid):
    project_data = filter(lambda (name, owner, team, teamneeded):name == projectname, projectdb.get_projectname_owner_team_teamneeded('projects'))
    if not project_data:
        raise error.ProjectError('Error with project join decorator on line 293')
    project_data = project_data[0]
    if project_data[2]:
        if any(a == user.username and c == int(jobid) for a, b, c in project_data[2]):
            return already_joined_project(projectname)
    request_data = requestdb.get_projectname_owner_requestlist('join_requests')
    testing_request_data = [[a, b, c] for a, b, c in request_data if a == projectname]

    if testing_request_data:

        if any(i['name'] == user.username and i['for_job'] == int(jobid) for i in testing_request_data[0][-1]):
            print "got in here failure"
            return join_failed(projectname)

    if not request_data:
        global requestdb
        print "got in here, worked"
        requestdb.insert('join_requests', ('projectname', projectname), ('owner', project_data[1]), ('requestlist', [{'name':user.username, 'for_job':int(jobid)}]))
        return join_confirmation(projectname)
    new_request_data = filter(lambda (name, owner, listing):name == projectname, request_data)
    if not new_request_data:
        global requestdb
        print "got in here 1, worked"
        requestdb.insert('join_requests', ('projectname', projectname), ('owner', project_data[1]), ('requestlist', [{'name':user.username, 'for_job':int(jobid)}]))
        return join_confirmation(projectname)
    #here, will need to check if user has already send request
    global requestdb
    print "+++++final new_request_data", new_request_data[0][-1]+[{'name':user.username, 'for_job':int(jobid)}]

    requestdb.update('join_requests', [('requestlist', new_request_data[0][-1]+[{'name':user.username, 'for_job':int(jobid)}])], [('projectname', projectname)])
    return join_confirmation(projectname)

def verifiy_confirm_request(route_handler):
    @functools.wraps(route_handler)
    def route_wrapper(**args):
        if not user.username:
            return flask.render_template('unauthorized.html')
        project_data = projectdb.get_projectname_owner('projects')
        if not any(a == args.get('projectname') and b == user.username for a, b in project_data):
            return flask.render_template('unauthorized.html')
        return route_handler(**args)
    return route_wrapper




@app.route('/decline_request/<projectname>/<dev_name>/<job_id>')
@verifiy_confirm_request
def decline_request(projectname, dev_name, job_id):
    request_listings = filter(lambda x:x['for_job'] != int(job_id), filter(lambda (name, owner, requests):owner == user.username and name == projectname and any(r['for_job'] == int(job_id) for r in requests), requestdb.get_projectname_owner_requestlist('join_requests'))[0][-1])
    global requestdb
    requestdb.update('join_requests', [('requestlist', request_listings)], [('projectname', projectname)])
    return flask.redirect('/{}'.format(user.username))

@app.route('/confirm_request/<projectname>/<dev_name>/<job_id>', methods=['GET', 'POST'])
@verifiy_confirm_request
def confirm_request(projectname, dev_name, job_id):

    job_request_titles = [filter(lambda x:x['id'] == int(job_id), i[-1]) for i in filter(lambda (pro_name, owner, teamneeded):pro_name == projectname and owner == user.username, projectdb.get_projectname_owner_teamneeded('projects'))][0][0]

    request_listings = filter(lambda x:x['for_job'] != int(job_id), filter(lambda (name, owner, requests):owner == user.username and name == projectname and any(r['for_job'] == int(job_id) for r in requests), requestdb.get_projectname_owner_requestlist('join_requests'))[0][-1])

    project_lists = filter(lambda (pro_name, owner, team):owner==user.username and pro_name == projectname, projectdb.get_projectname_owner_team('projects'))
    if not project_lists:
        raise error.FilterError('Error with filter on line 427, empty list')
    project_data = project_lists[0]

    global projectdb

    projectdb.update('projects', [('team', [[dev_name, job_request_titles[u'job_title'], int(job_id)]] if not project_data[-1] else project_data[-1]+[[dev_name, job_request_titles[u'job_title'], int(job_id)]])], [('projectname', projectname)])
    global requestdb
    requestdb.update('join_requests', [('requestlist', request_listings)], [('projectname', projectname)])

    reputation_data = [b for a, b in repdb.get_username_reputation('fullrep') if a == dev_name][0]
    current_time = datetime.datetime.now()
    newest_addition = reputation_data['times']+[[current_time.month, current_time.day, 50]]
    final_addition = [a+[sum(set(f for d, e, f in list(b)))] for a, b in itertools.groupby(sorted(newest_addition, key=lambda x:x[:2]), key=lambda x:x[:2])]
    global repdb

    repdb.update('fullrep', [('reputation', {'rep':100, 'times':final_addition})], [('username', dev_name)])

    reputation_data = [b for a, b in repdb.get_username_reputation('fullrep') if a == user.username][0]
    current_time = datetime.datetime.now()
    newest_addition = reputation_data['times']+[[current_time.month, current_time.day, 50]]
    final_addition = [a+[sum(set(f for d, e, f in list(b)))] for a, b in itertools.groupby(sorted(newest_addition, key=lambda x:x[:2]), key=lambda x:x[:2])]

    repdb.update('fullrep', [('reputation', {'rep':20, 'times':final_addition})], [('username', user.username)])
    global confirmationdb

    confirmationdb.insert('confirmations', ('owner', dev_name), ('message', [user.username, projectname]))
    return flask.redirect('/{}/{}'.format(user.username, projectname))

def verify_clear_all(the_route):
    @functools.wraps(the_route)
    def route_wrapper():
        if not user.username:
            return flask.render_template('unauthorized.html')
        return the_route()
    return route_wrapper

@app.route('/clear_all')
@verify_clear_all
def clear_all():
    global confirmationdb
    confirmationdb.delete('confirmations', ('owner', user.username))
    global requestdb
    #(projectname text, owner text, requestlist text)')
    requestdb.update('join_requests', [('requestlist', [])], [('owner', user.username)])
    if invitationdb.get_for_messages('invites'):
        if any(a == user.username for a, b in invitationdb.get_for_messages('invites')):
            global invitationdb
            invitationdb.update('invites', [('messages', [])], [('for', user.username)])
    dev_recommendations = tigerSqlite.Sqlite('recommendations.db')
    if any(a == user.username for a, b in dev_recommendations.get_touser_messages('dev_recs')):
        dev_recommendations.update('dev_recs', [('messages', [])], [('touser', user.username)])
    return flask.redirect('/{}'.format(user.username))

@app.route('/features', methods=['GET', 'POST'])
def features():
    if flask.request.method == 'POST':
        return flask.redirect('/search/{}/1'.format(flask.request.form['search_gitmeet']))
    return flask.render_template('features.html')

@app.route('/requirements', methods=['GET', 'POST'])
def requirements():
    if flask.request.method == 'POST':
        return flask.redirect('/search/{}/1'.format(flask.request.form['search_gitmeet']))
    return flask.render_template('requirements.html')

def return_home(targetuser, alert, alert_type):
    print "in return_home, checking this", (alert, alert_type)
    home_visitor_data = [] if not user.username else [i for i in userdb.get_username_name_avatar_email_summary_id_extra('users') if i[0] == user.username][0]
    try:
        user_data = [i for i in userdb.get_username_name_avatar_email_summary_id_extra('users') if i[0] == targetuser][0]
    except IndexError:
        return flask.render_template('404.html')
    project_data = projectdb.get_projectname_description_owner_id_team_teamneeded_requests_extra('projects')

    print "userdata here testing idiosyncrasy", user_data

    #['projectname', 'description', 'owner', 'id', 'team', 'teamneeded', 'requests', 'extra']
    visitor_data = userdb.get_username_extra('users')
    print "visitor_data", visitor_data
    try:
        user_rep = [b.get('rep', 0) for a, b in visitor_data if a == user.username][0]
    except IndexError:
        user_rep = 0
        print "interestingly, got in here"
    print "user_rep in <user>", user_rep

    user_projects =[c for c in [project_object.Project(i) for i in project_data] if c.owner == targetuser]

    if user.username:
        flag = len([a for a, b in get_repo_info() if b is not None]) != len(get_repo_info())
        github_projects = ["{}/{}".format(user.username, a) for a, b in get_repo_info() if b is not None and not any(c == a for c, d in projectdb.get_projectname_owner('projects'))]
    else:
        flag = False
        github_projects = []

    rep1, datetimes_rep = check_rep(user.username, username=targetuser)

    rep_object = rep_info.Rep(rep1, datetimes_rep)
    dates = rep_object.dates
    increase = rep_object.rep_increase
    class GithubProjects:
        def __init__(self, raw_projects):
            self.raw_projects = raw_projects
        @property
        def length(self):
            return len(self.raw_projects)

        @staticmethod
        def user_github_repos():
            return get_repo_info()

        def __iter__(self):
            for project in self.raw_projects:
                yield project


    return flask.render_template('user_home.html', home_user = [] if not home_visitor_data else gitmeet_user.User(home_visitor_data), user=gitmeet_user.User(user_data), visitor=user.username, visitor_avatar = user.avatar, github_projects = GithubProjects(github_projects), flag = flag, projects=user_projects, num=len(user_projects), joined=joined_projects.Joined(targetuser, projectdb), new_rep = rep_info.Rep(rep1, datetimes_rep), dates = dates, total_rep = increase, visitor_reputation = user_rep+rep1, tips=get_tips(user.username, username=targetuser), job_requests = dev_requests.Requests(user.username, requestdb, userdb, projectdb), messages = confirms.Messages(user.username, confirmationdb), bonuses = bonus_updates.Bonuses(user.username, bonusdb), invitations = invites.Invites(user.username, targetuser, projectdb), general_alert=alert, general_alert_type=alert_type, invitation_messages = messaged_invitations.Invitations(user.username, invitationdb))


def verify_invite_user(route_handler):
    @functools.wraps(route_handler)
    def route_wrapper(**args):
        if not user.username:
            return flask.render_template('unauthorized.html')
        if not any(a == args.get('projectname') and b == args.get('owner') for a, b in projectdb.get_projectname_owner('projects')):
            return flask.redirect('unauthorized.html')
        if not any(any(i['id'] == int(args.get('job_id')) for i in c) for a, b, c in projectdb.get_projectname_owner_teamneeded('projects') if a == args.get('projectname') and b == args.get('owner')):
            return flask.render_template('unauthorized.html')
        if invitationdb.get_for_messages('invites'):
            if any({'from':user.username, 'projectname':args.get('projectname'), 'job_id':int(args.get('job_id'))} in b for a, b in invitationdb.get_for_messages('invites') if a == args.get('targetuser')):
                return return_home(args.get('targetuser'), 'You already invited {targetuser} to {projectname} in that capacity'.format(**args), 'danger')
        project_team = [c for a, b, c in projectdb.get_projectname_owner_team('projects') if a == args.get('projectname') and b == args.get('owner')][0]
        if project_team:
            if any(i[0] == args.get('targetuser') and i[-1] == int(args.get('job_id')) for i in project_team):
                return return_home(args.get('targetuser'), '{targetuser} is already working in that capacity'.format(**args), 'danger')
        return route_handler(**args)
    return route_wrapper


@app.route('/top_projects', methods=['GET', 'POST'])
def top_projects():
    if flask.request.method == 'POST':
        return flask.redirect('/search/{search_gitmeet}/1'.format(**flask.request.form))
    return flask.render_template('top_projects.html', toproject = top_project.TopProjects())

@app.route('/invite_user/<owner>/<projectname>/<targetuser>/<job_id>', methods=['GET', 'POST'])
@verify_invite_user
def invite_user(owner, projectname, targetuser, job_id):


    home_visitor_data = [] if not user.username else [i for i in userdb.get_username_name_avatar_email_summary_id_extra('users') if i[0] == user.username][0]
    try:
        user_data = [i for i in userdb.get_username_name_avatar_email_summary_id_extra('users') if i[0] == targetuser][0]
    except IndexError:
        return flask.render_template('404.html')
    project_data = projectdb.get_projectname_description_owner_id_team_teamneeded_requests_extra('projects')

    print "userdata here testing idiosyncrasy", user_data

    #['projectname', 'description', 'owner', 'id', 'team', 'teamneeded', 'requests', 'extra']
    visitor_data = userdb.get_username_extra('users')
    print "visitor_data", visitor_data
    try:
        user_rep = [b.get('rep', 0) for a, b in visitor_data if a == user.username][0]
    except IndexError:
        user_rep = 0
        print "interestingly, got in here"
    print "user_rep in <user>", user_rep

    user_projects =[c for c in [project_object.Project(i) for i in project_data] if c.owner == targetuser]

    if user.username:
        flag = len([a for a, b in get_repo_info() if b is not None]) != len(get_repo_info())
        github_projects = ["{}/{}".format(user.username, a) for a, b in get_repo_info() if b is not None and not any(c == a for c, d in projectdb.get_projectname_owner('projects'))]
    else:
        flag = False
        github_projects = []

    rep1, datetimes_rep = check_rep(user.username, username=targetuser)

    rep_object = rep_info.Rep(rep1, datetimes_rep)
    dates = rep_object.dates
    increase = rep_object.rep_increase
    class GithubProjects:
        def __init__(self, raw_projects):
            self.raw_projects = raw_projects
        @property
        def length(self):
            return len(self.raw_projects)

        @staticmethod
        def user_github_repos():
            return get_repo_info()

        def __iter__(self):
            for project in self.raw_projects:
                yield project

    #(for text, messages text)
    data = invitationdb.get_for_messages('invites')
    if data:

        if any({'from':user.username, 'projectname':projectname, 'job_id':int(job_id)} in b for a, b in data):

            return flask.render_template('user_home.html', home_user = [] if not home_visitor_data else gitmeet_user.User(home_visitor_data), user=gitmeet_user.User(user_data), visitor=user.username, visitor_avatar = user.avatar, github_projects = GithubProjects(github_projects), flag = flag, projects=user_projects, num=len(user_projects), joined=joined_projects.Joined(targetuser, projectdb), new_rep = rep_info.Rep(rep1, datetimes_rep), dates = dates, total_rep = increase, visitor_reputation = user_rep+rep1, tips=get_tips(user.username, username=targetuser), job_requests = dev_requests.Requests(user.username, requestdb, userdb, projectdb), messages = confirms.Messages(user.username, confirmationdb), bonuses = bonus_updates.Bonuses(user.username, bonusdb), invitations = invites.Invites(user.username, targetuser, projectdb), general_alert="You already invited {} to {} in that capacity".format(targetuser, projectname), general_alert_type= "warning", invitation_messages = messaged_invitations.Invitations(user.username, invitationdb))
    if not data:
        global invitationdb

        invitationdb.insert('invites', ('for', targetuser), ('messages', [{'from':user.username, 'projectname':projectname, 'job_id':int(job_id)}]))
        return flask.render_template('user_home.html', home_user = [] if not home_visitor_data else gitmeet_user.User(home_visitor_data), user=gitmeet_user.User(user_data), visitor=user.username, visitor_avatar = user.avatar, github_projects = GithubProjects(github_projects), flag = flag, projects=user_projects, num=len(user_projects), joined=joined_projects.Joined(targetuser, projectdb), new_rep = rep_info.Rep(rep1, datetimes_rep), dates = dates, total_rep = increase, visitor_reputation = user_rep+rep1, tips=get_tips(user.username, username=targetuser), job_requests = dev_requests.Requests(user.username, requestdb, userdb, projectdb), messages = confirms.Messages(user.username, confirmationdb), bonuses = bonus_updates.Bonuses(user.username, bonusdb), invitations = invites.Invites(user.username, targetuser, projectdb), general_alert="Invitation sent!", general_alert_type= "success", invitation_messages = messaged_invitations.Invitations(user.username, invitationdb))
    if not any(a == targetuser for a, b in invitationdb.get_for_messages('invites')):
        global invitationdb
        print "down here, about to return return_home"
        invitationdb.insert('invites', ('for', targetuser), ('messages', [{'from':user.username, 'projectname':projectname, 'job_id':int(job_id)}]))
        return flask.render_template('user_home.html', home_user = [] if not home_visitor_data else gitmeet_user.User(home_visitor_data), user=gitmeet_user.User(user_data), visitor=user.username, visitor_avatar = user.avatar, github_projects = GithubProjects(github_projects), flag = flag, projects=user_projects, num=len(user_projects), joined=joined_projects.Joined(targetuser, projectdb), new_rep = rep_info.Rep(rep1, datetimes_rep), dates = dates, total_rep = increase, visitor_reputation = user_rep+rep1, tips=get_tips(user.username, username=targetuser), job_requests = dev_requests.Requests(user.username, requestdb, userdb, projectdb), messages = confirms.Messages(user.username, confirmationdb), bonuses = bonus_updates.Bonuses(user.username, bonusdb), invitations = invites.Invites(user.username, targetuser, projectdb), general_alert="Invitation sent!", general_alert_type= "success", invitation_messages = messaged_invitations.Invitations(user.username, invitationdb))

    try:
        total_messages = [b for a, b in invitationdb.get_for_messages('invites') if a == targetuser][0]
    except:
        raise error.MessageSearchError('cannot find user {}'.format(targetuser))
    global invitationdb
    invitationdb.update('invites', [('messages', total_messages+[{'from':user.username, 'projectname':projectname, 'job_id':int(job_id)}])], [('for', targetuser)])

    return flask.render_template('user_home.html', home_user = [] if not home_visitor_data else gitmeet_user.User(home_visitor_data), user=gitmeet_user.User(user_data), visitor=user.username, visitor_avatar = user.avatar, github_projects = GithubProjects(github_projects), flag = flag, projects=user_projects, num=len(user_projects), joined=joined_projects.Joined(targetuser, projectdb), new_rep = rep_info.Rep(rep1, datetimes_rep), dates = dates, total_rep = increase, visitor_reputation = user_rep+rep1, tips=get_tips(user.username, username=targetuser), job_requests = dev_requests.Requests(user.username, requestdb, userdb, projectdb), messages = confirms.Messages(user.username, confirmationdb), bonuses = bonus_updates.Bonuses(user.username, bonusdb), invitations = invites.Invites(user.username, targetuser, projectdb), general_alert="Invitation sent!", general_alert_type= "success", invitation_messages = messaged_invitations.Invitations(user.username, invitationdb))
#http://127.0.0.1:5000/accept_invite/pytohtml/1
def verify_accept_invite(route_handler):
    @functools.wraps(route_handler)
    def route_wrapper(**args):
        if not user.username:
            return flask.render_template('unauthorized.html')
        if not any(a == args.get('projectname') and b == args.get('owner') for a, b in projectdb.get_projectname_owner('projects')):
            return flask.render_template('unauthorized.html')
        if not any(any(b['id'] == int(args.get('job_id')) for b in c) for a, b, c in projectdb.get_projectname_owner_teamneeded('projects')):
            return flask.render_template('unauthorized.html')
        return route_handler(**args)
    return route_wrapper

#/accept_invite/{projectname}/{from_user}/{job_id}
@app.route('/accept_invite/<projectname>/<owner>/<job_id>', methods=['GET', 'POST'])
@verify_accept_invite
def accept_invite(projectname, owner, job_id):
    #projectdb.update('projects', [('team', [[dev_name, job_request_titles[u'job_title'], int(job_id)]] if not project_data[-1] else project_data[-1]+[[dev_name, job_request_titles[u'job_title'], int(job_id)]])], [('projectname', projectname)])
    team_needed = [c for a, b, c in projectdb.get_projectname_owner_teamneeded('projects') if a == projectname and b == owner][0]
    job_title = [b['job_title'] for b in team_needed if b['id'] == int(job_id)][0]
    current_project_team = [c for a, b, c in projectdb.get_projectname_owner_team('projects') if a == projectname and b == owner][0]
    global projectdb
    projectdb.update('projects', [('team', [[user.username, job_title, int(job_id)]] if not current_project_team else current_project_team+[[user.username, job_title, int(job_id)]])], [('projectname', projectname)])
    global invitationdb
    #{'from':user.username, 'projectname':projectname, 'job_id':int(job_id)}
    invitationdb.update('invites', [('messages', [i for i in [b for a, b in invitationdb.get_for_messages('invites') if a == user.username][0] if i['job_id'] != int(job_id)])], [('for', user.username)])
    return flask.redirect('/{}/{}'.format(owner, projectname))

@app.route('/<username>/<project>', methods=['GET', 'POST'])
def project(username, project):

    the_new_rep, datetimes_rep = check_rep(user.username, username=username)
    if user.username:
        user_data = [i for i in userdb.get_username_name_avatar_email_summary_id_extra('users') if i[0] == username][0]
        current_user_rep = user_data[-1]['rep']
    else:
        current_user_rep = ''
    if flask.request.method == method.POST:
        if "search_gitmeet" in flask.request.form:
            return flask.redirect('/search/{}/1'.format(flask.request.form['search_gitmeet']))
        if not any(a.startswith('job') for a, _ in flask.request.form.items()):
            new_description = flask.request.form["new_description"]
            gitter_link = flask.request.form['gitter_link']
            gitlab_link = flask.request.form['gitlab_link']
            project_tags = flask.request.form['project_tags']
            current_data = projectdb.get_projectname_extra('projects')

            current_extras = [b for a, b in current_data if a == project][0]
            current_projects = projectdb.get_projectname_teamneeded('projects')
            team_needed = [b for a, b in current_projects if a == project][0]
            team_needed = team_needed[0] if team_needed is not None and isinstance(team_needed[0], list) else team_needed

            if current_extras is None:
                projectdb.update('projects', [('description', new_description), ('extra', dict(zip(['gitter_link', 'gitlab_link', 'project_tags'], [gitter_link, gitlab_link, project_tags])))], [('projectname', project)])
                return flask.render_template('project.html', view_avatar = '' if user.avatar is None else user.avatar, visitor = user.username, projectname = project, description = new_description, owner=user.username, project_tags=filter(None, re.split(',\s*', project_tags)), gitter_link=gitter_link, gitlab_link=gitlab_link, jobs=Jobs(team_needed), disable_join=False, bugs=get_repo_issues(repo_name=project)[0], new_rep=rep_info.Rep(the_new_rep, datetimes_rep), tips=get_tips(user.username, username=username), warning = '', confirmation = '', current_user_rep = current_user_rep, tag_values=project_tags, job_requests = dev_requests.Requests(user.username, requestdb, userdb, projectdb), messages = confirms.Messages(user.username, confirmationdb), team = project_team.Team(project, projectdb), invitation_messages = messaged_invitations.Invitations(user.username, invitationdb), developer_recommendations = dev_recogs.Recommendations(user.username))
            current_new_vals = dict(zip(['gitter_link', 'gitlab_link', 'project_tags', 'disable_join'], [gitter_link, gitlab_link, project_tags, False]))
            new_extras = {a:current_new_vals.get(a, b) for a, b in current_extras.items()}
            current_projects = projectdb.get_projectname_teamneeded('projects')
            team_needed = [b for a, b in current_projects if a == project][0]
            team_needed = team_needed[0] if team_needed is not None and isinstance(team_needed[0], list) else team_needed
            projectdb.update('projects', [('description', new_description), ('extra', new_extras)], [('projectname', project)])
            return flask.render_template('project.html', view_avatar = '' if user.avatar is None else user.avatar, visitor = user.username, projectname = project, description = new_description, owner=user.username, project_tags=filter(None, re.split(',\s*', new_extras['project_tags'])), gitter_link=new_extras['gitter_link'], gitlab_link=new_extras['gitlab_link'], jobs=Jobs(team_needed), disable_join=current_extras.get('disable_join', False), bugs = get_repo_issues(repo_name=project)[0], new_rep=rep_info.Rep(the_new_rep, datetimes_rep), warning = '', tips=get_tips(user.username, username=username), current_user_rep = current_user_rep, tag_values=new_extras['project_tags'], confirmation = '', job_requests = dev_requests.Requests(user.username, requestdb, userdb, projectdb), messages = confirms.Messages(user.username, confirmationdb), team = project_team.Team(project, projectdb), invitation_messages = messaged_invitations.Invitations(user.username, invitationdb), developer_recommendations = dev_recogs.Recommendations(user.username))
        #evaluate_jobs

        job_title = flask.request.form['job_title']
        job_description = flask.request.form['job_description']
        job_tags = flask.request.form['job_tags']
        bug1 = flask.request.form['bug_to_fix']

        project_data = projectdb.get_projectname_description_owner_extra('projects')
        extras = [d for a, b, c, d in project_data if a == project][0]
        project_ids = projectdb.get_projectname_id('projects')
        current_projects = projectdb.get_projectname_teamneeded('projects')
        team_needed = [b for a, b in current_projects if a == project][0]
        team_needed = team_needed[0] if team_needed is not None and isinstance(team_needed[0], list) else team_needed
        current_team = [{'job_title':job_title, 'job_description':job_description, 'job_tags':re.split(',\s*', job_tags), 'bugs':bug1, 'id':1}] if team_needed is None else team_needed + [{'job_title':job_title, 'job_description':job_description, 'job_tags':re.split(',\s*', job_tags), 'id':len(team_needed)+1, 'bugs':bug1}]
        global projectdb
        projectdb.update('projects', [('teamneeded', current_team)], [('projectname', project)])
        return flask.render_template('project.html', view_avatar = '' if user.avatar is None else user.avatar, visitor = user.username, projectname = project, description = [b for a, b, c, d in project_data if a == project][0], owner = [c for a, b, c, d in project_data if a == project][0], id = [b for a, b in project_ids if a == project][0], project_tags = '' if extras is None else re.split(',\s*', extras['project_tags']), gitter_link = '' if extras is None else extras['gitter_link'], gitlab_link ='' if extras is None else extras['gitlab_link'], warning = '', confirmation = '', jobs=Jobs(current_team), disable_join=extras.get('disable_join', False) if extras else False, bugs=get_repo_issues(repo_name=project)[0] if user.username == username else None, new_rep = rep_info.Rep(the_new_rep, datetimes_rep), tips=get_tips(user.username, username=username), current_user_rep = current_user_rep, tag_values = '' if extras is None else extras['project_tags'], job_requests = dev_requests.Requests(user.username, requestdb, userdb, projectdb), messages = confirms.Messages(user.username, confirmationdb), team = project_team.Team(project, projectdb), invitation_messages = messaged_invitations.Invitations(user.username, invitationdb), developer_recommendations = dev_recogs.Recommendations(user.username))

    project_data = projectdb.get_projectname_description_owner_extra('projects')
    try:
        extras = [d for a, b, c, d in project_data if a == project][0]
    except IndexError:
        return flask.render_template('404.html')
    project_ids = projectdb.get_projectname_id('projects')
    current_projects = projectdb.get_projectname_teamneeded('projects')

    team_needed = [b for a, b in current_projects if a == project][0]
    team_needed = team_needed[0] if team_needed is not None and isinstance(team_needed[0], list) else team_needed
    return flask.render_template('project.html', view_avatar = '' if user.avatar is None else user.avatar, visitor = user.username, projectname = project, description = [b for a, b, c, d in project_data if a == project][0], owner = [c for a, b, c, d in project_data if a == project][0], id = [b for a, b in project_ids if a == project][0], project_tags = '' if extras is None else re.split(',\s*', extras['project_tags']), gitter_link = '' if extras is None else extras['gitter_link'], gitlab_link='' if extras is None else extras['gitlab_link'], warning = '', jobs=Jobs(team_needed), disable_join=extras.get('disable_join', False) if extras else False, bugs=get_repo_issues(repo_name=project)[0] if user.username == username else None, new_rep = rep_info.Rep(the_new_rep, datetimes_rep), tips=get_tips(user.username, username=username), current_user_rep=current_user_rep, tag_values = '' if extras is None else extras['project_tags'], job_requests = dev_requests.Requests(user.username, requestdb, userdb, projectdb), messages = confirms.Messages(user.username, confirmationdb), team = project_team.Team(project, projectdb), invitation_messages = messaged_invitations.Invitations(user.username, invitationdb), developer_recommendations = dev_recogs.Recommendations(user.username))

@app.route('/create_project/<username>/<projectname>', methods=['GET', 'POST'])
def create_project(username, projectname):

    if username != user.username:
        return flask.redirect('/')

    project_ids = [i[0] for i in projectdb.get_id('projects')]
    print "project_ids", project_ids
    reputation_data = [b for a, b in repdb.get_username_reputation('fullrep') if a == user.username][0]
    current_time = datetime.datetime.now()
    full_data = [i for i in userdb.get_username_name_avatar_email_summary_id_extra('users') if i[0] == username][0]
    new_extra = full_data[-1]
    newest_addition = reputation_data['times']+[[current_time.month, current_time.day, 50]]
    final_addition = [a+[sum(set(f for d, e, f in list(b)))] for a, b in itertools.groupby(sorted(newest_addition, key=lambda x:x[:2]), key=lambda x:x[:2])]
    global repdb

    repdb.update('fullrep', [('reputation', {'rep':50, 'times':final_addition})], [('username', username)])

    global projectdb
    projectdb.insert('projects', ('projectname', projectname), ('description', [b for a, b in get_repo_info() if a == projectname][0]), ('owner', username), ('id', max(project_ids)+1))

    return flask.redirect('/{}/{}'.format(username, projectname))





@app.route('/<username>', methods=['GET', 'POST'])
def user_profile(username):
    #TODO: need signout button
    #TODO: add gitmeet home link
    if flask.request.method == 'POST':
        keyword = flask.request.form['search_gitmeet']
        return flask.redirect('/search/{}/{}'.format(keyword, 1))
    home_visitor_data = [] if not user.username else [i for i in userdb.get_username_name_avatar_email_summary_id_extra('users') if i[0] == user.username][0]
    try:
        user_data = [i for i in userdb.get_username_name_avatar_email_summary_id_extra('users') if i[0] == username][0]
    except IndexError:
        return flask.render_template('404.html')
    project_data = projectdb.get_projectname_description_owner_id_team_teamneeded_requests_extra('projects')

    print "userdata here testing idiosyncrasy", user_data

    #['projectname', 'description', 'owner', 'id', 'team', 'teamneeded', 'requests', 'extra']
    visitor_data = userdb.get_username_extra('users')
    print "visitor_data", visitor_data
    try:
        user_rep = [b.get('rep', 0) for a, b in visitor_data if a == user.username][0]
    except IndexError:
        user_rep = 0
        print "interestingly, got in here"
    print "user_rep in <user>", user_rep

    user_projects =[c for c in [project_object.Project(i) for i in project_data] if c.owner == username]

    if user.username:
        flag = len([a for a, b in get_repo_info() if b is not None]) != len(get_repo_info())
        github_projects = ["{}/{}".format(user.username, a) for a, b in get_repo_info() if b is not None and not any(c == a for c, d in projectdb.get_projectname_owner('projects'))]
    else:
        flag = False
        github_projects = []

    rep1, datetimes_rep = check_rep(user.username, username=username)

    rep_object = rep_info.Rep(rep1, datetimes_rep)
    dates = rep_object.dates
    increase = rep_object.rep_increase
    class GithubProjects:
        def __init__(self, raw_projects):
            self.raw_projects = raw_projects
        @property
        def length(self):
            return len(self.raw_projects)

        @staticmethod
        def user_github_repos():
            return get_repo_info()

        def __iter__(self):
            for project in self.raw_projects:
                yield project


    return flask.render_template('user_home.html', home_user = [] if not home_visitor_data else gitmeet_user.User(home_visitor_data), user=gitmeet_user.User(user_data), visitor=user.username, visitor_avatar = user.avatar, github_projects = GithubProjects(github_projects), flag = flag, projects=user_projects, num=len(user_projects), joined=joined_projects.Joined(username, projectdb), new_rep = rep_info.Rep(rep1, datetimes_rep), dates = dates, total_rep = increase, visitor_reputation = user_rep+rep1, tips=get_tips(user.username, username=username), job_requests = dev_requests.Requests(user.username, requestdb, userdb, projectdb), messages = confirms.Messages(user.username, confirmationdb), bonuses = bonus_updates.Bonuses(user.username, bonusdb), invitations = invites.Invites(user.username, username, projectdb), general_alert="", general_alert_type= "", invitation_messages = messaged_invitations.Invitations(user.username, invitationdb), developer_recommendations = dev_recogs.Recommendations(user.username))


@app.route('/about', methods=['GET', 'POST'])
def about():
    if flask.request.method == 'POST':
        return flask.redirect('/search/{}/1'.format(flask.request.form['search_gitmeet']))
    return flask.render_template('about.html')


def verify_remove_teammate(route_handler):
    @functools.wraps(route_handler)
    def route_wrapper(**args):
        if not user.username:
            return flask.render_template('unauthorized.html')
        project_data = filter(lambda (pro_name, owner):owner == user.username and pro_name == args.get('projectname'), projectdb.get_projectname_owner('projects'))
        if not project_data:
            return flask.render_template('unauthorized.html')
        return route_handler(**args)
    return route_wrapper


@app.route('/remove_teammate/<projectname>/<user_name>/<job_id>')
@verify_remove_teammate
def remove_teammate(projectname, user_name, job_id):
    project_listing = filter(lambda (pro_name, owner, team):pro_name == projectname and owner == user.username, projectdb.get_projectname_owner_team('projects'))

    if not project_listing:
        return flask.render_template('404.html')
    print "-&"*10
    print "original_listing", project_listing[-1][-1]

    final_list = [i for i in project_listing[-1][-1] if i[0] == user_name and int(i[-1]) == int(job_id)]
    print "first final_list", final_list
    final_list = [i for i in project_listing[-1][-1] if i not in final_list]
    print "second final_list", final_list
    print "-&"*10
    #final_list = filter(lambda (u_name, job_title, the_id):the_id != int(job_id) and u_name != user_name, project_listing[-1][-1])
    global projectdb
    projectdb.update('projects', [('team', final_list)], [('projectname', projectname)])
    return flask.redirect('/{}/{}'.format(user.username, projectname))
def verify_give_bonus(route_handler):
    @functools.wraps(route_handler)
    def route_wrapper(**args):
        if not user.username:
            return flask.render_template('unauthorized.html')
        project_listings = projectdb.get_projectname_owner_team('projects')
        if not any(a == args.get('projectname') for a, b, c in project_listings):
            return flask.render_template('404.html')
        the_project = [[a, b, c] for a, b, c in project_listings if a == args.get('projectname') and b == user.username]
        if not the_project:
            return flask.render_template('404.html')

        if not any(i[0] == args.get('user_name') for i in the_project[0][-1]):
            return flask.render_template('404.html')
        return route_handler(**args)
    return route_wrapper


@app.route('/award_bonus/<projectname>/<user_name>/<job_id>')
@verify_give_bonus
def award_bonus(projectname, user_name, job_id):
    project_data = filter(lambda (pro_name, owner, team):pro_name == projectname and owner == user.username, projectdb.get_projectname_owner_team('projects'))[0][-1]

    try:
        job_name = [b for a, b, c, in project_data if a == user_name and c == int(job_id)][0]
    except IndexError:
        return flask.render_template('404.html')
    bonus_data = bonusdb.get_user_latest_awardfor('bonus')
    if not bonus_data or not any(a == user_name for a, b, c in bonus_data):

        user_extra = filter(lambda (u_name, extra):u_name == user_name, userdb.get_username_extra('users'))[0][-1]
        user_extra['rep'] += 200
        global userdb
        userdb.update('users', [('extra', user_extra)], [('username', user_name)])
        current_time = datetime.datetime.now()
        data = repdb.get_username_reputation('fullrep')
        rep_addition = [b for a, b in data if a == user_name][0]

        newest_addition = rep_addition['times']+[[current_time.month, current_time.day, 200]]

        final_addition = [a+[sum(set(f for d, e, f in list(b)))] for a, b in itertools.groupby(sorted(newest_addition, key=lambda x:x[:2]), key=lambda x:x[:2])]

        global repdb
        repdb.update('fullrep', [('reputation', {'rep':rep_addition['rep'], 'times':final_addition})], [('username', user_name)])

        global bonusdb
        bonusdb.insert('bonus', ('user', user_name), ('latest', [[200, True]]), ('awardfor', [[projectname, job_name, int(job_id)]]))
        return flask.redirect('/{}/{}'.format(user.username, projectname))
    try:
        final_bonus_data = [i for i in bonus_data if i[0] == user_name][0]
    except IndexError:
        return flask.render_template('404.html')
    user_extra = filter(lambda (u_name, extra):u_name == user_name, userdb.get_username_extra('users'))[0][-1]
    print "user_extra here", user_extra
    user_extra['rep'] += 200

    global userdb
    userdb.update('users', [('extra', user_extra)], [('username', user_name)])
    current_time = datetime.datetime.now()
    data = repdb.get_username_reputation('fullrep')
    rep_addition = [b for a, b in data if a == user_name][0]

    newest_addition = rep_addition['times']+[[current_time.month, current_time.day, 200]]

    final_addition = [a+[sum(set(f for d, e, f in list(b)))] for a, b in itertools.groupby(sorted(newest_addition, key=lambda x:x[:2]), key=lambda x:x[:2])]

    global repdb
    repdb.update('fullrep', [('reputation', {'rep':rep_addition['rep'], 'times':final_addition})], [('username', user_name)])
    global bonusdb
    bonusdb.update('bonus', [('latest', final_bonus_data[1]+[[200, True]])], [('user', user_name)])
    bonusdb.update('bonus', [('awardfor', final_bonus_data[-1]+[[projectname, user_name, int(job_id)]])], [('user', user_name)])

    return flask.redirect('/{}/{}'.format(user.username, projectname))




@app.route('/signout')
def signout():
    global user
    user.__dict__ = {"_user":None}
    return flask.redirect('/')

@github.access_token_getter
def token_getter():
    global user
    current_user = user.git_token
    if current_user:

        return current_user

@app.route('/github-callback')
@github.authorized_handler
def authorized(oauth_token):
    global user
    user.git_token = oauth_token
    data = github.get('user')
    email = data['email']
    print "oauth_token", oauth_token

    scope = flask.request.args.get('scope')
    next_url = flask.request.args.get('next') or flask.url_for('login')

    if oauth_token is None:
        flask.flash("Authorization failed.")
        return flask.redirect("/")

    global user
    user.username = data['login']

    #print "truthy", any(user.username == i[0] for i in userdb.get_username('users'))


    if not any(user.username == i[0] for i in userdb.get_username('users')):
        global userdb
        global repdb
        current_datetime = datetime.datetime.now()
        repdb.insert('fullrep', ('username', user.username), ('reputation', {'rep':100, 'times':[[current_datetime.month, current_datetime.day, 100]]}))
        #'CREATE TABLE fullrep (username text, reputation text)')
        ids = [i[0] for i in userdb.get_id('users')]
        #username text, name text,avatar text, email text, summary text, id int
        # {u'rep': 1000, u'receive_invites': [u'I wish to receive developer invitations'], u'display_email': [u'Show email on profile'], u'tags': [u'Python', u'Java', u'Decorators']}
        userdb.insert('users', ('username', user.username), ('name', data['name'] if data['name'] is not None else ''), ('avatar', data['avatar_url']), ('email', data['email'] if data['email'] is not None else ''), ('summary', data['bio'] if data['bio'] is not None else ''), ('id', 1 if not ids else max(ids)+1), ('extra', {u'rep': 0, u'receive_invites': [u'I wish to receive developer invitations'], u'display_email': [u'Show email on profile'], u'tags': []}))
    new_user_data = userdb.get_username_name_avatar_email_summary_id('users')
    _final_data = dict(zip(['name', 'avatar_url', 'email', 'bio', 'id'], [i for i in new_user_data if i[0] == user.username][0][1:]))
    print "_final_data", _final_data
    global user
    user.name = _final_data['name']
    user.email = _final_data['email']
    user.avatar = _final_data['avatar_url']
    user.bio = _final_data['bio']
    user.id = _final_data['id']
    print list(tigerSqlite.Sqlite.select_all('users', 'userprofiles.db'))

    r = requests.get('http://freegeoip.net/json/')
    if r.ok:
        user.location = json.loads(r.text)
    else:
        user.location = None

    return flask.redirect('/{}'.format(user.username))



    """
    database scheme:
    project name, description, gitter link, github link, [team members], owner, join requests, tags

    """
    """
    user database sceme:
    username, avatar_url, email, summary,

    """

@app.route('/sitemap.xml')
def sitemap():
    return flask.send_from_directory(app.static_folder, flask.request.path[1:])

@app.errorhandler(404)
def page_not_found(e, methods=['GET', 'POST']):
    if flask.request.method == 'POST':
        query = flask.request.form['search_gitmeet']
        return flask.redirect('/search/{}/1'.format(query))
    return flask.render_template('404.html')

if __name__ == "__main__":
    app.debug = True

app.run()
