from pathlib import Path

# import igem
import igem
import pandas as pd

TESTS_PATH = Path(__file__).parent.parent
DATA_PATH = TESTS_PATH / "data_files"
RESULT_PATH = TESTS_PATH / "r_test_output" / "interactions"


def test_exe_pairwire():

    # def main():
    # Read NHANES Main Table
    df_maintable = igem.load.from_csv(
        str(DATA_PATH / "nhanes_data_sample.csv")  # noqa E501
    )

    # list of Outcomes
    list_outcome = [
        "LBXHGB",
    ]

    # list of Covariates
    list_covariant = [
        "female",
        "black",
        "mexican",
        "other_hispanic",
        "other_eth",
        "SES_LEVEL",
    ]

    # result = epc.analyze.exe_teste()
    result = igem.analyze.exe_pairwise(
        df_maintable,
        list_outcome,
        list_covariant,
        report_betas=False,
        process_num=4,
    )
    n_result = round(result["LRT_pvalue"].sum(), 10)

    # Load pre-process result
    r_test = pd.read_csv(str(RESULT_PATH / "exe_pairwise.csv"))
    n_test = round(r_test["LRT_pvalue"].sum(), 10)

    print(result)
    assert n_test == n_result

    # # if __name__ == '__main__':
    # if __name__ == "IGEM_SandBox.igem.epc.tests.test_analyze.test_exe_pairwise":  # noqa E501
    #     main()
