import base64
import hashlib
import os


class MWBot:
    def __init__(self):
        self.ips = [
          "0.0.0.0/0",
          "::/0",
        ]
        self.perms = [
            "basic",
            "highvolume",
            "editpage",
            "editprotected",
            "editmycssjs",
            "editmyoptions",
            "editinterface",
            "editsiteconfig",
            "createeditmovepage",
            "uploadfile",
            "uploadeditmovefile",
            "patrol",
            "rollback",
            "blockusers",
            "viewdeleted",
            "viewrestrictedlogs",
            "delete",
            "oversight",
            "protect",
            "viewmywatchlist",
            "editmywatchlist",
            "sendemail",
            "createaccount",
            "privateinfo",
        ]

    def get_ips(self):
        """Helper function for generating column 'bp_restrictions'."""
        return """{"IPAddresses":["%s"]}""" % '","'.join(self.ips)

    def get_perms(self):
        """Helper function for generating column 'bp_grants'."""
        return """["%s"]""" % '","'.join(self.perms)

    def gen_password(self, password=None, salt=None, hash_name='sha512',
                     iterations=30000, dklen=64):
        """Helper function for generating column 'bp_password'. See also
        https://www.mediawiki.org/wiki/Manual:Bot_passwords_table"""
        bpassword = bytes(password, 'ascii')
        if salt is None:
            salt = os.urandom(16)
        return ':pbkdf2:%s:%d:%d:%s:%s' % (
            hash_name, iterations, dklen,
            base64.b64encode(salt).decode('ascii'),
            base64.b64encode(hashlib.pbkdf2_hmac(
                hash_name, bpassword, salt, iterations, dklen
            )).decode('ascii'))
