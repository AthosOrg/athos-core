import athos.plugin
import sqlite3

class Plugin(athos.plugin.Plugin):
    def __init__(self, matrix, config):
        super().__init__(matrix, config)

        self.conn = sqlite3.connect(config['database'])

    @athos.plugin.command(regex=r'popular (?P<text>\w+)')
    def popular(self, room, event, match):
        search_keyword = match.group('text')

        c = self.conn.cursor()
        c.execute(
            '''
                SELECT description, round(avg(cost), 2)
                FROM items
                WHERE description LIKE ?
                GROUP BY description
                ORDER BY count(description) DESC
                LIMIT 5
            ''', ['%%%s%%' % search_keyword])

        message = 'Results for "%s", sorted by popularity:\n\n' % search_keyword

        for row in c:
            message += '%s - %s %s\n' % (row + (self.config['currency'],))

        self.matrix.api.send_message(room, message)

    @athos.plugin.command(regex=r'cheapest (?P<text>\w+)')
    def cheapest(self, room, event, match):
        search_keyword = match.group('text')

        c = self.conn.cursor()
        c.execute(
            '''
                SELECT description, round(avg(cost), 2)
                FROM items
                WHERE description LIKE ?
                GROUP BY description
                ORDER BY 2
                LIMIT 5
            ''', ['%%%s%%' % search_keyword])

        message = 'Results for "%s", sorted by price:\n\n' % search_keyword

        for row in c:
            message += '%s - %s %s\n' % (row + (self.config['currency'],))

        self.matrix.api.send_message(room, message)