#!/usr/bin/env python3
"""
Create Samsung Exynos 850 compatible boot.img
Samsung requires:
1. DTBO header (magic d7b7ab1e) appended to kernel Image
2. ANDROID! boot.img header v2
3. kernel_addr=0x10008000, ramdisk_addr=0x11000000
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

# Build DTBO block (big-endian): header(28) + entry(32) + DTB
header_size = 28
entry_size = 32
dtbo_data_offset = header_size + entry_size

dtbo_header = bytearray(header_size)
struct.pack_into(">I", dtbo_header, 0, 0xd7b7ab1e)
struct.pack_into(">I", dtbo_header, 4, dtbo_data_offset + len(dtb))
struct.pack_into(">I", dtbo_header, 8, entry_size)
struct.pack_into(">I", dtbo_header, 12, 1)
struct.pack_into(">I", dtbo_header, 16, header_size)
struct.pack_into(">I", dtbo_header, 20, 4096)
struct.pack_into(">I", dtbo_header, 24, 0)

dtbo_entry = bytearray(entry_size)
struct.pack_into(">I", dtbo_entry, 0, dtbo_data_offset)
struct.pack_into(">I", dtbo_entry, 4, len(dtb))
for i in range(4):
    struct.pack_into(">I", dtbo_entry, 16 + i*4, 0xFFFFFFFF)

dtbo_block = bytes(dtbo_header) + bytes(dtbo_entry) + dtb
combined = bytearray(img + dtbo_block)
struct.pack_into("<Q", combined, 16, len(combined))

# Read ramdisk
ramdisk = b""
if ramdisk_path and os.path.exists(ramdisk_path):
    with open(ramdisk_path, "rb") as f:
        ramdisk = f.read()

# Build boot.img (header v2, Samsung Exynos 850)
pagesize = 2048
header = bytearray(pagesize)
header[0:8] = b"ANDROID!"
struct.pack_into("<I", header, 8, len(combined))
struct.pack_into("<I", header, 12, 0x10008000)
struct.pack_into("<I", header, 16, len(ramdisk))
struct.pack_into("<I", header, 20, 0x11000000)
struct.pack_into("<I", header, 32, 0x10000100)
struct.pack_into("<I", header, 36, pagesize)
struct.pack_into("<I", header, 40, 2)
struct.pack_into("<I", header, 44, 0x1a00018a)
header[48:64] = b"SRPUE06B013\x00\x00\x00\x00\x00"
cmdline = b"androidboot.hardware=exynos850 androidboot.selinux=enforce loop.max_part=7 console=ttyS0,115200n8"
header[64:64+len(cmdline)] = cmdline

with open(output_path, "wb") as f:
    f.write(header)
    f.write(combined)
    f.write(b"\x00" * ((pagesize - (len(combined) % pagesize)) % pagesize))
    if ramdisk:
        f.write(ramdisk)
        f.write(b"\x00" * ((pagesize - (len(ramdisk) % pagesize)) % pagesize))

print(f"Created {output_path}:")
print(f"  kernel+dtbo: {len(combined):,} bytes ({len(combined)/1024/1024:.1f} MB)")
print(f"  DTBO magic:  0xd7b7ab1e (Samsung requirement)")
print(f"  ramdisk:     {len(ramdisk):,} bytes")
print(f"  Total:       {os.path.getsize(output_path):,} bytes ({os.path.getsize(output_path)/1024/1024:.1f} MB)")
