#!/usr/bin/env python3
"""
Create Samsung Exynos 850 compatible boot.img
Samsung requires DTB appended to kernel Image.
"""
import struct
import sys
import os

kernel_path = sys.argv[1] if len(sys.argv) > 1 else "kernel-tree/arch/arm64/boot/Image"
dtb_path = sys.argv[2] if len(sys.argv) > 2 else "kernel-tree/arch/arm64/boot/dts/exynos/samsung-a12s.dtb"
ramdisk_path = sys.argv[3] if len(sys.argv) > 3 else ""
output_path = sys.argv[4] if len(sys.argv) > 4 else "boot.img"

with open(kernel_path, "rb") as f:
    img = bytearray(f.read())

with open(dtb_path, "rb") as f:
    dtb = f.read()

# Append DTB to kernel Image (Samsung requirement)
combined = bytearray(img + dtb)
struct.pack_into("<Q", combined, 16, len(combined))

ramdisk = b""
if ramdisk_path and os.path.exists(ramdisk_path):
    with open(ramdisk_path, "rb") as f:
        ramdisk = f.read()

pagesize = 2048
KERNEL_ADDR  = 0x10008000
RAMDISK_ADDR = 0x11000000
TAGS_ADDR    = 0x10000100
CMDLINE      = b"androidboot.hardware=exynos850 androidboot.selinux=enforce loop.max_part=7 console=ttyS0,115200n8"

header = bytearray(pagesize)
header[0:8] = b"ANDROID!"
struct.pack_into("<I", header, 8, len(combined))
struct.pack_into("<I", header, 12, KERNEL_ADDR)
struct.pack_into("<I", header, 16, len(ramdisk))
struct.pack_into("<I", header, 20, RAMDISK_ADDR)
struct.pack_into("<I", header, 24, 0)
struct.pack_into("<I", header, 28, 0)
struct.pack_into("<I", header, 32, TAGS_ADDR)
struct.pack_into("<I", header, 36, pagesize)
struct.pack_into("<I", header, 40, 2)
struct.pack_into("<I", header, 44, 0x1a00018a)
header[48:64] = b"SRPUE06B013\x00\x00\x00\x00\x00"
header[64:64+len(CMDLINE)] = CMDLINE

with open(output_path, "wb") as f:
    f.write(header)
    f.write(combined)
    f.write(b"\x00" * ((pagesize - (len(combined) % pagesize)) % pagesize))
    if ramdisk:
        f.write(ramdisk)
        f.write(b"\x00" * ((pagesize - (len(ramdisk) % pagesize)) % pagesize))

print(f"Created {output_path}:")
print(f"  kernel+dtb: {len(combined):,} bytes ({len(combined)/1024/1024:.1f} MB)")
print(f"  ramdisk:    {len(ramdisk):,} bytes")
print(f"  Total:      {os.path.getsize(output_path):,} bytes ({os.path.getsize(output_path)/1024/1024:.1f} MB)")
print(f"  DTB appended: YES (Samsung requirement)")
