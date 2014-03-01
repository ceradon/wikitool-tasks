from borg import BorgInit
from wikitools.wiki import Wiki

class DYK_Report(BorgInit):
    """
    Wikipedia bot that notifies editors that their atricles
    have been nominated to be on the Did You Know section of
    the Main Page."""
    def __init__(self):
        self._site = Wiki() # Initiate Wiki instance.
        
        user = "Cerabot"            # Retrieve vital login data
        passw = self.pass_retrieve  # for bot account.
        
        self._site.login(user, passw) # Now login.
        
        del user; del passw # Delete the login data.

if __name__ == "__main__":
    print "Troll."
    exit
