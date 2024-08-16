# MCU_FLASHER Moonraker Component

This Moonraker component enables the flashing of MCUs via a Klipper command from the Mainsail/Fluidd/KlipperScreen console.

## Installation

To install the MCU_FLASHER component, follow these steps:

1. Clone the repository:

   ```bash
   cd ~
   git clone https://github.com/juliapythoncpp/moonraker-mcu-flasher.git
   ```

2. Create symbolic links for the necessary files:

   ```bash
   ln -s moonraker-mcu-flasher/moonraker/mcu_flasher.py moonraker/moonraker/components/mcu_flasher.py
   ln -s moonraker-mcu-flasher/klipper_macro/mcu_flasher.klipper_macro.cfg printer_data/config/macros/mcu_flasher.cfg
   ```

    >⚠️ Ensure that the paths are consistent with your installation

3. Update your `moonraker.conf` file by adding `[mcu_flasher mcu_name]` sections for each MCU you wish to manage.

4. Add `[include macros/mcu_flasher.cfg]` to your `printer.cfg` file.

## Configuration

### Mcu_flasher sections

In your `moonraker.conf` file, add a section for each MCU you want to flash. Here is the template:

```ini
[mcu_flasher mcu_name] 
kconfig: 
  # Contains the `menuconfig` options for this mcu.
flash_cmd:
  # Command to flash the MCU (see below for details)
silent: True  # Enable to suppress all standard output messages
```

### flash_cmd examples

These are the exact commands you would typically type in your SSH shell to flash the MCU.

Some examples could be:

- klipper way: `make flash FLASH_DEVICE=/dev/serial/by-id/ID`
- if using canbus and katapult bootloader: `python3 ~/katapult/scripts/flashtool.py -i can0 -f ~/klipper/out/klipper.bin -u e3e8e93f53df`
- Or if multiple MCUs use the same firmware, you can flash them in sequence without recompiling Klipper

  ```bash
  flash_cmd:
    make flash FLASH_DEVICE=/dev/serial/by-id/ID1
    make flash FLASH_DEVICE=/dev/serial/by-id/ID2
  ```

For configuration examples, refer to the [example_mcu_flasher.moonraker.cfg](moonraker/example_mcu_flasher.moonraker.cfg) file in the repository.

## Usage / MCU flashing

You can flash the mcus from the Mainsail/Fluidd console:

- `FLASH_MCU mcu=all` to flash all mcus (in the declared order)
- `FLASH_MCU mcu=foobar` to flash the mcu named foobar
