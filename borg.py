import sys

class BorgInit(object)
    def __init__(self):
        pass

    @property
    def _pass_retrieve(self):
        """
        Retrieves the password for Wikipedia bot."""

        io = open("passfile", 'r+')
        contents = io.read()
        passw = contents.strip()
        
        return passw
