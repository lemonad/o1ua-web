# -*- coding: utf-8 -*-
import pprint
import web

urls = ('/', 'index')

render = web.template.render('templates/')
app = web.application(urls, globals())
db = web.database(dbn='sqlite', db='refdata.db')

class index:
    def GET(self):
        documents = db.select('documents')
        search = render.search_block(documents)
        return render.index(search)

if __name__ == "__main__": app.run()
