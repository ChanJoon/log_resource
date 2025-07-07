#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
plot_log.py
-----------
Read a CSV file produced by `cpu_mem_logger.py` and generate plots of CPU and memory usage.

Usage:
    python plot_log.py --file log.csv [--save output.png]

If --save is omitted, the plot will be shown in an interactive window.
"""
import argparse
from pathlib import Path
from typing import Optional

import pandas as pd
import matplotlib.pyplot as plt


def load_data(csv_path: Path) -> pd.DataFrame:
    """Load the CSV and clean FINAL row if present."""
    df = pd.read_csv(csv_path)
    df_clean = df[df['Timestamp'] != 'FINAL'].copy()
    # Convert Timestamp to datetime with microsecond precision
    df_clean['Timestamp'] = pd.to_datetime(df_clean['Timestamp'], format='%Y-%m-%d %H:%M:%S.%f')
    # Convert to seconds since start for better x-axis plotting
    if not df_clean.empty:
        start_time = df_clean['Timestamp'].iloc[0]
        df_clean['Seconds'] = (df_clean['Timestamp'] - start_time).dt.total_seconds()
        
    return df_clean


def plot_metrics(df: pd.DataFrame, save_path: Optional[Path] = None):
    """Plot CPU and Memory usage over time."""
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.set_title('CPU and Memory Usage')
    ax1.set_xlabel('Time')

    # CPU – use left y-axis
    ax1.set_ylabel('CPU %', color='tab:red')
    ax1.plot(df['Timestamp'], df['CPU %'], label='CPU %', color='tab:red')
    ax1.tick_params(axis='y', labelcolor='tab:red')

    # Memory – use right y-axis
    ax2 = ax1.twinx()
    ax2.set_ylabel('Memory %', color='tab:blue')
    ax2.plot(df['Timestamp'], df['Mem %'], label='Mem %', color='tab:blue')
    ax2.tick_params(axis='y', labelcolor='tab:blue')
    ax2.set_ylim(0.0, 1.0)

    # Average lines (optional if present)
    if 'Avg CPU %' in df.columns and 'Avg Mem %' in df.columns:
        avg_cpu = df['Avg CPU %'].dropna().iloc[-1]
        avg_mem = df['Avg Mem %'].dropna().iloc[-1]
        ax1.axhline(avg_cpu, color='tab:red', linestyle='--', alpha=0.5, label=f'Avg CPU {avg_cpu:.2f}%')
        ax2.axhline(avg_mem, color='tab:blue', linestyle='--', alpha=0.5, label=f'Avg Mem {avg_mem:.2f}%')

    fig.tight_layout()

    # Combine legends
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper left')

    if save_path:
        plt.savefig(save_path, dpi=300)
        print(f"Plot saved to {save_path}")
    else:
        plt.show()


def main():
    parser = argparse.ArgumentParser(description="Plot CPU & Memory usage from log.csv")
    parser.add_argument('--file', default='log.csv', help='Path to CSV file (default: log.csv)')
    parser.add_argument('--save', help='Path to output image file (e.g., plot.png). If omitted, shows the plot interactively.')
    args = parser.parse_args()

    csv_path = Path(args.file)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = load_data(csv_path)
    plot_metrics(df, Path(args.save) if args.save else None)


if __name__ == '__main__':
    main() 