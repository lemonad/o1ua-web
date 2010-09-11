PRAGMA foreign_keys = ON;

/* Example data */

INSERT INTO document_type (id, name)
        VALUES (1, "Systembeskrivning");

INSERT INTO document (id, title, type_id, location)
        VALUES (1,
                "Systembeskrivning 313",
                1,
                "http://ksu-srv-sps1/o1ua/ss313.doc");

INSERT INTO tag (id, name)
        VALUES (1, "ventilkaraktäristik");
INSERT INTO tag (id, name)
        VALUES (2, "pumpkurva");
INSERT INTO tag (id, name)
        VALUES (3, "313");

INSERT INTO tagged_object (id, tag_id, tag_type_id, object_id)
        VALUES (1, 1, 1, 1);
INSERT INTO tagged_object (id, tag_id, tag_type_id, object_id)
        VALUES (2, 2, 1, 1);
INSERT INTO tagged_object (id, tag_id, tag_type_id, object_id)
        VALUES (3, 3, 2, 1);
