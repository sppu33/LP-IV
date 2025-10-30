#!/usr/bin/env python3
"""
Simplified TSK-based helper to find and recover files from EXT filesystems.

Modes:
- --find-partitions: Scans a disk image for EXT superblock magic numbers.
- --list: Lists files in a partition (all files if offset given, else only deleted files).
- --recover-all: Recovers the files found by the list logic.
"""
import argparse
import os
import shutil
import subprocess
import sys
from typing import List, Tuple

# EXT filesystem magic number (found at bytes 56-57 in the superblock)
EXT_MAGIC = b'\x53\xef'

def find_ext_partitions(image_path: str) -> None:
    """Scans an image for EXT superblocks and prints their byte offsets."""
    print(f"[*] Scanning {image_path} for EXT partitions...", file=sys.stderr)
    try:
        with open(image_path, 'rb') as f:
            # The primary superblock is at byte 1024 from the start of the partition.
            # We will scan every 1MB for this pattern.
            chunk_size = 1024 * 1024
            offset = 0
            while chunk := f.read(chunk_size):
                # An EXT superblock is 1024 bytes from the start of the partition.
                # The magic number is 56 bytes inside the superblock.
                # So we are looking for the magic number at byte 1024 + 56 = 1080.
                if chunk[1080:1082] == EXT_MAGIC:
                    print(offset) # Print byte offset of the partition start
                offset += chunk_size
    except FileNotFoundError:
        print(f"Error: Image file not found at '{image_path}'", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred during scanning: {e}", file=sys.stderr)

def get_target_files(image_path: str, sector_offset: str = None) -> List[Tuple[str, str]]:
    """
    Uses 'fls' to find files.
    - With offset: finds ALL allocated files (for partition recovery).
    - Without offset: finds only DELETED files (for standard file recovery).
    """
    if not shutil.which("fls"):
        sys.exit("Error: 'fls' from 'sleuthkit' is required but not found.")

    cmd = ["fls", "-r", "-p"] # Recursive, show full path
    if sector_offset:
        print("[*] Searching for ALL existing files in partition...", file=sys.stderr)
        cmd.extend(["-o", sector_offset])
    else:
        print("[*] Searching for DELETED files in image...", file=sys.stderr)
        cmd.append("-d") # Find only deleted entries
    cmd.append(image_path)

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        print(f"Error: fls failed: {result.stderr.strip()}", file=sys.stderr)
        return []

    found_files = []
    # Parse fls output like: 'r/r * 12: secret_file.txt'
    for line in result.stdout.splitlines():
        if ":" not in line:
            continue
        meta, _, path = line.partition(":")
        inode = meta.split()[-1].strip("*") # Get last part of meta, remove deletion marker
        if inode.isdigit():
            found_files.append((inode, path.strip()))
    return found_files

def recover_files(image_path: str, outdir: str, files: List[Tuple[str, str]], sector_offset: str = None) -> int:
    """Recovers a list of files by inode using 'icat'."""
    if not shutil.which("icat"):
        sys.exit("Error: 'icat' from 'sleuthkit' is required but not found.")

    os.makedirs(outdir, exist_ok=True)
    print(f"[*] Recovering {len(files)} files to {outdir} ...")
    success_count = 0
    for inode, name in files:
        safe_name = name.replace("/", "_").strip("_") or "unnamed_file"
        out_path = os.path.join(outdir, f"recovered_{inode}_{safe_name}")

        cmd = ["icat"]
        if sector_offset:
            cmd.extend(["-o", sector_offset])
        cmd.extend([image_path, inode])

        try:
            with open(out_path, "wb") as f_out:
                # Run icat and pipe its stdout (the file content) to our output file
                subprocess.run(cmd, stdout=f_out, stderr=subprocess.PIPE, check=True)
            print(f"[+] Recovered inode {inode} ('{name}') -> {out_path}")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"[-] Failed to recover inode {inode}: {e.stderr.decode()}", file=sys.stderr)
            os.remove(out_path) # Clean up empty file on failure
    return success_count

def main():
    """Parse arguments and execute the requested action."""
    parser = argparse.ArgumentParser(description="Recover files and partitions from EXT filesystems.")
    parser.add_argument("-i", "--image", required=True, help="Path to the disk image")
    parser.add_argument("-o", "--outdir", help="Output directory for recovered files")
    parser.add_argument("-f", "--offset", help="Sector offset of the target partition")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--find-partitions", action="store_true", help="Scan for EXT partitions")
    group.add_argument("--list", action="store_true", help="List target files to be recovered")
    group.add_argument("--recover-all", action="store_true", help="Recover all target files")
    args = parser.parse_args()

    if args.find_partitions:
        find_ext_partitions(args.image)
        return

    files = get_target_files(args.image, sector_offset=args.offset)
    if not files:
        print("[*] No target files found.", file=sys.stderr)
        return

    if args.list:
        print("\nFound target files (inode : name):")
        for inode, name in files:
            print(f"{inode} : {name}")
    elif args.recover_all:
        if not args.outdir:
            parser.error("--outdir is required for --recover-all.")
        count = recover_files(args.image, args.outdir, files, sector_offset=args.offset)
        print(f"\n[*] Recovery complete. Successfully recovered {count}/{len(files)} files.")

if __name__ == "__main__":
    main()