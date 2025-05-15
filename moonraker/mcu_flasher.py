from __future__ import annotations
import logging
import os
import shutil
import subprocess

# Annotation imports
from typing import (
    TYPE_CHECKING,
    Dict,
    Literal,
)
if TYPE_CHECKING:
    from confighelper import ConfigHelper
    from .klippy_apis import KlippyAPI
    from .klippy_connection import KlippyConnection
    from .machine import Machine

from .shell_command import ShellCommandError


class McuFlasher:
    def __init__(self, config: ConfigHelper) -> None:
        self.mcus: Dict[str, Mcu] = {}
        self.server = config.get_server()
        self.kconn: KlippyConnection = self.server.lookup_component("klippy_connection")
        self.klippy_api: KlippyAPI = self.kconn.klippy_apis
        prefix_sections = config.get_prefix_sections("mcu_flasher")
        logging.info(f"Loading MCU flashers: {prefix_sections}")
        for section in prefix_sections:
            cfg = config[section]
            mcu_name = cfg.get_name().split(maxsplit=1)[-1].lower()
            try:
                mcu = Mcu(mcu_name, self.kconn.path, cfg)
                self.mcus[mcu_name] = mcu
                logging.info(f"Flashers for MCU '{mcu_name}' registered")
            except Exception as e:
                msg = f"Failed to load MCU flasher [{mcu_name}]\n{e}"
                self.server.add_warning(msg)
                continue
        self.server.register_remote_method("flash_mcu", self._call_flash_mcu)
    async def _call_flash_mcu(self, mcu: str = "all") -> None:
        if self.kconn.is_printing():
            raise self.server.error("Flashing Refused: Klippy is printing")
        mcu = mcu.lower()
        ks = self.mcus.keys() if mcu == "all" else [mcu]
        machine: Machine = self.server.lookup_component("machine")
        await machine.do_service_action("stop", "klipper")
        for m in ks:
            await self.mcus[m].flash()
        await machine.do_service_action("start", "klipper")
        await self.klippy_api.do_restart("FIRMWARE_RESTART")

class Mcu:
    def __init__(self, name: str, klipper_path: str, config: ConfigHelper):
        self.server = config.get_server()
        self.name: str = name
        self.klipper_path = klipper_path
        self.kconfig: str = config.get('kconfig').strip()
        self.flash_cmd: str = config.get('flash_cmd')
        self.silent: bool = config.get('silent', False)
    def _make_kconfig(self, kconfig_filename):
        try:
            src = os.path.expanduser(self.kconfig)
            if not os.path.isabs(src):
                src = os.path.join(self.klipper_path, src)
            if os.path.isfile(src):
                shutil.copy(src, kconfig_filename)
            else:
                tmp = os.path.join(self.klipper_path, ".defconfig.tmp")
                with open(tmp, "w") as f:
                    f.write(self.kconfig)
                shutil.copy(tmp, kconfig_filename)
            env = os.environ.copy()
            env["KCONFIG_CONFIG"] = kconfig_filename
            kconf_script = os.path.join(self.klipper_path, "lib", "kconfiglib", "olddefconfig.py")
            kconfig_src   = os.path.join(self.klipper_path, "src", "Kconfig")
            subprocess.check_call(
                ["python3", kconf_script, kconfig_src],
                cwd=self.klipper_path,
                env=env
            )
        except Exception:
            logging.exception("Failed to write kconfig file")
            raise self.server.error("Error writing kconfig file")
    def _log(self, msg: str, prefix: Literal['//', '!!'] = '//'):
        marker = '!!' if type=='err' else '//'
        msg = f"{prefix} {msg}"
        logging.info(msg)
        self.server.send_event('server:gcode_response', msg)
    async def _run_cmd(self, cmd: str):
        cmd = cmd.strip(' \n')
        if len(cmd) == 0:
            return
        self._log(f"> {cmd}")
        cmd = f"bash -c '{cmd}{ ' >/dev/null' if self.silent else '' }'"
        shell_cmd = self.server.lookup_component("shell_command")
        def decode(msg):
            if isinstance(msg, bytes):
                msg = msg.decode()
            return msg
        await shell_cmd.run_cmd_async(cmd,
            lambda out: self._log(f"  {decode(out)}"),
            lambda err: self._log(f"  {decode(err)}", '!!'),
            timeout=300, log_stderr=True, cwd=self.klipper_path)
    async def flash(self) -> None:
        self._log(f"<<<<<<<<<<<<<<< {self.name}: start flashing... >>>>>>>>>>>>>>")
        try:
            kconfig_filename = os.path.join(self.klipper_path, ".config")
            self._make_kconfig(kconfig_filename)
            make_cmd = f"make KCONFIG_CONFIG={kconfig_filename}"
            logging.info(f"mcu_flasher: Compile firmware for '{self.name}'...")
            await self._run_cmd(f"{make_cmd} olddefconfig")
            await self._run_cmd(f"{make_cmd}")
            logging.info(f"mcu_flasher: Flash firmware on '{self.name}'...")
            for cmd in self.flash_cmd.split('\n'):
                await self._run_cmd(cmd)
            logging.info(f"mcu_flasher: Firmware flashed successfully on '{self.name}'")
            self._log(f"  {self.name}: flashing SUCCEED\n")
        except ShellCommandError as e:
            logging.exception(f"Flashing of '{self.name}' failed, stderr: {e.stderr}")
            self._log(f"  {self.name}: flashing FAILED\n", '!!')
def load_component(config: ConfigHelper) -> McuFlasher:
    return McuFlasher(config)
