PRAGMA foreign_keys = ON;

CREATE TABLE document_type (
        id integer PRIMARY KEY,
        name text
);

CREATE TABLE document (
        id integer PRIMARY KEY,
        title text,
        type_id integer NULL REFERENCES document_type (id),
        location text
);
CREATE INDEX document_type_id
        ON document (type_id);


/* Generic tagging */

CREATE TABLE tag (
        id integer NOT NULL PRIMARY KEY,
        name text NOT NULL UNIQUE
);
CREATE TABLE "tag_type" (
        id integer NOT NULL PRIMARY KEY,
        model text NOT NULL,
        name text NOT NULL
);
CREATE TABLE tagged_object (
        id integer NOT NULL PRIMARY KEY,
        tag_id integer NOT NULL REFERENCES tag (id),
        tag_type_id integer NOT NULL REFERENCES tag_type (id),
        object_id integer unsigned NOT NULL,
        UNIQUE (tag_id, object_id)
);
CREATE INDEX tagged_object_tag_id
        ON tagged_object (tag_id);
CREATE INDEX tagged_object_object_id
        ON tagged_object (object_id);
CREATE INDEX tagged_object_tag_type_id
        ON tagged_object (tag_type_id);


/* Insert tagging types to support tagging documents with
   regular tags as well as systems */
INSERT INTO tag_type (id, model, name)
        VALUES (1, "document", "tag");
INSERT INTO tag_type (id, model, name)
        VALUES (2, "document", "system");
