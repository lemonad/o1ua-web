# -*- coding: utf-8 -*-
from exceptions import IndexError, TypeError

import web

# TODO: Unused tags should be removed when they're not referenced anymore


class Tagging:
    def __init__(self, web_db):
        self.db = web_db

    def get_tag_names(self, model, tag_type):
        tag_type_id = self._get_tag_type(model, tag_type)
        tags = self.get_tags(tag_type_id)
        return [tag_name for (tag_id, tag_name) in tags]

    def get_tags(self, tag_type_id):
        tags = self.db.query("SELECT tag.id, tag.name "
                             "FROM tagged_object, tag "
                             "WHERE tagged_object.tag_id = tag.id "
                             "AND tagged_object.tag_type_id = $tag_type_id",
                             vars={'tag_type_id': tag_type_id})
        return [(tag.id, tag.name) for tag in tags]

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
        tag_type_id_list = self._get_tag_types(model, tag_types)

        # Fetch unique tagged objects
        tag_types_sql = web.db.sqlors("tag_type_id = ", tag_type_id_list)
        tag_ids_sql = web.db.sqlors("tag_id = ", tag_id_list)
        objs = self.db.query("SELECT DISTINCT object_id FROM tagged_object "
                             "WHERE %s AND %s" % (str(tag_types_sql),
                                                  str(tag_ids_sql)))
        return [obj.object_id for obj in objs]

    def get_tag_names_for_object(self, model, tag_type, object_id):
        """ Returns a list of associated tag names for the given model,
        tag_type and object.

        """
        tags = self.get_tags_for_object(model, tag_type, object_id)
        return [tag_name for (tag_id, tag_name) in tags]

    def get_tag_ids_for_object(self, model, tag_type, object_id):
        """ Returns a list of associated tag IDs for the given model,
        tag_type and object.

        """
        tags = self.get_tags_for_object(model, tag_type, object_id)
        return [tag_id for (tag_id, tag_name) in tags]

    def get_tags_for_object(self, model, tag_type, object_id):
        """ Returns a list of associated tags for the given model, tag_type
        and object. Each item of the list is a tuple of tag id and name.

        """
        tag_type_id = self._get_tag_type(model, tag_type)
        tags = self.db.query("SELECT tag.id, tag.name "
                             "FROM tagged_object AS tobj, tag "
                             "WHERE tobj.tag_type_id = $tag_type_id "
                             "AND tobj.object_id = $obj_id "
                             "AND tobj.tag_id = tag.id",
                             vars={'tag_type_id': tag_type_id,
                                   'obj_id': object_id})
        return [(tag.id, tag.name) for tag in tags]

    def update_tags_for_object(self, model, tag_type, object_id, tag_names):
        """ Given a list of tags, adds and removes object tagging. """

        tag_list = self.get_tags_for_object(model, tag_type, object_id)
        current_tags = {}
        for (tag_id, tag_name) in tag_list:
            current_tags[tag_name] = tag_id

        # Add new object tags
        for tag_name in tag_names:
            if tag_name in current_tags:
                del current_tags[tag_name]
            else:
                self.add_tag_for_object(model, tag_type, object_id, tag_name)

        # Remove no longer used object tags
        for tag_name in current_tags:
            self.remove_tag_for_object(model, tag_type, object_id, tag_name)

    def add_tag_for_object(self, model, tag_type, object_id, tag_name):
        tag_type_id = self._get_tag_type(model, tag_type)

        tag_id = self.add_tag(tag_name)
        if not self._is_object_tagged_by_id(model,
                                            tag_type_id,
                                            object_id,
                                            tag_id):
            tobj_id = self.db.insert("tagged_object",
                                     tag_id=tag_id,
                                     tag_type_id=tag_type_id,
                                     object_id=object_id)

    def remove_tag_for_object(self, model, tag_type, object_id, tag_name):
        tag_type_id = self._get_tag_type(model, tag_type)

        tag_id = self._get_tag_id_by_name(tag_name)
        if not tag_id:
            return

        if self._is_object_tagged_by_id(model,
                                        tag_type_id,
                                        object_id,
                                        tag_id):
            self.db.delete("tagged_object",
                           where="tag_id = $tag_id "
                                 "AND tag_type_id = $tag_type_id "
                                 "AND object_id = $object_id",
                           vars={'tag_id': tag_id,
                                 'tag_type_id': tag_type_id,
                                 'object_id': object_id})

    def add_tag(self, tag_name):
        """ Adds a new tag and returns it's ID. """
        
        tag_id = self._get_tag_id_by_name(tag_name)
        if tag_id:
            return tag_id

        tag_id = self.db.insert('tag', name=tag_name)
        return tag_id

    def split_comma_separated_tags(self, tag_str):
        """ Returns a list of tag names given a comma separated string. """

        raw_tags = tag_str.split(',')
        tags = [tag.strip() for tag in raw_tags]
        return [tag for tag in tags if len(tag) > 0]

    def _get_tag_id_by_name(self, tag_name):
        tag = self.db.select("tag",
                             where="name = $name",
                             limit=1,
                             vars={'name': tag_name})
        try:
            return tag[0].id
        except IndexError:
            return None

    def _get_tag_type(self, model, name):
        if not isinstance(name, str):
            raise TypeError('Tag type name must be a single string')
        return self._get_tag_types(model, name)

    def _get_tag_types(self, model, names):
        """ Returns the ID(s) for the specified tag type(s) given
        a model and name(s).

        names               if a list of names, returns a list of tag
                            type ids, otherwise return a single tag type ID.

        """
        names_sql = web.db.sqlors("name = ", names)
        tag_type_ids = self.db.select('tag_type',
                                      what='id',
                                      where="model = $model " \
                                            "AND %s" % str(names_sql),
                                      vars={'model': model})
        if isinstance(names, list):
            return [tag_type.id for tag_type in tag_type_ids]
        else:
            return tag_type_ids[0].id

    def _is_object_tagged_by_id(self, model, tag_type_id, object_id, tag_id):
        tagged_object = self.db.select("tagged_object",
                                       where="tag_id = $tag_id "
                                             "AND tag_type_id = $tag_type_id "
                                             "AND object_id = $object_id",
                                       limit=1,
                                       vars={'tag_id': tag_id,
                                             'tag_type_id': tag_type_id,
                                             'object_id': object_id})
        if tagged_object:
            return True
        else:
            return False

