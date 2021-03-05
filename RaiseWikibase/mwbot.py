import base64
import hashlib
import os


class MWBot:
    ips = [
        "0.0.0.0/0",
        "::/0",
    ]
    perms = [
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

    def get_ips(ips=ips):
        """Helper function for generating column 'bp_restrictions'."""
        return """{"IPAddresses":["%s"]}""" % '","'.join(ips)

    def get_perms(perms=perms):
        """Helper function for generating column 'bp_grants'."""
        return """["%s"]""" % '","'.join(perms)

    def gen_password(password, salt=None, hash_name='sha512',
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
