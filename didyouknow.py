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
    the Main Page."""

    def __init__(self):
        self._site = Wiki() # Initiate Wiki instance.
        super(DYKReport, self).__init__()
        
        user = "Cerabot"            # Retrieve vital login data
        passw = self._pass_retrieve  # for bot account.
        
        self._site.login(user, passw) # Now login.
        
        # "Created by" and "Nominated by" regular expressions
        """
        self._nominator_is_not_creator_regex = compile(
            r"Created by \[\[User:(.*?)\|.*?\]\] \(\[\[(.*?)\|" +
            r"talk\]\]\). Nominated by \[\[User:(.*?)\|.*?\]\]" +
            r" \(\[\[(.*?)\|talk\]\]\) at (.*?)\<")

        self._creator_is_nominator_regex = compile(
            r"(\<small\>)?Created by (\[\[User:(.*?)\|.*?\]\]) " +
            r"\(\[\[(.*?)\|talk\]\]\)\. Self-? ?nominated at " +
            r"(.*?)\</small>.")
        """

        del user; del passw # Delete the login data.

    def _parse_page(self, page="Template talk:Did you know"):
        dyk = Page(self._site, title=page) # Initiate Page instance
        text = dyk.getWikiText()           # and get text of page.

        # Parse the page's content for wikicode and gather all the
        # templates that begin with "{{Did you know"
        text = text.decode("utf-8")
        parsed = Parser.parse(text)
        templates = [a for a in parsed.filter_templates() if 
                        str(a).startswith("{{Did you know")]

        # Iterate over the template list and get all page names
        pages = {
             "nominator_is_creator": [],
             "nominator_is_not_creator": [],
             }
        for template in templates:
            name = str(template.name)
            page = Page(self._site, title=name)
            wikitext = page.getWikiText()
            x = findall(r"\<small\>(.*?)\</small\>")
            a = [b for b in x if "by [[" in b]

if __name__ == "__main__":
    print "Troll."
    exit
