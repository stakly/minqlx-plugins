# This plugin created by stakly <root@qw3rty.org>
# Copyright (c) 2016 stakly
#
# This plugin displays end round damage statistic and best round damager
# Supported gametypes: clanarena, domination, freezetag

import minqlx
from collections import defaultdict

VERSION = "v0.1"
SUPPORTED_GAMETYPES = ("ca", "dom", "ft")


class rdamage(minqlx.Plugin):
    def __init__(self):
        super().__init__()

        self.add_hook("game_start", self.handle_game_start)
        self.add_hook("round_start", self.handle_round_start)
        self.add_hook("round_end", self.handle_round_end)

        self.red_start = defaultdict(int)
        self.blue_start = defaultdict(int)
        self.game_supported = True

    def handle_game_start(self, game):
        try:
            gt = self.game.type_short
            if gt not in SUPPORTED_GAMETYPES:
                return minqlx.RET_STOP_ALL
                self.game_supported = False
        except AttributeError:
            return minqlx.RET_STOP_ALL

    def handle_round_start(self, data):
        if not self.game_supported:
            return

        teams = self.teams()
        red_start = teams["red"].copy()
        blue_start = teams["blue"].copy()

        for p in blue_start:
            self.blue_start[p.name] = p.stats.damage_dealt

        for p in red_start:
            self.red_start[p.name] = p.stats.damage_dealt

    def handle_round_end(self, data):
        if not self.game_supported:
            return

        teams = self.teams()
        red_end = teams["red"].copy()
        blue_end = teams["blue"].copy()
        round_damage = defaultdict(int)
        try:
            self.msg("^1RED SCORES: {}, PLAYERS ROUND DAMAGE:".format(self.game.red_score))
            for p in red_end:
                round_damage[p.name] = p.stats.damage_dealt-self.red_start[p.name]
                if round_damage[p.name] >= 0:
                    self.msg("^1  {0:<15} ^1: ^1{1}".format(p.name, round_damage[p.name]))
        except AttributeError:
            return minqlx.RET_STOP_ALL

        try:
            self.msg("^4BLUE SCORES: {}, PLAYERS ROUND DAMAGE:".format(self.game.blue_score))
            for p in blue_end:
                round_damage[p.name] = p.stats.damage_dealt-self.blue_start[p.name]
                if round_damage[p.name] >= 0:
                    self.msg("^4  {0:<15} ^4: ^4{1}".format(p.name, round_damage[p.name]))
        except AttributeError:
            return minqlx.RET_STOP_ALL

        round_damage = sorted(round_damage.items(), key=lambda t: t[1], reverse=True)
        n1player = round_damage[0][0]
        damage = round_damage[0][1]
        color = 7
        for t in teams:
            for p in teams[t]:
                if t == "red":
                    if p.name == n1player:
                        color = 1
                        break
                if t == "blue":
                    if p.name == n1player:
                        color = 4
                        break
            else:
                continue
            break
        if damage > 0:
            self.msg("^3*** BEST ROUND PLAYER ^{}{} ^3WITH ^{}{} ^3DAMAGE ***^7".format(color, n1player, color, damage))
