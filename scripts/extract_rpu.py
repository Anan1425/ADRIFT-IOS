#!/usr/bin/env python3
"""
Download and extract Ren'Py DLC (renios) from .rpu files.
Uses the correct block-based format.

Usage: python extract_rpu.py <renpy_version> <dlc_name> <output_dir>
"""

import sys
import os
import json
import zlib
import hashlib
import urllib.request
import tempfile


def download(url, dest=None, timeout=300):
    """Download a URL with retry, return bytes or save to file."""
    print(f"  Downloading: {url}")
    last_error = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
            if dest:
                with open(dest, 'wb') as f:
                    f.write(data)
                print(f"  Saved: {dest} ({len(data)} bytes)")
            return data
        except Exception as e:
            last_error = e
            print(f"  Attempt {attempt+1} failed: {e}")
            if attempt < 2:
                import time
                time.sleep(5)
    raise last_error


def extract_rpu(renpy_version, dlc_name, output_dir):
    base_url = f"https://www.renpy.org/dl/{renpy_version}"

    # Step 1: Download updates.json to find DLC info
    print(f"[1/5] Fetching updates.json")
    updates = json.loads(download(f"{base_url}/updates.json").decode('utf-8'))

    if dlc_name not in updates:
        print(f"ERROR: DLC '{dlc_name}' not found")
        print(f"Available: {list(updates.keys())}")
        sys.exit(1)

    rpu_url = updates[dlc_name]['rpu_url']
    print(f"  Filelist: {rpu_url}")

    # Step 2: Download and parse filelist
    print(f"[2/5] Downloading filelist")
    filelist_data = download(f"{base_url}/{rpu_url}")
    fl = json.loads(zlib.decompress(filelist_data).decode('utf-8'))

    files = fl.get('files', [])
    directories = fl.get('directories', [])
    blocks = fl.get('blocks', [])
    print(f"  {len(files)} files, {len(directories)} dirs, {len(blocks)} blocks")

    # Step 3: Build segment hash -> block mapping
    print(f"[3/5] Building segment index")
    seg_map = {}  # hash -> (block_name, offset, size, compressed)
    for block in blocks:
        block_name = block['name']
        for seg in block.get('segments', []):
            seg_map[seg['hash']] = (
                block_name,
                seg['offset'],
                seg['size'],
                seg.get('compressed', 0)
            )
    print(f"  Indexed {len(seg_map)} segments")

    # Step 4: Download all block files
    print(f"[4/5] Downloading {len(blocks)} data blocks")
    block_dir = tempfile.mkdtemp(prefix='rpu_blocks_')
    block_data = {}

    for block in blocks:
        block_name = block['name']
        block_path = os.path.join(block_dir, block_name)
        if not os.path.exists(block_path):
            try:
                download(f"{base_url}/rpu/{block_name}", block_path)
            except Exception as e:
                print(f"  ERROR: Failed to download block {block_name}: {e}")
                sys.exit(1)

        # Read block file (skip 14-byte RPU-BLOCK-1.0 header)
        with open(block_path, 'rb') as f:
            header = f.read(14)
            if header == b"RPU-BLOCK-1.0\r\n":
                block_data[block_name] = f.read()
            else:
                f.seek(0)
                block_data[block_name] = f.read()

    # Step 5: Reconstruct files
    print(f"[5/5] Reconstructing {len(files)} files")
    os.makedirs(output_dir, exist_ok=True)

    # Create directories
    for d in directories:
        os.makedirs(os.path.join(output_dir, d['name']), exist_ok=True)

    success = 0
    failed = 0

    for f in files:
        name = f['name']
        segments = f.get('segments', [])
        xbit = f.get('xbit', False)

        out_path = os.path.join(output_dir, name)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        try:
            with open(out_path, 'wb') as out:
                for seg in segments:
                    file_offset = seg['offset']
                    file_size = seg['size']
                    seg_hash = seg['hash']

                    if seg_hash not in seg_map:
                        raise Exception(f"Segment hash {seg_hash} not found in any block")

                    block_name, block_offset, block_size, compressed = seg_map[seg_hash]

                    data = block_data[block_name][block_offset:block_offset + block_size]

                    if compressed == 1:  # COMPRESS_ZLIB
                        data = zlib.decompress(data)

                    # Verify size
                    if len(data) != file_size:
                        print(f"  WARNING: {name} segment size mismatch: expected {file_size}, got {len(data)}")

                    out.seek(file_offset)
                    out.write(data)

            if xbit:
                os.chmod(out_path, 0o755)

            success += 1
            if success <= 5 or success % 50 == 0:
                print(f"  [{success}/{len(files)}] {name}")
        except Exception as e:
            failed += 1
            print(f"  FAILED: {name}: {e}")

    # Cleanup
    import shutil
    shutil.rmtree(block_dir, ignore_errors=True)

    print(f"\n{'='*50}")
    print(f"Done: {success} succeeded, {failed} failed")
    print(f"Output: {output_dir}")

    # Verify
    hash_file = os.path.join(output_dir, 'hash.txt')
    if os.path.exists(hash_file):
        print(f"[OK] hash.txt found")
        with open(hash_file) as f:
            print(f"  {f.read().strip()[:80]}")
    else:
        print(f"[WARNING] hash.txt not found")
        print(f"  Top-level: {os.listdir(output_dir)[:20]}")

    if failed > 0:
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} <renpy_version> <dlc_name> <output_dir>")
        sys.exit(1)
    extract_rpu(sys.argv[1], sys.argv[2], sys.argv[3])
