#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import web
from web.form import Dropdown, Form, notnull, regexp, Textarea, Textbox

from tagging import Tagging
from search import Search
from document import Document

urls = ("/", "index",
        "/alla-dokument/", "all_documents",
        "/dokument/", "new_document",
        "/dokument/([0-9]+)/",
        "edit_document")

search_form = Form(
    Textbox("q",
            autofocus="autofocus",
            size="60",
            placeholder="Sök efter titlar, taggar och system")
)
document_form = Form(
    Textarea("title",
             regexp(".*[^\s].*", "Dokumentet måste ha en titel"),
             class_="span-16"),
    Dropdown("document_type", "", class_="span-6"),
    Textbox("location",
            regexp(".*[^\s].*", "Var kan det här dokumentet hittas?"),
            class_="span-16"),
    Textbox("systems", class_="span-16"),
    Textbox("tags", class_="span-16")
)
render = web.template.render("templates/")
app = web.application(urls, globals())
db = web.database(dbn="sqlite", db="refdata.db")
db.query("PRAGMA foreign_keys = ON")
tagging = Tagging(db)
searching = Search(db, tagging)
documenting = Document(db, tagging, searching)


class index():
    def GET(self):
        form = search_form()
        if form.validates() and form["q"].value:
            documents = searching.search(form["q"].value)
        else:
            documents = None
        search_block = render.search_block(form, documents)
        return render.base(search_block, nav="search")

class all_documents():
    def GET(self):
        documents = searching.search(u'*')
        block = render.all_documents_block(documents)
        return render.base(block, nav="all-documents")

class new_document():
    def GET(self):
        tag_names = tagging.get_tag_names("document", "tag")
        document_types = documenting.get_document_types_with_null()

        form = document_form()
        form["document_type"].args = document_types

        doc_block = render.document_block(form, None, tag_names)
        return render.base(doc_block, nav="new-document")

    def POST(self):
        tag_names = tagging.get_tag_names("document", "tag")
        document_types = documenting.get_document_types_with_null()

        form = document_form()
        if not form.validates():
            form["document_type"].args = document_types

            doc_block = render.document_block(form, None, tag_names)
            return render.base(doc_block, nav="new-document")

        document_id = documenting.add_document(form["title"].value,
                                               form["document_type"].value,
                                               form["location"].value,
                                               form["systems"].value,
                                               form["tags"].value)
        raise web.seeother("/dokument/%d/" % document_id)

class edit_document():
    def GET(self, document_id):
        tag_names = tagging.get_tag_names("document", "tag")
        document_types = documenting.get_document_types_with_null()

        document = db.select("document",
                             where="id = $id",
                             limit=1,
                             vars={'id': document_id})[0]

        system_names = tagging.get_tag_names_for_object("document",
                                                        "system",
                                                        document.id)
        comma_sep_systems = ", ".join(system_names)
        tag_names = tagging.get_tag_names_for_object("document",
                                                     "tag",
                                                     document.id)
        comma_sep_tags = ", ".join(tag_names)

        form = document_form()
        form["title"].value = document.title
        form["document_type"].args = document_types
        form["document_type"].value = document.type_id
        form["location"].value = document.location
        form["systems"].value = comma_sep_systems
        form["tags"].value = comma_sep_tags

        doc_block = render.document_block(form, document, tag_names)
        return render.base(doc_block, nav="edit-document")

    def POST(self, document_id):
        tag_names = tagging.get_tag_names("document", "tag")
        document_types = documenting.get_document_types_with_null()

        document = db.select("document",
                             where="id = $id",
                             limit=1,
                             vars={'id': document_id})[0]

        form = document_form()
        if not form.validates():
            form["document_type"].args = document_types

            doc_block = render.document_block(form, document, tag_names)
            return render.base(doc_block, nav="edit-document")
        else:
            documenting.update_document(document_id,
                                        form["title"].value,
                                        form["document_type"].value,
                                        form["location"].value,
                                        form["systems"].value,
                                        form["tags"].value)
            raise web.seeother("/dokument/%d/" % document.id)


if __name__ == "__main__":
    app.run()
