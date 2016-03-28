#!/usr/bin/env python
# -*- coding: utf-8 -*-
import web
import os
# import view
# import config
# from view import render

# URL structure:
# Regular expression that matches a URL + name of class which
# will handle the request.
urls = (
    '/apagar', 'apagar',
    '/', 'index'
)


class apagar:
    def GET(self):
        return 'Resource -> ' + self.__class__.__name__ \
                              + ' PID: ' \
                              + str(os.getpid()) + '\n'

# class index:
#    def GET(self):
#        i = web.input(name=None)
#        return render.index(i.name)


def startrest():
    webapp = web.application(urls, globals())
    webapp.internalerror = web.debugerror
    webapp.run()

if __name__ == '__main__':
    startrest()
