import athos.plugin

class Plugin(athos.plugin.Plugin):
    @athos.plugin.command(regex=r'search( for)? (?P<text>\w+)')
    def search(self, room, event, match):
        self.matrix.api.send_message(room, match.group('text'))