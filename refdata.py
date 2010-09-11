#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pprint
import web
from web import form
from whoosh.fields import ID, KEYWORD, Schema, TEXT
from whoosh.index import create_in, open_dir
from whoosh.qparser import MultifieldParser

import document_tagging

search_form = form.Form(form.Textbox('',
                                     autofocus='autofocus',
                                     size="60",
                                     placeholder="Sök efter titlar, taggar och system"))
# <input id="q" name="q" size="60" placeholder="Sök efter titlar, taggar och system" autofocus>

def index_everything():
    writer = ix.writer()

    documents = db.select('document')
    for document in documents:
        # Get tags for document
        tags = tagging.get_tags_for_object("document",
                                           "tag",
                                           document.id)
        tag_names = [tag_name for (tag_id, tag_name) in tags]
        tag_str = ', '.join(tag_names)
        print "tag_str =", tag_str

        # Get systems for document
        systems = tagging.get_tags_for_object("document",
                                              "system",
                                              document.id)
        system_names = [tag_name for (tag_id, tag_name) in systems]
        system_str = ', '.join(system_names)
        print "system_str =", system_str

        writer.add_document(title=document.title,
                            tags=tag_str,
                            systems=system_str)
    writer.commit()

def search(query_str):
    """ Returns a list of documents given a search query. """

    searcher = ix.searcher()
    queryparser = MultifieldParser(["title", "tags", "systems"],
                                   schema=ix.schema)
    query = queryparser.parse(query_str)
    results = searcher.search(query, limit=1)
    for r in results:
        print r

urls = ('/', 'index')

render = web.template.render('templates/')
app = web.application(urls, globals())
db = web.database(dbn='sqlite', db='refdata.db')
# Ensure foreign keys are activated in SQLite
db.query("PRAGMA foreign_keys = ON")
tagging = document_tagging.Tagging(db)

schema = Schema(doc_id=ID(stored=True),
                title=TEXT(stored=True, field_boost=2.0),
                systems=KEYWORD(lowercase=True),
                tags=KEYWORD(lowercase=True))
if not os.path.exists("whoosh_index"):
    os.mkdir("whoosh_index")
ix = create_in("whoosh_index", schema)
ix = open_dir("whoosh_index")
index_everything()

class index:
    def GET(self):
        form = search_form()
        if form.validates():
            print form

        # tags = tagging.get_tags_for_object("document", "tag", 1)
        #         for (tag_id, tag_name) in tags:
        #             print "(tag) tag_id = %d, tag_name = '%s'" % (tag_id, tag_name)
        #         systems = tagging.get_tags_for_object("document", "system", 1)
        #         for (tag_id, tag_name) in systems:
        #             print "(system) tag_id = %d, tag_name = '%s'" % (tag_id, tag_name)
        #         t = tagging.split_comma_separated_tags("  jonas,,hello,   wårld")
        #         print "tags =", ', '.join(t)
        #         docs = tagging.get_object_ids_for_tag("document",
        #                                       ['system', 'tag'],
        #                                       ["pumpkurva", "313"])
        #         print "docs for tag =", docs
        search(u"pump*")


        # tag_type_id = get_tag_type('document', 'tag')
        # system_type_id = get_tag_type('document', 'system')

        # db.query("SELECT * FROM foo WHERE x = $x", vars=dict(x='f'))
        documents = db.select('document')
        search_block = render.search_block(form, documents)
        return render.index(search_block, nav="search")

if __name__ == "__main__": app.run()
