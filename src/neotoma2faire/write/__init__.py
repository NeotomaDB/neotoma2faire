"""Functions that take a DataFrame and write it into the FAIRe workbook.

Each module owns one FAIRe sheet.  All functions follow the signature
``add_<sheet>(wb, ...) -> None | DataFrame`` so the orchestrator
:func:`neotoma2faire.make_template.make_template` can call them uniformly.
"""
from .age_models import add_age_models
from .amp_data import add_amp_data
from .elow_quant import add_elow_quant
from .experiment_run import add_experiment_run
from .final_reads import add_final_reads
from .project import add_project
from .readme import modify_README
from .samples import add_samples
from .std_data import add_std_data
from .taxa import add_taxa

__all__ = [
    "add_age_models",
    "add_amp_data",
    "add_elow_quant",
    "add_experiment_run",
    "add_final_reads",
    "add_project",
    "add_samples",
    "add_std_data",
    "add_taxa",
    "modify_README",
]
