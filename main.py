# -*- coding: utf-8 -*-
import random
import hashlib
import tornado.auth
import tornado.escape
import tornado.ioloop
import tornado.web
import tornado.websocket
import subprocess
import os.path

from tornado.options import define, options, parse_command_line

define("port", 8080)


class ScriptException(Exception):
    def __init__(self, returncode, stdout, stderr, script):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        Exception.__init__('Error in script')


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_id = self.get_secure_cookie("sessid")
        if not user_id:
            return None
        return user_id


@tornado.web.authenticated
class SocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print(("User " + self.get_current_user + " connected"))

    #Usage: command is an list
    def call(self, command):
        # Spaces cause errors!
        proc = subprocess.Popen(command,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            stdin=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if proc.returncode:
            raise ScriptException(proc.returncode, stdout, stderr, command)
        return stdout, stderr

    def on_message(self, message):
        self.sessid = message[0:41]
        message = message[41:]
        f = open(self.sessid, 'w')
        f.write(message)
        self.call(['java', 'javaFiddleUtils', self.sessid])


class HomeHandler(BaseHandler):
    def get(self):
        if self.get_current_user() is not None:
            self.render("index.html")
        else:
            self.redirect("/auth/login")


class AuthLoginHandler(BaseHandler):
    def get(self):
        h = hashlib.new('sha1')
        h.update(str(random.random()))
        self.sessid = h.hexdigest()
        self.set_secure_cookie("sessid", self.sessid)
        self.redirect("/")


class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_all_cookies()
        subprocess.call(['rm', '-rf', self.get_current_user() + '.java'])
        subprocess.call(['rm', '-rf', self.get_current_user() + '.class'])
        self.write("logout successful")


def main():
    testServer = tornado.web.Application(
        [
            (r"/", HomeHandler),
            (r"/auth/login", AuthLoginHandler),
            (r"/auth/logout", AuthLogoutHandler),
            (r"/server", SocketHandler)
        ],
        title="Scoring Server",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        xsrf_cookies=True,
        cookie_secret="testbed",  #TODO: Generate Random value
        login_url="/auth/login",
        debug=True  #TODO: Disable debug
    )
    testServer.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
    parse_command_line()


if __name__ == "__main__":
    main()