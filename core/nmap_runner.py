import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NMAP_PATH = os.path.join(BASE_DIR, "bundled", "nmap", "nmap")

def get_nmap():
    if os.path.exists(NMAP_PATH):
        return NMAP_PATH
    return "nmap"

def scan_single(target, options):
    cmd = [get_nmap()] + options + [target]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )
    return target, result.stdout or result.stderr

def scan_multiple(targets, options, workers=3):
    results = {}
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(scan_single, t, options)
            for t in targets
        ]
        for future in as_completed(futures):
            target, output = future.result()
            results[target] = output
    return results

