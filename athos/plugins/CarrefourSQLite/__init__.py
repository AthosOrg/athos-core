import athos.plugin
import sqlite3

class Plugin(athos.plugin.Plugin):
    def __init__(self, matrix, athos, config):
        super().__init__(matrix, athos, config)

        print(config['database'])
        self.conn = sqlite3.connect(config['database'])

    @athos.plugin.command(regex=r'help(?P<command> .+|)')
    def help(self, room, event, match):
        command = match.group('command').strip()

        if command == '':
            message = 'Available commands: '

            commands = []
            for handler in self.athos.handlers:
                if handler.get('description'):
                    commands.append(handler['description'].split(' ')[0])

            message += ', '.join(commands)

            self.matrix.api.send_message(room, message)

        else:
            for handler in self.athos.handlers:
                if handler.get('description'):
                    if handler['description'].split(' ')[0].lower() == command.lower():
                        self.matrix.api.send_message(room, handler['description'])
                        return
            
            self.matrix.api.send_message(room, 'The specified command does not exist')


    @athos.plugin.command(
        regex=r'popular (?P<text>.+)',
        description='popular <product>: Searches for the most bought products.\n   Example: popular vino')
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

    @athos.plugin.command(regex=r'cheapest (?P<text>.+)',
        description='cheapest <product>: Searches for the lowest price products.\n   Example: cheapest pano')
    def cheapest(self, room, event, match,):
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

    @athos.plugin.command(regex=r'find (?P<product>.+) (?P<lower_limit>\d+) (?P<upper_limit>\d+)',
        description='find <product> <low> <high>: Finds products between two prices.\n   Example: find queso 1 3')
    def search(self, room, event, match):
        search_keyword = match.group('product')
        lower_limit = int(match.group('lower_limit'))
        upper_limit = int(match.group('upper_limit'))

        c = self.conn.cursor()
        c.execute(
            '''
                SELECT description, round(avg(cost), 2) AS avg_price
                FROM items
                WHERE (description LIKE ?)
                GROUP BY description
                HAVING (avg_price BETWEEN ? AND ?)
                ORDER BY count(description)
                LIMIT 5
            ''', ['%%%s%%' % search_keyword, lower_limit, upper_limit])

        message = 'Results for "%s", between %s and %s %s, sorted by popularity: \n\n' % (search_keyword, lower_limit, upper_limit,self.config['currency'])

        for row in c:
            message += '%s - %s %s\n' % (row + (self.config['currency'],))

        self.matrix.api.send_message(room, message)

    @athos.plugin.command(regex=r'browse (?P<country>.+)',
        description='browse <country>: Gets carrefour website url for a country.\n   Example: browse Spain')
    def browse(self, room, event, match):
        country = match.group('country')
        url = 'http://www.carrefour.com/worldmap/ajax/getlinks/' + country.lower() + '/primary/'

        message = 'URL for %s Carrefour: %s \n' % (country, url)

        self.matrix.api.send_message(room, message)        

    @athos.plugin.command(regex=r'expensive (?P<text>.+)',
        description='expensive <product>: Searches for the highest price products.\n   Example: expensive pano')
    def expensive(self, room, event, match,):
        search_keyword = match.group('text')
    
        c = self.conn.cursor()
        c.execute(
            '''
                SELECT description, round(avg(cost), 2)
                FROM items
                WHERE description LIKE ?
                GROUP BY description
                ORDER BY 2 desc
                LIMIT 5
            ''', ['%%%s%%' % search_keyword])

        message = 'Results for "%s", sorted by price:\n\n' % search_keyword

        for row in c:
            message += '%s - %s %s\n' % (row + (self.config['currency'],))

        self.matrix.api.send_message(room, message)