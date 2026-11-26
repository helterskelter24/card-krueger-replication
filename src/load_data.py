"""Read Card & Krueger's public.dat and build the analysis variables.

The raw file is the fixed-width ASCII file distributed on David Card's website
(njmin.zip). Missing values are coded as ".". Column order follows the codebook.
"""
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data" / "public.dat"

COLUMNS = (
    "sheet chain co_owned state southj centralj northj pa1 pa2 shore "
    # wave 1 (Feb-Mar 1992)
    "ncalls empft emppt nmgrs wage_st inctime firstinc bonus pctaff meals "
    "open hrsopen psoda pfry pentree nregs nregs11 "
    # wave 2 (Nov-Dec 1992)
    "type2 status2 date2 ncalls2 empft2 emppt2 nmgrs2 wage_st2 inctime2 "
    "firstin2 special2 meals2 open2r hrsopen2 psoda2 pfry2 pentree2 nregs2 nregs112"
).split()

CHAINS = {1: "bk", 2: "kfc", 3: "roys", 4: "wendys"}
NEW_MIN = 5.05  # NJ minimum wage from April 1, 1992


def fte(ft, pt, mgr, pt_weight=0.5, include_managers=True):
    """Full-time-equivalent employment: FT + managers + 0.5 * PT (Card-Krueger)."""
    out = ft + pt_weight * pt
    if include_managers:
        out = out + mgr
    return out


def load(path=DATA):
    df = pd.read_csv(path, sep=r"\s+", header=None, names=COLUMNS, na_values=".")
    assert len(df) == 410, "public.dat should have 410 stores"

    df["nj"] = df["state"]
    df["fte"] = fte(df.empft, df.emppt, df.nmgrs)
    df["fte2"] = fte(df.empft2, df.emppt2, df.nmgrs2)

    # Four stores were temporarily closed in wave 2 (renovation, road
    # construction, mall fire). The paper's base case leaves them missing;
    # one robustness check sets their wave-2 employment to zero.
    df["temp_closed"] = df.status2.isin([2, 4, 5]).astype(int)
    df["perm_closed"] = (df.status2 == 3).astype(int)
    df["fte2_tc0"] = np.where(df.temp_closed == 1, 0.0, df.fte2)

    df["dfte"] = df.fte2 - df.fte

    # Chain dummies (Burger King is the omitted group in regressions)
    for k, name in CHAINS.items():
        df[name] = (df.chain == k).astype(int)

    # Wage gap: proportional raise needed to reach $5.05 (0 for PA and for NJ
    # stores already paying at least $5.05).
    gap = (NEW_MIN - df.wage_st) / df.wage_st
    df["gap"] = np.where(df.nj == 0, 0.0, np.where(df.wage_st >= NEW_MIN, 0.0, gap))
    df.loc[df.wage_st.isna(), "gap"] = np.nan

    # NJ regions (southern NJ omitted) and PA regions (PA1 omitted)
    df["region"] = np.select(
        [df.southj == 1, df.centralj == 1, df.northj == 1, df.pa1 == 1, df.pa2 == 1],
        ["south_nj", "central_nj", "north_nj", "pa1", "pa2"],
        default="unknown",
    )
    return df


def balanced(df):
    """Table 4 sample: stores with employment and starting-wage data in both waves.

    Permanently closed stores have wave-2 employment of 0 and no wage, so the
    wage requirement is applied to wave 2 only for stores that are open.
    """
    ok = df.fte.notna() & df.fte2.notna() & df.wage_st.notna()
    ok &= df.wage_st2.notna() | (df.perm_closed == 1)
    return df[ok].copy()
