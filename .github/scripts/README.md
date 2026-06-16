# postmarketOS for Samsung Galaxy A12s (SM-A127F)

## Flash via Odin
1. Enter Download Mode: Vol+Vol- + USB
2. Open Odin3
3. Put boot.img in BL field
4. Click Start

## Flash via TWRP
dd if=/sdcard/boot.img of=/dev/block/by-name/boot

## Files
- boot.img - Kernel + DTB + initramfs
- samsung-a12s.dtb - Device Tree Blob
