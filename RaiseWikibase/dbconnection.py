import hashlib
import os
import random
import string
import MySQLdb
from RaiseWikibase.docker import docker_names, docker_env, docker_ports
from RaiseWikibase.mwbot import MWBot
import re
import datetime


class DBConnection:
    def __init__(self):
        [self.docker_mysql, self.docker_wikibase] = docker_names()
        self.mysql_env = docker_env(self.docker_mysql)
        self.mysql_ports = docker_ports(self.docker_mysql)
        self.wikibase_env = docker_env(self.docker_wikibase)

        self.conn = self.mysql_connect()
        self.user_id = self.get_admin_user_id()

        self.create_content_models()
        self.model_ids = self.get_content_models()

    def mysql_connect(self):
        """Helper function connecting to SQL database."""
        conn = MySQLdb.connect(
            database=self.mysql_env["MYSQL_DATABASE"],
            user=self.mysql_env["MYSQL_USER"],
            password=self.mysql_env["MYSQL_PASSWORD"],
            host=self.mysql_ports["3306/tcp"][0]["HostIp"],
            port=int(self.mysql_ports["3306/tcp"][0]["HostPort"])
        )
        conn.autocommit = False
        conn.charset = 'utf-8'
        return conn

    def get_admin_user_id(self):
        """Helper function for retrieving primary admin user id."""
        cur = self.conn.cursor()
        cur.execute("SELECT user_id FROM user WHERE user_name = '%s'" \
                    % self.wikibase_env["MW_ADMIN_NAME"])
        out = cur.fetchone()[0]
        cur.close()
        return out

    def bot_create(self, name, password=None, salt=None, token=None):
        """Creates a bot with a random or given password. Returns the
        password."""
        fullname = '%s@%s' % (self.wikibase_env["MW_ADMIN_NAME"], name)
        cur = self.conn.cursor()
        if self.bot_exists(name):
            return (fullname, None)
        if password is None:
            # 'random' password is actually a string in base32 encoding of
            # length 32
            password = ''.join([
                random.choice(string.ascii_lowercase[:22] + string.digits)
                for i in range(32)
            ])
        if token is None:
            token = hashlib.md5(os.urandom(16)).hexdigest()
        query = """INSERT INTO bot_passwords VALUES ({bp_user}, '{bp_app_id}',
        '{bp_password}', '{bp_token}', '{bp_restrictions}',
        '{bp_grants}')""".format(
            bp_user=self.user_id,
            bp_app_id=name,
            bp_password=MWBot.gen_password(password, salt),
            bp_token=token,
            bp_restrictions=MWBot.get_ips(),
            bp_grants=MWBot.get_perms(),
        )
        cur.execute(query)
        self.conn.commit()
        cur.close()
        return (fullname, password)

    def bot_delete(self, name=None):
        """Deletes bot matching name (or all if no name was given)."""
        cur = self.conn.cursor()
        query = "DELETE FROM bot_passwords"
        if not name is None:
            query += " WHERE bp_app_id = '%s'" % name
        cur.execute(query)
        self.conn.commit()
        cur.close()

    def bot_exists(self, name):
        """Returns True if bot with given name exists, False otherwise."""
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM bot_passwords WHERE bp_user = %d AND" \
                    " bp_app_id = '%s'" % (self.user_id, name))
        out = True if len(cur.fetchall()) != 0 else False
        cur.close()
        return out

    def bot_list(self):
        """Returns a list of all bots."""
        ret = []
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM bot_passwords")
        for row in cur.fetchall():
            ret.append(row)
        cur.close()
        return ret

    def bot_schema(self):
        """Returns a tuple containing the names of the bot table columns."""
        cur = self.conn.cursor()
        cur.execute("DESCRIBE bot_passwords")
        out = tuple(i[0] for i in cur.fetchall())
        cur.close()
        return out

    def create_content_models(self):
        """Creates a few content models"""
        cur = self.conn.cursor()
        q = "INSERT IGNORE INTO content_models (model_name ) VALUES('wikibase-item'),('wikibase-property'),('wikibase-lexeme'),('Scribunto'),('sanitized-css')"
        cur.execute(q)
        self.conn.commit()
        cur.close()

    def get_content_models(self):
        """Returns the existing content models from content_models-table"""
        cur = self.conn.cursor()
        q = "SELECT * FROM content_models"
        cur.execute(q)
        out = dict((y.decode('utf-8'), x) for x, y in cur.fetchall())
        self.conn.commit()
        cur.close()
        return out

    def get_last_eid(self, content_model=None):
        """Returns the last entity ID (int) for the given content_model.
        If wb_id_counters-table has no counters for the given content_model,
        then sets the last entity ID to zero."""
        cur = self.conn.cursor()
        try:
            q0 = "SELECT id_type FROM wb_id_counters WHERE id_type='{db_content_model}'".format(
                db_content_model=content_model)
            cur.execute(q0)
            counters = cur.fetchone()[0]
            if counters == content_model.encode('UTF-8'):
                q = """SELECT id_value AS next_id from wb_id_counters where id_type='{db_content_model}'""".format(
                    db_content_model=content_model)
                cur.execute(q)
                eid = cur.fetchone()[0]
        except Exception:
            eid = 0
        cur.close()
        return eid

    def get_text_id(self):
        """Returns the last text_id (int) in text-table"""
        cur = self.conn.cursor()
        q = "SELECT max(old_id) FROM text"
        cur.execute(q)
        text_id = cur.fetchone()[0]
        cur.close()
        return text_id

    def get_page_id(self):
        """Returns the last page_id (int) in page-table"""
        cur = self.conn.cursor()
        q = "SELECT max(page_id) FROM page"
        cur.execute(q)
        page_id = cur.fetchone()[0]
        cur.close()
        return page_id

    def get_rev_id(self):
        """Returns the last revision_id (int) in revision-table"""
        cur = self.conn.cursor()
        q = "SELECT max(rev_id) FROM revision"
        cur.execute(q)
        page_id = cur.fetchone()[0]
        cur.close()
        return page_id

    def get_comment_id(self):
        """Returns the last comment_id (int) in comment-table"""
        cur = self.conn.cursor()
        q = "SELECT max(comment_id) FROM comment"
        cur.execute(q)
        comment_id = cur.fetchone()[0]
        cur.close()
        return comment_id

    def get_content_id(self):
        """Returns the last content_id (int) in content-table"""
        cur = self.conn.cursor()
        q = "SELECT max(content_id) FROM content"
        cur.execute(q)
        content_id = cur.fetchone()[0]
        cur.close()
        return content_id

    def get_model_id(self, content_model=None):
        """Returns model_id (int) for the given content_model in content_models-table"""
        cur = self.conn.cursor()
        q = "SELECT model_id FROM content_models WHERE model_name='{db_content_model}'""".format(
            db_content_model=content_model)
        cur.execute(q)
        mid = cur.fetchone()[0]
        cur.close()
        return mid

    def update_wb_id_counters(self, new_eid=None, content_model=None):
        """Inserts the new QID into wb_id_counters-table"""
        cur = self.conn.cursor()
        q = "INSERT INTO wb_id_counters(id_value,id_type) VALUES(1,'{content_model}') ON DUPLICATE KEY UPDATE id_value = id_value + 1".format(
            content_model=content_model)
        cur.execute(q)
        cur.close()
        pass

    def search_text_str(self, substring=None, strict=None):
        """Searches a substring in old_text of text-table and returns page_title"""
        cur = self.conn.cursor()
        try:
            if strict:
                q1 = """SELECT old_id FROM text WHERE old_text LIKE '%"{substr}"%'""".format(
                    substr=substring)
            else:
                q1 = """SELECT old_id FROM text WHERE old_text LIKE '%{substr}%'""".format(
                    substr=substring)
            cur.execute(q1)
            ids = ', '.join([str(x[0]) for x in cur.fetchall()])
            q2 = "SELECT page_title FROM page WHERE page_latest in (" + ids + ")"
            cur.execute(q2)
            eids = [x[0].decode('utf-8') for x in cur.fetchall()]
        except Exception:
            eids = []
        cur.close()
        return eids

    def search_text_eid(self, eid=None):
        """Searches eid in old_text of text-table and returns old_id and old_text"""
        cur = self.conn.cursor()
        try:
            q1 = """SELECT old_id, old_text FROM text WHERE old_text LIKE '%"id":"{db_eid}"%'""".format(
                db_eid=eid)
            cur.execute(q1)
            out = cur.fetchone()
        except Exception:
            out = ()
        cur.close()
        return out

    def get_old_lendata(self, page_id=None):
        """Returns old len(data) for the given page_id."""
        cur = self.conn.cursor()
        q = """SELECT rc_new_len FROM recentchanges WHERE rc_id <= '{db_page_id}' ORDER BY rc_id DESC LIMIT 1""".format(
            db_page_id=page_id)
        cur.execute(q)
        out = cur.fetchone()[0]
        return out

    def get_page_latest(self, page_title=None, namespace=None):
        """Returns [page_id (int), page_latest (int)] in page-table for the 
        given page_title and namespace"""
        cur = self.conn.cursor()
        q = """SELECT page_id, page_latest FROM page WHERE page_title='{db_page_title}' and page_namespace='{db_page_namespace}'""".format(
            db_page_title=page_title,
            db_page_namespace=namespace)
        cur.execute(q)
        (page_id, page_latest) = cur.fetchall()[0]
        cur.close()
        return [page_id, page_latest]

    def get_ids(self, new=None, page_title=None, namespace=None):
        """Returns [text_id, page_id, comment_id, content_id, rev_id]"""
        if new:
            rev_id = self.get_rev_id() + 1
            page_id = self.get_page_id() + 1
        if not new:
            [page_id, rev_id] = self.get_page_latest(page_title=page_title, namespace=namespace)
        text_id = self.get_text_id() + 1
        comment_id = self.get_comment_id() + 1
        content_id = self.get_content_id() + 1
        return [text_id, page_id, comment_id, content_id, rev_id]

    def insert(self, text_id=None, text=None, page_id=None, page_title=None,
               comment_id=None, content_id=None, model_id=None,
               content_model=None, namespace=None,
               rev_id=None, new=False, ip=None):
        """Inserts data into 9 tables during creation and edit of a page"""
        timenow = re.sub("[^0-9]", "", datetime.datetime.now().isoformat())[0:14]
        len_data = len(text)
        sha1hash = hashlib.sha1(text.encode()).hexdigest()[0:31]
        if new:
            action = 'create'
        else:
            action = 'edit'
        comment = "/* wbeditentity-" + action + "-" + content_model + ":0| */"
        chash = hash(comment) % 10 ** 9
        cur = self.conn.cursor()
        if new is True:
            page_latest = rev_id
            rev_parent_id = 0
            rc_source = "mw.new"
            rc_last_oldid = 0
            rc_type = 1
            rc_old_len = 0
        elif new is False:
            rev_parent_id = rev_id
            rc_source = "mw.edit"
            rc_last_oldid = rev_id
            rc_type = 0
            rc_old_len = self.get_old_lendata(page_id=page_id)
            rev_id = self.get_rev_id() + 1
            page_latest = rev_id
        else:
            raise ValueError('{} is not a valid "new" parameter. Use "True" or "False".'.format(new))
        q1 = "INSERT INTO text VALUES('{db_text_id}','{db_text}','utf-8')".format(
            db_text_id=text_id,
            db_text=text)
        q2 = """REPLACE INTO page VALUES('{db_page_id}','{db_namespace}','{db_page_title}','',0,'{db_new}',
            rand(),'{db_timenow}','{db_timenow}','{db_page_latest}','{db_len}','{db_content_model}',NULL)""".format(
            db_page_id=page_id,
            db_page_title=page_title,
            db_namespace=namespace,
            db_timenow=timenow,
            db_page_latest=page_latest,
            db_len=len_data,
            db_content_model=content_model,
            db_new=int(new))
        q3 = """INSERT INTO revision VALUES(NULL,'{db_page_id}','{db_comment_id}',
            0,'{db_timenow}',0,0,'{db_len}','{db_rev_parent_id}','{db_sha1hash}')""".format(
            db_comment_id=comment_id,
            db_page_id=page_id,
            db_timenow=timenow,
            db_len=len_data,
            db_sha1hash=sha1hash,
            db_rev_parent_id=rev_parent_id)
        q4 = "INSERT INTO comment VALUES('{db_comment_id}','{db_chash}','{db_comment}',NULL)".format(
            db_comment_id=comment_id,
            db_chash=chash,
            db_comment=comment)
        q5 = "INSERT INTO revision_comment_temp VALUES ('{db_rev_id}','{db_comment_id}')".format(
            db_rev_id=rev_id,
            db_comment_id=comment_id)
        q6 = "INSERT INTO revision_actor_temp VALUES( '{db_rev_id}', 1, '{db_timenow}', '{db_page_id}')".format(
            db_rev_id=rev_id,
            db_timenow=timenow,
            db_page_id=page_id)
        q7 = """INSERT INTO content VALUES('{db_content_id}','{db_len_data}',
            '{db_sha1hash}','{db_model_id}','{db_tt_text_id}')""".format(
            db_content_id=content_id,
            db_len_data=len_data,
            db_sha1hash=sha1hash,
            db_model_id=model_id,
            db_tt_text_id='tt:' + str(text_id))
        q8 = "INSERT INTO slots VALUES( '{db_text_id}', 1, '{db_content_id}', '{db_text_id}')".format(
            db_text_id=text_id,
            db_content_id=content_id)
        q9 = """INSERT INTO recentchanges VALUES ( NULL,'{db_timenow}',1,
            '{db_namespace}','{db_page_title}','{db_comment_id}',0,0,'{db_new}',
            '{db_page_id}','{db_rev_id}','{db_rc_last_oldid}','{db_rc_type}',
            '{db_rc_source}',2,'{db_rc_ip}','{db_rc_old_len}','{db_len_data}',0,0,NULL,'',''  )""".format(
            db_timenow=timenow,
            db_namespace=namespace,
            db_page_title=page_title,
            db_comment_id=comment_id,
            db_page_id=page_id,
            db_rc_old_len=rc_old_len,
            db_len_data=len_data,
            db_rev_id=rev_id,
            db_new=int(new),
            db_rc_type=rc_type,
            db_rc_source=rc_source,
            db_rc_ip=ip,
            db_rc_last_oldid=rc_last_oldid)
        cur.execute(q1)
        cur.execute(q2)
        cur.execute(q3)
        cur.execute(q4)
        cur.execute(q5)
        cur.execute(q6)
        cur.execute(q7)
        cur.execute(q8)
        cur.execute(q9)
        cur.close()
        pass
