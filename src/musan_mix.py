#!/usr/bin/env python3
"""Create resumable, offline MUSAN Noise mixes for every indexed 2-second clip."""
from __future__ import annotations

import argparse
import csv
import hashlib
import math
import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Iterable

import numpy as np
import soundfile as sf


SAMPLE_RATE = 16_000
FRAMES = SAMPLE_RATE * 2
NOISE_FLOOR_DBFS = -30.0
DEFAULT_SNRS = (20, 15, 10)
DEFAULT_SEED = 42
DOWNLOAD_COMPLETE_MARKER = ".musan_noise_download_complete"
METADATA_FIELDS = [
    "filepath", "source_filepath", "label", "source_file", "start_sec", "variant",
    "aug_tags", "is_augmented", "origin_label", "group_id", "musan_snr", "musan_source",
    "musan_start_sample", "seed", "clean_rms_reference", "noise_rms", "measured_snr_db",
    "status", "error",
]


def rms(samples: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(samples, dtype=np.float64)))) if samples.size else 0.0


def dbfs_to_rms(dbfs: float) -> float:
    return float(10 ** (dbfs / 20.0))


def deterministic_rng(seed: int, source_path: str, snr: int) -> np.random.Generator:
    digest = hashlib.sha256(f"{seed}\0{source_path}\0{snr}".encode("utf-8")).digest()
    return np.random.default_rng(int.from_bytes(digest[:8], "big"))


@lru_cache(maxsize=8)
def read_mono_16k(path_str: str) -> np.ndarray:
    """Load an audio file into a mono 16 kHz float32 waveform."""
    samples, sample_rate = sf.read(path_str, dtype="float32", always_2d=True)
    mono = np.asarray(samples.mean(axis=1), dtype=np.float32)
    if sample_rate != SAMPLE_RATE:
        try:
            import librosa
        except ImportError as exc:  # pragma: no cover - depends on local input format
            raise RuntimeError("16 kHz 이외의 WAV를 처리하려면 librosa가 필요합니다.") from exc
        mono = np.asarray(
            librosa.resample(mono, orig_sr=sample_rate, target_sr=SAMPLE_RATE), dtype=np.float32
        )
    return mono


def fit_frames(samples: np.ndarray, frames: int = FRAMES) -> np.ndarray:
    if samples.size == 0:
        return np.zeros(frames, dtype=np.float32)
    if samples.size < frames:
        repeats = math.ceil(frames / samples.size)
        return np.tile(samples, repeats)[:frames].astype(np.float32, copy=False)
    return samples[:frames].astype(np.float32, copy=False)


def find_noise_files(musan_root: Path) -> list[Path]:
    files = [
        path for path in musan_root.rglob("*.wav")
        if "noise" in {part.lower() for part in path.relative_to(musan_root).parts[:-1]}
    ]
    return sorted(files)


def download_noise(cache_dir: Path) -> Path:
    """Download only the upstream Noise directory into the dataset-local cache."""
    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise RuntimeError(
            "MUSAN 자동 다운로드에는 huggingface_hub가 필요합니다. "
            "requirements-mac.txt를 설치하거나 --musan-root를 지정하세요."
        ) from exc
    cache_dir.mkdir(parents=True, exist_ok=True)
    snapshot_download(
        repo_id="FluidInference/musan",
        repo_type="dataset",
        local_dir=str(cache_dir),
        allow_patterns=["noise/**", "**/noise/**"],
    )
    (cache_dir / DOWNLOAD_COMPLETE_MARKER).write_text("FluidInference/musan Noise\n", encoding="utf-8")
    return cache_dir


def resolve_musan_root(args: argparse.Namespace) -> Path:
    if args.musan_root is not None:
        root = args.musan_root.expanduser().resolve()
        if not root.exists():
            raise FileNotFoundError(f"MUSAN root not found: {root}")
        return root
    cache_dir = (args.download_dir or (args.data_root / ".cache" / "musan")).expanduser().resolve()
    if not (cache_dir / DOWNLOAD_COMPLETE_MARKER).exists() or not find_noise_files(cache_dir):
        print(f"[DOWNLOAD] MUSAN Noise -> {cache_dir}")
        download_noise(cache_dir)
    return cache_dir


def output_path(output_root: Path, source_filepath: str, snr: int) -> Path:
    source = Path(source_filepath)
    return output_root / source.parent / f"{source.stem}_musan-snr{snr}.wav"


