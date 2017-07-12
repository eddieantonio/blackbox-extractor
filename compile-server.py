#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from BaseHTTPServer import HTMLServer, BaseHTTPRequestHandler

class BlackBoxServer(BaseHTTPRequestHandler):
    raise NotImplementedError

