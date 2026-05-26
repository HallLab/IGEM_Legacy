"""
This command aims to access the functions of GE.FILTER and return searches
through the command line. Example:

    $ python manage.py filter --term_map {parameters}
    $ python manage.py filter --gene_exposome {parameters}
    $ python manage.py filter --snp_exposome {parameters}
    $ python manage.py filter --word_map {parameters}
    $ python manage.py filter --parameters_file {parameters}
    $ python manage.py filter --word_to_term {parameters}

    $ python manage.py filter --term_map 'term=["gene:246126"], path_out="result.csv"' # noqa E051
"""

import os
import re
import sys

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand

try:
    x = str(settings.BASE_DIR)
    sys.path.append(x)
    from ge import filter  # noqa F401
except:  # noqa E722
    raise

from ge.filter import positions_to_term


def _extract_path_in(parameters: str) -> str:
    m = re.search(r"path_in\s*=\s*['\"]([^'\"]+)['\"]", parameters)
    if not m:
        raise ValueError("Missing required parameter: path_in='...'")
    return m.group(1)

def _read_parameters_file(path_in: str) -> pd.DataFrame:
    dfp = pd.read_csv(path_in)
    dfp.columns = [c.strip().lower() for c in dfp.columns]
    required = {"index", "parameter", "value"}
    if not required.issubset(set(dfp.columns)):
        raise ValueError(f"Parameters file must have columns: {sorted(required)}")
    return dfp

def _get_input_terms(dfp: pd.DataFrame) -> set[str]:
    terms = dfp[
        (dfp["index"].astype(str).str.lower() == "filter") &
        (dfp["parameter"].astype(str).str.lower() == "term")
    ]["value"].astype(str).str.strip().tolist()
    return set(t for t in terms if t)

def _get_path_out(dfp: pd.DataFrame) -> str:
    # Expect: index=path, parameter=path, value=/.../out.csv
    rows = dfp[
        (dfp["index"].astype(str).str.lower() == "path") &
        (dfp["parameter"].astype(str).str.lower() == "path")
    ]["value"].astype(str).str.strip().tolist()
    if not rows:
        raise ValueError("Could not find path_out in parameters file (row: index=path, parameter=path)")
    return rows[0]

def _pick_col(df: pd.DataFrame, candidates: list[str]) -> str:
    for c in candidates:
        if c in df.columns:
            return c
    raise ValueError(f"Could not find any candidate columns: {candidates}. Available: {list(df.columns)}")




