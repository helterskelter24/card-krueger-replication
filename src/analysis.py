"""Replicate Card & Krueger (1994), Tables 3, 4 and the Table 5 robustness checks.

Run from the repository root:
    python src/analysis.py
Writes CSV and Markdown tables to output/.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from load_data import balanced, fte, load

OUT = Path(__file__).resolve().parents[1] / "output"
OUT.mkdir(exist_ok=True)

CONTROLS = "kfc + roys + wendys + co_owned"            # chain + ownership
REGIONS = "centralj + northj + pa1 + pa2"              # southern NJ omitted


def mean_se(x):
    x = x.dropna()
    return x.mean(), x.std(ddof=1) / np.sqrt(len(x)), len(x)


def change_se(g, before, after):
    """Mean change in a column pair and its standard error.

    Uses every store with data in each wave (unbalanced means), and gets the
    standard error of the difference allowing for the within-store covariance
    among stores observed in both waves, as in the paper's Table 3 row 3.
    """
    a, b = g[before], g[after]
    ma, sa, na = mean_se(a)
    mb, sb, nb = mean_se(b)
    both = a.notna() & b.notna()
    cov = np.cov(a[both], b[both], ddof=1)[0, 1] * both.sum() / (na * nb)
    return mb - ma, np.sqrt(sa**2 + sb**2 - 2 * cov)


def table3(df):
    rows = []
    pa, nj = df[df.nj == 0], df[df.nj == 1]

    def add(label, m_pa, s_pa, m_nj, s_nj, diff=None, sdiff=None):
        if diff is None:
            diff, sdiff = m_nj - m_pa, np.sqrt(s_pa**2 + s_nj**2)
        rows.append(dict(row=label, PA=m_pa, PA_se=s_pa, NJ=m_nj, NJ_se=s_nj,
                         NJ_minus_PA=diff, diff_se=sdiff))

    for label, col in [("1. FTE before", "fte"), ("2. FTE after", "fte2")]:
        m0, s0, _ = mean_se(pa[col]); m1, s1, _ = mean_se(nj[col])
        add(label, m0, s0, m1, s1)

    c0, e0 = change_se(pa, "fte", "fte2")
    c1, e1 = change_se(nj, "fte", "fte2")
    add("3. Change in mean FTE", c0, e0, c1, e1)

    bal = df[df.fte.notna() & df.fte2.notna()]
    m0, s0, _ = mean_se(bal[bal.nj == 0].dfte); m1, s1, _ = mean_se(bal[bal.nj == 1].dfte)
    add("4. Change in mean FTE, balanced sample", m0, s0, m1, s1)

    tc = df.assign(d=df.fte2_tc0 - df.fte).dropna(subset=["d"])
    m0, s0, _ = mean_se(tc[tc.nj == 0].d); m1, s1, _ = mean_se(tc[tc.nj == 1].d)
    add("5. Change, temporarily closed stores = 0", m0, s0, m1, s1)

    t = pd.DataFrame(rows)
    t["t_stat"] = t.NJ_minus_PA / t.diff_se
    t["paper_PA"], t["paper_NJ"], t["paper_diff"] = zip(*t.row.map(PAPER_T3))
    return t


def did_regression(df):
    """Same 2x2 DiD as a stacked panel regression: FTE_it = a + b NJ + c Post + d NJ*Post."""
    long = pd.concat([
        df[["sheet", "nj", "fte"]].assign(post=0),
        df[["sheet", "nj", "fte2"]].rename(columns={"fte2": "fte"}).assign(post=1),
    ]).dropna(subset=["fte"])
    m = smf.ols("fte ~ nj * post", long)
    out = {}
    for name, fit in {
        "conventional": m.fit(),
        "HC1 robust": m.fit(cov_type="HC1"),
        "clustered by store": m.fit(cov_type="cluster", cov_kwds={"groups": long.sheet}),
    }.items():
        out[name] = (fit.params["nj:post"], fit.bse["nj:post"], fit.tvalues["nj:post"])
    return pd.DataFrame(out, index=["estimate", "se", "t"]).T


PAPER_T4 = {"(i)": 2.33, "(ii)": 2.30, "(iii)": 15.65, "(iv)": 14.92, "(v)": 11.91}


def table4(b, cov="nonrobust"):
    specs = {
        "(i)":   ("nj", ""),
        "(ii)":  ("nj", CONTROLS),
        "(iii)": ("gap", ""),
        "(iv)":  ("gap", CONTROLS),
        "(v)":   ("gap", CONTROLS + " + " + REGIONS),
    }
    rows = []
    for col, (x, ctrl) in specs.items():
        f = f"dfte ~ {x}" + (f" + {ctrl}" if ctrl else "")
        r = smf.ols(f, b).fit(cov_type=cov)
        rows.append(dict(spec=col, regressor=x, coef=r.params[x], se=r.bse[x],
                         t=r.tvalues[x], controls=ctrl or "none", n=int(r.nobs),
                         se_regression=np.sqrt(r.scale), paper_coef=PAPER_T4[col]))
    return pd.DataFrame(rows)


PAPER_T3 = {  # Card & Krueger (1994) Table 3, columns (i)-(iii): (PA, NJ, NJ-PA)
    "1. FTE before": (23.33, 20.44, -2.89),
    "2. FTE after": (21.17, 21.03, -0.14),
    "3. Change in mean FTE": (-2.16, 0.59, 2.76),
    "4. Change in mean FTE, balanced sample": (-2.28, 0.47, 2.75),
    "5. Change, temporarily closed stores = 0": (-2.28, 0.23, 2.51),
}

PAPER_T5 = {  # Table 5: (NJ level, GAP level, NJ proportional, GAP proportional)
    1: (2.30, 14.92, 0.05, 0.34), 2: (2.20, 14.42, 0.04, 0.34),
    3: (2.34, 14.69, 0.05, 0.28), 4: (2.34, 15.23, 0.06, 0.30),
    5: (2.27, 14.60, 0.04, 0.17), 6: (2.58, 16.88, 0.06, 0.42),
    7: (2.27, 15.79, 0.05, 0.40), 8: (2.41, 14.08, 0.05, 0.31),
    9: (None, None, 0.13, 0.81), 12: (None, -0.30, None, -0.33),
}


def prop_change(e1, e2, perm_closed):
    """Change in employment divided by average employment in the two waves;
    set to -1 for permanently closed stores (paper footnote 18)."""
    return np.where(perm_closed == 1, -1.0, (e2 - e1) / ((e1 + e2) / 2))


def robustness(df):
    """Replicate Table 5: specification tests of the reduced-form models.

    Every model includes chain dummies and a company-owned dummy. Columns are
    the NJ-dummy and GAP coefficients for the level change in FTE, then the same
    for the proportional change in FTE.
    """
    def run(d, label, row, extra="", weighted=False, regressors=("nj", "gap"),
            levels=True):
        out = {"row": row, "spec": label}
        for x in ("nj", "gap"):
            for kind, y in (("level", "dfte"), ("prop", "pchg")):
                key = f"{x}_{kind}"
                if x not in regressors or (kind == "level" and not levels):
                    out[key], out[key + "_se"] = np.nan, np.nan
                    continue
                f = f"{y} ~ {x} + {CONTROLS}{extra}"
                m = smf.wls(f, d, weights=d.fte) if weighted else smf.ols(f, d)
                r = m.fit()
                out[key], out[key + "_se"] = r.params[x], r.bse[x]
                out["n"] = int(r.nobs)
        paper = PAPER_T5.get(row)
        if paper:
            for k, v in zip(["paper_nj_level", "paper_gap_level", "paper_nj_prop", "paper_gap_prop"], paper):
                out[k] = v
        return out

    def with_fte(d, **kw):
        d = d.copy()
        e1 = fte(d.empft, d.emppt, d.nmgrs, **kw)
        e2 = fte(d.empft2, d.emppt2, d.nmgrs2, **kw)
        d["dfte"] = e2 - e1
        d["pchg"] = prop_change(e1, e2, d.perm_closed)
        return d

    base = with_fte(balanced(df))
    rows = [run(base, "Base specification", 1)]

    # 2. Temporarily closed stores: wave-2 employment set to 0 (adds 4 stores)
    d = df.loc[balanced(df).index.union(df.index[df.temp_closed == 1])].copy()
    d["perm_closed"] = d.perm_closed | d.temp_closed
    d[["empft2", "emppt2", "nmgrs2"]] = d[["empft2", "emppt2", "nmgrs2"]].where(d.temp_closed == 0, 0.0)
    rows.append(run(with_fte(d), "Treat 4 temporarily closed stores as closed", 2))

    rows.append(run(with_fte(balanced(df), include_managers=False), "Exclude managers from FTE", 3))
    rows.append(run(with_fte(balanced(df), pt_weight=0.4), "Part-time = 0.4 x full-time", 4))
    rows.append(run(with_fte(balanced(df), pt_weight=0.6), "Part-time = 0.6 x full-time", 5))
    rows.append(run(base[base.shore == 0], "Exclude NJ shore stores", 6))

    # 7. Week of wave-2 interview (Sun-Sat weeks of Nov 1992; Dec grouped).
    # One date is coded 111191, an obvious typo for 111192.
    ds = base.date2.astype("Int64").astype(str).str.zfill(6).str.replace(r"91$", "92", regex=True)
    dt = pd.to_datetime(ds, format="%m%d%y", errors="coerce")
    d = base.assign(week2=np.select(
        [dt.dt.month == 12, dt.dt.day <= 7, dt.dt.day <= 14], ["dec", "w1", "w2"], "w3"))
    rows.append(run(d, "Add wave-2 interview-week dummies", 7, extra=" + C(week2)"))

    rows.append(run(base[base.ncalls < 3], "Exclude stores called back 3+ times in wave 1", 8))
    rows.append(run(base, "Weight by wave-1 employment (WLS)", 9, weighted=True, levels=False))

    # 12. Placebo: PA stores only, with a GAP defined as if PA had a $5.05 minimum
    pa = base[base.nj == 0].copy()
    pa["gap"] = np.clip((5.05 - pa.wage_st) / pa.wage_st, 0, None)
    rows.append(run(pa, "Placebo: PA stores only, GAP to $5.05", 12, regressors=("gap",)))

    # Extra (not in the paper): region dummies added to the NJ-dummy model
    rows.append(run(base, "Extra: add NJ region dummies (south NJ omitted)", 13,
                    extra=" + centralj + northj"))
    # Extra: GAP identified only from variation within New Jersey
    rows.append(run(base[base.nj == 1], "Extra: NJ stores only", 14, regressors=("gap",)))

    cols = ["row", "spec", "n",
            "nj_level", "nj_level_se", "paper_nj_level", "gap_level", "gap_level_se", "paper_gap_level",
            "nj_prop", "nj_prop_se", "paper_nj_prop", "gap_prop", "gap_prop_se", "paper_gap_prop"]
    return pd.DataFrame(rows).reindex(columns=cols)


def wages(df):
    """Starting-wage check: the policy actually bit in NJ (paper Table 2 / Figure 1)."""
    rows = []
    for state, g in df.groupby("nj"):
        rows.append(dict(
            state="NJ" if state else "PA",
            wage_before=g.wage_st.mean(), wage_after=g.wage_st2.mean(),
            share_below_505_before=(g.wage_st.dropna() < 5.05).mean(),
            share_at_505_after=(g.wage_st2.dropna().round(2) == 5.05).mean(),
        ))
    return pd.DataFrame(rows)


def format_t5(t5):
    def cell(r, key, digits):
        if pd.isna(r[key]):
            return "-"
        txt = f"{r[key]:.{digits}f} ({r[key + '_se']:.{digits}f})"
        p = r.get("paper_" + key)
        return txt + (f" [{p:.{digits}f}]" if pd.notna(p) else "")
    out = pd.DataFrame({
        "row": t5.row, "specification": t5.spec, "n": t5.n,
        "NJ dummy, level": [cell(r, "nj_level", 2) for _, r in t5.iterrows()],
        "GAP, level": [cell(r, "gap_level", 2) for _, r in t5.iterrows()],
        "NJ dummy, prop": [cell(r, "nj_prop", 3) for _, r in t5.iterrows()],
        "GAP, prop": [cell(r, "gap_prop", 2) for _, r in t5.iterrows()],
    })
    return out.to_markdown(index=False)


def to_md(df, floatfmt=".2f"):
    return df.to_markdown(index=False, floatfmt=floatfmt)


def main():
    df = load()
    b = balanced(df)

    t3 = table3(df)
    reg = did_regression(df)
    t4 = table4(b)
    t4r = table4(b, cov="HC1")
    t5 = robustness(df)
    w = wages(df)

    t3.to_csv(OUT / "table3_did_means.csv", index=False)
    reg.to_csv(OUT / "did_regression.csv")
    t4.to_csv(OUT / "table4_regressions.csv", index=False)
    t4r.to_csv(OUT / "table4_regressions_hc1.csv", index=False)
    t5.to_csv(OUT / "table5_robustness.csv", index=False)
    w.to_csv(OUT / "wages.csv", index=False)

    headline = t3.iloc[2]
    md = [
        "# Results\n",
        f"Headline DiD (Table 3, row 3): **{headline.NJ_minus_PA:+.2f} FTE** "
        f"(SE {headline.diff_se:.2f}, t = {headline.t_stat:.2f}); "
        f"that is {headline.NJ_minus_PA / t3.iloc[0].NJ:.1%} of NJ's pre-period mean FTE.\n",
        "## Table 3: mean FTE employment by state and wave\n", to_md(t3),
        "\n## 2x2 DiD as a stacked regression (all stores with data in a wave)\n",
        reg.reset_index().rename(columns={"index": "standard errors"}).to_markdown(index=False, floatfmt=".2f"),
        "\n## Table 4: regression-adjusted DiD (dependent variable: change in FTE, balanced sample)\n",
        "Conventional OLS standard errors, as in the paper:\n", to_md(t4.drop(columns="controls")),
        "\nControls: (ii), (iv): chain dummies (KFC, Roy Rogers, Wendy's; Burger King omitted) and "
        "company-owned dummy. (v) adds region dummies (central NJ, north NJ, PA1, PA2; south NJ omitted).\n",
        "\nSame regressions with HC1 robust standard errors:\n", to_md(t4r.drop(columns="controls")),
        "\n## Table 5: specification tests (chain and ownership controls in every model)\n",
        "Each cell: our estimate (standard error) [paper's estimate]. Level = change in FTE; "
        "prop = change in FTE divided by average FTE across the two waves (closed stores = -1).\n",
        format_t5(t5),
        "\n## Starting wages\n", to_md(w, ".3f"),
    ]
    (OUT / "results.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
