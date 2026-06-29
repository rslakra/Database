#!/usr/bin/env python3
"""Demo: import/export CSV and JSON via dataio connectors."""

import json
import tempfile
from pathlib import Path

from _bootstrap import bootstrap

bootstrap()

from catalog import Column, Constraint, Table
from datatype.data_formats import DataFormat
from document import Collection
from engine import MultiModelDatabase


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        db = MultiModelDatabase("connector-demo")

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

        csv_file = tmp_path / "pets.csv"
        csv_file.write_text(
            "name,owner,species\nPuffball,Diane,hamster\nSlim,Benny,snake\n",
            encoding="utf-8",
        )
        imported = db.data.import_table(csv_file, "Pets")
        print(f"Imported {imported} rows from CSV")

        export_csv = tmp_path / "pets_export.csv"
        exported = db.data.export_table(export_csv, "Pets")
        print(f"Exported {exported} rows to {export_csv.name}")

        events = Collection("events")
        db.create_collection(events)

        json_file = tmp_path / "events.json"
        json_file.write_text(
            json.dumps(
                [
                    {"type": "login", "user": "diane"},
                    {"type": "purchase", "user": "benny", "amount": 42},
                ]
            ),
            encoding="utf-8",
        )
        doc_count = db.data.import_collection(json_file, "events", fmt=DataFormat.JSON)
        print(f"Imported {doc_count} documents from JSON")

        export_json = tmp_path / "events_export.jsonl"
        out = db.data.export_collection(export_json, "events", fmt=DataFormat.JSONL)
        print(f"Exported {out} documents to JSONL")
        print(export_json.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
