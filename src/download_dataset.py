"""Parallel HF dataset downloader.

Why not `hf download`: it tops out ~5 files/s here. Plain per-file GETs hit HF's resolver rate limit
("resolvers" 5000 req / 300 s ~= 16 files/s sustained). The git-LFS batch API hands out CDN URLs for
hundreds of objects per request ("api" limit 1000 / 300 s), so this resolves in batches and GETs the CDN
with a thread pool. Resumable: skips files that exist with the right size. Writes tmp then renames.

usage: python src/download_dataset.py [--workers 64] [--batch 200] [--local-dir data/miimo] [--exclude PAT ...]
"""
import argparse
import fnmatch
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from huggingface_hub import HfApi, get_token, hf_hub_url

REPO = "retrina0678/miimo-audio-dataset"
LFS_BATCH = f"https://huggingface.co/datasets/{REPO}.git/info/lfs/objects/batch"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--local-dir", default="data/miimo")
    ap.add_argument("--workers", type=int, default=64)
    ap.add_argument("--batch", type=int, default=200)
    ap.add_argument("--exclude", action="append", default=["musan_mixed_2s/*", "*/raw/*"])
    ap.add_argument("--retries", type=int, default=5)
    a = ap.parse_args()
    root = Path(a.local_dir)
    tok = get_token()
    if not tok:
        sys.exit("not logged in: run `hf auth login`")
    auth = {"Authorization": f"Bearer {tok}"}

    print("listing repo tree...", flush=True)
    api = HfApi()
    files = [f for f in api.list_repo_tree(REPO, repo_type="dataset", recursive=True)
             if getattr(f, "size", None) is not None and not any(fnmatch.fnmatch(f.rfilename, p) for p in a.exclude)]
    def local(path):  # HF has dirs like "esc50 /" (trailing space); Windows cannot create those
        return root.joinpath(*(c.strip() for c in path.split("/")))

    todo = [f for f in files if not (local(f.rfilename).is_file() and local(f.rfilename).stat().st_size == f.size)]
    print(f"total={len(files)} already={len(files) - len(todo)} todo={len(todo)} bytes={sum(f.size for f in todo) / 1e9:.2f}GB", flush=True)

    local = threading.local()

    def sess():
        if not hasattr(local, "s"):
            local.s = requests.Session()
        return local.s

    def lfs_urls(objs):
        """sha256 -> (href, headers) via LFS batch API; honors 429 window."""
        body = {"operation": "download", "transfers": ["basic"], "objects": [{"oid": o.lfs.sha256, "size": o.size} for o in objs]}
        h = {"Accept": "application/vnd.git-lfs+json", "Content-Type": "application/vnd.git-lfs+json", **auth}
        for i in range(a.retries):
            r = requests.post(LFS_BATCH, json=body, headers=h, timeout=60)
            if r.status_code == 429:
                wait = int(r.headers.get("Retry-After", 30))
                print(f"lfs batch 429, sleeping {wait}s", flush=True)
                time.sleep(wait)
                continue
            r.raise_for_status()
            out = {}
            for o in r.json()["objects"]:
                d = o.get("actions", {}).get("download")
                if d:
                    out[o["oid"]] = (d["href"], d.get("header") or {})
            return out
        raise RuntimeError("lfs batch failed after retries")

    def fetch(path, size, url, headers):
        dst = local(path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        tmp = dst.with_name(dst.name + ".part")
        err = None
        for i in range(a.retries):
            try:
                r = sess().get(url, headers=headers, timeout=120)
                if r.status_code == 429:
                    time.sleep(5 * (i + 1))
                    continue
                r.raise_for_status()
                if len(r.content) != size:
                    raise IOError(f"size {len(r.content)} != {size}")
                tmp.write_bytes(r.content)
                os.replace(tmp, dst)
                return size
            except Exception as e:  # transient 404/5xx/conn reset seen in practice
                err = e
                time.sleep(1 + i)
        raise RuntimeError(f"{path}: {err}")

    done = fail = nbytes = 0
    failed = []
    t0 = time.time()
    with ThreadPoolExecutor(a.workers) as ex:
        for b in range(0, len(todo), a.batch):
            chunk = todo[b:b + a.batch]
            lfs = [f for f in chunk if getattr(f, "lfs", None)]
            urls = lfs_urls(lfs) if lfs else {}
            jobs = []
            for f in chunk:
                if getattr(f, "lfs", None) and f.lfs.sha256 in urls:
                    href, hdr = urls[f.lfs.sha256]
                else:  # non-LFS (csv/md/py) or batch miss: fall back to resolver
                    href, hdr = hf_hub_url(REPO, f.rfilename, repo_type="dataset"), auth
                jobs.append(ex.submit(fetch, f.rfilename, f.size, href, hdr))
            for fut in jobs:
                try:
                    nbytes += fut.result()
                    done += 1
                except Exception as e:
                    fail += 1
                    failed.append(str(e))
            dt = time.time() - t0
            n = done + fail
            print(f"{n}/{len(todo)} done={done} fail={fail} {done / dt:.1f} files/s {nbytes / dt / 1e6:.1f} MB/s "
                  f"eta={(len(todo) - n) / max(done / dt, 1e-9) / 60:.0f}min", flush=True)
    print(f"finished: done={done} fail={fail} in {(time.time() - t0) / 60:.1f}min", flush=True)
    for f in failed[:50]:
        print("FAILED", f)
    (root.parent / "download_failed.txt").write_text("\n".join(failed), encoding="utf-8")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
