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

    def __init__(self):
        self._site = Wiki()

        user = "Cerabot"
        passw = BorgInit().pass_retrieve

        self._site.login(user, passw)

        del user; del passw

    def _parse_page(self, page="Template talk:Did you know", 
            host="tools-db", database=""):
        dyk = Page(self._site, title=page)
        text = dyk.getWikiText()

        error = "Well, damn, we {0}. Don't know if it's on our end, "
            "but I can't proceed. Exiting. Here's the error thrown: {1}"
        login = BorgInit.database_retrieve
        database = database if database else "_cerabot"
        try:
            conn = Database.connect(host=host, db=database, user=login[0],
                passwd=login[1], cursorclass=Cursors.DictCursor)
        excpet Exception, e:
            e = error.format("couldn't connect to the database", e)
        cursor = conn.cursor()
        table_name = "did_you_know"
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = '{0}'
            """.format(tablename))
        if not cursor.fetchone()[0] == 1:
            table_did_exist = False
            cursor.execute("""
            CREATE TABLE did_you_know(
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(255) NOT NULL,
                been_handled INT NOT NULL,
                timestamp DATETIME
            )
            """)
        else:
            table_did_exist = True
            cursor.execute("""
            SELECT * 
            FROM did_you_know
            WHERE been_handled = 0
            """)
            new_templates = cursor.fetchall()
        text = text.decode("utf-8")
        parsed = Parser.parse(text)
        templates = [a for a in parsed.filter_templates() if 
                        str(a).startswith("{{Did you know")]
        newtemplates = []
        for template in templates:
            name = str(template).replace("{{", "Template:").replace(
                "}}", "")
            dyk_page = Page(self._site, title=name)
            article_page = Page(self._site, title=name.split("/")[1])
            page_creator = article_page.getHistory(direction="newer",
                content=False, limit=1)[0]["user"]
            dyk_creator = dyk_page.getHistory(direction="newer",
                content=False, limit=1)[0]["user"]
            if page_creator.lower() != dyk_creator.lower():
                newtemplates.append((page, page_creator, dyk_creator))
            else:
                continue

        for template in newtemplates:
            creator_is_nominator = False
            if template[1].lower() != template[2].lower():
                creator_is_nominator = True
                matched = findall(r"\<small\>(.*?)\</small\>")
                matched = match.group(1)
                x = compile(r"\[\[User:(.*?)\|.*?\]\] \(\[\[.*?\|" +
                    r"talk\]\]\)")
                creators = x.match(matched.split("&nbsp;")[0])
                if len(creators.remove(template[1])) > 0:
                    dyk_nom_not_creator.append({
                        "pagename":name.split("/")[1],
                        "pagecreator":creators.append(template[1]),
                        "dykname":name,
                        "dykcreator":template[2],
                        })
                else:
                    dyk_nom_not_creator.append({
                        "pagename":name.split("/")[1],
                        "pagecreator":[template[1]],
                        "dykname":name,
                        "dykcreator":template[2],
                        })
            else:
                continue
        return dyk_nom_not_creator

if __name__ == "__main__":
    print "Troll."
    exit
