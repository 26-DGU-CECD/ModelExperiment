"""Parallel HF dataset downloader. `hf download` tops out ~5 files/s here regardless of workers;
plain HTTP GETs scale linearly, so this lists the repo tree and fetches with a thread pool.
Resumable: skips files that exist with the right size. Writes tmp then renames.

usage: python src/download_dataset.py [--workers 64] [--local-dir data/miimo] [--exclude PAT ...]
"""
import argparse
import fnmatch
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from huggingface_hub import HfApi, get_token, hf_hub_url

REPO = "retrina0678/miimo-audio-dataset"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--local-dir", default="data/miimo")
    ap.add_argument("--workers", type=int, default=64)
    ap.add_argument("--exclude", action="append", default=["musan_mixed_2s/*", "*/raw/*"])
    ap.add_argument("--retries", type=int, default=5)
    a = ap.parse_args()
    root = Path(a.local_dir)
    tok = get_token()
    if not tok:
        sys.exit("not logged in: run `hf auth login`")
    headers = {"Authorization": f"Bearer {tok}"}

    print("listing repo tree...", flush=True)
    api = HfApi()
    files = [(f.rfilename, f.size) for f in api.list_repo_tree(REPO, repo_type="dataset", recursive=True)
             if getattr(f, "size", None) is not None and not any(fnmatch.fnmatch(f.rfilename, p) for p in a.exclude)]
    todo = [(p, s) for p, s in files if not ((root / p).is_file() and (root / p).stat().st_size == s)]
    print(f"total={len(files)} already={len(files) - len(todo)} todo={len(todo)} bytes={sum(s for _, s in todo) / 1e9:.2f}GB", flush=True)

    local = threading.local()

    def sess():
        if not hasattr(local, "s"):
            local.s = requests.Session()
            local.s.headers.update(headers)
        return local.s

    def fetch(path, size):
        dst = root / path
        dst.parent.mkdir(parents=True, exist_ok=True)
        tmp = dst.with_name(dst.name + ".part")
        url = hf_hub_url(REPO, path, repo_type="dataset")
        for i in range(a.retries):
            try:
                r = sess().get(url, timeout=120)
                if r.status_code == 429:
                    time.sleep(2 ** i)
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
    t0 = time.time()
    failed = []
    with ThreadPoolExecutor(a.workers) as ex:
        futs = {ex.submit(fetch, p, s): p for p, s in todo}
        for fut in as_completed(futs):
            try:
                nbytes += fut.result()
                done += 1
            except Exception as e:
                fail += 1
                failed.append(str(e))
            if (done + fail) % 500 == 0 or done + fail == len(todo):
                dt = time.time() - t0
                print(f"{done + fail}/{len(todo)} done={done} fail={fail} {done / dt:.1f} files/s {nbytes / dt / 1e6:.1f} MB/s "
                      f"eta={(len(todo) - done - fail) / max(done / dt, 1e-9) / 60:.0f}min", flush=True)
    print(f"finished: done={done} fail={fail} in {(time.time() - t0) / 60:.1f}min", flush=True)
    for f in failed[:50]:
        print("FAILED", f)
    (root.parent / "download_failed.txt").write_text("\n".join(failed), encoding="utf-8")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
