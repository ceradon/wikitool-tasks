from re import compile, match, findall
import sys as Sysyem
from borg import BorgInit
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
            handle_old_pages=False):
        dyk = Page(self._site, title=page)
        text = dyk.getWikiText()

        text = text.decode("utf-8")
        parsed = Parser.parse(text)
        templates = [a for a in parsed.filter_templates() if 
                        str(a).startswith("{{Did you know")]

        dyk_nom_not_creator = []
        for template in templates:
            creator_is_nominator = False
            name = str(template).relplace("{{", "Template:").replace(
                "}}", "")
            page = Page(self._site, title=name)
            page_creator = page.getHistory(direction="newer",
                content=False, limit=1)[1]["user"]
            dyk_creator = page.getHistory(direction="newer",
                content=False, limit=1)[1]["user"]
            if page_creator.lower() != dyk_creator.lower():
                creator_is_nominator = True
                matched = findall(r"\<small\>(.*?)\</small\>")
                matched = match.group(1)
                x = compile(r"\[\[User:(.*?)\|.*?\]\] \(\[\[.*?\|" +
                    r"talk\]\]\)")
                creators = x.match(matched.split("&nbsp;")[0])
                if len(creators.remove(page_creator)) > 0:
                    dyk_nom_not_creator.append({
                        "pagename":name.split("/")[1],
                        "pagecreator":creators.append(page_creator),
                        "dykname":name,
                        "dykcreator":dyk_creator,
                        })
                else:
                    dyk_nom_not_creator.append({
                        "pagename":name.split("/")[1],
                        "pagecreator":[page_creator],
                        "dykname":name,
                        "dykcreator":dyk_creator,
                        })
            else:
                continue
        return dyk_nom_is_creator

if __name__ == "__main__":
    print "Troll."
    exit
