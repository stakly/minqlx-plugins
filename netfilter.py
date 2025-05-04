# This plugin created by stakly <root@qw3rty.org>
# Copyright (c) 2024 stakly
#
# This plugin permit only current players IP's via netfilter and drop other connections
# !netlock - to lock current players IP's in whitelist
# !netunlock - to unlock
#
# PREPARING:
# packages required: iptables conntrack
# sudo - if running QL under separated user
#
# sudoers: 
# ql ALL=(ALL) NOPASSWD: /usr/sbin/iptables
# ql ALL=(ALL) NOPASSWD: /usr/sbin/conntrack
#
# iptables:
# iptables -A OUTPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
# iptables -A OUTPUT -p udp --sport 27966 -j DROP
# iptables -N QLFILTER
# iptables -A INPUT -p udp --dport 27966 -j QLFILTER
# iptables -A INPUT -p udp --dport 27966 -j DROP

import minqlx
import threading
import os

EXEC_IPTABLES_COMMAND = "/usr/bin/sudo /usr/sbin/iptables"
EXEC_CONNTRACK_COMMAND = "/usr/bin/sudo /usr/sbin/conntrack"
IPTABLES_CHAIN = "QLFILTER"

class netfilter(minqlx.Plugin):
    
    def __init__(self):
        self.add_command("netlock", self.cmd_lock, 4)
        self.add_command("netunlock", self.cmd_unlock, 4)

    @minqlx.thread
    def cmd_lock(self, player, msg, channel):
        os.system("{0} -F {1}".format(EXEC_IPTABLES_COMMAND, IPTABLES_CHAIN))
        for p in minqlx.Player.all_players():
            channel.reply("locking IP's")
            os.system("{0} -A {1} -s {2} -j ACCEPT".format(EXEC_IPTABLES_COMMAND, IPTABLES_CHAIN, p.ip))
        os.system("{0} -D -p udp --dport {1}".format(EXEC_CONNTRACK_COMMAND, minqlx.get_cvar("net_port")))
        os.system("{0} -D -p udp --sport {1}".format(EXEC_CONNTRACK_COMMAND, minqlx.get_cvar("net_port")))
        
    @minqlx.thread
    def cmd_unlock(self, player, msg, channel):
        channel.reply("unlocking IP's")
        os.system("{0} -F {1}".format(EXEC_IPTABLES_COMMAND, IPTABLES_CHAIN))
        os.system("{0} -A {1} -j ACCEPT".format(EXEC_IPTABLES_COMMAND, IPTABLES_CHAIN))
        os.system("{0} -D -p udp --dport {1}".format(EXEC_CONNTRACK_COMMAND, minqlx.get_cvar("net_port")))
        os.system("{0} -D -p udp --sport {1}".format(EXEC_CONNTRACK_COMMAND, minqlx.get_cvar("net_port")))

