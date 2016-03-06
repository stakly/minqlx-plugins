# This plugin created by stakly <root@qw3rty.org>
# Copyright (c) 2016 stakly
#
# This plugin displays end round damage statistic and best round damager
# Supported gametypes: clanarena, domination, freezetag
# test

import minqlx
from collections import defaultdict

VERSION = 'v0.2'
SUPPORTED_GAMETYPES = ('ca', 'dom', 'ft')


class rdamage(minqlx.Plugin):
    def __init__(self):
        super().__init__()

        self.add_hook('game_start', self.handle_game_start)
        self.add_hook('round_start', self.handle_round_start)
        self.add_hook('round_end', self.handle_round_end)
        self.add_hook('kill', self.handle_kill)

        self.allplayers = defaultdict(dict)
        self.game_supported = True

    def handle_game_start(self, data):
        try:
            gt = self.game.type_short
            if gt not in SUPPORTED_GAMETYPES:
                self.game_supported = False
                return minqlx.RET_STOP_ALL
        except AttributeError:
            return minqlx.RET_STOP_ALL

    def handle_round_start(self, round_number):
        if not self.game_supported:
            return minqlx.RET_STOP

        teams = self.teams()
        red_start = teams['red'].copy()
        blue_start = teams['blue'].copy()

        for p in red_start:
            self.allplayers[p.name] = {}
            self.allplayers[p.name]['team'] = 'red'
            self.allplayers[p.name]['damage'] = p.stats.damage_dealt
            self.allplayers[p.name]['frags'] = 0

        for p in blue_start:
            self.allplayers[p.name] = {}
            self.allplayers[p.name]['team'] = 'blue'
            self.allplayers[p.name]['damage'] = p.stats.damage_dealt
            self.allplayers[p.name]['frags'] = 0

    def handle_kill(self, victim, killer, data):
        if not self.game_supported:
            return minqlx.RET_STOP

        if not data['WARMUP']:
            try:
                self.allplayers[killer.name]['frags'] += 1
            except KeyError:
                return minqlx.RET_STOP

    def handle_round_end(self, data):
        if not self.game_supported:
            return minqlx.RET_STOP

        teams = self.teams()
        red_end = teams['red'].copy()
        blue_end = teams['blue'].copy()
        self.msg("^3*** ROUND {} END ***".format(data['ROUND']))
        try:
            self.msg('^1RED SCORES: {}, PLAYERS ROUND DAMAGE:'.format(self.game.red_score))
            for p in red_end:
                frags = self.allplayers[p.name]['frags']
                frags_msg = ''
                if frags > 0:
                    end = 'S' if frags > 1 else ''
                    frags_msg = ' ({} FRAG{})'.format(frags, end)
                self.allplayers[p.name]['damage'] = p.stats.damage_dealt-self.allplayers[p.name]['damage']
                if self.allplayers[p.name]['damage'] >= 0:
                    self.msg('^1  {0:<15} ^1: ^1{1}{2}'.format(p.name, self.allplayers[p.name]['damage'], frags_msg))
        except AttributeError:
            return minqlx.RET_STOP

        try:
            self.msg('^4BLUE SCORES: {}, PLAYERS ROUND DAMAGE:'.format(self.game.blue_score))
            for p in blue_end:
                frags = self.allplayers[p.name]['frags']
                frags_msg = ''
                if frags > 0:
                    end = 'S' if frags > 1 else ''
                    frags_msg = ' ({} FRAG{})'.format(frags, end)
                self.allplayers[p.name]['damage'] = p.stats.damage_dealt-self.allplayers[p.name]['damage']
                if self.allplayers[p.name]['damage'] >= 0:
                    self.msg('^4  {0:<15} ^4: ^4{1}{2}'.format(p.name, self.allplayers[p.name]['damage'], frags_msg))
        except AttributeError:
            return minqlx.RET_STOP

        n1player = next(iter (sorted(self.allplayers.items(), key=lambda x: x[1]['damage'], reverse=True)))
        self.allplayers.clear()

        nickname = n1player[0]
        damage = n1player[1]['damage']
        team = n1player[1]['team']
        if team is 'red':
            color = 1
        elif team is 'blue':
            color = 4
        else:
            color = 7

        if damage > 0:
            frags = n1player[1]['frags']
            frags_msg = ''
            if frags > 0:
                end = 'S' if frags > 1 else ''
                frags_msg = ' ^3WITH ^{}{} ^3FRAG{}'.format(color, frags, end)
            self.msg('^3*** MOST DAMAGE ^{}{} ^3BY ^{}{}{} ^3***'
                     .format(color, damage, color, nickname, frags_msg))
