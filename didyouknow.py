from re import compile, match, findall
import sys as System
from borg import BorgInit
import MySQLdb as Database
import MySQLdb.cursors as Cursors
from wikitools.wiki import Wiki
from wikitools.page import Page
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
            timestamp DATETIME
        )
    """
    insert_query = """
        INSERT INTO did_you_know (
        name, to_be_handled, creator, nominator, timestamp)
        VALUES ('{0}', {1}, '{2}', '{3}', '{4}')
    """

    def __init__(self):
        self._site = Wiki()

        user = "Cerabot"
        passw = BorgInit().pass_retrieve()

        self.cursor = None
        self.conn = None

        self._site.login(user, passw)

        del user; del passw

    def _parse_page(self, page="Template talk:Did you know", 
            host="tools-db", database=""):
        dyk = Page(self._site, title=page)
        text = dyk.getWikiText()

        error = "Well, damn, we {0}. Don't know if it's on our end, " \
            "but I can't proceed. Here's the error thrown: {1}. Exiting."
        login = BorgInit().database_retrieve()
        database = database if database else login[0] + "_cerabot"
        try:
            self.conn = Database.connect(host=host, db=database, user=login[0],
                passwd=login[1], cursorclass=Cursors.DictCursor)
        except Exception, e:
            e = error.format("couldn't connect to the database", e)
            print e
            exit()
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.create_query)
        self.cursor.execute("SELECT COUNT(*) FROM did_you_know")
        if not self.cursor.fetchone() >= 0:
            return
        else:
            text = text.decode("utf-8")
            parsed = Parser.parse(text)
            templates = []
            for template in parsed.filter_templates():
                template = unicode(template)
                if template.startswith("{{Template:Did you know nominations") \
                    or template.startswith("{{Did you know nominations"):
                    templates.append(template)
            q = []
            for template in templates:
                name = unicode(template).replace("{{", "Template:").replace(
                    "}}", "")
                if name.startswith("Template:Template:"):
                    name = name.replace("Template:Template:", "Template:")
                dyk, article = (Page(self._site, title=name), Page(self._site, 
                    title=name.split("/")[1]))
                dyk_text = dyk.getWikiText()
                if dyk_text.startswith("{{#if:yes|"):
                    continue
                try:
                    a = article.getHistory(direction="newer", content=False, 
                        limit=1)[0]
                    d = dyk.getHistory(direction="newer", content=False, 
                        limit=1)[0]
                except Exception:
                    continue
                values = {
                    "name":name,
                    "creator":a["user"],
                    "nominator":d["user"],
                    "timestamp":a["timestamp"],
                    "to_be_handled":0
                }
                if a["user"].lower() != d["user"].lower():
                    values["to_be_handled"] = 1
                    q.append(values)
                else:
                    q.append(values)
            for item in q:
                form = self.insert_query.format(item["name"],
                    item["to_be_handled"], item["creator"], 
                    item["nominator"], item["timestamp"])
                self.cursor.execute(form)

if __name__ == "__main__":
    test = DYKReport()
    test._parse_page()
    exit()
