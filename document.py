# -*- coding: utf-8 -*-

class Document:
    def __init__(self, web_db, tagging, searching):
        self.db = web_db
        self.tagging = tagging
        self.searching = searching

    def get_document_types_with_null(self):
        types = self.get_document_types()
        types.insert(0, (None, ""))
        return types

    def get_document_types(self):
        doctypes = self.db.select("document_type")
        return [(doctype.id, doctype.name) for doctype in doctypes]

    def add_document(self,
                     title,
                     document_type_id,
                     location,
                     comma_sep_systems,
                     comma_sep_tags):
        # Add document
        document_id = self.db.insert("document",
                                     title=title.strip(),
                                     type_id=document_type_id,
                                     location=location.strip())

        # Add related systems
        systems_lower = comma_sep_systems.lower()
        systems = self.tagging.split_comma_separated_tags(systems_lower)
        self.tagging.update_tags_for_object("document",
                                            "system",
                                            document_id,
                                            systems)
        # Add related tags
        tags_lower = comma_sep_tags.lower()
        tags = self.tagging.split_comma_separated_tags(tags_lower)
        self.tagging.update_tags_for_object("document",
                                            "tag",
                                            document_id,
                                            tags)

        # Index document
        self.searching.index_document(document_id)

        return document_id

    def update_document(self,
                        document_id,
                        title,
                        document_type_id,
                        location,
                        comma_sep_systems,
                        comma_sep_tags):
        # Update document
        self.db.update("document",
                       where="id = $id",
                       vars={'id': document_id},
                       title=title.strip(),
                       type_id=document_type_id,
                       location=location.strip())

        # Update related systems
        systems_lower = comma_sep_systems.lower()
        systems = self.tagging.split_comma_separated_tags(systems_lower)
        self.tagging.update_tags_for_object("document",
                                            "system",
                                            document_id,
                                            systems)
        # Update related tags
        tags_lower = comma_sep_tags.lower()
        tags = self.tagging.split_comma_separated_tags(tags_lower)
        self.tagging.update_tags_for_object("document",
                                            "tag",
                                            document_id,
                                            tags)

        # Index document
        self.searching.index_document(document_id)
