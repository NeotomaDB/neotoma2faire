"""Tests for neotoma2faire.extract.experiment_run."""

from unittest.mock import patch

import pandas as pd
import pytest

from neotoma2faire.extract.experiment_run import get_experiment_run


_LIB_ROW = {
    "samp_name": "Sample_1087",
    "lib_id": "LIB001",
    "seq_run_id": "RUN001",
    "assay_type": "metabarcoding",
    "target_gene": "18S rRNA",
    "subfragment": "V4",
    "pcr_primer_name_forward": "TAReuk454FWD1",
    "pcr_primer_name_reverse": "TAReukREV3",
    "lib_layout": "paired",
    "seq_meth": "Illumina MiSeq",
}


class TestGetExperimentRun:
    def test_returns_dataframe(self):
        with patch("neotoma2faire.extract.experiment_run.run_dataset_query",
                   return_value=pd.DataFrame([_LIB_ROW])):
            result = get_experiment_run(55582)
        assert isinstance(result, pd.DataFrame)

    def test_empty_when_no_rows(self):
        with patch("neotoma2faire.extract.experiment_run.run_dataset_query",
                   return_value=pd.DataFrame()):
            result = get_experiment_run(55582)
        assert result.empty

    def test_has_lib_id_column(self):
        with patch("neotoma2faire.extract.experiment_run.run_dataset_query",
                   return_value=pd.DataFrame([_LIB_ROW])):
            result = get_experiment_run(55582)
        assert "lib_id" in result.columns

    def test_has_assay_type_column(self):
        with patch("neotoma2faire.extract.experiment_run.run_dataset_query",
                   return_value=pd.DataFrame([_LIB_ROW])):
            result = get_experiment_run(55582)
        assert "assay_type" in result.columns

    def test_has_sequencing_columns(self):
        with patch("neotoma2faire.extract.experiment_run.run_dataset_query",
                   return_value=pd.DataFrame([_LIB_ROW])):
            result = get_experiment_run(55582)
        for col in ("target_gene", "subfragment", "pcr_primer_name_forward",
                    "pcr_primer_name_reverse", "lib_layout", "seq_meth"):
            assert col in result.columns

    def test_multiple_rows(self):
        rows = [dict(_LIB_ROW, lib_id=f"LIB00{i}") for i in range(1, 4)]
        with patch("neotoma2faire.extract.experiment_run.run_dataset_query",
                   return_value=pd.DataFrame(rows)):
            result = get_experiment_run(55582)
        assert len(result) == 3
