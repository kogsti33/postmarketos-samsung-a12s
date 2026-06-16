#!/usr/bin/env python3
"""
Create Samsung Exynos-compatible boot.img.

Samsung Exynos 850 uses a different boot image format than standard Android.
The BOOT partition contains raw kernel Image + DTB, no special header.
For Heimdall, we flash the raw Image directly.
"""
import struct
import sys
import os

kernel_path = sys.argv[1] if len(sys.argv) > 1 else "kernel-tree/arch/arm64/boot/Image"
dtb_path = sys.argv[2] if len(sys.argv) > 2 else "kernel-tree/arch/arm64/boot/dts/exynos/samsung-a12s.dtb"
output_path = sys.argv[3] if len(sys.argv) > 3 else "boot.img"

with open(kernel_path, "rb") as f:
    kernel = f.read()

print(f"Kernel size: {len(kernel)} bytes ({len(kernel)/1024/1024:.1f} MB)")
print(f"Kernel starts with: {kernel[:4].hex()}")

# Samsung Exynos 850 (SM-A127F) BOOT partition layout:
# The kernel is flashed raw via Heimdall.
# For boot.img format, Samsung uses a proprietary header.
#
# However, for postmarketOS on Exynos devices, the recommended
# approach is to flash Image and DTB separately via Heimdall:
#   heimdall flash --BOOT arch/arm64/boot/Image
#
# If creating boot.img is needed, use the Samsung-specific format:
# Header (2048 bytes):
#   0x000-0x007: "ANDROID!" magic
#   0x008-0x00B: kernel size
#   0x00C-0x00F: kernel load address
#   0x010-0x013: ramdisk size (0 for raw kernel)
#   0x014-0x017: ramdisk load address
#   0x018-0x01B: second stage size
#   0x01C-0x01F: second stage load address
#   0x020-0x023: tags address
#   0x024-0x027: page size
#   0x028-0x02B: header version
#   0x02C-0x02F: OS version
#   0x030-0x03F: name
#   0x040-0x0FF: cmdline (null-terminated)
#   ... padded to page size

pagesize = 2048
cmdline = b"console=ttyS0,115200n8 root=/dev/mmcblk0p2 rootwait androidboot.hardware=exynos850"

header = bytearray(pagesize)
# Magic
header[0:8] = b"ANDROID!"
# Kernel size
struct.pack_into("<I", header, 8, len(kernel))
# Kernel addr
struct.pack_into("<I", header, 12, 0x00008000)
# Ramdisk size (0 - no ramdisk)
struct.pack_into("<I", header, 16, 0)
# Ramdisk addr
struct.pack_into("<I", header, 20, 0x02000000)
# Page size
struct.pack_into("<I", header, 36, pagesize)
# Header version
struct.pack_into("<I", header, 40, 0)
# Cmdline
header[16384:16384 + len(cmdline)] = cmdline

with open(output_path, "wb") as f:
    f.write(header)
    f.write(kernel)
    # Pad to page boundary
    pad = (pagesize - (len(kernel) % pagesize)) % pagesize
    if pad:
        f.write(b"\x00" * pad)

print(f"Created {output_path}: {os.path.getsize(output_path)} bytes")
print("")
print("NOTE: Samsung Exynos 850 may not accept this boot.img format.")
print("For recovery, use Heimdall to flash raw Image:")
print(f"  heimdall flash --BOOT {kernel_path}")
