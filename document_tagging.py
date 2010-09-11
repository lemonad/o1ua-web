# -*- coding: utf-8 -*-
import web

class Tagging:
    def __init__(self, web_db):
        self.db = web_db

    def get_tag_type(self, model, name):
        """ Returns the ID of the specified tag_type given a model and name. """

        tag_type = self.db.select(['tag_type'],
                                  what='id',
                                  where="model=$model AND name=$name",
                                  vars={'model': model,
                                        'name': name},
                                  limit=1)
        return tag_type[0].id

    def get_object_ids_for_tag(self, model, tag_types, tag_names):
        """ Returns a list of object ids for a specific model tagged with
        the given tag(s) within the specified tag type(s).

        e.g. get_object_ids_for_tag('document', ['system', 'tag'], 'hello')

        model                   The name of the tagged model.
        tag_types               A single tag type or a list of tag types.
        tag_names               A single tag name or a list of tag names.

        """
        # FIXME: SQL injection checks! sqlors should not be trusted in queries

        # Fetch tag IDs for tags
        tags_sql = web.db.sqlors("name = ", tag_names)
        tags = self.db.select('tag',
                              where=str(tags_sql))
        tag_id_list = [tag.id for tag in tags]

        # Fetch tag type IDs for specified model
        names_sql = web.db.sqlors("name = ", tag_types)
        tag_type_ids = self.db.select('tag_type',
                                      what='id',
                                      where="model = $model " \
                                            "AND %s" % str(names_sql),
                                      vars={'model': model})
        tag_type_id_list = [tag_type.id for tag_type in tag_type_ids]

        # Fetch unique tagged objects
        tag_types_sql = web.db.sqlors("tag_type_id = ", tag_type_id_list)
        tag_ids_sql = web.db.sqlors("tag_id = ", tag_id_list)
        docs = self.db.query("SELECT DISTINCT object_id FROM tagged_object "
                             "WHERE %s AND %s" % (str(tag_types_sql),
                                                  str(tag_ids_sql)))
        return [doc.object_id for doc in docs]

    def get_tags_for_object(self, model, tag_type, document_id):
        """ Returns a list of associated tags for the given model, tag_type
        and document. Each item of the list is a tuple of tag id and name.

        """
        tag_type_id = self.get_tag_type(model, tag_type)
        tags = self.db.query("SELECT tag.id, tag.name "
                             "FROM tagged_object AS tobj, tag "
                             "WHERE tobj.tag_type_id = $tag_type_id "
                             "AND tobj.object_id = $doc_id "
                             "AND tobj.tag_id = tag.id",
                             vars={'tag_type_id': tag_type_id,
                                   'doc_id': document_id})
        return [(tag.id, tag.name) for tag in tags]

    def split_comma_separated_tags(self, tag_str):
        """ Returns a list of tag names given a comma separated string. """

        raw_tags = tag_str.split(',')
        tags = [tag.strip() for tag in raw_tags]
        return [tag for tag in tags if len(tag) > 0]
