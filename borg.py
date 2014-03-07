import sys

class BorgInit(object):
    @property
    def pass_retrieve(self):
        """
        Retrieves the password for Wikipedia bot."""

        io = open("passfile", 'r+')
        contents = io.read()
        passw = contents.strip()
        
        return passw
