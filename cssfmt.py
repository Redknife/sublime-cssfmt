# coding: utf-8

import os
import platform
import sublime
import sublime_plugin
from subprocess import Popen, PIPE

# monkeypatch `Region` to be iterable
sublime.Region.totuple = lambda self: (self.a, self.b)
sublime.Region.__iter__ = lambda self: self.totuple().__iter__()

CSSFMT_PATH = os.path.join(sublime.packages_path(), os.path.dirname(os.path.realpath(__file__)), 'cssfmt.js')


class CssfmtCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        syntax = self.get_syntax()
        if not syntax:
            return

        if not self.has_selection():
            region = sublime.Region(0, self.view.size())
            originalBuffer = self.view.substr(region)
            formated = self.fmt(originalBuffer)
            if formated:
                self.view.replace(edit, region, formated)
            return

        for region in self.view.sel():
            if region.empty():
                continue
            originalBuffer = self.view.substr(region)
            formated = self.fmt(originalBuffer)
            if formated:
                self.view.replace(edit, region, formated)

    def fmt(self, css):
        folder = os.path.dirname(self.view.file_name())
        try:
            p = Popen(['node', CSSFMT_PATH] + [folder],
                      stdout=PIPE, stdin=PIPE, stderr=PIPE,
                      env=self.get_env(), shell=self.is_windows())
        except OSError:
            raise Exception("Couldn't find Node.js. Make sure it's in your " +
                            '$PATH by running `node -v` in your command-line.')
        stdout, stderr = p.communicate(input=css.encode('utf-8'))
        if stdout:
            sublime.status_message('CSSfmt done!')
            return stdout.decode('utf-8')
        else:
            sublime.status_message('CSSfmt error:\n%s' % stderr.decode('utf-8'))
            sublime.error_message('CSSfmt error:\n%s' % stderr.decode('utf-8'))
            print(stderr.decode('utf-8'))

    def get_env(self):
        env = None
        if self.is_osx():
            env = os.environ.copy()
            env['PATH'] += self.get_node_path()
        return env

    def get_node_path(self):
        return self.get_settings().get('node-path')

    def get_settings(self):
        settings = self.view.settings().get('cssfmt')
        if settings is None:
            settings = sublime.load_settings('cssfmt.sublime-settings')
        return settings

    def get_syntax(self):
        if self.is_css():
            return 'css'
        if self.is_scss():
            return 'scss'
        if self.is_sass():
            return 'sass'
        if self.is_less():
            return 'less'
        if self.is_unsaved_buffer_without_syntax():
            return 'css'
        return False

    def has_selection(self):
        for sel in self.view.sel():
            start, end = sel
            if start != end:
                return True
        return False

    def is_osx(self):
        return platform.system() == 'Darwin'

    def is_windows(self):
        return platform.system() == 'Windows'

    def is_unsaved_buffer_without_syntax(self):
        return self.view.file_name() == None and self.is_plaintext() == True

    def is_plaintext(self):
        return self.view.scope_name(0).startswith('text.plain')

    def is_css(self):
        return self.view.scope_name(0).startswith('source.css')

    def is_scss(self):
        return self.view.scope_name(0).startswith('source.scss') or self.view.file_name().endswith('.scss')

    def is_sass(self):
        return self.view.scope_name(0).startswith('source.sass')

    def is_less(self):
        return self.view.scope_name(0).startswith('source.less')
