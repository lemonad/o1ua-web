# -*- coding: utf-8 -*-
import os
from whoosh.fields import ID, KEYWORD, Schema, TEXT
from whoosh.index import create_in, open_dir
from whoosh.qparser import MultifieldParser

class Search:
    def __init__(self, web_db, tagging):
        self.db = web_db
        self.tagging = tagging
        # Store everything so document listings can be based
        # solely on index
        self.schema = Schema(id=ID(unique=True, stored=True),
                             title=TEXT(stored=True, field_boost=2.0),
                             location=TEXT(stored=True),
                             type=TEXT(stored=True),
                             systems=KEYWORD(stored=True,
                                             lowercase=True,
                                             commas=True),
                             tags=KEYWORD(stored=True,
                                          lowercase=True,
                                          commas=True))
        if not os.path.exists("whoosh_index"):
            os.mkdir("whoosh_index")
        # Create and clear index
        ix = create_in("whoosh_index", self.schema)
        self.ix = open_dir("whoosh_index")
        self.index_everything()

    def index_document(self, document_id):
        writer = self.ix.writer()

        document = self.db.select("document",
                                  where="id = $id",
                                  vars={'id': document_id})[0]

        # Get document type as a string
        if document.type_id:
            doctype = self.db.select("document_type",
                                     where="id = $id",
                                     vars={'id': document.type_id})[0].name
        else:
            doctype = ""

        # Get tags for document
        tags = self.tagging.get_tag_names_for_object("document",
                                                     "tag",
                                                     document.id)
        tag_str = ', '.join(tags)

        # Get systems for document
        systems = self.tagging.get_tag_names_for_object("document",
                                                        "system",
                                                        document.id)
        system_str = ', '.join(systems)

        # If no existing document matches the unique fields of the
        # document we're updating, update_document acts just like
        # add_document
        writer.update_document(id=unicode(document.id),
                               _stored_id=document.id,
                               title=unicode(document.title),
                               type=unicode(doctype),
                               location=unicode(document.location),
                               tags=unicode(tag_str),
                               systems=unicode(system_str))
        writer.commit()

    def index_everything(self):
        writer = self.ix.writer()

        documents = self.db.select('document')
        for document in documents:
            # Get document type as a string
            if document.type_id:
                doctype = self.db.select("document_type",
                                         where="id = $id",
                                         vars={'id': document.type_id})[0].name
            else:
                doctype = ""

            # Get tags for document
            tags = self.tagging.get_tag_names_for_object("document",
                                                         "tag",
                                                         document.id)
            tag_str = ', '.join(tags)

            # Get systems for document
            systems = self.tagging.get_tag_names_for_object("document",
                                                            "system",
                                                            document.id)
            system_str = ', '.join(systems)

            writer.add_document(id=unicode(document.id),
                                _stored_id=document.id,
                                title=unicode(document.title),
                                type=unicode(doctype),
                                location=unicode(document.location),
                                tags=unicode(tag_str),
                                systems=unicode(system_str))
        writer.commit()

    def search(self, query_str):
        """ Returns a list of documents given a search query. """

        searcher = self.ix.searcher()
        queryparser = MultifieldParser(["title", "tags", "systems"],
                                       schema=self.ix.schema)
        query = queryparser.parse(query_str)
        results = searcher.search(query, sortedby="type, title")
        #ids = [str(result['id']) for result in results]
        #sql_ids = ','.join(ids)
        #documents = self.db.query("SELECT * from document "
        #                          "WHERE id IN (%s)" % sql_ids)
        return results
