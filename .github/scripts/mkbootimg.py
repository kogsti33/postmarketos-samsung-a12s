#!/usr/bin/env python3
"""
Create Samsung Exynos 850 compatible boot.img
Based on analysis of stock Samsung boot.img (SM-A127F)
"""
import struct
import sys
import os

kernel_path = sys.argv[1] if len(sys.argv) > 1 else "kernel-tree/arch/arm64/boot/Image"
ramdisk_path = sys.argv[2] if len(sys.argv) > 2 else ""
output_path = sys.argv[3] if len(sys.argv) > 3 else "boot.img"

with open(kernel_path, "rb") as f:
    kernel = f.read()

ramdisk = b""
if ramdisk_path and os.path.exists(ramdisk_path):
    with open(ramdisk_path, "rb") as f:
        ramdisk = f.read()

pagesize = 2048

# Samsung Exynos 850 (SM-A127F) boot parameters
# Derived from stock boot.img analysis
KERNEL_ADDR  = 0x10008000
RAMDISK_ADDR = 0x11000000
TAGS_ADDR    = 0x10000100
CMDLINE      = b"androidboot.hardware=exynos850 androidboot.selinux=enforce loop.max_part=7 console=ttyS0,115200n8"

# Build header (page 1)
header = bytearray(pagesize)

# Magic
header[0:8] = b"ANDROID!"
# Kernel size
struct.pack_into("<I", header, 8, len(kernel))
# Kernel addr
struct.pack_into("<I", header, 12, KERNEL_ADDR)
# Ramdisk size
struct.pack_into("<I", header, 16, len(ramdisk))
# Ramdisk addr
struct.pack_into("<I", header, 20, RAMDISK_ADDR)
# Second stage size (0)
struct.pack_into("<I", header, 24, 0)
# Second stage addr (0)
struct.pack_into("<I", header, 28, 0)
# Tags addr
struct.pack_into("<I", header, 32, TAGS_ADDR)
# Page size
struct.pack_into("<I", header, 36, pagesize)
# Header version (2 for Samsung)
struct.pack_into("<I", header, 40, 2)
# OS version
struct.pack_into("<I", header, 44, 0)
# Name (16 bytes)
name = b"SRPUE06B013"
header[48:48+len(name)] = name
# Cmdline (512 bytes at offset 64)
header[64:64+len(CMDLINE)] = CMDLINE

with open(output_path, "wb") as f:
    f.write(header)
    # Kernel
    f.write(kernel)
    # Pad to page boundary
    pad = (pagesize - (len(kernel) % pagesize)) % pagesize
    if pad:
        f.write(b"\x00" * pad)
    # Ramdisk
    if ramdisk:
        f.write(ramdisk)
        # Pad to page boundary
        pad = (pagesize - (len(ramdisk) % pagesize)) % pagesize
        if pad:
            f.write(b"\x00" * pad)

print(f"Created {output_path}:")
print(f"  Kernel:   {len(kernel):,} bytes ({len(kernel)/1024/1024:.1f} MB)")
print(f"  Ramdisk:  {len(ramdisk):,} bytes ({len(ramdisk)/1024/1024:.1f} MB)")
print(f"  Total:    {os.path.getsize(output_path):,} bytes ({os.path.getsize(output_path)/1024/1024:.1f} MB)")
print(f"  kernel_addr:  0x{KERNEL_ADDR:08x}")
print(f"  ramdisk_addr: 0x{RAMDISK_ADDR:08x}")
print(f"  header_version: 2")
