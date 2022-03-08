"""Pan.

Setup remote speakers with pulseaudio.
"""
import logging
import asyncio
from pathlib import Path
from aiohttp import web
from cleo import Command, Application
from configparser import ConfigParser
from loguru import logger
import time
import re
import subprocess

REG = re.compile(r"""(?P<key>[\w\-]+)=(?P<value>[\S\s]*?)($|\s)""")
STATIC = (Path(__file__).parent / 'static' / 'dist').absolute()


def kv_pairs(text):
    return {m.group("key"): m.group("value") for m in REG.finditer(text)}


class Sink(dict):
    """Sink"""

    def __init__(self, line):
        names = ['id', 'type', 'module', 'ch', 'freq', 'status']
        self.update(zip(names, line.split('\t')))


class Module(dict):
    """Module"""

    def __init__(self, line):
        names = ['id', 'type', 'args']
        self.update(zip(names, line.split('\t')))
        if self.get('args'):
            self['args'] = kv_pairs(self['args'])
            if 'slaves' in self['args']:
                self['args']['slaves'] = self['args']['slaves'].split(',')
        else:
            self['args'] = None


class AudioSystem:

    def __init__(self, configfile):
        config = ConfigParser()
        config.read(configfile)
        instances = {}
        logger.debug(f'Parsing config {configfile}')
        for pulse_server in config.sections():
            pulse_server = config[pulse_server]
            logger.debug(f'Parsing server {pulse_server}')
            instances[pulse_server.get('ip')] = PulseInstance(
                self, pulse_server.get('ip'), pulse_server.get('status'),
                pulse_server.get('remoteip'), pulse_server.get('defaultsink'))
        self.instances = instances

    @property
    def sorted_instances(self):
        key = lambda x: {'emitter': 1, 'receiver': 2}.get(x.expected_status, 0)
        return sorted(self.instances.values(), key=key)


class PulseInstance:
    """Represents a remote pulseaudio instance"""

    def __init__(self, parent, ip, status, remoteip, defaultsink):
        self.cmd = ['pactl', '-s', ip]
        self.parent = parent
        self.ip = ip
        self.expected_status = status
        self.remoteip = remoteip
        self.defaultsink = defaultsink

    def execute(self, args):
        try:
            return subprocess.check_output(self.cmd + args)
        except Exception as err:
            logger.exception(err)
        return b''

    @property
    def status(self):
        """Check status (emitter, receiver, disabled, corrupted)"""
        # On emitters, make sure that the default sink is combined
        # with the RTP sink so we don't lose local sound
        if self.expected_status == 'emitter':
            if self.combined_sink_status == 'ok':
                if self.get_modules_by_name('module-rtp-send'):
                    logger.debug('rtp-send module enabled, sink matches')
                    return 'emitter'
            return 'corrupted'
        elif self.expected_status == 'receiver':
            # Check if the remote pulse instance on the associated emitter has
            # own ip in rtp emitter
            remote = self.parent.instances[self.remoteip]
            senders = [
                a for a in remote.get_modules_by_name('module-rtp-send')
                if a['args']['destination_ip'] == self.ip
            ]
            if len(senders) != 1:
                logger.debug(f'Number of senders is wrong: {len(senders)}')
                return 'corrupted'
            if self.get_modules_by_name('module-rtp-recv'):
                logger.debug('Receiver module is enabled')
                return 'receiver'
            logger.debug('Receiver module is not enabled')
            return 'corrupted'
        elif self.expected_status == 'disabled':
            remote = self.parent.instances[self.remoteip]
            for module in remote.get_modules_by_name('module-rtp-send'):
                # If any of the remote args matches our ip
                # and we're disabled, we should be "corrupted" so it's dirty
                if module['args']['destination_ip'] == self.remoteip:
                    return 'corrupted'
            if self.get_modules_by_name('module-rtp-recv'):
                # We're a receiver, not disabled
                return 'corrupted'
            return 'disabled'

    def clean(self):
        """Clean.

        Check that we're not the receiving end of any rtp-sender dest.
        Check that we don't have any rtp-recv module loaded
        Unload those if needed
        """
        if mods := self.get_modules_by_name('module-rtp-recv'):
            logger.info(f'Unloading receiver mods: {[a["id"] for a in mods]}')
            for mod in mods:
                self.unload_module(mod['id'])

        if mods := self.get_modules_by_name('module-combine-sink'):
            logger.info(f'Unloading combine mods: {[a["id"] for a in mods]}')
            for mod in mods:
                self.unload_module(mod['id'])

        for remote in self.parent.instances.values():
            if rem_mods := remote.get_modules_by_name('module-rtp-send'):
                for rem_mod in rem_mods:
                    if rem_mod['args']['destination_ip'] == self.ip:
                        remote.unload_module(rem_mod['id'])

    def set_as_receiver(self):
        """Set as receiver (speaker)"""
        logger.debug(f'Loading rtp-recv on {self.ip}')
        self.load_module('module-rtp-recv', 'latency_msec=50',
                         'sap_address=0.0.0.0')
        remote = self.parent.instances[self.remoteip]
        logger.debug(f'Loading rtp-send on {remote.ip}')
        remote.load_module('module-rtp-send', 'source=rtp.monitor',
                           f'destination_ip={self.ip}')
        if ',' in self.defaultsink:
            # Combined default sink on a receiver, check if it's correctly
            # configured and fix it.
            # I was testing if there was a combine sink before, but this i
            # after cleanup, if it's dirty, it'll re-do everything
            self.load_module('module-combine-sink',
                             f'slaves={self.defaultsink}')
            self.set_defaultsink('combined')

    def set_as_emitter(self):
        """Set as emitter (source)"""
        logger.debug(f'Loading null sink for rtp on {self.ip}')
        self.load_module('module-combine-sink',
                         f'slaves=rtp,{self.defaultsink}')
        self.set_defaultsink('combined')

    def load_module(self, mod_name, *args):
        return self.execute(['load-module', mod_name] + list(args))

    def unload_module(self, modid):
        return self.execute(['unload-module', modid])

    def set_defaultsink(self, sink=None):
        sink = sink or self.defaultsink
        return self.execute(['set-default-sink', sink])

    @property
    def dirty(self):
        """Check if it's dirty (needs reconfiguring)"""
        return self.status != self.expected_status

    @property
    def sinks(self):
        """Sinks"""
        sinks = self.execute(['list', 'sinks', 'short'])
        return [Sink(sink) for sink in sinks.decode().split('\n') if sink]

    @property
    def modules(self):
        """Modules"""
        mods = self.execute(['list', 'modules', 'short'])
        return [Module(mod) for mod in mods.decode().split('\n') if mod]

    def get_modules_by_name(self, name):
        return [m for m in self.modules if m['type'] == name]

    @property
    def combined_sink_status(self):
        has_module = False
        for mod in self.get_modules_by_name('module-combine-sink'):
            has_module = True
            stat = ['rtp'] if self.expected_status == 'emitter' else []
            if mod['args']['slaves'] == stat + [self.defaultsink]:
                return 'ok'
        if has_module:
            return 'corrupted'
        else:
            return 'ko'

    def ensure_status(self):
        if not self.dirty:
            logger.info(f'{self.ip} - Status OK, no changes needed')
            return

        logger.info(f'{self.ip} from {self.status} to {self.expected_status}')
        self.clean()
        if self.expected_status == 'receiver':
            self.set_as_receiver()
        elif self.expected_status == 'emitter':
            self.set_as_emitter()


