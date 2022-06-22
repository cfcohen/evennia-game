#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
A demonstration of a pernicous ECHO problem.
"""

from django.conf import settings
from twisted.conch.telnet import ECHO

from evennia import Command, CmdSet
from evennia import syscmdkeys
from evennia.utils.evmenu import EvMenu
from evennia.utils.utils import class_from_module
from evennia.server.portal.telnet import TelnetProtocol

_ACCOUNT = class_from_module(settings.BASE_ACCOUNT_TYPECLASS)

# ----------------------------------------------------------------------------------------
def node_username(caller):

    def _check_username(caller, raw_string, **kwargs):
        # No validation, because that's not the point.  Keep it simple.
        return "node_password", {"name": raw_string.rstrip()}

    text = "Please enter your user name."
    options = {"key": "_default", "goto": _check_username}
    return text, options

# ----------------------------------------------------------------------------------------
def node_password(session, raw_string, **kwargs):

    def _check_input(session, password, **kwargs):
        password = password.rstrip()
        # Moving this line from here... to a few lines below also fixes the problem.
        session.msg("In _check_input(), turning echo on.", options={'echo': True})

        account, errors = _ACCOUNT.authenticate(
            username=kwargs['name'], password=password,
            ip=session.address, session=session)

        if account:
            # This is where the line from above needs to be moved to.
            #session.msg("In _check_input(), turning echo on.", options={'echo': True})
            kwargs["account"] = account
            return ("node_login", kwargs)
        else:
            session.msg("|r{}|n".format("\n".join(errors)))
            # One unexpected fix is to add this node!
            #return ("node_bogus", kwargs)
            return ("node_password", kwargs)

    session.msg("In node_password(), turning echo off.", options={'echo': False})
    text = "Password: "
    options = ( {"key": "_default", "goto": (_check_input, kwargs)}, )
    return text, options

# ----------------------------------------------------------------------------------------
def node_login(session, raw_text, **kwargs):
    session.msg("Logging in... {}".format(kwargs["account"].username))
    session.sessionhandler.login(session, kwargs["account"])
    return "", None

# ----------------------------------------------------------------------------------------
def node_bogus(session, raw_string, **kwargs):
    def _check_input(session, raw_value, **kwargs):
        return "node_password"

    text = "Please press enter."
    options = ( {"key": "_default", "goto": (_check_input, kwargs)}, )
    return text, options

# ----------------------------------------------------------------------------------------
class CmdLogin(Command):
    key = syscmdkeys.CMD_LOGINSTART
    locks = "cmd:all()"
    arg_regex = r"^$"

    def func(self):
        EvMenu(
            self.caller,
            "login",
            startnode="node_username",
            cmd_on_exit=None,
        )

# ----------------------------------------------------------------------------------------
class CmdEchoTest(Command):
    "Conduct an echotest once logged in (shows that it work usually)."

    key = "echotest"
    locks = "cmd:all()"

    def func(self):
        self.msg("Turning echo off for three seconds.", options={'echo': False})
        yield 3
        self.msg("Turning echo on for three seconds.", options={'echo': True})
        yield 3
        self.msg("Turning echo off for three seconds.", options={'echo': False})
        yield 3
        self.msg("Turning echo on for three seconds.", options={'echo': True})
        yield 3

        self.msg("Turning echo off for three seconds.", options={'echo': False})
        yield 3
        self.msg("Turning echo off (again) for three seconds.", options={'echo': False})
        yield 3
        self.msg("Turning echo on for three seconds.", options={'echo': True})
        yield 3
        self.msg("Turning echo on (again) for three seconds.", options={'echo': True})
        yield 3

        self.msg("Test complete.")

# ----------------------------------------------------------------------------------------
class LoginCmdSet(CmdSet):
    key = "DefaultLogin"
    priority = 0

    def at_cmdset_creation(self):
        self.add(CmdLogin())

# Local Variables:
# mode: python
# fill-column: 90
# eval: (flyspell-buffer)
# eval: (column-number-mode)
# End:
