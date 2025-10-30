#!/bin/bash
# Corrected demo for recovering a deleted partition and a file.
# Requires: parted, sleuthkit (mmls), root privileges.

set -e # Exit immediately if a command fails.

# --- Configuration ---
IMG="disk.img"
RECOVER_DIR="./recovered_files_$(date +%s)"
TMP_FILE="./secret_file.txt"
IMG_SIZE_MB=50

# --- Cleanup Function ---
trap 'echo "[*] Cleaning up..."; sudo losetup -d $(losetup -a | grep "$IMG" | cut -d: -f1) 2>/dev/null; rm -rf "$IMG" "$RECOVER_DIR" "$TMP_FILE"; echo "[+] Done."' EXIT

# --- Main Script ---
if (( EUID != 0 )); then
   echo "[-] Error: This script must be run with sudo."
   exit 1
fi

echo "[0] Creating a temporary file to place on the partition..."
echo "This data was recovered from a deleted partition." > $TMP_FILE

echo "[1] Creating a ${IMG_SIZE_MB}MB disk image: $IMG"
dd if=/dev/zero of=$IMG bs=1M count=$IMG_SIZE_MB status=progress

echo "[2] Creating two EXT2 partitions..."
parted -s "$IMG" -- mktable msdos \
    mkpart primary ext2 1MiB 25MiB \
    mkpart primary ext2 25MiB 49MiB

echo "[3] Initial partition layout:"
mmls "$IMG"

P2_START_SECTOR=$(mmls "$IMG" | awk '/000:001/ {print $3}')
# FIX: Force bash to treat the sector as a base-10 number to avoid octal conversion.
P2_OFFSET_BYTES=$((10#$P2_START_SECTOR * 512))
echo "[+] Partition 2 starts at sector $P2_START_SECTOR (byte offset $P2_OFFSET_BYTES)."

echo "[4] Formatting Partition 2 and writing a secret file..."
LOOP_DEV=$(sudo losetup --find --show -o "$P2_OFFSET_BYTES" "$IMG")
sudo mkfs.ext2 -F "$LOOP_DEV" >/dev/null
# FIX: Use a more reliable here-doc method for debugfs.
sudo debugfs -w "$LOOP_DEV" <<EOF
write $TMP_FILE secret_file.txt
quit
EOF
sudo losetup -d "$LOOP_DEV"
echo "[+] File 'secret_file.txt' written to Partition 2."

echo -e "\n*** DELETING PARTITION 2 FROM PARTITION TABLE ***"
sleep 1
parted -s "$IMG" rm 2
echo "[5] Partition 2 deleted. The data is now orphaned. New layout:"
mmls "$IMG"

echo -e "\n[6] Scanning for lost EXT partitions using a4.py..."
# The python script now only prints the byte offset to stdout
RECOVERED_OFFSET_BYTES=$(sudo ./a4.py -i "$IMG" --find-partitions | grep "^${P2_OFFSET_BYTES}$")
if [[ -z "$RECOVERED_OFFSET_BYTES" ]]; then
    echo "[-] Critical error: Failed to find the lost partition."
    exit 1
fi
RECOVERED_OFFSET_SECTORS=$((RECOVERED_OFFSET_BYTES / 512))
echo "[+] Success! Found partition at offset $RECOVERED_OFFSET_BYTES (sector $RECOVERED_OFFSET_SECTORS)."

echo -e "\n[7] Listing files in the found partition..."
sudo ./a4.py -i "$IMG" --list --offset "$RECOVERED_OFFSET_SECTORS"

echo -e "\n[8] Recovering all files from the partition..."
mkdir -p "$RECOVER_DIR"
sudo ./a4.py -i "$IMG" --recover-all --outdir "$RECOVER_DIR" --offset "$RECOVERED_OFFSET_SECTORS"

echo -e "\n[9] Verifying contents of the recovered file:"
cat "$RECOVER_DIR"/*
echo -e "\n[✅ Demo complete]"