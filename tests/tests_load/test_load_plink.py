import pytest
from igem.load import load_plink
from pathlib import Path


def test_load_plink_data_structure():
    # Path to the test data files
    data_dir = Path(__file__).parent / "data"
    prefix = data_dir / "genomics_xyz"

    bed = prefix.with_suffix(".bed")
    bim = prefix.with_suffix(".bim")
    fam = prefix.with_suffix(".fam")

    if not (bed.exists() and bim.exists() and fam.exists()):
        pytest.skip("Arquivos PLINK de teste não estão disponíveis.")

    # Load data
    G = load_plink(str(bed), str(bim), str(fam))

    # Basic checks for the loaded data structure
    assert G.ndim == 2
    assert set(G.dims) == {"sample", "variant"}

    # Test if the data is numeric
    variant_id = "variant5"
    sample_id = "1"
    assert (G.sel(sample=sample_id, variant=variant_id).values) == 1.0
    assert (G.a0.sel(variant=variant_id).values) == "A"
    assert len(G.sel(variant=variant_id).values) == 3061
