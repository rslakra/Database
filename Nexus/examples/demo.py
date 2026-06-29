#!/usr/bin/env python3
"""Quick demo: SQL table + document collection on one Nexus engine."""

from _bootstrap import bootstrap

bootstrap()

from catalog import Column, Constraint, Table
from document import Collection, Document
from engine import MultiModelDatabase


def main() -> None:
    db = MultiModelDatabase("demo")

    pets = Table(
        name="Pets",
        columns=[
            Column("id", "INT", nullable=False, auto_increment=True),
            Column("name", "VARCHAR(20)", nullable=False),
            Column("owner", "VARCHAR(20)"),
            Column("species", "VARCHAR(20)"),
        ],
        constraints=[Constraint("primary_key", columns=["id"])],
    )
    db.create_table(pets)

    db.execute_sql(
        "INSERT INTO Pets (name, owner, species) VALUES ('Puffball', 'Diane', 'hamster')"
    )
    sql_rows = db.execute_sql("SELECT name, owner, species FROM Pets WHERE species = 'hamster'")
    print("SQL:", sql_rows)

    posts = Collection("posts")
    db.create_collection(posts)
    db.create_text_index("idx_posts_body", collection="posts", field="body")

    db.insert_document(
        Document(
            collection=posts,
            data={"title": "Nexus", "body": "multi-model database engine", "tags": ["sql", "document"]},
        )
    )
    nosql_rows = db.execute_nosql(db.documents.find("posts", filter={"title": "Nexus"}))
    print("Document:", nosql_rows)

    search = db.execute_nosql(
        db.documents.text_search("posts", index="idx_posts_body", term="multi")
    )
    print("Search:", search)


if __name__ == "__main__":
    main()
