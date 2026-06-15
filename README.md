# postmarketOS port for Samsung Galaxy A12s (SM-A127F)

Porting [postmarketOS](https://postmarketos.org/) to Samsung Galaxy A12s (SM-A127F) with Exynos 850 SoC.

## Device Info

| Feature | Specification |
|---------|--------------|
| SoC | Samsung Exynos 850 (Exynos 3830) |
| CPU | Octa-core 4x Cortex-A55 @ 2.0 GHz + 4x Cortex-A55 @ 1.6 GHz |
| GPU | Mali-G51 MP1 |
| RAM | 3/4/6 GB LPDDR4x |
| Storage | 32/64/128 GB eMMC + microSD |
| Display | 6.5" PLS TFT 720x1600 |
| Battery | 5000 mAh |

## Current Status

- [x] Kernel source identified (mainline mt6763 tree)
- [x] DTS created for Samsung Galaxy A12s
- [x] GitHub Actions CI/CD pipeline configured
- [ ] Kernel boots to console
- [ ] Display working
- [ ] Touchscreen working
- [ ] WiFi working
- [ ] Bluetooth working
- [ ] Camera working
- [ ] Sound working
- [ ] Cellular modem working

## Building

### Via GitHub Actions (Recommended)

Push to main branch or trigger workflow manually. Artifacts will be available in the Actions tab.

### Locally

```bash
# Install dependencies (Ubuntu/Debian)
sudo apt-get install gcc-aarch64-linux-gnu binutils-aarch64-linux-gnu \
    bc bison flex libssl-dev libelf-dev python3 device-tree-compiler

# Clone kernel
git clone --depth=1 https://gitlab.com/mtk-mainline/mt6763/linux.git kernel-tree
cd kernel-tree

# Apply Samsung A12s DTS
cp ../kernel/dts/samsung-a12s.dts arch/arm64/boot/dts/exynos/
sed -i '/exynos850-e850-96.dtb/a\\t\tsamsung-a12s.dtb' arch/arm64/boot/dts/exynos/Makefile

# Build
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- samsung-a12s_defconfig
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j$(nproc) Image dtbs modules
```

## Flashing

### Prerequisites

- [Heimdall](https://github.com/Benjamin-Dobell/Heimdall) installed
- Device in download mode (Volume Up + Volume Down + USB)

### Flash

```bash
# Boot into download mode
# Power off device, then hold Vol Up + Vol Down while connecting USB

# Flash kernel
heimdall flash --BOOT arch/arm64/boot/Image --DTBO arch/arm64/boot/dts/exynos/samsung-a12s.dtb
```

## Project Structure

```
├── .github/workflows/build.yml  # GitHub Actions CI/CD
├── kernel/
│   ├── dts/samsung-a12s.dts    # Device Tree Source
│   └── configs/samsung-a12s_defconfig  # Kernel config
└── pmaports/
    ├── device/device-samsung-a12s/  # Device package
    ├── kernel/linux-postmarketos-samsung-exynos850/  # Kernel package
    ├── firmware/firmware-samsung-a12s/  # Firmware package
    └── soc/soc-samsung-exynos850/  # SoC package
```

## Credits

- [postmarketOS](https://postmarketos.org/) team
- [mtk-mainline](https://gitlab.com/mtk-mainline/mt6763/linux) project for kernel source
- Samsung for hardware documentation

## License

This project is licensed under the GPL-2.0 License.
