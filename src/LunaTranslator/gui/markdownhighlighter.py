#!/usr/bin/python
# -*- coding: utf-8 -*-

# MarkdownHighlighter is a simple syntax highlighter for Markdown syntax.
# The initial code for MarkdownHighlighter was taken from niwmarkdowneditor by John Schember
# Copyright 2009 John Schember, Copyright 2012 Rupesh Kumar

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

'''
Highlight Markdown text
'''

import re, os, json
from qtsymbols import *

class MarkdownHighlighter(QSyntaxHighlighter):

    MARKDOWN_KEYS_REGEX = {
        'Bold' : re.compile(r'(?P<delim>\*\*)(?P<text>.+)(?P=delim)'),
        'uBold': re.compile(r'(?P<delim>__)(?P<text>[^_]{2,})(?P=delim)'),
        'Italic': re.compile(r'(?P<delim>\*)(?P<text>[^*]{2,})(?P=delim)'),
        'uItalic': re.compile(r'(?P<delim>_)(?P<text>[^_]+)(?P=delim)'),
        'Link': re.compile(r'(?u)(^|(?P<pre>[^!]))\[.*?\]:?[ \t]*\(?[^)]+\)?'),
        'Image': re.compile(r'(?u)!\[.*?\]\(.+?\)'),
        'HeaderAtx': re.compile(r'(?u)^\#{1,6}(.*?)\#*(\n|$)'),
        'Header': re.compile(r'^(.+)[ \t]*\n(=+|-+)[ \t]*\n+'),
        'CodeBlock': re.compile(r'^([ ]{4,}|\t).*'),
        'UnorderedList': re.compile(r'(?u)^\s*(\* |\+ |- )+\s*'),
        'UnorderedListStar': re.compile(r'^\s*(\* )+\s*'),
        'OrderedList': re.compile(r'(?u)^\s*(\d+\. )\s*'),
        'BlockQuote': re.compile(r'(?u)^\s*>+\s*'),
        'BlockQuoteCount': re.compile(r'^[ \t]*>[ \t]?'),
        'CodeSpan': re.compile(r'(?P<delim>`+).+?(?P=delim)'),
        'HR': re.compile(r'(?u)^(\s*(\*|-)\s*){3,}$'),
        'eHR': re.compile(r'(?u)^(\s*(\*|=)\s*){3,}$'),
        'Html': re.compile(r'<.+?>')
    }

    def __init__(self, parent):
        QSyntaxHighlighter.__init__(self, parent)
        self.parent:QTextEdit = parent

        self.defaultTheme =  {"background-color":"#d7d7d7", "color":"#191970", "bold": {"color":"#859900", "font-weight":"bold", "font-style":"normal"}, "emphasis": {"color":"#b58900", "font-weight":"bold", "font-style":"italic"}, "link": {"color":"#cb4b16", "font-weight":"normal", "font-style":"normal"}, "image": {"color":"#cb4b16", "font-weight":"normal", "font-style":"normal"}, "header": {"color":"#2aa198", "font-weight":"bold", "font-style":"normal"}, "unorderedlist": {"color":"#dc322f", "font-weight":"normal", "font-style":"normal"}, "orderedlist": {"color":"#dc322f", "font-weight":"normal", "font-style":"normal"}, "blockquote": {"color":"#dc322f", "font-weight":"normal", "font-style":"normal"}, "codespan": {"color":"#dc322f", "font-weight":"normal", "font-style":"normal"}, "codeblock": {"color":"#ff9900", "font-weight":"normal", "font-style":"normal"}, "line": {"color":"#2aa198", "font-weight":"normal", "font-style":"normal"}, "html": {"color":"#c000c0", "font-weight":"normal", "font-style":"normal"}}
        #self.setTheme(self.defaultTheme)
        
        fn = os.path.join(os.path.dirname(__file__), "markdownhighlighter.theme.json")
        with open(fn, "r") as ff:
            self.setTheme(json.load(ff)["solarized"])

    def setTheme(self, theme):
        self.theme = theme
        self.MARKDOWN_KWS_FORMAT = {}

        pal = self.parent.palette()
        # pal.setColor(QPalette.ColorRole.Base, QColor(theme['background-color']))
        self.parent.setPalette(pal)
        self.parent.setTextColor(QColor(theme['color']))

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['bold']['color'])))
        format.setFontWeight(QFont.Weight.Bold if theme['bold']['font-weight']=='bold' else QFont.Weight.Normal)
        format.setFontItalic(True if theme['bold']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['Bold'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['bold']['color'])))
        format.setFontWeight(QFont.Weight.Bold if theme['bold']['font-weight']=='bold' else QFont.Weight.Normal)
        format.setFontItalic(True if theme['bold']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['uBold'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['emphasis']['color'])))
        format.setFontWeight(QFont.Weight.Bold if theme['emphasis']['font-weight']=='bold' else QFont.Weight.Normal)
        format.setFontItalic(True if theme['emphasis']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['Italic'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['emphasis']['color'])))
        format.setFontWeight(QFont.Weight.Bold if theme['emphasis']['font-weight']=='bold' else QFont.Weight.Normal)
        format.setFontItalic(True if theme['emphasis']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['uItalic'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['link']['color'])))
        format.setFontWeight(QFont.Weight.Bold if theme['link']['font-weight']=='bold' else QFont.Weight.Normal)
        format.setFontItalic(True if theme['link']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['Link'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['image']['color'])))
        format.setFontWeight(QFont.Weight.Bold if theme['image']['font-weight']=='bold' else QFont.Weight.Normal)
        format.setFontItalic(True if theme['image']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['Image'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['header']['color'])))
        format.setFontWeight(QFont.Weight.Bold if theme['header']['font-weight']=='bold' else QFont.Weight.Normal)
        format.setFontItalic(True if theme['header']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['Header'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['header']['color'])))
        format.setFontWeight(QFont.Weight.Bold if theme['header']['font-weight']=='bold' else QFont.Weight.Normal)
        format.setFontItalic(True if theme['header']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['HeaderAtx'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['unorderedlist']['color'])))
        format.setFontWeight(QFont.Weight.Bold if theme['unorderedlist']['font-weight']=='bold' else QFont.Weight.Normal)
        format.setFontItalic(True if theme['unorderedlist']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['UnorderedList'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['orderedlist']['color'])))
        format.setFontWeight(QFont.Weight.Bold if theme['orderedlist']['font-weight']=='bold' else QFont.Weight.Normal)
        format.setFontItalic(True if theme['orderedlist']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['OrderedList'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['blockquote']['color'])))
        format.setFontWeight(QFont.Weight.Bold if theme['blockquote']['font-weight']=='bold' else QFont.Weight.Normal)
        format.setFontItalic(True if theme['blockquote']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['BlockQuote'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['codespan']['color'])))
        format.setFontWeight(QFont.Weight.Bold if theme['codespan']['font-weight']=='bold' else QFont.Weight.Normal)
        format.setFontItalic(True if theme['codespan']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['CodeSpan'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['codeblock']['color'])))
        format.setFontWeight(QFont.Weight.Bold if theme['codeblock']['font-weight']=='bold' else QFont.Weight.Normal)
        format.setFontItalic(True if theme['codeblock']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['CodeBlock'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['line']['color'])))
        format.setFontWeight(QFont.Weight.Bold if theme['line']['font-weight']=='bold' else QFont.Weight.Normal)
        format.setFontItalic(True if theme['line']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['HR'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['line']['color'])))
        format.setFontWeight(QFont.Weight.Bold if theme['line']['font-weight']=='bold' else QFont.Weight.Normal)
        format.setFontItalic(True if theme['line']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['eHR'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['html']['color'])))
        format.setFontWeight(QFont.Weight.Bold if theme['html']['font-weight']=='bold' else QFont.Weight.Normal)
        format.setFontItalic(True if theme['html']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['HTML'] = format

        self.rehighlight()

    def highlightBlock(self, text):
        self.highlightMarkdown(text,0)
        self.highlightHtml(text)

    def highlightMarkdown(self, text, strt):
        cursor = QTextCursor(self.document())
        bf = cursor.blockFormat()
        self.setFormat(0, len(text), QColor(self.theme['color']))
        #bf.clearBackground()
        #cursor.movePosition(QTextCursor.End)
        #cursor.setBlockFormat(bf)

        #Block quotes can contain all elements so process it first
        self.highlightBlockQuote(text, cursor, bf, strt)

        #If empty line no need to check for below elements just return
        if self.highlightEmptyLine(text, cursor, bf, strt):
            return

        #If horizontal line, look at pevious line to see if its a header, process and return
        if self.highlightHorizontalLine(text, cursor, bf, strt):
            return

        if self.highlightAtxHeader(text, cursor, bf, strt):
            return

        self.highlightList(text, cursor, bf, strt)

        self.highlightLink(text, cursor, bf, strt)

        self.highlightImage(text, cursor, bf, strt)

        self.highlightCodeSpan(text, cursor, bf, strt)

        self.highlightEmphasis(text, cursor, bf, strt)

        self.highlightBold(text, cursor, bf, strt)

        self.highlightCodeBlock(text, cursor, bf, strt)

    def highlightBlockQuote(self, text, cursor, bf, strt):
        found = False
        mo = re.search(self.MARKDOWN_KEYS_REGEX['BlockQuote'],text)
        if mo:
            self.setFormat(mo.start(), mo.end() - mo.start(), self.MARKDOWN_KWS_FORMAT['BlockQuote'])
            unquote = re.sub(self.MARKDOWN_KEYS_REGEX['BlockQuoteCount'],'',text)
            spcs = re.match(self.MARKDOWN_KEYS_REGEX['BlockQuoteCount'],text)
            spcslen = 0
            if spcs:
                spcslen = len(spcs.group(0))
            self.highlightMarkdown(unquote,spcslen)
            found = True
        return found

    def highlightEmptyLine(self, text:str, cursor, bf, strt):
        textAscii = str(text.replace('\u2029','\n'))
        if textAscii.strip():
            return False
        else:
            return True

    def highlightHorizontalLine(self, text, cursor, bf, strt):
        found = False
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['HR'],text):
            prevBlock = self.currentBlock().previous()
            prevCursor = QTextCursor(prevBlock)
            prev = prevBlock.text()
            prevAscii = str(prev.replace('\u2029','\n'))
            if prevAscii.strip():
                #print "Its a header"
                prevCursor.select(QTextCursor.SelectionType.LineUnderCursor)
                #prevCursor.setCharFormat(self.MARKDOWN_KWS_FORMAT['Header'])
                formatRange = QTextLayout.FormatRange()
                formatRange.format = self.MARKDOWN_KWS_FORMAT['Header']
                formatRange.length = prevCursor.block().length()
                formatRange.start = 0
                prevCursor.block().layout().setAdditionalFormats([formatRange])
            self.setFormat(mo.start()+strt, mo.end() - mo.start(), self.MARKDOWN_KWS_FORMAT['HR'])

        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['eHR'],text):
            prevBlock = self.currentBlock().previous()
            prevCursor = QTextCursor(prevBlock)
            prev = prevBlock.text()
            prevAscii = str(prev.replace('\u2029','\n'))
            if prevAscii.strip():
                #print "Its a header"
                prevCursor.select(QTextCursor.SelectionType.LineUnderCursor)
                #prevCursor.setCharFormat(self.MARKDOWN_KWS_FORMAT['Header'])
                formatRange = QTextLayout.FormatRange()
                formatRange.format = self.MARKDOWN_KWS_FORMAT['Header']
                formatRange.length = prevCursor.block().length()
                formatRange.start = 0
                prevCursor.block().layout().setAdditionalFormats([formatRange])
            self.setFormat(mo.start()+strt, mo.end() - mo.start(), self.MARKDOWN_KWS_FORMAT['HR'])
        return found

    def highlightAtxHeader(self, text, cursor, bf, strt):
        found = False
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['HeaderAtx'],text):
            #bf.setBackground(QBrush(QColor(7,54,65)))
            #cursor.movePosition(QTextCursor.End)
            #cursor.mergeBlockFormat(bf)
            self.setFormat(mo.start()+strt, mo.end() - mo.start(), self.MARKDOWN_KWS_FORMAT['HeaderAtx'])
            found = True
        return found

    def highlightList(self, text, cursor, bf, strt):
        found = False
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['UnorderedList'],text):
            self.setFormat(mo.start()+strt, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['UnorderedList'])
            found = True

        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['OrderedList'],text):
            self.setFormat(mo.start()+strt, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['OrderedList'])
            found = True
        return found

    def highlightLink(self, text, cursor, bf, strt):
        found = False
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['Link'],text):
            self.setFormat(mo.start()+strt, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['Link'])
            found = True
        return found

    def highlightImage(self, text, cursor, bf, strt):
        found = False
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['Image'],text):
            self.setFormat(mo.start()+strt, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['Image'])
            found = True
        return found

    def highlightCodeSpan(self, text, cursor, bf, strt):
        found = False
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['CodeSpan'],text):
            self.setFormat(mo.start()+strt, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['CodeSpan'])
            found = True
        return found

    def highlightBold(self, text, cursor, bf, strt):
        found = False
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['Bold'],text):
            self.setFormat(mo.start()+strt, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['Bold'])
            found = True

        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['uBold'],text):
            self.setFormat(mo.start()+strt, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['uBold'])
            found = True
        return found

    def highlightEmphasis(self, text, cursor, bf, strt):
        found = False
        unlist = re.sub(self.MARKDOWN_KEYS_REGEX['UnorderedListStar'],'',text)
        spcs = re.match(self.MARKDOWN_KEYS_REGEX['UnorderedListStar'],text)
        spcslen = 0
        if spcs:
            spcslen = len(spcs.group(0))
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['Italic'],unlist):
            self.setFormat(mo.start()+strt+spcslen, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['Italic'])
            found = True
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['uItalic'],text):
            self.setFormat(mo.start()+strt, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['uItalic'])
            found = True
        return found

    def highlightCodeBlock(self, text:str, cursor, bf, strt):
        found = False
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['CodeBlock'],text):
            stripped = text.lstrip()
            if stripped[0] not in ('*','-','+','>'):
                self.setFormat(mo.start()+strt, mo.end() - mo.start(), self.MARKDOWN_KWS_FORMAT['CodeBlock'])
                found = True
        return found

    def highlightHtml(self, text):
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['Html'], text):
            self.setFormat(mo.start(), mo.end() - mo.start(), self.MARKDOWN_KWS_FORMAT['HTML'])
