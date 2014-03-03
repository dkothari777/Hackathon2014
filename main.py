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
import sys

from tornado.options import define, options, parse_command_line
from StringIO import StringIO


define("port", 8080)


class ScriptException(Exception):
    def __init__(self, returncode, stdout, stderr, script):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        Exception.__init__(self, 'Error in script')


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_id = self.get_cookie("plainssid")
        if not user_id:
            return None
        return user_id


class JavaHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print(("Java user connected"))

    def on_message(self, message):
        self.sessid = 'A' + message[0:40]
        message = message[40:]
        print((self.sessid))
        print(message)
        f = open('tmp/' + self.sessid + '.tmp', 'w+')
        f.write(message)
        f.close()
        f = open('tmp/' + self.sessid + '.java', 'w+')
        f.write("public class " + self.sessid +
            " {\npublic static void main( String[] args ) {\n"+open('tmp/'+
                self.sessid+'.tmp').read()+"}\n}")
        f.close()
        print f
        print "Running JavaFiddleUtils"
        output = subprocess.PIPE
        err = subprocess.PIPE
        print 'cd ./tmp; javac '+self.sessid+'.java'
        r1 = subprocess.check_output('cd ./tmp; javac '+self.sessid+'.java', shell=True)
        r2 = subprocess.check_output('cd ./tmp; java '+self.sessid, shell=True)
        print r2
        self.write_message(r2)

    def on_close(self):
        print "User is done"


class PyHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print(("Python user connected"))

    def on_message(self, message):
        self.sessid = message[0:40]
        message = message[40:]
        out = eval(message)
        self.write_message(out)


class HomeHandler(BaseHandler):
    def get(self):
        try:
            code = open('tmp/A'+self.get_current_user()+'.tmp').read()
        except IOError, e:
            code = 'System.out.print("Hello, World!");'
        if self.get_current_user() is not None:
            self.render("index.html", code = code)
        else:
            self.redirect("/auth/login")


class AuthLoginHandler(BaseHandler):
    def get(self):
        h = hashlib.new('sha1')
        h.update(str(random.random()))
        self.sessid = h.hexdigest()
        self.set_cookie("plainssid", self.sessid)
        self.redirect("/")


class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_all_cookies()
        subprocess.call(['rm', '-rf',
            "tmp/" + self.get_current_user() + '*'])


class ParseHandler(BaseHandler):

    def get(self):
        self.get


def main():
    testServer = tornado.web.Application(
        [
            (r"/", HomeHandler),
            (r"/auth/login", AuthLoginHandler),
            (r"/auth/logout", AuthLogoutHandler),
            (r"/java", JavaHandler),
            (r"/python", PyHandler),
            (r"/parse", ParseHandler)
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
