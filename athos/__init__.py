import collections
import os
import importlib
import logging

import athos
import athos.plugin
import yaml

import json # TODO: tirar

from matrix_client.client import MatrixClient
from matrix_client.api import MatrixRequestError

log = logging.getLogger(__name__)


class AthosMatrixClient(MatrixClient):
    def send(self, *args, **kwargs):
        kwargs['api_path'] = '/_matrix/client/r0'

        self.api._send(*args, **kwargs)

    def leave_room(self, room):
        self.send(
            'POST',
            '/rooms/%s/leave' % room)

    def accept_invite(self, room, invite):
        try:
            self.send(
                'POST',
                '/rooms/%s/join' % room)
        except MatrixRequestError as e:
            if e.code == 404:
                log.info('The room %s does not exist' % room)

                # dismiss event
                self.leave_room(room)

    def mark_read(self, room, event):
        self.send(
            'POST',
            '/rooms/%s/receipt/m.read/%s' % (room, event['event_id']))

class Athos(object):
    def __init__(self, config):
        self.config = config
        self.handlers = []

        self.matrix = AthosMatrixClient(self.config['matrix']['hostname'])

    def start(self):
        try:
            self.token = self.matrix.login_with_password(
                self.config['matrix']['username'],
                self.config['matrix']['password'],
            )

        except MatrixRequestError as e:
            if e.code == 403:
                log.critical("Wrong username or password.")
            else:
                log.critical("An error ocurred: %s" % e)

            raise e

        # event processing loop
        sync_token = None
        while True:
            response = self.matrix.api.sync(
                since=sync_token,
                timeout_ms=1000,
                filter=self.matrix.sync_filter,
                set_presence='online')
            sync_token = response["next_batch"]

            # accept pending invites
            for room, invite in response['rooms']['invite'].items():
                self.matrix.accept_invite(room, invite)

            # process joined room events
            for room_id, sync_room in response['rooms']['join'].items():
                # last event marked as read
                read_marker = None

                # ephemeral events
                for e in sync_room["ephemeral"]["events"]:
                    # receipt marker
                    if e['type'] == 'm.receipt':

                        for event_id, marker in e['content'].items():
                            if 'm.read' not in marker:
                                continue

                            if self.matrix.user_id in marker['m.read']:
                                read_marker = event_id


                # timeline events
                if len(sync_room["timeline"]["events"]) > 0:
                    for e in sync_room["timeline"]["events"]:
                        if read_marker:
                            if e['event_id'] == read_marker:
                                read_marker = None

                            logging.info('Event %s ignored', e['event_id'])
                            continue

                        # message sent to room
                        if e['type'] == 'm.room.message':

                            if e['content']['msgtype'] == 'm.text':
                                logging.info('New message on %s: %s', room_id, e['content']['body'])

                            self.check_handlers(room_id, e)



                    # mark last event as read
                    self.matrix.mark_read(room_id, e)


    def register_handler(self, handler, options):
        log.debug('Registering handler with options %s', options)

        matchers = []

        if 'type' in options:
            matchers.append(athos.plugin.TypeMatcher(options['type']))

        if 'regex' in options:
            matchers.append(athos.plugin.RegexMatcher(options['regex']))

        self.handlers.append({
            'handler': handler,
            'matchers': matchers
        })

    def check_handlers(self, room, event):
        print('Handlers: %s' % self.handlers)

        for handler in self.handlers:
            kwargs = {}
            match = None

            for matcher in handler['matchers']:
                match = matcher.check(event)

                print('Matcher %s: %s', matcher, match)

                if match is False:
                    break
                elif match is not True:
                    kwargs.update(match)

            # everything is true, call the handler
            if match:
                handler['handler'](room, event, **kwargs)



    def load_plugin(self, plugin):
        """
        Loads a plugin into the Athos core

        :param plugin: Plugin instance
        """

        for name in dir(plugin):
            attribute = getattr(plugin, name)

            try:
                options = attribute._athos
            except AttributeError:
                continue

            self.register_handler(attribute, options)
            log.info('Registered handler %s', attribute)

        logging.info('Loaded %s', plugin)

def main(config):
    """
    Starts the athos core

    :param config list: Config dictionary
    """

    def update(d, u):
        """
        Updates a dictionary recursively.
        The dictionary is edited in-place.

        :param d: Dictionary to be updated
        :param u: Dictionary with the changes
        :return: Updated dictionary
        """
        for k, v in u.items():
            if isinstance(v, collections.Mapping):
                r = update(d.get(k, {}), v)
                d[k] = r
            else:
                d[k] = u[k]
        return d

    # setup logger
    if config['verbose']:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.basicConfig(level=log_level)

    # load the default config
    with open(os.path.join(os.path.dirname(athos.__file__), 'default.yml')) as f:
        default = yaml.load(f)
        config = update(default, config)

    # create an Athos instance
    core = Athos(config)

    # load the plugins
    for plug_name, plug_config in config['plugins'].items():
        plugin_cls = importlib.import_module('athos.plugins.%s' % plug_name).Plugin
        plugin_obj = plugin_cls(core.matrix, plug_config)
        core.load_plugin(plugin_obj)

    # start Athos
    core.start()