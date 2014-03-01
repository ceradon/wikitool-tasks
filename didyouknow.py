from wikitools.wiki import Wiki

class DYK_Report(object):
    """
    Wikipedia bot that notifies editors that their atricles
    have been nominated to be on the Did You Know section of
    the Main Page."""
    def __init__(self):
        self._site = Wiki() # Initiate Wiki instance.

if __name__ == "__main__":
    print "Troll."
    exit
