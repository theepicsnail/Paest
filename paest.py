#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import webapp2
import jinja2
import os

from google.appengine.ext import ndb
from google.appengine.api import users

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

PAEST_ROOT = ndb.Key('paest', 'root')

class Post(ndb.Model):
    author = ndb.UserProperty()
    content = ndb.TextProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        args = {}
        templ = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(templ.render(args))
    
class Create(webapp2.RequestHandler):
    def post(self):
        post = Post(parent=PAEST_ROOT)
        for old in Post.query().order(-Post.date).fetch(10, offset=10):
            print "DELETE:", old
            old.key.delete()

        if users.get_current_user():
            post.author = users.get_current_user()
        post.content = self.request.get('content')
        key = post.put()
        self.redirect('/view/{}'.format(key.id()))

class View(webapp2.RequestHandler):
    def get(self, post_id):
        post = Post.get_by_id(int(post_id), PAEST_ROOT)
        print "Found:", post
        templ = JINJA_ENVIRONMENT.get_template('view.html')
        self.response.write(templ.render({
            'post':post
        }))

class Raw(webapp2.RequestHandler):
    def get(self, post_id):
        post = Post.get_by_id(int(post_id), PAEST_ROOT)
        print post.content
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(post.content)

app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/create', Create),
  ('/view/(\d+)', View),
  ('/raw/(\d+)', Raw)
], debug=True)
