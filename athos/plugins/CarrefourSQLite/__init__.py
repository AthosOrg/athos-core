import athos.plugin
import sqlite3

class Plugin(athos.plugin.Plugin):
    def __init__(self, matrix, config):
        super().__init__(matrix, config)

        print(config['database'])
        self.conn = sqlite3.connect(config['database'])

    @athos.plugin.command(regex=r'popular (?P<text>.+)(?P<max_results>| \d+)')
    def popular(self, room, event, match):
        search_keyword = match.group('text')
        max_results = min(self.config['max_results'], int(match.group('max_results')) or 5)

        c = self.conn.cursor()
        c.execute(
            '''
                SELECT description, round(avg(cost), 2)
                FROM items
                WHERE description LIKE ?
                GROUP BY description
                ORDER BY count(description) DESC
                LIMIT ?
            ''', ['%%%s%%' % search_keyword, max_results])

        message = 'Results for "%s", sorted by popularity:\n\n' % search_keyword

        for row in c:
            message += '%s - %s %s\n' % (row + (self.config['currency'],))

        self.matrix.api.send_message(room, message)

    @athos.plugin.command(regex=r'cheapest (?P<text>.+?)(?P<max_results>^| \d+)')
    def cheapest(self, room, event, match):
        search_keyword = match.group('text')
        max_results = min(self.config['max_results'], int(match.group('max_results')) or 5)

        c = self.conn.cursor()
        c.execute(
            '''
                SELECT description, round(avg(cost), 2)
                FROM items
                WHERE description LIKE ?
                GROUP BY description
                ORDER BY 2
                LIMIT ?
            ''', ['%%%s%%' % search_keyword, max_results])

        message = 'Results for "%s", sorted by price:\n\n' % search_keyword

        for row in c:
            message += '%s - %s %s\n' % (row + (self.config['currency'],))

        self.matrix.api.send_message(room, message)

    @athos.plugin.command(regex=r'search (?P<product>.+) (?P<lower_limit>\d+) (?P<upper_limit>\d+)')
    def search(self, room, event, match):
        search_keyword = match.group('product')
        max_results = self.config['max_results']
        lower_limit = match.group('lower_limit')
        upper_limit = match.group('upper_limit')

        c = self.conn.cursor()
        #TODO: por o between a funcionar
        c.execute(
            '''
                SELECT description, round(avg(cost), 2)
                FROM items
                WHERE description LIKE ? AND (2 BETWEEN ? AND ?) 
                GROUP BY description
                ORDER BY 2
                LIMIT ?
            ''', ['%%%s%%' % search_keyword, lower_limit, upper_limit, max_results])

        message = 'Results for "%s", between %s and %s %s: \n\n' % (search_keyword, lower_limit, upper_limit,self.config['currency'])

        for row in c:
            message += '%s - %s %s\n' % (row + (self.config['currency'],))

        self.matrix.api.send_message(room, message)        