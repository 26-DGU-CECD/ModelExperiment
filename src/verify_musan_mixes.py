#!/usr/bin/env python3
"""Verify MUSAN mix files, metadata linkage, format, and measured SNR."""
from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path

import numpy as np
import soundfile as sf


SAMPLE_RATE = 16_000
FRAMES = SAMPLE_RATE * 2


def rms(samples: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(samples, dtype=np.float64)))) if samples.size else 0.0


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def resolve_path(data_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else data_root / path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--metadata", default="clip_metadata.csv")
    parser.add_argument("--mix-metadata", default="musan_mix_metadata.csv")
    parser.add_argument("--snrs", nargs="+", type=int, default=[20, 15, 10])
    parser.add_argument("--limit", type=int, default=0, help="입력 클립 수 제한 (스모크 검증용)")
    parser.add_argument("--snr-tolerance-db", type=float, default=0.25)
    parser.add_argument("--noise-floor-dbfs", type=float, default=-30.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.data_root.expanduser().resolve()
    source_rows = sorted(load_csv(root / args.metadata), key=lambda row: row["filepath"])
    if args.limit > 0:
        source_rows = source_rows[: args.limit]
    mixed_rows = load_csv(root / args.mix_metadata)
    source_by_path = {row["filepath"]: row for row in source_rows}
    complete = [
        row for row in mixed_rows
        if row.get("status") == "complete" and row.get("source_filepath") in source_by_path
    ]
    expected = len(source_rows) * len(args.snrs)
    errors: list[str] = []
    if len(complete) != expected:
        errors.append(f"complete metadata rows={len(complete)} expected={expected}")

    expected_groups = {f"aug_{row.get('source_file', '')}" for row in source_rows}
    floor_rms = 10 ** (args.noise_floor_dbfs / 20.0)
    seen_paths: set[str] = set()
    for row in complete:
        filepath = row.get("filepath", "")
        if filepath in seen_paths:
            errors.append(f"duplicate output metadata filepath: {filepath}")
            continue
        seen_paths.add(filepath)
        source_path = row.get("source_filepath", "")
        source = source_by_path.get(source_path)
        if source is None:
            errors.append(f"unknown source_filepath: {source_path}")
            continue
        for field in ("label", "source_file", "start_sec", "origin_label"):
            if row.get(field, "") != source.get(field, ""):
                errors.append(f"{filepath}: {field} does not match source")
        expected_group = f"aug_{source.get('source_file', '')}"
        if row.get("group_id") != expected_group or row.get("group_id") not in expected_groups:
            errors.append(f"{filepath}: group_id does not match source_file")
        output = resolve_path(root, filepath)
        original = resolve_path(root, source_path)
        if not output.exists() or not original.exists():
            errors.append(f"missing output or source file: {filepath}")
            continue
        info = sf.info(output)
        if (info.samplerate, info.channels, info.frames, info.subtype) != (SAMPLE_RATE, 1, FRAMES, "FLOAT"):
            errors.append(f"{filepath}: expected 16 kHz mono 2 s FLOAT WAV")
            continue
        clean, _ = sf.read(original, dtype="float32", always_2d=True)
        mixed, _ = sf.read(output, dtype="float32", always_2d=True)
        clean_mono = clean.mean(axis=1)[:FRAMES]
        mixed_mono = mixed.mean(axis=1)[:FRAMES]
        if clean_mono.size != FRAMES or mixed_mono.size != FRAMES:
            errors.append(f"{filepath}: expected 32000 samples")
            continue
        original_clean_rms = rms(clean_mono)
        reference_rms = float(row.get("clean_rms_reference", max(original_clean_rms, floor_rms)))
        # Peak protection in the mixer scales clean and noise together.  For
        # non-silent clips the recorded post-scale clean RMS reconstructs that
        # clean component exactly; subtracting the unscaled source would make
        # a correct mix appear to have the wrong SNR.
        if original_clean_rms >= floor_rms and original_clean_rms > 0:
            clean_component = clean_mono * np.float32(reference_rms / original_clean_rms)
        else:
            clean_component = clean_mono
        noise_rms = rms(mixed_mono - clean_component)
        if noise_rms <= 0:
            errors.append(f"{filepath}: measured noise RMS is zero")
            continue
        measured_snr = 20.0 * math.log10(reference_rms / noise_rms)
        target_snr = float(row.get("musan_snr", "nan"))
        if abs(measured_snr - target_snr) > args.snr_tolerance_db:
            errors.append(f"{filepath}: SNR={measured_snr:.3f} target={target_snr:.3f}")

    if errors:
        print("[FAILED] MUSAN mix verification", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    print(f"[OK] verified complete_rows={len(complete)} expected_rows={expected}")


if __name__ == "__main__":
    main()
