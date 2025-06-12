from pathlib import Path
from igem.load import from_csv, from_tsv


TESTS_PATH = Path(__file__).parent.parent
DATA_PATH = TESTS_PATH / "data_files"


def test_load_from_csv():
    df = from_csv(DATA_PATH / "load_one_row.csv", index_col=None)
    assert len(df) == 1


def test_load_from_tsv():
    df = from_tsv(DATA_PATH / "load_one_row.tsv", index_col=None)
    assert len(df) == 1
