import tigerSqlite
import os

def db_data(db_instances):
    def wrapper(cls):
        userdb, projecdb = db_instances(cls)
        return userdb.get_username('users'), projecdb.get_projectname_owner('projects')
    return wrapper


class SiteMap:
    def __init__(self, default_url = 'http://www.gitmeet.net/', **kwargs):
        self.default_url = default_url
        self.kwargs = kwargs
        self.template = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url>
          <loc>http://www.gitmeet.net/</loc>
          <priority>1.00</priority>
        </url>
        <url>
          <loc>http://www.gitmeet.net/features</loc>
          <lastmod>2018-02-05T14:41:51+00:00</lastmod>
          <priority>0.80</priority>
        </url>
        <url>
          <loc>http://www.gitmeet.net/about_new_version</loc>
          <lastmod>2018-02-05T14:41:51+00:00</lastmod>
          <priority>0.80</priority>
        </url>
        <url>
          <loc>http://www.gitmeet.net/top_projects</loc>
          <lastmod>2018-02-05T14:41:51+00:00</lastmod>
          <priority>0.80</priority>
        </url>
        <url>
          <loc>http://www.gitmeet.net/about</loc>
          <lastmod>2018-02-05T14:41:51+00:00</lastmod>
          <priority>0.80</priority>
        </url>
        <url>
          <loc>http://www.gitmeet.net/requirements</loc>
          <lastmod>2018-02-05T14:41:51+00:00</lastmod>
          <priority>0.80</priority>
        </url>
        <url>
          <loc>http://www.gitmeet.net/report_issues</loc>
          <lastmod>2018-02-05T14:41:51+00:00</lastmod>
          <priority>0.80</priority>
        </url>
        <url>
          <loc>http://www.gitmeet.net/settings</loc>
          <lastmod>2018-02-05T14:41:51+00:00</lastmod>
          <priority>0.64</priority>
        </url>
        <url>
          <loc>http://www.gitmeet.net/terms_and_conditions</loc>
          <lastmod>2018-02-05T14:41:51+00:00</lastmod>
          <priority>0.64</priority>
        </url>
        <url>
          <loc>http://www.gitmeet.net/terms_of_service</loc>
          <lastmod>2018-02-05T14:41:51+00:00</lastmod>
          <priority>0.64</priority>
        </url>
        {}
</urlset>
        """

    @db_data
    def get_pairings(self):
        return tigerSqlite.Sqlite('userprofiles.db'), tigerSqlite.Sqlite('projects.db')

    def __enter__(self):
        self.users, self.projects = self.get_pairings()
        self.extras = '\n'.join('\t<{}>{}</{}>'.format(a, b, a) for a, b in self.kwargs.items())
        self.template = self.template.format('\n'.join('<url>\n{}\n</url>'.format('\t<loc>{}{}</loc>\n\t<priority>{}</priority>\n\t{}'.format(self.default_url, user, 0.8, self.extras)) for [user] in self.users)+'\n'.join('<url>\n{}\n</url>'.format('\t<loc>{}{}/{}</loc>\n\t<priority>{}</priority>\n\t{}'.format(self.default_url, user, projectname, 0.6, self.extras)) for projectname, user in self.projects))

    def __exit__(self, *args):
        f = open('sitemap.xml', 'w' if 'sitemap.xml' in os.listdir(os.getcwd()) else 'a')
        f.write(self.template)
        f.close()


with SiteMap(changefreq='weekly') as sitemap:
    pass
