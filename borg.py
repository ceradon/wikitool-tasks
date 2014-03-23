from os.path import expanduser
import sys
import ConfigParser as Config

class BorgInit(object):
    @property
    def pass_retrieve(self):
        """
        Retrieves the password for Wikipedia bot.
        """
        io = open(expanduser("~", "passfile"), 'r+')
        contents = io.read()
        passw = contents.strip()
        io.close()
        
        return passw

    @property
    def database_retrieve(self):
        """
        Retrieves the login details for Cerabot's Wikimedia
        Tool Labs database account."""
        config = Config.ConfigParser()
        config.read(expanduser("~") + "/replica.my.cnf")
        contents = config.items("client")
        username = contents[0][1].strip("'")
        password = contents[1][1].strip("'")

        return username, password
