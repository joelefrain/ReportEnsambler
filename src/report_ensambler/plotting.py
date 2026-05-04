from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def build_synthetic_data(seed: int = 42, points: int = 36) -> pd.DataFrame:
    """Crea una serie inventada, estable y útil para tests visuales."""
    rng = np.random.default_rng(seed)
    x = np.arange(points)
    trend = 0.22 * x
    seasonal = 2.7 * np.sin(x / 4.0)
    noise = rng.normal(0.0, 0.55, size=points)
    measured = 18 + trend + seasonal + noise
    limit = np.full(points, 24.0)
    return pd.DataFrame({"period": x + 1, "measured": measured, "limit": limit})


def create_example_plot(seed: int = 42, title: str = "Synthetic monitoring plot"):
    """Retorna una figura Matplotlib con datos sintéticos."""
    df = build_synthetic_data(seed=seed)
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=144)
    ax.plot(
        df["period"], df["measured"], marker="o", linewidth=1.6, label="Measured value"
    )
    ax.plot(
        df["period"], df["limit"], linestyle="--", linewidth=1.4, label="Design limit"
    )
    ax.fill_between(df["period"], df["measured"], df["limit"], alpha=0.08)
    ax.set_title(title)
    ax.set_xlabel("Synthetic period")
    ax.set_ylabel("Invented units")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    fig.tight_layout()
    return fig


def save_example_plot(
    path: str | Path, seed: int = 42, title: str = "Synthetic monitoring plot"
) -> Path:
    """Guarda el plot de ejemplo y cierra la figura."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = create_example_plot(seed=seed, title=title)
    fig.savefig(path, format=path.suffix.lstrip(".") or "png", bbox_inches="tight")
    plt.close(fig)
    return path
