# This plugin created by stakly <root@qw3rty.org>
# Copyright (c) 2016 stakly
#
# This plugin displays end round damage statistic and best round damager
# Supported gametypes: clanarena, domination, freezetag

import minqlx
from collections import defaultdict

VERSION = 'v0.4'
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

        self.allplayers.clear()
        teams = self.teams()
        red_start = teams['red'].copy()
        blue_start = teams['blue'].copy()

        for p in red_start:
            self.fill_dict(p, 'red')

        for p in blue_start:
            self.fill_dict(p, 'blue')

    def handle_kill(self, victim, killer, data):
        if not self.game_supported:
            return minqlx.RET_STOP

        if not data['WARMUP']:
            try:
                self.allplayers[killer.steam_id]['frags'] += 1
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
                self.team_message(p)
        except AttributeError:
            return minqlx.RET_STOP

        try:
            self.msg('^4BLUE SCORES: {}, PLAYERS ROUND DAMAGE:'.format(self.game.blue_score))
            for p in blue_end:
                self.team_message(p)
        except AttributeError:
            return minqlx.RET_STOP

        leader = next(iter(sorted(self.allplayers.items(), key=lambda x: x[1]['damage'], reverse=True)))
        looser = next(iter(sorted(self.allplayers.items(), key=lambda x: x[1]['damage'])))
        self.summary_message(leader, 'MOST DAMAGE')
        self.summary_message(looser, 'LEAST DAMAGE')

    def fill_dict(self, player, team):
        p = player
        self.allplayers[p.steam_id] = {}
        self.allplayers[p.steam_id]['name'] = p.clean_name
        self.allplayers[p.steam_id]['team'] = team
        self.allplayers[p.steam_id]['damage'] = p.stats.damage_dealt
        self.allplayers[p.steam_id]['frags'] = 0

    def team_message(self, player):
        p = player
        frags = self.allplayers[p.steam_id]['frags']
        frags_msg = ''
        if frags > 0:
            end = 'S' if frags > 1 else ''
            frags_msg = ' ({} FRAG{})'.format(frags, end)
        self.allplayers[p.steam_id]['damage'] = p.stats.damage_dealt-self.allplayers[p.steam_id]['damage']
        damage = self.allplayers[p.steam_id]['damage']
        if damage >= 0:
            frags_msg = ' ^3(AFK?)' if damage == 0 else frags_msg
            self.msg('^1  {0:<20}^1: ^1{1:<5}{2}'
                     .format(p.clean_name, self.allplayers[p.steam_id]['damage'], frags_msg))

    def summary_message(self, player_dict, text_prefix):
        nickname = player_dict[1]['name']
        damage = player_dict[1]['damage']
        team = player_dict[1]['team']
        if team is 'red':
            color = 1
        elif team is 'blue':
            color = 4
        else:
            color = 7

        if damage >= 0:
            frags = player_dict[1]['frags']
            frags_msg = ' ^3(AFK?)' if damage == 0 else ''
            if frags > 0:
                end = 'S' if frags > 1 else ''
                frags_msg = ' ^3WITH ^{}{} ^3FRAG{}'.format(color, frags, end)
            self.msg('^3*** {} ^{}{} ^3BY ^{}{}{} ^3***'
                     .format(text_prefix, color, damage, color, nickname, frags_msg))
