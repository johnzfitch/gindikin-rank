#!/usr/bin/env python3
"""es_figure.py — generate Etch & Sketch-styled figures from Python.

For when a model (or you) is already computing data in Python and wants a
figure that matches the kit's data register, to drop into a document with
``\\esincludefig{fig.pdf}{FIG. N}{caption}``.

Usage
-----
    from es_figure import es_style, es_save
    import matplotlib.pyplot as plt

    es_style()                       # apply the kit register (robust: no usetex)
    fig, ax = plt.subplots()
    ax.plot(xs, ys, label="cos s")
    ax.set_xlabel("s"); ax.set_ylabel(r"$\\kappa(s)$")
    ax.legend()
    es_save(fig, "fig.pdf")          # tight vector PDF sized for one column

Three registers, in increasing order of fidelity to the document:

    es_style()                 mathtext (default). Always runs, no LaTeX needed.
                               Prose is TeX Gyre Schola; MATH is matplotlib's
                               Computer Modern mathtext, which does NOT match the
                               document's Libertinus Math. Fine for a figure whose
                               labels are words and numbers.

    es_style(backend="pgf")    LuaLaTeX via the PGF backend, with the kit's own
                               font selection. Figure math is set in the SAME font
                               as the body, because it is set by the same engine.
                               This is the right register for a figure whose labels
                               carry real notation. Needs lualatex on PATH.

    es_style(usetex=True)      LaTeX via the usetex path. Legacy; needs cm-super
                               and tex-gyre installed. Prefer backend="pgf".

ONE THING THE FIGURE CANNOT INHERIT: the kit's inline-fraction policy. In the
body, ``\\tfrac{3}{2}`` sets as a case fraction; a figure label written
``$\\frac{3}{2}$`` stacks, even under backend="pgf", because the policy lives in
etch-math.sty and a figure preamble cannot load the whole document kit. Write
axis labels as ``$3/2$`` when the body has ``\\tfrac32`` beside them, or the same
value will appear in two different forms on one page.
"""
from __future__ import annotations
import os
import matplotlib as mpl
import matplotlib.pyplot as plt

# the kit palette (mirrors etch-and-sketch.mplstyle prop_cycle)
ES_PALETTE = ["#4A6E8A", "#C97D2C", "#4A6B4F", "#8C3A3A", "#6A7986", "#2C3E50"]
ES_PANEL = "#FAF7F0"
ES_GRID = "#E2E1DA"
ES_INK = "#2C3E50"
ES_GREY = "#6A7986"

_HERE = os.path.dirname(os.path.abspath(__file__))
_MPLSTYLE = os.path.join(_HERE, "etch-and-sketch.mplstyle")


# The kit's font selection, as a LaTeX preamble. It mirrors etch-math.sty
# section 1 exactly, including the Libertinus -> STIX Two -> Latin Modern math
# fallback chain, so a figure built through the PGF backend resolves the same
# faces the document does. Kept in sync by hand; it is nine lines, and the
# alternative (loading etch-math.sty itself) would drag geometry, hyperref and
# tcolorbox into a standalone figure.
ES_TEX_PREAMBLE = r"""
\usepackage{fontspec}
\usepackage[math-style=TeX]{unicode-math}
\setmainfont{TeX Gyre Schola}[Numbers={Lining,Proportional},Ligatures=TeX]
\IfFontExistsTF{Libertinus Math}
  {\setmathfont{Libertinus Math}[Scale=MatchUppercase]}
  {\IfFontExistsTF{STIX Two Math}
     {\setmathfont{STIX Two Math}[Scale=MatchUppercase]}
     {\setmathfont{Latin Modern Math}[Scale=MatchUppercase]}}
\pagestyle{empty}
"""


def es_style(usetex: bool = False, backend: str | None = None) -> None:
    """Apply the Etch & Sketch data register to matplotlib's rcParams.

    Prefers the bundled .mplstyle if present; otherwise sets an equivalent
    register inline.

    backend="pgf" switches to the LuaLaTeX PGF backend with the kit's font
    preamble, so figure MATH is set in the document's math font instead of
    matplotlib's Computer Modern mathtext. Without it, a figure carrying real
    notation is typographically foreign to the page it sits on -- the exact
    defect skills/matplotlib-figures/SKILL.md warns about, which the kit's own
    default used to cause.
    """
    if os.path.exists(_MPLSTYLE):
        try:
            plt.style.use(_MPLSTYLE)
        except Exception:
            _inline_style()
    else:
        _inline_style()

    if backend == "pgf":
        mpl.use("pgf")
        mpl.rcParams.update({
            "pgf.texsystem": "lualatex",
            "pgf.rcfonts": False,       # do not let matplotlib re-declare fonts
            "pgf.preamble": ES_TEX_PREAMBLE,
            "text.usetex": False,       # the PGF backend does its own TeX run
            "font.family": "serif",
        })
        return

    mpl.rcParams["text.usetex"] = bool(usetex)
    if not usetex:
        # mathtext: the closest match available without a TeX run. Note this is
        # Computer Modern math against a Libertinus Math body -- use
        # backend="pgf" when the labels carry notation.
        mpl.rcParams["mathtext.fontset"] = "cm"
        mpl.rcParams["font.family"] = "serif"


def _inline_style() -> None:
    mpl.rcParams.update({
        "font.family": "serif",
        "font.size": 9.0,
        "axes.labelsize": 9.0, "axes.titlesize": 10.0,
        "xtick.labelsize": 8.0, "ytick.labelsize": 8.0, "legend.fontsize": 8.0,
        "figure.figsize": (5.5, 3.4), "savefig.dpi": 300, "savefig.bbox": "tight",
        "savefig.format": "pdf", "savefig.facecolor": "white",
        "axes.prop_cycle": mpl.cycler(color=ES_PALETTE),
        "axes.facecolor": ES_PANEL, "axes.edgecolor": ES_GREY, "axes.linewidth": 0.6,
        "axes.grid": True, "axes.grid.axis": "y", "axes.axisbelow": True,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.labelcolor": ES_INK,
        "grid.color": ES_GRID, "grid.linewidth": 0.4, "grid.alpha": 0.8,
        "xtick.direction": "in", "ytick.direction": "in",
        "xtick.color": ES_GREY, "ytick.color": ES_GREY,
        "lines.linewidth": 1.4, "lines.markersize": 5.0,
        "legend.frameon": True, "legend.framealpha": 0.95,
        "legend.edgecolor": ES_GREY, "legend.facecolor": "white",
        "legend.fancybox": False,
    })


def es_save(fig, path: str, **kw) -> str:
    """Save a tight vector PDF sized for a single column. Returns the path."""
    kw.setdefault("bbox_inches", "tight")
    kw.setdefault("facecolor", "white")
    fig.savefig(path, **kw)
    return path


if __name__ == "__main__":
    # smoke test: produce a small demo figure
    import numpy as np
    es_style()
    xs = np.linspace(-3, 3, 200)
    fig, ax = plt.subplots(figsize=(5.0, 3.0))
    ax.plot(xs, np.cos(xs), label=r"$\cos s$")
    ax.plot(xs, np.sin(xs), label=r"$\sin s$")
    ax.plot(xs, xs / 2, label=r"$s/2$")
    ax.set_xlabel("s"); ax.set_ylabel(r"$\kappa(s)$")
    ax.legend(loc="upper left")
    es_save(fig, "es_demo_fig.pdf")
    print("wrote es_demo_fig.pdf")
