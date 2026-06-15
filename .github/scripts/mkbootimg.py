#!/usr/bin/env python3
import struct
import sys

kernel_path = "kernel-tree/arch/arm64/boot/Image"
ramdisk_path = "postmarketos.cpio.gz"
output_path = "boot.img"

with open(kernel_path, "rb") as f:
    kernel = f.read()
with open(ramdisk_path, "rb") as f:
    ramdisk = f.read()

pagesize = 2048
cmdline = b"console=ttyS0,115200n8 root=/dev/mmcblk0p2 rootwait"

header = bytearray(pagesize)
header[0:8] = b"ANDROID!"
struct.pack_into("<I", header, 8, len(kernel))
struct.pack_into("<I", header, 12, 0x00008000)
struct.pack_into("<I", header, 16, len(ramdisk))
struct.pack_into("<I", header, 20, 0x02000000)
struct.pack_into("<I", header, 36, pagesize)
header[16384:16384 + len(cmdline)] = cmdline

with open(output_path, "wb") as f:
    f.write(header)
    f.write(kernel)
    f.write(b"\x00" * ((pagesize - (len(kernel) % pagesize)) % pagesize))
    f.write(ramdisk)

print(f"Created {output_path}: kernel={len(kernel)}B, ramdisk={len(ramdisk)}B")