def display_path(path: Path, data_root: Path) -> str:
    try:
        return str(path.relative_to(data_root))
    except ValueError:
        return str(path)


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def source_rows_from_corpus(data_root: Path, metadata_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Use metadata as the source of truth, while covering unindexed clip WAVs too."""
    by_path = {str(row.get("filepath", "")): dict(row) for row in metadata_rows}
    for wav in sorted(data_root.glob("*/clips_2s/*.wav")):
        relative = str(wav.relative_to(data_root))
        if relative in by_path:
            continue
        by_path[relative] = {
            "filepath": relative,
            "label": wav.parent.parent.name,
            "source_file": wav.stem,
            "start_sec": "",
            "variant": "unknown",
            "aug_tags": "",
            "is_augmented": "0",
            "origin_label": "",
        }
    return [by_path[key] for key in sorted(by_path)]


def write_metadata(path: Path, rows: Iterable[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.stem}.tmp.csv")
    with temporary.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=METADATA_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, path)


def choose_noise_segment(
    noise_files: list[Path], musan_root: Path, rng: np.random.Generator
) -> tuple[np.ndarray, str, int]:
    order = rng.permutation(len(noise_files))
    for idx in order:
        source = noise_files[int(idx)]
        samples = read_mono_16k(str(source))
        if samples.size == 0:
            continue
        if samples.size < FRAMES:
            segment = fit_frames(samples)
            start = 0
        else:
            start = int(rng.integers(0, samples.size - FRAMES + 1))
            segment = samples[start : start + FRAMES]
        if rms(segment) > 1e-12:
            return segment, str(source.relative_to(musan_root)), start
    raise RuntimeError("usable MUSAN Noise WAV를 찾지 못했습니다.")


def create_mix(clean: np.ndarray, noise: np.ndarray, snr: int, floor_rms: float) -> tuple[np.ndarray, float, float, float]:
    clean_rms = rms(clean)
    reference_rms = max(clean_rms, floor_rms)
    noise_rms = rms(noise)
    scaled_noise = noise * np.float32(reference_rms / (10 ** (snr / 20.0)) / noise_rms)
    mixed = clean + scaled_noise
    peak = float(np.max(np.abs(mixed))) if mixed.size else 0.0
    if peak > 1.0:
        mixed = mixed / np.float32(peak)
        scaled_noise = scaled_noise / np.float32(peak)
        reference_rms /= peak
    measured_noise_rms = rms(scaled_noise)
    measured_snr = 20.0 * math.log10(reference_rms / measured_noise_rms)
    return mixed.astype(np.float32), reference_rms, measured_noise_rms, measured_snr


def write_float_wav(path: Path, samples: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.stem}.tmp.wav")
    sf.write(temporary, samples, SAMPLE_RATE, subtype="FLOAT")
    os.replace(temporary, path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--musan-root", type=Path, help="로컬 MUSAN root (Noise 하위 폴더 포함)")
    parser.add_argument("--download-dir", type=Path, help="자동 다운로드 캐시 (기본: <data-root>/.cache/musan)")
    parser.add_argument("--output-root", type=Path, help="기본: <data-root>/musan_mixed_2s")
    parser.add_argument("--metadata", default="clip_metadata.csv")
    parser.add_argument("--mix-metadata", default="musan_mix_metadata.csv")
    parser.add_argument("--snrs", nargs="+", type=int, default=list(DEFAULT_SNRS))
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--limit", type=int, default=0, help="입력 클립 수 제한 (스모크 테스트용)")
    parser.add_argument("--metadata-flush-every", type=int, default=1000,
                        help="완료 상태를 원자적으로 저장할 출력 수 간격")
    parser.add_argument("--noise-floor-dbfs", type=float, default=NOISE_FLOOR_DBFS)
    parser.add_argument("--only", type=Path, default=None,
                        help="CSV with a filepath column (relative to --data-root): mix only these clips, skip the corpus glob. "
                             "label/source_file/is_augmented columns are carried over when present (label_fine preferred).")
    parser.add_argument("--output-strip", type=int, default=0,
                        help="drop this many leading path components of the source path when building the output path "
                             "(e.g. 2 turns data/miimo/<label>/... into <output-root>/<label>/...)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.data_root = args.data_root.expanduser().resolve()
    if not args.data_root.exists():
        raise FileNotFoundError(f"data-root not found: {args.data_root}")
    if args.metadata_flush_every < 1:
        raise ValueError("--metadata-flush-every must be >= 1")
    if args.only is not None:  # explicit clip list (e.g. data/splits/manifest_test_clean.csv); no corpus glob
        source_meta_path = args.only
        source_rows = []
        for row in load_csv(args.only):
            source_rows.append({"filepath": row["filepath"], "label": row.get("label_fine") or row.get("label", ""),
                                "source_file": row.get("source_file", ""), "start_sec": row.get("start_sec", ""),
                                "variant": row.get("variant", ""), "aug_tags": row.get("aug_tags", ""),
                                "is_augmented": row.get("is_augmented", ""), "origin_label": row.get("origin_label", "")})
    else:
        source_meta_path = args.data_root / args.metadata
        metadata_rows = load_csv(source_meta_path)
        source_rows = source_rows_from_corpus(args.data_root, metadata_rows)
    if not source_rows:
        raise RuntimeError(f"input metadata is empty or missing: {source_meta_path}")
    output_root = (args.output_root or (args.data_root / "musan_mixed_2s")).expanduser().resolve()
    musan_root = resolve_musan_root(args)
    noise_files = find_noise_files(musan_root)
    if not noise_files:
        raise RuntimeError(f"MUSAN Noise WAV를 찾지 못했습니다: {musan_root}")

    valid_rows = [row for row in source_rows if not str(row.get("filepath", "")).startswith("musan_mixed_2s/")]
    if args.limit > 0:
        valid_rows = valid_rows[: args.limit]
    mix_meta_path = Path(args.mix_metadata) if Path(args.mix_metadata).is_absolute() else args.data_root / args.mix_metadata
    mix_meta_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_by_path = {row.get("filepath", ""): row for row in load_csv(mix_meta_path)}
    floor_rms = dbfs_to_rms(args.noise_floor_dbfs)
    written = skipped = failed = changed_since_flush = 0

    for source_row in valid_rows:
        source_filepath = str(source_row["filepath"])
        clean_path = args.data_root / source_filepath
        if not clean_path.exists():
            print(f"[MISSING] {clean_path}", file=sys.stderr)
            failed += len(args.snrs)
            continue
        clean = fit_frames(read_mono_16k(str(clean_path)))
        for snr in args.snrs:
            out_path = output_path(output_root, "/".join(Path(source_filepath).parts[args.output_strip:]), snr)
            row_path = display_path(out_path, args.data_root)
            previous = metadata_by_path.get(row_path)
            if previous and previous.get("status") == "complete" and out_path.exists():
                skipped += 1
                continue
            try:
                rng = deterministic_rng(args.seed, source_filepath, snr)
                noise, noise_source, noise_start = choose_noise_segment(noise_files, musan_root, rng)
                mixed, reference_rms, noise_rms, measured_snr = create_mix(clean, noise, snr, floor_rms)
                write_float_wav(out_path, mixed)
                result = {
                    "filepath": row_path,
                    "source_filepath": source_filepath,
                    "label": source_row.get("label", ""),
                    "source_file": source_row.get("source_file", ""),
                    "start_sec": source_row.get("start_sec", ""),
                    "variant": "musan",
                    "aug_tags": f"musan_snr{snr}",
                    "is_augmented": "1",
                    "origin_label": source_row.get("origin_label", ""),
                    "group_id": f"aug_{source_row.get('source_file', '')}",
                    "musan_snr": str(snr),
                    "musan_source": noise_source,
                    "musan_start_sample": str(noise_start),
                    "seed": str(args.seed),
                    "clean_rms_reference": f"{reference_rms:.12g}",
                    "noise_rms": f"{noise_rms:.12g}",
                    "measured_snr_db": f"{measured_snr:.12g}",
                    "status": "complete",
                    "error": "",
                }
                metadata_by_path[row_path] = result
                written += 1
                changed_since_flush += 1
            except Exception as exc:
                metadata_by_path[row_path] = {
                    "filepath": row_path, "source_filepath": source_filepath,
                    "label": source_row.get("label", ""), "source_file": source_row.get("source_file", ""),
                    "start_sec": source_row.get("start_sec", ""), "variant": "musan",
                    "aug_tags": f"musan_snr{snr}", "is_augmented": "1",
                    "origin_label": source_row.get("origin_label", ""),
                    "group_id": f"aug_{source_row.get('source_file', '')}", "musan_snr": str(snr),
                    "musan_source": "", "musan_start_sample": "", "seed": str(args.seed),
                    "clean_rms_reference": "", "noise_rms": "", "measured_snr_db": "",
                    "status": "failed", "error": str(exc),
                }
                failed += 1
                changed_since_flush += 1
                print(f"[FAILED] {source_filepath} snr={snr}: {exc}", file=sys.stderr)
            if changed_since_flush >= args.metadata_flush_every:
                write_metadata(mix_meta_path, (metadata_by_path[key] for key in sorted(metadata_by_path)))
                changed_since_flush = 0

    if changed_since_flush:
        write_metadata(mix_meta_path, (metadata_by_path[key] for key in sorted(metadata_by_path)))
    print(f"[DONE] written={written} skipped={skipped} failed={failed} metadata={mix_meta_path}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