async def watcher(configfile):
    while True:
        audio = AudioSystem(configfile)
        for instance in audio.sorted_instances:
            try:
                logger.debug(f'Checking {instance.ip} status')
                instance.ensure_status()
            except Exception as err:
                logger.exception(err)
        await asyncio.sleep(5)


class Watcher(Command):
    """Watch and setup (if needed) changes on audio system each 5s

    watch
        {--config=? : Set configuration file}
    """

    def handle(self):
        # Setup receivers first.
        asyncio.run(watcher(self.option('config')))


class Config(Command):
    """Configure audio system

    setup
        {--config=? : Set configuration file}
        {--name=? : Source name to setup}
        {--status=? : Status (receiver, emitter, disabled)}
        {--remoteip=? : Remote IP (i.e, emitter if status is receiver)}
        {--defaultsink=? : Default sink to setup pulseaudio to}
    """

    def handle(self):
        configfile = self.option('config')
        config = ConfigParser()
        config.read(configfile)
        name = self.option('name')
        if name not in config.sections():
            config.add_section(name)

        for option in ('ip', 'status', 'remoteip', 'defaultsink'):
            if opt := self.option('option'):
                config[option] = opt

        config.write(open(configfile, 'w'))


APP = web.Application()


class ConfigView(web.View):

    async def get(self):
        config = self.request.app['config']
        conf = {s: dict(config.items(s)) for s in config.sections()}
        return web.json_response(conf)

    async def post(self):
        config = self.request.app['config']
        in_json = await self.request.json()
        for key in in_json:
            if key not in config.sections():
                config.add_section(key)
            for option in ('ip', 'status', 'remoteip', 'defaultsink'):
                if opt := in_json[key].get(option):
                    config[key][option] = opt
        config.write(open(self.request.app['configfile'], 'w'))
        return web.json_response({'status': 'ok'})


async def setup_watcher(app):
    configfile = app['configfile']
    logger.info("Starting background task")
    await asyncio.create_task(watcher(configfile))
    logger.info("Finished bg task")


class Server(Command):
    """Serve API

    serve
        {--config=? : Set configuration file}
        {--host=? : Host}
        {--port=? : Port}
        {--prefix= : Base URL prefix}
    """

    def handle(self):
        configfile = self.option('config')
        prefix = self.option('prefix') or ''
        config = ConfigParser()
        config.read(configfile)
        APP['config'] = config
        APP['configfile'] = configfile
        APP.router.add_routes([
            web.view(f'{prefix}/api/config', ConfigView),
        ])
        APP.router.add_static(f'{prefix}/', str(STATIC))
        # APP.on_startup.append(setup_watcher)
        logging.basicConfig(level=logging.DEBUG)
        web.run_app(APP, host=self.option('host'), port=int(self.option('port'))) 


def main():
    app = Application()
    app.add(Watcher())
    app.add(Config())
    app.add(Server())
    app.run()


if __name__ == "__main__":
    main()
