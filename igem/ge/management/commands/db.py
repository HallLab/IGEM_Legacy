"""
Process to maintain the content of the Igem Database

    $ python manage.py db --get_data {parameters}
    $ python manage.py db --sync_db {parameters}

    $ python manage.py db --get_data 'table="datasource"' # noqa E051
    $ python manage.py db --sync_db 'table="all", path="/root/back"' # noqa E051

"""
import os
import sys

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand
from ge.models import Term, WordTerm

try:
    x = str(settings.BASE_DIR)
    sys.path.append(x)
    from ge import db  # noqa F401
except:  # noqa E722
    raise


class Command(BaseCommand):
    help = "Process to maintain the content of the GE.db"

    def add_arguments(self, parser):
        parser.add_argument(
            "--get_data",
            type=str,
            metavar="parameters",
            action="store",
            default=None,
            help="Get data from GE.db",
        )

        parser.add_argument(
            "--sync_db",
            type=str,
            metavar="parameters",
            action="store",
            default=None,
            help="Sync IGEM DB",
        )

        parser.add_argument(
            "--load",
            type=str,
            metavar="table",
            action="store",
            default=None,
            help="Load CSV into a specific table (e.g., wordterm)",
        )

        parser.add_argument(
            "--path",
            type=str,
            metavar="csv_path",
            action="store",
            default=None,
            help="Path to the input CSV file used by --load",
        )

    def handle(self, *args, **options):
        # GET DATA
        if options["get_data"]:
            parameters = str(options["get_data"]).lower()
            self.stdout.write(self.style.SUCCESS("Get data from GE.db"))
            self.stdout.write(
                self.style.HTTP_REDIRECT(
                    f"  Informed parameters: {parameters}"
                )  # noqa E501
            )
            print()  # give a space
            # Run function
            try:
                df = {}
                exec("df = db.get_data(" + parameters + ")", globals(), df)  # noqa E501
                if (df["df"].__class__.__name__) == "DataFrame":
                    print(df["df"])
            except Exception as e:
                self.stdout.write(self.style.ERROR_OUTPUT(f"  {e}"))

        # SYNC IGEM DB in Client Version
        if options["sync_db"]:
            parameters = str(options["sync_db"]).lower()
            self.stdout.write(self.style.SUCCESS("Start of IGEM db synchronization for client version"))  # noqa E501
            self.stdout.write(
                self.style.HTTP_REDIRECT(
                    f"  Informed parameters: {parameters}"
                )  # noqa E501
            )
            print()  # give a space
            # Run function
            try:
                df = {}
                exec("df = db.sync_db(" + parameters + ")", globals(), df)  # noqa E501
                if (df["df"].__class__.__name__) == "DataFrame":
                    print(df["df"])
            except Exception as e:
                self.stdout.write(self.style.ERROR_OUTPUT(f"  {e}"))

        # LOAD BLOCK
        if options.get("load"):
            v_table = str(options["load"]).lower()
            v_path = options.get("path")  # do NOT lower() the path

            if not v_path:
                self.stdout.write(self.style.HTTP_BAD_REQUEST('  Inform the path to load'))
                sys.exit(2)
            if not os.path.isfile(v_path):
                self.stdout.write(self.style.HTTP_BAD_REQUEST('  File not found'))
                self.stdout.write(self.style.HTTP_BAD_REQUEST('  Inform the path and the file in CSV format to load'))
                sys.exit(2)

            if v_table == 'wordterm':
                # python manage.py db --load wordterm --path /path/seu_export.csv
                # python manage.py db --load wordterm  --path /Users/andrerico/Works/Projects/igem/nikki/genes_to_igem.csv 

                try:
                    DFR = pd.read_csv(v_path)

                    # Normalize column names
                    DFR.columns = [c.lower() for c in DFR.columns]

                    # Expected columns: word, status, commute, term_id
                    required_cols = {"word", "status", "commute", "term_id"}
                    missing = required_cols - set(DFR.columns)
                    if missing:
                        self.stdout.write(self.style.ERROR(f"  Missing columns: {sorted(list(missing))}"))
                        self.stdout.write(self.style.ERROR("  Expected: word,status,commute,term_id"))
                        sys.exit(2)

                    # Normalize word (string)
                    DFR["word"] = DFR["word"].astype(str).str.strip().str.lower()

                    # Normalize booleans (support 0/1, true/false, True/False)
                    def norm_bool_series(s):
                        s = s.astype(str).str.strip().str.lower()
                        return s.replace({
                            "true": "True",
                            "false": "False",
                            "1": "True",
                            "0": "False",
                        })

                    DFR["status"] = norm_bool_series(DFR["status"])
                    DFR["commute"] = norm_bool_series(DFR["commute"])
                    # DFR["status"] = DFR["status"].map({"True": True, "False": False})
                    # DFR["commute"] = DFR["commute"].map({"True": True, "False": False})

                    # print(DFR)

                    # term_id as int
                    DFR["term_id"] = DFR["term_id"].astype(int)

                except IOError as e:
                    self.stdout.write(self.style.ERROR("ERRO:"))
                    print(e)
                    sys.exit(2)
                except Exception as e:
                    self.stdout.write(self.style.ERROR("ERRO parsing CSV:"))
                    print(e)
                    sys.exit(2)

                # Validate: no nulls
                if DFR.isnull().values.any():
                    self.stdout.write(self.style.ERROR("  Null values detected. Check log file"))
                    DFR.to_csv(str(v_path + ".log"), index=False)
                    sys.exit(2)

                model_instances = [
                    WordTerm(
                        word=record.word,
                        term_id=record.term_id,
                        status=record.status,
                        commute=record.commute,
                    )
                    for record in DFR.itertuples(index=False)
                ]

                WordTerm.objects.bulk_create(model_instances, ignore_conflicts=True)
                self.stdout.write(self.style.SUCCESS("  Load with success to WordTerm"))

            elif v_table == "term":
                # Example:
                # python manage.py db --load term --path /path/terms.csv

                try:
                    # DFR = pd.read_csv(v_path)
                    DFR = pd.read_csv(v_path, encoding="utf-8")

                    # Normalize column names
                    DFR.columns = [c.lower() for c in DFR.columns]

                    # Expected columns
                    required_cols = {"term", "description", "term_category_id", "term_group_id"}
                    missing = required_cols - set(DFR.columns)
                    if missing:
                        self.stdout.write(self.style.ERROR(f"  Missing columns: {sorted(list(missing))}"))
                        self.stdout.write(self.style.ERROR("  Expected: term,description,term_category_id,term_group_id"))
                        sys.exit(2)

                    # Normalize strings
                    DFR["term"] = DFR["term"].astype(str).str.strip().str.lower()
                    DFR["description"] = DFR["description"].astype(str).str.strip()

                    # IDs as int
                    DFR["term_category_id"] = DFR["term_category_id"].astype(int)
                    DFR["term_group_id"] = DFR["term_group_id"].astype(int)

                except IOError as e:
                    self.stdout.write(self.style.ERROR("ERRO:"))
                    print(e)
                    sys.exit(2)
                except Exception as e:
                    self.stdout.write(self.style.ERROR("ERRO parsing CSV:"))
                    print(e)
                    sys.exit(2)

                # Validate: no nulls
                if DFR.isnull().values.any():
                    self.stdout.write(self.style.ERROR("  Null values detected. Check log file"))
                    DFR.to_csv(str(v_path + ".log"), index=False)
                    sys.exit(2)

                # Optional: remove empty terms
                DFR = DFR[DFR["term"].notnull() & (DFR["term"] != "")]

                model_instances = [
                    Term(
                        term=record.term,
                        description=record.description,
                        term_category_id=record.term_category_id,
                        term_group_id=record.term_group_id,
                    )
                    for record in DFR.itertuples(index=False)
                ]

                Term.objects.bulk_create(model_instances, ignore_conflicts=True, batch_size=5000)
                self.stdout.write(self.style.SUCCESS("  Load with success to Term"))

            else:
                self.stdout.write(self.style.HTTP_NOT_FOUND('Table not recognized in the system. Choose one of the options: '))
                self.stdout.write(self.style.HTTP_NOT_FOUND('   database | dataset | ds_column | keyge | category | group | prefix | keywords'))
