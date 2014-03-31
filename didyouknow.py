from re import compile, match, findall
import sys
from chardet import detect
from borg import BorgInit
import oursql
from wikitools.wiki import Wiki
from wikitools.page import Page
import mwparserfromhell as Parser

class DYKReport(BorgInit):
    """
    Wikipedia bot that notifies editors that their atricles
    have been nominated to be on the Did You Know section of
    the Main Page.
    """
    create_query = u"""
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

        self.cursor = None
        self.conn = None

        self._site.login(user, passw)

        del user; del passw

    def _process_page(self, page="Template talk:Did you know", 
            host="tools-db", database=""):
        dyk = Page(self._site, title=page)
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

        error = "Couldn't connect to database. oursql threw error: {0}."
        login = BorgInit().database_retrieve()
        database = database if database else login[0] + "_cerabot"
        try:
            self.conn = oursql.connect(host=host, db=database, 
                user=login[0], passwd=login[1])
            self.cursor = self.conn.cursor(oursql.DictCursor)
        except Exception, e:
            e = error.format(e)
            print e
            return False
        self.cursor.execute(self.create_query)
        self.cursor.execute("SELECT COUNT(*) FROM did_you_know")
        if self.cursor.fetchone()["COUNT(*)"] >= 1:
            templates = self.templates
            self.cursor.execute("SELECT * FROM did_you_know")
            rows = self.cursor.rowcount
            while rows:
                data = self.cursor.fetchone()
                if data["name"] in templates:
                    templates.remove(data["name"])
                    rows -= 1
                else:
                    continue
            self._handle_sql_query(templates=templates)
            return True
        else:
            self._handle_sql_query(templates=self.templates)
            return True

    def _handle_sql_query(self, templates=None):
        q = []
        for template in templates:
            dyk, article = (Page(self._site, title=template), Page(
                self._site, title=template.split("/")[1]))
            categories = dyk.getCategories()
            s = " ".join(categories)
            result = findall("Category:Passed DYK nominations from", s)
            if result:
                continue
            try:
                print "B"
                a = article.getHistory(direction="newer", content=False, 
                    limit=1)[0]
                d = dyk.getHistory(direction="newer", content=False, 
                    limit=1)[0]
            except Exception:
                print "C"
                continue
            values = {
                "name":unicode(template),
                "creator":unicode(a["user"]),
                "nominator":unicode(d["user"]),
                "timestamp":unicode(a["timestamp"]),
                "to_be_handled":0
            }
            print "D"
            if a["user"].lower() != d["user"].lower():
                values["to_be_handled"] = 1
            print values
            self.cursor.execute(self.insert_query, (
                values["name"], 
                values["to_be_handled"], 
                values["creator"], 
                values["nominator"],
                values["timestamp"]
            ))
        self.conn.commit()

    def _handle_page(self, page):
        pass

if __name__ == "__main__":
    test = DYKReport()
    test._process_page()
