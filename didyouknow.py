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
        newtemplates = []
        for template in templates:
            name = str(template).replace("{{", "Template:").replace(
                "}}", "")
            page = Page(self._site, title=name)
            wikitext = page.getWikiText()
            page_creator = page.getHistory(direction="newer",
                content=False, limit=1)[0]["user"]
            dyk_creator = page.getHistory(direction="newer",
                content=False, limit=1)[0]["user"]
            if page_creator.lower() != dyk_creator.lower():
                newtemplates.append((page, page_creator, dyk_creator))
            else:
                continue

        dyk_nom_not_creator = []
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