class Command(BaseCommand):
    help = "This command aims to access the functions of GE.FILTER \
            through the command line"

    def add_arguments(self, parser):
        parser.add_argument(
            "--term_map",
            type=str,
            metavar="parameters",
            action="store",
            default=None,
            help="returns data from TermMap",
        )
        parser.add_argument(
            "--gene_exposome",
            type=str,
            metavar="parameters",
            action="store",
            default=None,
            help="returns TermMap in Gene layout",
        )
        parser.add_argument(
            "--snp_exposome",
            type=str,
            metavar="parameters",
            action="store",
            default=None,
            help="returns TermMap in SNP layout",
        )
        parser.add_argument(
            "--word_map",
            type=str,
            metavar="parameters",
            action="store",
            default=None,
            help="returns data from WordMap",
        )
        parser.add_argument(
            "--parameters_file",
            type=str,
            metavar="parameters",
            action="store",
            default=None,
            help="create a parameters file",
        )
        parser.add_argument(
            "--word_to_term",
            type=str,
            metavar="parameters",
            action="store",
            default=None,
            help="convert words in terms",
        )

        # Function to get position to list of terms map
        parser.add_argument(
            "--positions_to_term_map",
            type=str,
            metavar="parameters",
            action="store",
            default=None,
            help="convert position in terms map",
        )
        parser.add_argument(
            '--exposome',
            type=str,
            metavar="parameters",
            action="store",
            default=None,
            help="convert position in terms map"
            )
        parser.add_argument('--assembly', type=int, default=38)
        parser.add_argument('--boundaries', type=int, default=10000)
        parser.add_argument('--delimiter', default=None)
        parser.add_argument('--has_header', default=True)

        parser.add_argument(
            "--term_map_internal",
            type=str,
            metavar="parameters",
            action="store",
            default=None,
            help="returns only relationships where BOTH terms are in the input term list (induced subgraph)",
        )

    def handle(self, *args, **options):
        # POSITION TO TERMS MAP
        if options["positions_to_term_map"]:
            # python manage.py filter --position_to_term_map input_file.txt --assembly=38 --search_range=10000 # noqa E501
            input_file = options['positions_to_term_map']
            exposome = options['exposome']
            assembly = options['assembly']
            boundaries = options['boundaries']
            delimiter = options['delimiter']
            has_header = options['has_header']

            # Call Operation Function
            self.stdout.write(self.style.SUCCESS("Run Terms Report from Genomic Positions")) # noqa E501
            try:
                return_function = positions_to_term(
                    input_file,
                    exposome,
                    assembly,
                    boundaries,
                    delimiter,
                    has_header
                    )
                if return_function:
                    self.stdout.write(self.style.SUCCESS(
                        "Process completed successfully"
                        ))
                else:
                    self.stdout.write(self.style.ERROR_OUTPUT(
                        "Process completed with error!"
                        ))
            except Exception as e:
                self.stdout.write(self.style.ERROR_OUTPUT(f"  {e}"))

        # TERM_MAP
        if options["term_map"]:
            parameters = str(options["term_map"]).lower()
            self.stdout.write(self.style.SUCCESS("Run term_map Report"))
            self.stdout.write(
                self.style.HTTP_REDIRECT(
                    f"  Informed parameters: {parameters}"
                )  # noqa E501
            )
            print()  # give a space
            # Run function
            try:
                df = {}
                exec(
                    "df = filter.term_map(" + parameters + ")", globals(), df
                )  # noqa E501
                if (df["df"].__class__.__name__) == "DataFrame":
                    print(df["df"])

            except Exception as e:
                self.stdout.write(self.style.ERROR_OUTPUT(f"  {e}"))

        # GENE_EXPOSOME
        if options["gene_exposome"]:
            parameters = str(options["gene_exposome"]).lower()
            self.stdout.write(self.style.SUCCESS("Run gene_exposome report"))
            self.stdout.write(
                self.style.HTTP_REDIRECT(
                    f"  Informed parameters: {parameters}"
                )  # noqa E501
            )
            print()  # give a space
            # Run function
            try:
                df = {}
                exec(
                    "df = filter.gene_exposome(" + parameters + ")",
                    globals(),
                    df,  # noqa E501
                )  # noqa E501
                if (df["df"].__class__.__name__) == "DataFrame":
                    print(df["df"])

            except Exception as e:
                self.stdout.write(self.style.ERROR_OUTPUT(f"  {e}"))

        # SNP_EXPOSOME
        if options["snp_exposome"]:
            parameters = str(options["snp_exposome"]).lower()
            self.stdout.write(self.style.SUCCESS("Run snp_exposome report"))
            self.stdout.write(
                self.style.HTTP_REDIRECT(
                    f"  Informed parameters: {parameters}"
                )  # noqa E501
            )
            print()  # give a space
            # Run function
            try:
                df = {}
                exec(
                    "df = filter.snp_exposome(" + parameters + ")",
                    globals(),
                    df,  # noqa E501
                )  # noqa E501
                if (df["df"].__class__.__name__) == "DataFrame":
                    print(df["df"])

            except Exception as e:
                self.stdout.write(self.style.ERROR_OUTPUT(f"  {e}"))

        # WORD_MAP
        if options["word_map"]:
            parameters = str(options["word_map"]).lower()
            self.stdout.write(self.style.SUCCESS("Run word_map report"))
            self.stdout.write(
                self.style.HTTP_REDIRECT(
                    f"  Informed parameters: {parameters}"
                )  # noqa E501
            )
            print()  # give a space
            # Run function
            try:
                df = {}
                exec(
                    "df = filter.word_map(" + parameters + ")", globals(), df
                )  # noqa E501
                if (df["df"].__class__.__name__) == "DataFrame":
                    print(df["df"])

            except Exception as e:
                self.stdout.write(self.style.ERROR_OUTPUT(f"  {e}"))

        # Parameters File
        if options["parameters_file"]:
            parameters = str(options["parameters_file"]).lower()
            self.stdout.write(self.style.SUCCESS("Create a Parameters File"))
            self.stdout.write(
                self.style.HTTP_REDIRECT(
                    f"  Informed parameters: {parameters}"
                )  # noqa E501
            )
            print()  # give a space
            # Run function
            try:
                df = {}
                exec(
                    "df = filter.parameters_file(" + parameters + ")",
                    globals(),
                    df,  # noqa E501
                )  # noqa E501
                if (df["df"].__class__.__name__) == "DataFrame":
                    print(df["df"])

            except Exception as e:
                self.stdout.write(self.style.ERROR_OUTPUT(f"  {e}"))

        # word_to_term
        if options["word_to_term"]:
            parameters = str(options["word_to_term"]).lower()
            self.stdout.write(
                self.style.SUCCESS("Run the word to term converter")
            )  # noqa E501
            self.stdout.write(
                self.style.HTTP_REDIRECT(
                    f"  Informed parameters: {parameters}"
                )  # noqa E501
            )
            print()  # give a space
            # Run function
            try:
                df = {}
                exec(
                    "df = filter.word_to_term(" + parameters + ")",
                    globals(),
                    df,  # noqa E501
                )  # noqa E501
                if (df["df"].__class__.__name__) == "DataFrame":
                    print(df["df"])

            except Exception as e:
                self.stdout.write(self.style.ERROR_OUTPUT(f"  {e}"))

        if options["term_map_internal"]:
            parameters = str(options["term_map_internal"])  # DO NOT .lower() (paths!)
            self.stdout.write(self.style.SUCCESS("Run term_map_internal (induced subgraph)"))
            self.stdout.write(self.style.HTTP_REDIRECT(f"  Informed parameters: {parameters}"))
            print()

            try:
                path_in = _extract_path_in(parameters)
                dfp = _read_parameters_file(path_in)

                input_terms = _get_input_terms(dfp)
                path_out = _get_path_out(dfp)

                # 1) Run the normal term_map (it writes to path_out)
                ctx = {}
                exec("df = filter.term_map(" + parameters + ")", globals(), ctx)

                # 2) Load the produced CSV and filter it
                if not os.path.isfile(path_out):
                    raise FileNotFoundError(f"term_map output file not found: {path_out}")

                df_full = pd.read_csv(path_out)

                col_t1 = _pick_col(df_full, ["term_1", "term_1_id", "term1", "term1_id"])
                col_t2 = _pick_col(df_full, ["term_2", "term_2_id", "term2", "term2_id"])

                s1 = df_full[col_t1].astype(str).str.strip()
                s2 = df_full[col_t2].astype(str).str.strip()

                df_internal = df_full[s1.isin(input_terms) & s2.isin(input_terms)].copy()

                # 3) Save internal output next to path_out
                base, ext = os.path.splitext(path_out)
                out_internal = f"{base}_internal{ext or '.csv'}"
                df_internal.to_csv(out_internal, index=False)

                self.stdout.write(self.style.SUCCESS(f"✅ Internal term_map saved to: {out_internal}"))
                self.stdout.write(self.style.SUCCESS(f"   Rows full: {len(df_full):,} | internal: {len(df_internal):,}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR_OUTPUT(f"  {e}"))