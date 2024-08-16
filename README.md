# MCU_FLASHER Moonraker Component

This Moonraker component enables the flashing of MCUs via a G-code command.

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

3. Update your `moonraker.conf` file by adding `[mcu_flasher mcu_name]` sections for each MCU you wish to manage.

## Configuration

### MCU_Flasher Sections

In your `moonraker.conf` file, add a section for each MCU you want to flash. Here is the template:

```ini
[mcu_flasher mcu_name] 
kconfig: 
  # Configuration options specific to this MCU
flash_cmd:
  # Command to flash the MCU
  # Additional commands for flashing others MCUs with the same firmware
silent: True  # Enable to suppress all standard output messages
```

For configuration examples, refer to the [example_mcu_flasher.moonraker.cfg](moonraker/example_mcu_flasher.moonraker.cfg) file in the repository.

## MCUs Flashing

Type in the Mainsail/Fluidd console:

- `FLASH_MCU mcu=all` to flash all mcus (in the declared order)
- `FLASH_MCU mcu=foobar` to flash the mcu named foobar
