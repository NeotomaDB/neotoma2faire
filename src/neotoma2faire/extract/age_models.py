"""Build the age-depth table for the ``ageModels`` sheet.

``ageModels`` is not part of the FAIRe checklist — it is the extra sheet the
Okoboji workbook carries to describe the core's chronology, one row per sample.

Everything it needs is already in the :func:`~.data.get_data` frame: the
sample columns (``samp_name``, ``depth``, ``thickness``, ``analysisunitname``),
the chronology columns (``agemodel``, ``modelagetype``, ``age``), and the
sedimentation rate — which Neotoma stores as an ordinary datum
(``variablename == "Sedimentation rate"``, taxon group "Laboratory analyses")
rather than as part of the chronology.

The age column is named after the chronology it came from, ``agemodel(agetype)``
— e.g. ``CRS(Calendar years BP)`` — mirroring Okoboji's ``CRS(CalendarYear)``.
Datasets without a chronology still get the sheet: the age column is headed
``Age`` and left blank, while depths and thicknesses are written as usual.
"""

import pandas as pd

from ..utils import sort_samples

#: Neotoma variable name that carries the sedimentation rate datum.
SED_RATE_VARIABLE = "Sedimentation rate"

#: Column header used when the dataset has no chronology to name the ages after.
DEFAULT_AGE_COLUMN = "Age"

# get_data() column -> ageModels column.  The age column is inserted separately
# because its header depends on the chronology.
_RENAMES = {
    "samp_name": "Sample",
    "analysisunitname": "SampleInterval(cm)",
    "depth": "PlotDepth(cm)",
    "thickness": "Thickness(cm)",
    "agemodel": "AgeModel",
    "modelagetype": "AgeType",
}


def _age_column_name(df: pd.DataFrame) -> str:
    """Name the age column after the chronology, as ``agemodel(agetype)``."""
    def first(column):
        if column not in df.columns:
            return None
        values = df[column].dropna()
        return values.iloc[0] if not values.empty else None

    agemodel, agetype = first("agemodel"), first("modelagetype")
    if agemodel and agetype:
        return f"{agemodel}({agetype})"
    return agemodel or agetype or DEFAULT_AGE_COLUMN


def get_age_models(df: pd.DataFrame) -> pd.DataFrame:
    """Build the ``ageModels`` table from a :func:`~.data.get_data` frame.

    Deduplicates *df* to one row per ``sampleid`` (the same approach as
    :func:`~.sample_metadata.get_sample_metadata`) and merges in each sample's
    sedimentation-rate datum.  Columns missing from *df* are emitted blank
    rather than raising, so datasets that record no depths or no chronology
    still produce a usable sheet.

    Args:
        df (pandas.DataFrame): Long-format frame from :func:`~.data.get_data`
            (one row per sample × datum).

    Returns:
        pandas.DataFrame: One row per sample with the columns ``Sample``,
        ``<agemodel>(<agetype>)``, ``SampleInterval(cm)``, ``PlotDepth(cm)``,
        ``Thickness(cm)``, ``SedimentationRate(cm-yr)``, ``AgeModel``,
        ``AgeType``, ``SedRateUnits``.
    """
    age_column = _age_column_name(df)
    columns = [
        "Sample",
        age_column,
        "SampleInterval(cm)",
        "PlotDepth(cm)",
        "Thickness(cm)",
        "SedimentationRate(cm-yr)",
        "AgeModel",
        "AgeType",
        "SedRateUnits",
    ]
    if df.empty:
        return pd.DataFrame(columns=columns)

    out = df.drop_duplicates(subset=["sampleid"]).reset_index(drop=True)
    out = out.rename(columns=_RENAMES)
    out[age_column] = out["age"] if "age" in out.columns else None

    # Sedimentation rate lives in the datum rows, one per sample at most.
    if "variablename" in df.columns:
        rates = df[df["variablename"] == SED_RATE_VARIABLE].drop_duplicates(subset=["sampleid"])
        rates = rates[["sampleid", "value", "units"]].rename(
            columns={"value": "SedimentationRate(cm-yr)", "units": "SedRateUnits"}
        )
        out = out.merge(rates, on="sampleid", how="left")

    for column in columns:
        if column not in out.columns:
            out[column] = None
    # Same order as every other sheet; the columns are already renamed by here.
    return sort_samples(out[columns], name_col="Sample", depth_col="PlotDepth(cm)")
