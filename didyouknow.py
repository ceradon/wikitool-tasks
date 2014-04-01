from re import compile, match, findall
import sys
from chardet import detect
from borg import BorgInit
import oursql
from wikitools.wiki import Wiki
from wikitools.page import Page
from wikitools.user import User
import mwparserfromhell as Parser

class DYKReport(BorgInit):
    """
    Wikipedia bot that notifies editors that their atricles
    have been nominated to be on the Did You Know section of
    the Main Page.
    """
    create_query = """
        CREATE TABLE IF NOT EXISTS did_you_know (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL,
            creator VARCHAR(255) NOT NULL,
            nominator VARCHAR(255) NOT NULL,
            to_be_handled INT NOT NULL,
            timestamp VARCHAR(255)
        )
    """
    insert_query = u"""
        INSERT INTO did_you_know (
        name, to_be_handled, creator, nominator, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """
    templates = []

    def __init__(self):
        self._site = Wiki()

        user = "Cerabot"
        passw = BorgInit().pass_retrieve()

        self._site.login(user, passw)

        del user; del passw

    def _process_page(self, cursor):
        dyk = Page(self._site, title="Template talk:Did you know")
        text = dyk.getWikiText()
        text = text.decode("utf-8")
        parsed = Parser.parse(text)
        for name in parsed.filter_templates():
            name = unicode(name)
            if name.startswith("{{Template:Did you know nominations") \
                or name.startswith("{{Did you know nominations"):
                name = unicode(name).replace("{{", "Template:").replace(
                    "}}", "")
                name = name.replace("Template:Template:", "Template:")
                self.templates.append(name)
            else:
                continue

        cursor.execute(self.create_query)
        cursor.execute("SELECT COUNT(*) FROM did_you_know")
        if cursor.fetchone()["COUNT(*)"] >= 1:
            print "A"
            templates = self.templates
            cursor.execute("SELECT * FROM did_you_know")
            data = cursor.fetchall()
            for item in data:
                if item["name"] in templates:
                    templates.remove(item["name"])
                else:
                    continue
            self._handle_sql_query(cursor, templates=templates)
            return True
        else:
            print "B"
            self._handle_sql_query(cursor, templates=self.templates)
            return True

    def _handle_sql_query(self, cursor, templates=None):
        q = []
        for template in templates:
            print "C"
            dyk, article = (Page(self._site, title=template), Page(
                self._site, title=template.split("/")[1]))
            print dyk, article
            categories = dyk.getCategories()
            s = " ".join(categories)
            result = findall("Category:Passed DYK nominations from", s)
            if result:
                continue
            try:
                a = article.getHistory(direction="newer", content=False, 
                    limit=1)[0]
                d = dyk.getHistory(direction="newer", content=False, 
                    limit=1)[0]
            except Exception, e:
                print e
                continue
            values = {
                "name":unicode(template),
                "creator":unicode(a["user"]),
                "nominator":unicode(d["user"]),
                "timestamp":unicode(a["timestamp"]),
                "to_be_handled":0
            }
            if a["user"].lower() != d["user"].lower():
                values["to_be_handled"] = 1
            cursor.execute(self.insert_query, (
                values["name"], 
                values["to_be_handled"], 
                values["creator"], 
                values["nominator"],
                values["timestamp"]
            ))

    def _handle_pages(self, cursor):
        cursor.execute("""SELECT name, creator FROM did_you_know 
                          WHERE to_be_handled = 1;
                       """)
        data = cursor.fetchall()
        for item in data:
            title = item["name"]
            creator = item["creator"]
#           user = User(self._site, creator, check=True)
            user = User(self._site, "Ceradon", check=True)
            if not user.exists:
                continue
            if user.isBlocked():
                continue
            if user.isIP:
                continue
            user_talk = user.getTalkPage(check=True)
            text = user_talk.getWikiText()
            message = "\n==Message from Cerabot==\n" \
                    "{{SUBST:User:Cerabot/Umbox|article=%s|" \
                    "include_links=yes}}" % unicode(title.split("/")[1])
            newtext = text + message 
            summary = "Notifying [[User:{0}|{0}]] of [[{1}|Did you " \
                "know nomination]] ([[User:Cerabot/Run/Task 2|" \
                "bot task]])".format(user.name, user_talk.title)
            check_page = Page(self._site, "User:Cerabot/Run/Task 2")
            check_text = check_page.getWikiText()
            if not check_text.strip().lower() == "yes":
                return
            user_talk.edit(text=newtext, summary=summary, bot=True,
                minor=True)
            print "I'm done"; exit() # Only do one page for now
        return

    def _database_cleanup(self, cursor):
        pass

    def deploy_task(self, database="", host="tools-db"):
        error = "Couldn't connect to database. oursql threw error: {0}."
        login = BorgInit().database_retrieve()
        database = database if database else login[0] + "_cerabot"
        try:
            conn = oursql.connect(host=host, db=database, 
                user=login[0], passwd=login[1])
            cursor = conn.cursor(oursql.DictCursor)
        except Exception, e:
            e = error.format(e)
            print e
            return False
#       self._process_page(cursor)
        self._handle_pages(cursor)
        self._database_cleanup(cursor)

if __name__ == "__main__":
    task = DYKReport()
    task.deploy_task()
