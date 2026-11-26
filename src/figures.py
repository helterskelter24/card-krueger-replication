"""Figure 1 of the paper: distribution of starting wages in NJ and PA, before and after."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from load_data import load

OUT = Path(__file__).resolve().parents[1] / "output"


def main():
    df = load()
    bins = np.arange(4.25, 5.65, 0.10)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
    for ax, col, title in [(axes[0], "wage_st", "February 1992 (before)"),
                           (axes[1], "wage_st2", "November 1992 (after)")]:
        for state, label, color in [(1, "New Jersey", "#2f6db5"), (0, "Pennsylvania", "#d9822b")]:
            w = df.loc[df.nj == state, col].dropna().clip(upper=5.55)
            ax.hist(w, bins=bins, weights=np.full(len(w), 100 / len(w)), alpha=0.65,
                    label=f"{label} (n={len(w)})", color=color, edgecolor="white")
        ax.axvline(5.05, color="black", lw=1, ls="--")
        ax.set_title(title)
        ax.set_xlabel("Starting wage ($/hour)")
    axes[0].set_ylabel("Percent of stores")
    axes[0].legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "fig1_starting_wages.png", dpi=150)


if __name__ == "__main__":
    main()
