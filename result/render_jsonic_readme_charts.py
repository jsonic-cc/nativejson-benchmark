#!/usr/bin/env python3
"""Render the same-run Jsonic++/RapidJSON charts embedded in README.md."""

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "result"
SAMPLE = ROOT / "sample"
PERFORMANCE_CSV = RESULT / "performance_AMDEPYC9V7480-CoreProcessor_linux64_gcc13.3.csv"
CONFORMANCE_CSV = RESULT / "conformance.csv"
LIBRARIES = ("Jsonic++ (C++17)", "RapidJSON (C++)")
COLORS = {"Jsonic++ (C++17)": "#f28c45", "RapidJSON (C++)": "#596579"}


def load_performance():
    totals = defaultdict(float)
    with PERFORMANCE_CSV.open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            if row["Library"] in LIBRARIES and row["Type"][:1] in "1234":
                totals[(row["Library"], row["Type"].split(". ", 1)[1])] += float(row["Time (ms)"])
    return totals


def load_conformance():
    passed = defaultdict(int)
    totals = defaultdict(int)
    with CONFORMANCE_CSV.open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            if row["Library"] not in LIBRARIES:
                continue
            category = row["Type"].split(". ", 1)[1]
            totals[(row["Library"], category)] += 1
            passed[(row["Library"], category)] += row["Result"] == "true"
    return passed, totals


def style_axis(axis):
    axis.set_facecolor("#f7f8fa")
    axis.grid(axis="x", color="#dfe3e8", linewidth=0.8)
    axis.set_axisbelow(True)
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.tick_params(axis="y", length=0)


def render_performance():
    totals = load_performance()
    operations = ("Parse", "Stringify", "Prettify", "Statistics")
    figure, axes = plt.subplots(2, 2, figsize=(13, 7.5))
    figure.subplots_adjust(top=0.84, bottom=0.08, left=0.08, right=0.98, hspace=0.38, wspace=0.20)
    figure.suptitle("Jsonic++ versus RapidJSON — same-run performance", y=0.98,
                    fontsize=20, weight="bold")
    figure.text(0.5, 0.925, "Total time across Canada, CITM catalog and Twitter; lower is better",
                ha="center", fontsize=11, color="#59616d")

    for axis, operation in zip(axes.flat, operations):
        values = [totals[(library, operation)] for library in LIBRARIES]
        bars = axis.barh(["Jsonic++", "RapidJSON"], values,
                         color=[COLORS[library] for library in LIBRARIES], height=0.55)
        axis.invert_yaxis()
        axis.set_title(operation, loc="left", fontsize=14, weight="bold")
        axis.set_xlabel("Total time (ms)")
        axis.set_xlim(0, max(values) * 1.22)
        style_axis(axis)
        for bar, value in zip(bars, values):
            axis.text(value + max(values) * 0.025, bar.get_y() + bar.get_height() / 2,
                      f"{value:.3f} ms", va="center", fontsize=10, weight="bold")

    output = SAMPLE / "jsonic_vs_rapidjson_performance.png"
    figure.savefig(output, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def render_conformance():
    passed, totals = load_conformance()
    categories = ("Parse Validation", "Parse Double", "Parse String", "Roundtrip")
    positions = np.arange(len(categories))
    width = 0.36
    figure, axis = plt.subplots(figsize=(13, 6.5))
    figure.subplots_adjust(top=0.79, bottom=0.13, left=0.08, right=0.98)

    for index, library in enumerate(LIBRARIES):
        percentages = [100 * passed[(library, category)] / totals[(library, category)]
                       for category in categories]
        offset = (index - 0.5) * width
        bars = axis.bar(positions + offset, percentages, width, label=library,
                        color=COLORS[library])
        for bar, category, percentage in zip(bars, categories, percentages):
            score = f"{passed[(library, category)]}/{totals[(library, category)]}"
            axis.text(bar.get_x() + bar.get_width() / 2, percentage + 1.5, score,
                      ha="center", va="bottom", fontsize=10, weight="bold")

    figure.suptitle("Jsonic++ versus RapidJSON — conformance", y=0.98,
                    fontsize=20, weight="bold")
    figure.text(0.5, 0.915, "136 cases total; higher is better", ha="center",
                fontsize=11, color="#59616d")
    axis.set_ylabel("Cases passed (%)")
    axis.set_xticks(positions, categories)
    axis.set_ylim(0, 112)
    axis.grid(axis="y", color="#dfe3e8", linewidth=0.8)
    axis.set_axisbelow(True)
    axis.spines[["top", "right"]].set_visible(False)
    axis.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.13), ncol=2)

    output = SAMPLE / "jsonic_vs_rapidjson_conformance.png"
    figure.savefig(output, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(figure)


if __name__ == "__main__":
    render_performance()
    render_conformance()
