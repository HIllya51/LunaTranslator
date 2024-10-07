# Each letter is of the format:
#
#   ('<letter>', <replacement>)
#
# And replacement is of the format:
#
#   ('<isolated>', '<initial>', '<medial>', '<final>')
#
# Where <letter> is the string to replace, and <isolated> is the replacement in
# case <letter> should be in isolated form, <initial> is the replacement in
# case <letter> should be in initial form, <medial> is the replacement in case
# <letter> should be in medial form, and <final> is the replacement in case
# <letter> should be in final form. If no replacement is specified for a form,
# then no that means the letter doesn't support this form.

UNSHAPED = 255
ISOLATED = 0
INITIAL = 1
MEDIAL = 2
FINAL = 3

TATWEEL = '\u0640'
ZWJ = '\u200D'
LETTERS_ARABIC = {
    # ARABIC LETTER HAMZA
    '\u0621': ('\uFE80', '', '', ''),
    # ARABIC LETTER ALEF WITH MADDA ABOVE
    '\u0622': ('\uFE81', '', '', '\uFE82'),
    # ARABIC LETTER ALEF WITH HAMZA ABOVE
    '\u0623': ('\uFE83', '', '', '\uFE84'),
    # ARABIC LETTER WAW WITH HAMZA ABOVE
    '\u0624': ('\uFE85', '', '', '\uFE86'),
    # ARABIC LETTER ALEF WITH HAMZA BELOW
    '\u0625': ('\uFE87', '', '', '\uFE88'),
    # ARABIC LETTER YEH WITH HAMZA ABOVE
    '\u0626': ('\uFE89', '\uFE8B', '\uFE8C', '\uFE8A'),
    # ARABIC LETTER ALEF
    '\u0627': ('\uFE8D', '', '', '\uFE8E'),
    # ARABIC LETTER BEH
    '\u0628': ('\uFE8F', '\uFE91', '\uFE92', '\uFE90'),
    # ARABIC LETTER TEH MARBUTA
    '\u0629': ('\uFE93', '', '', '\uFE94'),
    # ARABIC LETTER TEH
    '\u062A': ('\uFE95', '\uFE97', '\uFE98', '\uFE96'),
    # ARABIC LETTER THEH
    '\u062B': ('\uFE99', '\uFE9B', '\uFE9C', '\uFE9A'),
    # ARABIC LETTER JEEM
    '\u062C': ('\uFE9D', '\uFE9F', '\uFEA0', '\uFE9E'),
    # ARABIC LETTER HAH
    '\u062D': ('\uFEA1', '\uFEA3', '\uFEA4', '\uFEA2'),
    # ARABIC LETTER KHAH
    '\u062E': ('\uFEA5', '\uFEA7', '\uFEA8', '\uFEA6'),
    # ARABIC LETTER DAL
    '\u062F': ('\uFEA9', '', '', '\uFEAA'),
    # ARABIC LETTER THAL
    '\u0630': ('\uFEAB', '', '', '\uFEAC'),
    # ARABIC LETTER REH
    '\u0631': ('\uFEAD', '', '', '\uFEAE'),
    # ARABIC LETTER ZAIN
    '\u0632': ('\uFEAF', '', '', '\uFEB0'),
    # ARABIC LETTER SEEN
    '\u0633': ('\uFEB1', '\uFEB3', '\uFEB4', '\uFEB2'),
    # ARABIC LETTER SHEEN
    '\u0634': ('\uFEB5', '\uFEB7', '\uFEB8', '\uFEB6'),
    # ARABIC LETTER SAD
    '\u0635': ('\uFEB9', '\uFEBB', '\uFEBC', '\uFEBA'),
    # ARABIC LETTER DAD
    '\u0636': ('\uFEBD', '\uFEBF', '\uFEC0', '\uFEBE'),
    # ARABIC LETTER TAH
    '\u0637': ('\uFEC1', '\uFEC3', '\uFEC4', '\uFEC2'),
    # ARABIC LETTER ZAH
    '\u0638': ('\uFEC5', '\uFEC7', '\uFEC8', '\uFEC6'),
    # ARABIC LETTER AIN
    '\u0639': ('\uFEC9', '\uFECB', '\uFECC', '\uFECA'),
    # ARABIC LETTER GHAIN
    '\u063A': ('\uFECD', '\uFECF', '\uFED0', '\uFECE'),
    # ARABIC TATWEEL
    TATWEEL:  (TATWEEL,   TATWEEL,  TATWEEL,  TATWEEL),
    # ARABIC LETTER FEH
    '\u0641': ('\uFED1', '\uFED3', '\uFED4', '\uFED2'),
    # ARABIC LETTER QAF
    '\u0642': ('\uFED5', '\uFED7', '\uFED8', '\uFED6'),
    # ARABIC LETTER KAF
    '\u0643': ('\uFED9', '\uFEDB', '\uFEDC', '\uFEDA'),
    # ARABIC LETTER LAM
    '\u0644': ('\uFEDD', '\uFEDF', '\uFEE0', '\uFEDE'),
    # ARABIC LETTER MEEM
    '\u0645': ('\uFEE1', '\uFEE3', '\uFEE4', '\uFEE2'),
    # ARABIC LETTER NOON
    '\u0646': ('\uFEE5', '\uFEE7', '\uFEE8', '\uFEE6'),
    # ARABIC LETTER HEH
    '\u0647': ('\uFEE9', '\uFEEB', '\uFEEC', '\uFEEA'),
    # ARABIC LETTER WAW
    '\u0648': ('\uFEED', '', '', '\uFEEE'),
    # ARABIC LETTER (UIGHUR KAZAKH KIRGHIZ)? ALEF MAKSURA
    '\u0649': ('\uFEEF', '\uFBE8', '\uFBE9', '\uFEF0'),
    # ARABIC LETTER YEH
    '\u064A': ('\uFEF1', '\uFEF3', '\uFEF4', '\uFEF2'),
    # ARABIC LETTER ALEF WASLA
    '\u0671': ('\uFB50', '', '', '\uFB51'),
    # ARABIC LETTER U WITH HAMZA ABOVE
    '\u0677': ('\uFBDD', '', '', ''),
    # ARABIC LETTER TTEH
    '\u0679': ('\uFB66', '\uFB68', '\uFB69', '\uFB67'),
    # ARABIC LETTER TTEHEH
    '\u067A': ('\uFB5E', '\uFB60', '\uFB61', '\uFB5F'),
    # ARABIC LETTER BEEH
    '\u067B': ('\uFB52', '\uFB54', '\uFB55', '\uFB53'),
    # ARABIC LETTER PEH
    '\u067E': ('\uFB56', '\uFB58', '\uFB59', '\uFB57'),
    # ARABIC LETTER TEHEH
    '\u067F': ('\uFB62', '\uFB64', '\uFB65', '\uFB63'),
    # ARABIC LETTER BEHEH
    '\u0680': ('\uFB5A', '\uFB5C', '\uFB5D', '\uFB5B'),
    # ARABIC LETTER NYEH
    '\u0683': ('\uFB76', '\uFB78', '\uFB79', '\uFB77'),
    # ARABIC LETTER DYEH
    '\u0684': ('\uFB72', '\uFB74', '\uFB75', '\uFB73'),
    # ARABIC LETTER TCHEH
    '\u0686': ('\uFB7A', '\uFB7C', '\uFB7D', '\uFB7B'),
    # ARABIC LETTER TCHEHEH
    '\u0687': ('\uFB7E', '\uFB80', '\uFB81', '\uFB7F'),
    # ARABIC LETTER DDAL
    '\u0688': ('\uFB88', '', '', '\uFB89'),
    # ARABIC LETTER DAHAL
    '\u068C': ('\uFB84', '', '', '\uFB85'),
    # ARABIC LETTER DDAHAL
    '\u068D': ('\uFB82', '', '', '\uFB83'),
    # ARABIC LETTER DUL
    '\u068E': ('\uFB86', '', '', '\uFB87'),
    # ARABIC LETTER RREH
    '\u0691': ('\uFB8C', '', '', '\uFB8D'),
    # ARABIC LETTER JEH
    '\u0698': ('\uFB8A', '', '', '\uFB8B'),
    # ARABIC LETTER VEH
    '\u06A4': ('\uFB6A', '\uFB6C', '\uFB6D', '\uFB6B'),
    # ARABIC LETTER PEHEH
    '\u06A6': ('\uFB6E', '\uFB70', '\uFB71', '\uFB6F'),
    # ARABIC LETTER KEHEH
    '\u06A9': ('\uFB8E', '\uFB90', '\uFB91', '\uFB8F'),
    # ARABIC LETTER NG
    '\u06AD': ('\uFBD3', '\uFBD5', '\uFBD6', '\uFBD4'),
    # ARABIC LETTER GAF
    '\u06AF': ('\uFB92', '\uFB94', '\uFB95', '\uFB93'),
    # ARABIC LETTER NGOEH
    '\u06B1': ('\uFB9A', '\uFB9C', '\uFB9D', '\uFB9B'),
    # ARABIC LETTER GUEH
    '\u06B3': ('\uFB96', '\uFB98', '\uFB99', '\uFB97'),
    # ARABIC LETTER NOON GHUNNA
    '\u06BA': ('\uFB9E', '', '', '\uFB9F'),
    # ARABIC LETTER RNOON
    '\u06BB': ('\uFBA0', '\uFBA2', '\uFBA3', '\uFBA1'),
    # ARABIC LETTER HEH DOACHASHMEE
    '\u06BE': ('\uFBAA', '\uFBAC', '\uFBAD', '\uFBAB'),
    # ARABIC LETTER HEH WITH YEH ABOVE
    '\u06C0': ('\uFBA4', '', '', '\uFBA5'),
    # ARABIC LETTER HEH GOAL
    '\u06C1': ('\uFBA6', '\uFBA8', '\uFBA9', '\uFBA7'),
    # ARABIC LETTER KIRGHIZ OE
    '\u06C5': ('\uFBE0', '', '', '\uFBE1'),
    # ARABIC LETTER OE
    '\u06C6': ('\uFBD9', '', '', '\uFBDA'),
    # ARABIC LETTER U
    '\u06C7': ('\uFBD7', '', '', '\uFBD8'),
    # ARABIC LETTER YU
    '\u06C8': ('\uFBDB', '', '', '\uFBDC'),
    # ARABIC LETTER KIRGHIZ YU
    '\u06C9': ('\uFBE2', '', '', '\uFBE3'),
    # ARABIC LETTER VE
    '\u06CB': ('\uFBDE', '', '', '\uFBDF'),
    # ARABIC LETTER FARSI YEH
    '\u06CC': ('\uFBFC', '\uFBFE', '\uFBFF', '\uFBFD'),
    # ARABIC LETTER E
    '\u06D0': ('\uFBE4', '\uFBE6', '\uFBE7', '\uFBE5'),
    # ARABIC LETTER YEH BARREE
    '\u06D2': ('\uFBAE', '', '', '\uFBAF'),
    # ARABIC LETTER YEH BARREE WITH HAMZA ABOVE
    '\u06D3': ('\uFBB0', '', '', '\uFBB1'),

    # ZWJ
    ZWJ: (ZWJ, ZWJ, ZWJ, ZWJ),
}

LETTERS_ARABIC_V2 = {
    # ARABIC LETTER HAMZA
    '\u0621': ('\uFE80', '', '', ''),
    # ARABIC LETTER ALEF WITH MADDA ABOVE
    '\u0622': ('\u0622', '', '', '\uFE82'),
    # ARABIC LETTER ALEF WITH HAMZA ABOVE
    '\u0623': ('\u0623', '', '', '\uFE84'),
    # ARABIC LETTER WAW WITH HAMZA ABOVE
    '\u0624': ('\u0624', '', '', '\uFE86'),
    # ARABIC LETTER ALEF WITH HAMZA BELOW
    '\u0625': ('\u0625', '', '', '\uFE88'),
    # ARABIC LETTER YEH WITH HAMZA ABOVE
    '\u0626': ('\u0626', '\uFE8B', '\uFE8C', '\uFE8A'),
    # ARABIC LETTER ALEF
    '\u0627': ('\u0627', '', '', '\uFE8E'),
    # ARABIC LETTER BEH
    '\u0628': ('\u0628', '\uFE91', '\uFE92', '\uFE90'),
    # ARABIC LETTER TEH MARBUTA
    '\u0629': ('\u0629', '', '', '\uFE94'),
    # ARABIC LETTER TEH
    '\u062A': ('\u062A', '\uFE97', '\uFE98', '\uFE96'),
    # ARABIC LETTER THEH
    '\u062B': ('\u062B', '\uFE9B', '\uFE9C', '\uFE9A'),
    # ARABIC LETTER JEEM
    '\u062C': ('\u062C', '\uFE9F', '\uFEA0', '\uFE9E'),
    # ARABIC LETTER HAH
    '\u062D': ('\uFEA1', '\uFEA3', '\uFEA4', '\uFEA2'),
    # ARABIC LETTER KHAH
    '\u062E': ('\u062E', '\uFEA7', '\uFEA8', '\uFEA6'),
    # ARABIC LETTER DAL
    '\u062F': ('\u062F', '', '', '\uFEAA'),
    # ARABIC LETTER THAL
    '\u0630': ('\u0630', '', '', '\uFEAC'),
    # ARABIC LETTER REH
    '\u0631': ('\u0631', '', '', '\uFEAE'),
    # ARABIC LETTER ZAIN
    '\u0632': ('\u0632', '', '', '\uFEB0'),
    # ARABIC LETTER SEEN
    '\u0633': ('\u0633', '\uFEB3', '\uFEB4', '\uFEB2'),
    # ARABIC LETTER SHEEN
    '\u0634': ('\u0634', '\uFEB7', '\uFEB8', '\uFEB6'),
    # ARABIC LETTER SAD
    '\u0635': ('\u0635', '\uFEBB', '\uFEBC', '\uFEBA'),
    # ARABIC LETTER DAD
    '\u0636': ('\u0636', '\uFEBF', '\uFEC0', '\uFEBE'),
    # ARABIC LETTER TAH
    '\u0637': ('\u0637', '\uFEC3', '\uFEC4', '\uFEC2'),
    # ARABIC LETTER ZAH
    '\u0638': ('\u0638', '\uFEC7', '\uFEC8', '\uFEC6'),
    # ARABIC LETTER AIN
    '\u0639': ('\u0639', '\uFECB', '\uFECC', '\uFECA'),
    # ARABIC LETTER GHAIN
    '\u063A': ('\u063A', '\uFECF', '\uFED0', '\uFECE'),
    # ARABIC TATWEEL
    TATWEEL:  (TATWEEL,   TATWEEL,  TATWEEL,  TATWEEL),
    # ARABIC LETTER FEH
    '\u0641': ('\u0641', '\uFED3', '\uFED4', '\uFED2'),
    # ARABIC LETTER QAF
    '\u0642': ('\u0642', '\uFED7', '\uFED8', '\uFED6'),
    # ARABIC LETTER KAF
    '\u0643': ('\u0643', '\uFEDB', '\uFEDC', '\uFEDA'),
    # ARABIC LETTER LAM
    '\u0644': ('\u0644', '\uFEDF', '\uFEE0', '\uFEDE'),
    # ARABIC LETTER MEEM
    '\u0645': ('\u0645', '\uFEE3', '\uFEE4', '\uFEE2'),
    # ARABIC LETTER NOON
    '\u0646': ('\u0646', '\uFEE7', '\uFEE8', '\uFEE6'),
    # ARABIC LETTER HEH
    '\u0647': ('\u0647', '\uFEEB', '\uFEEC', '\uFEEA'),
    # ARABIC LETTER WAW
    '\u0648': ('\u0648', '', '', '\uFEEE'),
    # ARABIC LETTER (UIGHUR KAZAKH KIRGHIZ)? ALEF MAKSURA
    '\u0649': ('\u0649', '\uFBE8', '\uFBE9', '\uFEF0'),
    # ARABIC LETTER YEH
    '\u064A': ('\u064A', '\uFEF3', '\uFEF4', '\uFEF2'),
    # ARABIC LETTER ALEF WASLA
    '\u0671': ('\u0671', '', '', '\uFB51'),
    # ARABIC LETTER U WITH HAMZA ABOVE
    '\u0677': ('\u0677', '', '', ''),
    # ARABIC LETTER TTEH
    '\u0679': ('\u0679', '\uFB68', '\uFB69', '\uFB67'),
    # ARABIC LETTER TTEHEH
    '\u067A': ('\u067A', '\uFB60', '\uFB61', '\uFB5F'),
    # ARABIC LETTER BEEH
    '\u067B': ('\u067B', '\uFB54', '\uFB55', '\uFB53'),
    # ARABIC LETTER PEH
    '\u067E': ('\u067E', '\uFB58', '\uFB59', '\uFB57'),
    # ARABIC LETTER TEHEH
    '\u067F': ('\u067F', '\uFB64', '\uFB65', '\uFB63'),
    # ARABIC LETTER BEHEH
    '\u0680': ('\u0680', '\uFB5C', '\uFB5D', '\uFB5B'),
    # ARABIC LETTER NYEH
    '\u0683': ('\u0683', '\uFB78', '\uFB79', '\uFB77'),
    # ARABIC LETTER DYEH
    '\u0684': ('\u0684', '\uFB74', '\uFB75', '\uFB73'),
    # ARABIC LETTER TCHEH
    '\u0686': ('\u0686', '\uFB7C', '\uFB7D', '\uFB7B'),
    # ARABIC LETTER TCHEHEH
    '\u0687': ('\u0687', '\uFB80', '\uFB81', '\uFB7F'),
    # ARABIC LETTER DDAL
    '\u0688': ('\u0688', '', '', '\uFB89'),
    # ARABIC LETTER DAHAL
    '\u068C': ('\u068C', '', '', '\uFB85'),
    # ARABIC LETTER DDAHAL
    '\u068D': ('\u068D', '', '', '\uFB83'),
    # ARABIC LETTER DUL
    '\u068E': ('\u068E', '', '', '\uFB87'),
    # ARABIC LETTER RREH
    '\u0691': ('\u0691', '', '', '\uFB8D'),
    # ARABIC LETTER JEH
    '\u0698': ('\u0698', '', '', '\uFB8B'),
    # ARABIC LETTER VEH
    '\u06A4': ('\u06A4', '\uFB6C', '\uFB6D', '\uFB6B'),
    # ARABIC LETTER PEHEH
    '\u06A6': ('\u06A6', '\uFB70', '\uFB71', '\uFB6F'),
    # ARABIC LETTER KEHEH
    '\u06A9': ('\u06A9', '\uFB90', '\uFB91', '\uFB8F'),
    # ARABIC LETTER NG
    '\u06AD': ('\u06AD', '\uFBD5', '\uFBD6', '\uFBD4'),
    # ARABIC LETTER GAF
    '\u06AF': ('\u06AF', '\uFB94', '\uFB95', '\uFB93'),
    # ARABIC LETTER NGOEH
    '\u06B1': ('\u06B1', '\uFB9C', '\uFB9D', '\uFB9B'),
    # ARABIC LETTER GUEH
    '\u06B3': ('\u06B3', '\uFB98', '\uFB99', '\uFB97'),
    # ARABIC LETTER NOON GHUNNA
    '\u06BA': ('\u06BA', '', '', '\uFB9F'),
    # ARABIC LETTER RNOON
    '\u06BB': ('\u06BB', '\uFBA2', '\uFBA3', '\uFBA1'),
    # ARABIC LETTER HEH DOACHASHMEE
    '\u06BE': ('\u06BE', '\uFBAC', '\uFBAD', '\uFBAB'),
    # ARABIC LETTER HEH WITH YEH ABOVE
    '\u06C0': ('\u06C0', '', '', '\uFBA5'),
    # ARABIC LETTER HEH GOAL
    '\u06C1': ('\u06C1', '\uFBA8', '\uFBA9', '\uFBA7'),
    # ARABIC LETTER KIRGHIZ OE
    '\u06C5': ('\u06C5', '', '', '\uFBE1'),
    # ARABIC LETTER OE
    '\u06C6': ('\u06C6', '', '', '\uFBDA'),
    # ARABIC LETTER U
    '\u06C7': ('\u06C7', '', '', '\uFBD8'),
    # ARABIC LETTER YU
    '\u06C8': ('\u06C8', '', '', '\uFBDC'),
    # ARABIC LETTER KIRGHIZ YU
    '\u06C9': ('\u06C9', '', '', '\uFBE3'),
    # ARABIC LETTER VE
    '\u06CB': ('\u06CB', '', '', '\uFBDF'),
    # ARABIC LETTER FARSI YEH
    '\u06CC': ('\u06CC', '\uFBFE', '\uFBFF', '\uFBFD'),
    # ARABIC LETTER E
    '\u06D0': ('\u06D0', '\uFBE6', '\uFBE7', '\uFBE5'),
    # ARABIC LETTER YEH BARREE
    '\u06D2': ('\u06D2', '', '', '\uFBAF'),
    # ARABIC LETTER YEH BARREE WITH HAMZA ABOVE
    '\u06D3': ('\u06D3', '', '', '\uFBB1'),
    # Kurdish letter YEAH
    '\u06ce': ('\uE004', '\uE005', '\uE006', '\uE004'),
    # Kurdish letter Hamza same as arabic Teh without the point
    '\u06d5': ('\u06d5', '', '', '\uE000'),
    # ZWJ
    ZWJ: (ZWJ, ZWJ, ZWJ, ZWJ),
}
LETTERS_KURDISH = {
    # ARABIC LETTER HAMZA
    '\u0621': ('\uFE80', '', '', ''),
    # ARABIC LETTER ALEF WITH MADDA ABOVE
    '\u0622': ('\u0622', '', '', '\uFE82'),
    # ARABIC LETTER ALEF WITH HAMZA ABOVE
    '\u0623': ('\u0623', '', '', '\uFE84'),
    # ARABIC LETTER WAW WITH HAMZA ABOVE
    '\u0624': ('\u0624', '', '', '\uFE86'),
    # ARABIC LETTER ALEF WITH HAMZA BELOW
    '\u0625': ('\u0625', '', '', '\uFE88'),
    # ARABIC LETTER YEH WITH HAMZA ABOVE
    '\u0626': ('\u0626', '\uFE8B', '\uFE8C', '\uFE8A'),
    # ARABIC LETTER ALEF
    '\u0627': ('\u0627', '', '', '\uFE8E'),
    # ARABIC LETTER BEH
    '\u0628': ('\u0628', '\uFE91', '\uFE92', '\uFE90'),
    # ARABIC LETTER TEH MARBUTA
    '\u0629': ('\u0629', '', '', '\uFE94'),
    # ARABIC LETTER TEH
    '\u062A': ('\u062A', '\uFE97', '\uFE98', '\uFE96'),
    # ARABIC LETTER THEH
    '\u062B': ('\u062B', '\uFE9B', '\uFE9C', '\uFE9A'),
    # ARABIC LETTER JEEM
    '\u062C': ('\u062C', '\uFE9F', '\uFEA0', '\uFE9E'),
    # ARABIC LETTER HAH
    '\u062D': ('\uFEA1', '\uFEA3', '\uFEA4', '\uFEA2'),
    # ARABIC LETTER KHAH
    '\u062E': ('\u062E', '\uFEA7', '\uFEA8', '\uFEA6'),
    # ARABIC LETTER DAL
    '\u062F': ('\u062F', '', '', '\uFEAA'),
    # ARABIC LETTER THAL
    '\u0630': ('\u0630', '', '', '\uFEAC'),
    # ARABIC LETTER REH
    '\u0631': ('\u0631', '', '', '\uFEAE'),
    # ARABIC LETTER ZAIN
    '\u0632': ('\u0632', '', '', '\uFEB0'),
    # ARABIC LETTER SEEN
    '\u0633': ('\u0633', '\uFEB3', '\uFEB4', '\uFEB2'),
    # ARABIC LETTER SHEEN
    '\u0634': ('\u0634', '\uFEB7', '\uFEB8', '\uFEB6'),
    # ARABIC LETTER SAD
    '\u0635': ('\u0635', '\uFEBB', '\uFEBC', '\uFEBA'),
    # ARABIC LETTER DAD
    '\u0636': ('\u0636', '\uFEBF', '\uFEC0', '\uFEBE'),
    # ARABIC LETTER TAH
    '\u0637': ('\u0637', '\uFEC3', '\uFEC4', '\uFEC2'),
    # ARABIC LETTER ZAH
    '\u0638': ('\u0638', '\uFEC7', '\uFEC8', '\uFEC6'),
    # ARABIC LETTER AIN
    '\u0639': ('\u0639', '\uFECB', '\uFECC', '\uFECA'),
    # ARABIC LETTER GHAIN
    '\u063A': ('\u063A', '\uFECF', '\uFED0', '\uFECE'),
    # ARABIC TATWEEL
    TATWEEL:  (TATWEEL,   TATWEEL,  TATWEEL,  TATWEEL),
    # ARABIC LETTER FEH
    '\u0641': ('\u0641', '\uFED3', '\uFED4', '\uFED2'),
    # ARABIC LETTER QAF
    '\u0642': ('\u0642', '\uFED7', '\uFED8', '\uFED6'),
    # ARABIC LETTER KAF
    '\u0643': ('\u0643', '\uFEDB', '\uFEDC', '\uFEDA'),
    # ARABIC LETTER LAM
    '\u0644': ('\u0644', '\uFEDF', '\uFEE0', '\uFEDE'),
    # ARABIC LETTER MEEM
    '\u0645': ('\u0645', '\uFEE3', '\uFEE4', '\uFEE2'),
    # ARABIC LETTER NOON
    '\u0646': ('\u0646', '\uFEE7', '\uFEE8', '\uFEE6'),
    # ARABIC LETTER HEH
    '\u0647': ('\uFBAB', '\uFBAB', '\uFBAB', '\uFBAB'),
    # ARABIC LETTER WAW
    '\u0648': ('\u0648', '', '', '\uFEEE'),
    # ARABIC LETTER (UIGHUR KAZAKH KIRGHIZ)? ALEF MAKSURA
    '\u0649': ('\u0649', '\uFBE8', '\uFBE9', '\uFEF0'),
    # ARABIC LETTER YEH
    '\u064A': ('\u064A', '\uFEF3', '\uFEF4', '\uFEF2'),
    # ARABIC LETTER ALEF WASLA
    '\u0671': ('\u0671', '', '', '\uFB51'),
    # ARABIC LETTER U WITH HAMZA ABOVE
    '\u0677': ('\u0677', '', '', ''),
    # ARABIC LETTER TTEH
    '\u0679': ('\u0679', '\uFB68', '\uFB69', '\uFB67'),
    # ARABIC LETTER TTEHEH
    '\u067A': ('\u067A', '\uFB60', '\uFB61', '\uFB5F'),
    # ARABIC LETTER BEEH
    '\u067B': ('\u067B', '\uFB54', '\uFB55', '\uFB53'),
    # ARABIC LETTER PEH
    '\u067E': ('\u067E', '\uFB58', '\uFB59', '\uFB57'),
    # ARABIC LETTER TEHEH
    '\u067F': ('\u067F', '\uFB64', '\uFB65', '\uFB63'),
    # ARABIC LETTER BEHEH
    '\u0680': ('\u0680', '\uFB5C', '\uFB5D', '\uFB5B'),
    # ARABIC LETTER NYEH
    '\u0683': ('\u0683', '\uFB78', '\uFB79', '\uFB77'),
    # ARABIC LETTER DYEH
    '\u0684': ('\u0684', '\uFB74', '\uFB75', '\uFB73'),
    # ARABIC LETTER TCHEH
    '\u0686': ('\u0686', '\uFB7C', '\uFB7D', '\uFB7B'),
    # ARABIC LETTER TCHEHEH
    '\u0687': ('\u0687', '\uFB80', '\uFB81', '\uFB7F'),
    # ARABIC LETTER DDAL
    '\u0688': ('\u0688', '', '', '\uFB89'),
    # ARABIC LETTER DAHAL
    '\u068C': ('\u068C', '', '', '\uFB85'),
    # ARABIC LETTER DDAHAL
    '\u068D': ('\u068D', '', '', '\uFB83'),
    # ARABIC LETTER DUL
    '\u068E': ('\u068E', '', '', '\uFB87'),
    # ARABIC LETTER RREH
    '\u0691': ('\u0691', '', '', '\uFB8D'),
    # ARABIC LETTER JEH
    '\u0698': ('\u0698', '', '', '\uFB8B'),
    # ARABIC LETTER VEH
    '\u06A4': ('\u06A4', '\uFB6C', '\uFB6D', '\uFB6B'),
    # ARABIC LETTER PEHEH
    '\u06A6': ('\u06A6', '\uFB70', '\uFB71', '\uFB6F'),
    # ARABIC LETTER KEHEH
    '\u06A9': ('\u06A9', '\uFB90', '\uFB91', '\uFB8F'),
    # ARABIC LETTER NG
    '\u06AD': ('\u06AD', '\uFBD5', '\uFBD6', '\uFBD4'),
    # ARABIC LETTER GAF
    '\u06AF': ('\u06AF', '\uFB94', '\uFB95', '\uFB93'),
    # ARABIC LETTER NGOEH
    '\u06B1': ('\u06B1', '\uFB9C', '\uFB9D', '\uFB9B'),
    # ARABIC LETTER GUEH
    '\u06B3': ('\u06B3', '\uFB98', '\uFB99', '\uFB97'),
    # ARABIC LETTER NOON GHUNNA
    '\u06BA': ('\u06BA', '', '', '\uFB9F'),
    # ARABIC LETTER RNOON
    '\u06BB': ('\u06BB', '\uFBA2', '\uFBA3', '\uFBA1'),
    # ARABIC LETTER HEH DOACHASHMEE
    '\u06BE': ('\u06BE', '\uFBAC', '\uFBAD', '\uFBAB'),
    # ARABIC LETTER HEH WITH YEH ABOVE
    '\u06C0': ('\u06C0', '', '', '\uFBA5'),
    # ARABIC LETTER HEH GOAL
    '\u06C1': ('\u06C1', '\uFBA8', '\uFBA9', '\uFBA7'),
    # ARABIC LETTER KIRGHIZ OE
    '\u06C5': ('\u06C5', '', '', '\uFBE1'),
    # ARABIC LETTER OE
    '\u06C6': ('\u06C6', '', '', '\uFBDA'),
    # ARABIC LETTER U
    '\u06C7': ('\u06C7', '', '', '\uFBD8'),
    # ARABIC LETTER YU
    '\u06C8': ('\u06C8', '', '', '\uFBDC'),
    # ARABIC LETTER KIRGHIZ YU
    '\u06C9': ('\u06C9', '', '', '\uFBE3'),
    # ARABIC LETTER VE
    '\u06CB': ('\u06CB', '', '', '\uFBDF'),
    # ARABIC LETTER FARSI YEH
    '\u06CC': ('\u06CC', '\uFBFE', '\uFBFF', '\uFBFD'),
    # ARABIC LETTER E
    '\u06D0': ('\u06D0', '\uFBE6', '\uFBE7', '\uFBE5'),
    # ARABIC LETTER YEH BARREE
    '\u06D2': ('\u06D2', '', '', '\uFBAF'),
    # ARABIC LETTER YEH BARREE WITH HAMZA ABOVE
    '\u06D3': ('\u06D3', '', '', '\uFBB1'),
    # Kurdish letter YEAH
    '\u06ce': ('\uE004', '\uE005', '\uE006', '\uE004'),
    # Kurdish letter Hamza same as arabic Teh without the point
    '\u06d5': ('\u06d5', '', '', '\uE000'),
    # ZWJ
    ZWJ: (ZWJ, ZWJ, ZWJ, ZWJ),
}

def connects_with_letter_before(letter,LETTERS):
    if letter not in LETTERS:
        return False
    forms = LETTERS[letter]
    return forms[FINAL] or forms[MEDIAL]


def connects_with_letter_after(letter,LETTERS):
    if letter not in LETTERS:
        return False
    forms = LETTERS[letter]
    return forms[INITIAL] or forms[MEDIAL]


def connects_with_letters_before_and_after(letter,LETTERS):
    if letter not in LETTERS:
        return False
    forms = LETTERS[letter]
    return forms[MEDIAL]

# Each ligature is of the format:
#
#   ('<key>', <replacement>)
#
# Where <key> is used in the configuration and <replacement> is of the format:
#
#   ('<match>', ('<isolated>', '<initial>', '<medial>', '<final>'))
#
# Where <match> is the string to replace, and <isolated> is the replacement in
# case <match> was in isolated form, <initial> is the replacement in case
# <match> was in initial form, <medial> is the replacement in case <match> was
# in medial form, and <final> is the replacement in case <match> was in final
# form. If no replacement is specified for a form, then no replacement of
# <match> will occur.

# Order here is important, it should be:
#   1. Sentences
#   2. Words
#   3. Letters
# This way we make sure we replace the longest ligatures first

from itertools import chain

SENTENCES_LIGATURES = (
    ('ARABIC LIGATURE BISMILLAH AR-RAHMAN AR-RAHEEM', (
        '\u0628\u0633\u0645\u0020'
        '\u0627\u0644\u0644\u0647\u0020'
        '\u0627\u0644\u0631\u062D\u0645\u0646\u0020'
        '\u0627\u0644\u0631\u062D\u064A\u0645',

        ('\uFDFD', '', '', '')
    )),
    ('ARABIC LIGATURE JALLAJALALOUHOU', (
        '\u062C\u0644\u0020\u062C\u0644\u0627\u0644\u0647',

        ('\uFDFB', '', '', '')
    )),
    ('ARABIC LIGATURE SALLALLAHOU ALAYHE WASALLAM', (
        '\u0635\u0644\u0649\u0020'
        '\u0627\u0644\u0644\u0647\u0020'
        '\u0639\u0644\u064A\u0647\u0020'
        '\u0648\u0633\u0644\u0645',

        ('\uFDFA', '', '', '')
    )),
)

WORDS_LIGATURES = (
    ('ARABIC LIGATURE ALLAH', (
        '\u0627\u0644\u0644\u0647', ('\uFDF2', '', '', ''),
    )),
    ('ARABIC LIGATURE AKBAR', (
        '\u0623\u0643\u0628\u0631', ('\uFDF3', '', '', ''),
    )),
    ('ARABIC LIGATURE ALAYHE', (
        '\u0639\u0644\u064A\u0647', ('\uFDF7', '', '', ''),
    )),
    ('ARABIC LIGATURE MOHAMMAD', (
        '\u0645\u062D\u0645\u062F', ('\uFDF4', '', '', ''),
    )),
    ('ARABIC LIGATURE RASOUL', (
        '\u0631\u0633\u0648\u0644', ('\uFDF6', '', '', ''),
    )),
    ('ARABIC LIGATURE SALAM', (
        '\u0635\u0644\u0639\u0645', ('\uFDF5', '', '', ''),
    )),
    ('ARABIC LIGATURE SALLA', (
        '\u0635\u0644\u0649', ('\uFDF9', '', '', ''),
    )),
    ('ARABIC LIGATURE WASALLAM', (
        '\u0648\u0633\u0644\u0645', ('\uFDF8', '', '', ''),
    )),
    ('RIAL SIGN', (
        '\u0631[\u06CC\u064A]\u0627\u0644', ('\uFDFC', '', '', ''),
    )),
)

LETTERS_LIGATURES = (
    ('ARABIC LIGATURE AIN WITH ALEF MAKSURA', (
        '\u0639\u0649', ('\uFCF7', '', '', '\uFD13'),
    )),
    ('ARABIC LIGATURE AIN WITH JEEM', (
        '\u0639\u062C', ('\uFC29', '\uFCBA', '', ''),
    )),
    ('ARABIC LIGATURE AIN WITH JEEM WITH MEEM', (
        '\u0639\u062C\u0645', ('', '\uFDC4', '', '\uFD75'),
    )),
    ('ARABIC LIGATURE AIN WITH MEEM', (
        '\u0639\u0645', ('\uFC2A', '\uFCBB', '', ''),
    )),
    ('ARABIC LIGATURE AIN WITH MEEM WITH ALEF MAKSURA', (
        '\u0639\u0645\u0649', ('', '', '', '\uFD78'),
    )),
    ('ARABIC LIGATURE AIN WITH MEEM WITH MEEM', (
        '\u0639\u0645\u0645', ('', '\uFD77', '', '\uFD76'),
    )),
    ('ARABIC LIGATURE AIN WITH MEEM WITH YEH', (
        '\u0639\u0645\u064A', ('', '', '', '\uFDB6'),
    )),
    ('ARABIC LIGATURE AIN WITH YEH', (
        '\u0639\u064A', ('\uFCF8', '', '', '\uFD14'),
    )),
    ('ARABIC LIGATURE ALEF MAKSURA WITH SUPERSCRIPT ALEF', (
        '\u0649\u0670', ('\uFC5D', '', '', '\uFC90'),
    )),
    ('ARABIC LIGATURE ALEF WITH FATHATAN', (
        '\u0627\u064B', ('\uFD3D', '', '', '\uFD3C'),
    )),
    ('ARABIC LIGATURE BEH WITH ALEF MAKSURA', (
        '\u0628\u0649', ('\uFC09', '', '', '\uFC6E'),
    )),
    ('ARABIC LIGATURE BEH WITH HAH', (
        '\u0628\u062D', ('\uFC06', '\uFC9D', '', ''),
    )),
    ('ARABIC LIGATURE BEH WITH HAH WITH YEH', (
        '\u0628\u062D\u064A', ('', '', '', '\uFDC2'),
    )),
    ('ARABIC LIGATURE BEH WITH HEH', (
        '\u0628\u0647', ('', '\uFCA0', '\uFCE2', ''),
    )),
    ('ARABIC LIGATURE BEH WITH JEEM', (
        '\u0628\u062C', ('\uFC05', '\uFC9C', '', ''),
    )),
    ('ARABIC LIGATURE BEH WITH KHAH', (
        '\u0628\u062E', ('\uFC07', '\uFC9E', '', ''),
    )),
    ('ARABIC LIGATURE BEH WITH KHAH WITH YEH', (
        '\u0628\u062E\u064A', ('', '', '', '\uFD9E'),
    )),
    ('ARABIC LIGATURE BEH WITH MEEM', (
        '\u0628\u0645', ('\uFC08', '\uFC9F', '\uFCE1', '\uFC6C'),
    )),
    ('ARABIC LIGATURE BEH WITH NOON', (
        '\u0628\u0646', ('', '', '', '\uFC6D'),
    )),
    ('ARABIC LIGATURE BEH WITH REH', (
        '\u0628\u0631', ('', '', '', '\uFC6A'),
    )),
    ('ARABIC LIGATURE BEH WITH YEH', (
        '\u0628\u064A', ('\uFC0A', '', '', '\uFC6F'),
    )),
    ('ARABIC LIGATURE BEH WITH ZAIN', (
        '\u0628\u0632', ('', '', '', '\uFC6B'),
    )),
    ('ARABIC LIGATURE DAD WITH ALEF MAKSURA', (
        '\u0636\u0649', ('\uFD07', '', '', '\uFD23'),
    )),
    ('ARABIC LIGATURE DAD WITH HAH', (
        '\u0636\u062D', ('\uFC23', '\uFCB5', '', ''),
    )),
    ('ARABIC LIGATURE DAD WITH HAH WITH ALEF MAKSURA', (
        '\u0636\u062D\u0649', ('', '', '', '\uFD6E'),
    )),
    ('ARABIC LIGATURE DAD WITH HAH WITH YEH', (
        '\u0636\u062D\u064A', ('', '', '', '\uFDAB'),
    )),
    ('ARABIC LIGATURE DAD WITH JEEM', (
        '\u0636\u062C', ('\uFC22', '\uFCB4', '', ''),
    )),
    ('ARABIC LIGATURE DAD WITH KHAH', (
        '\u0636\u062E', ('\uFC24', '\uFCB6', '', ''),
    )),
    ('ARABIC LIGATURE DAD WITH KHAH WITH MEEM', (
        '\u0636\u062E\u0645', ('', '\uFD70', '', '\uFD6F'),
    )),
    ('ARABIC LIGATURE DAD WITH MEEM', (
        '\u0636\u0645', ('\uFC25', '\uFCB7', '', ''),
    )),
    ('ARABIC LIGATURE DAD WITH REH', (
        '\u0636\u0631', ('\uFD10', '', '', '\uFD2C'),
    )),
    ('ARABIC LIGATURE DAD WITH YEH', (
        '\u0636\u064A', ('\uFD08', '', '', '\uFD24'),
    )),
    ('ARABIC LIGATURE FEH WITH ALEF MAKSURA', (
        '\u0641\u0649', ('\uFC31', '', '', '\uFC7C'),
    )),
    ('ARABIC LIGATURE FEH WITH HAH', (
        '\u0641\u062D', ('\uFC2E', '\uFCBF', '', ''),
    )),
    ('ARABIC LIGATURE FEH WITH JEEM', (
        '\u0641\u062C', ('\uFC2D', '\uFCBE', '', ''),
    )),
    ('ARABIC LIGATURE FEH WITH KHAH', (
        '\u0641\u062E', ('\uFC2F', '\uFCC0', '', ''),
    )),
    ('ARABIC LIGATURE FEH WITH KHAH WITH MEEM', (
        '\u0641\u062E\u0645', ('', '\uFD7D', '', '\uFD7C'),
    )),
    ('ARABIC LIGATURE FEH WITH MEEM', (
        '\u0641\u0645', ('\uFC30', '\uFCC1', '', ''),
    )),
    ('ARABIC LIGATURE FEH WITH MEEM WITH YEH', (
        '\u0641\u0645\u064A', ('', '', '', '\uFDC1'),
    )),
    ('ARABIC LIGATURE FEH WITH YEH', (
        '\u0641\u064A', ('\uFC32', '', '', '\uFC7D'),
    )),
    ('ARABIC LIGATURE GHAIN WITH ALEF MAKSURA', (
        '\u063A\u0649', ('\uFCF9', '', '', '\uFD15'),
    )),
    ('ARABIC LIGATURE GHAIN WITH JEEM', (
        '\u063A\u062C', ('\uFC2B', '\uFCBC', '', ''),
    )),
    ('ARABIC LIGATURE GHAIN WITH MEEM', (
        '\u063A\u0645', ('\uFC2C', '\uFCBD', '', ''),
    )),
    ('ARABIC LIGATURE GHAIN WITH MEEM WITH ALEF MAKSURA', (
        '\u063A\u0645\u0649', ('', '', '', '\uFD7B'),
    )),
    ('ARABIC LIGATURE GHAIN WITH MEEM WITH MEEM', (
        '\u063A\u0645\u0645', ('', '', '', '\uFD79'),
    )),
    ('ARABIC LIGATURE GHAIN WITH MEEM WITH YEH', (
        '\u063A\u0645\u064A', ('', '', '', '\uFD7A'),
    )),
    ('ARABIC LIGATURE GHAIN WITH YEH', (
        '\u063A\u064A', ('\uFCFA', '', '', '\uFD16'),
    )),
    ('ARABIC LIGATURE HAH WITH ALEF MAKSURA', (
        '\u062D\u0649', ('\uFCFF', '', '', '\uFD1B'),
    )),
    ('ARABIC LIGATURE HAH WITH JEEM', (
        '\u062D\u062C', ('\uFC17', '\uFCA9', '', ''),
    )),
    ('ARABIC LIGATURE HAH WITH JEEM WITH YEH', (
        '\u062D\u062C\u064A', ('', '', '', '\uFDBF'),
    )),
    ('ARABIC LIGATURE HAH WITH MEEM', (
        '\u062D\u0645', ('\uFC18', '\uFCAA', '', ''),
    )),
    ('ARABIC LIGATURE HAH WITH MEEM WITH ALEF MAKSURA', (
        '\u062D\u0645\u0649', ('', '', '', '\uFD5B'),
    )),
    ('ARABIC LIGATURE HAH WITH MEEM WITH YEH', (
        '\u062D\u0645\u064A', ('', '', '', '\uFD5A'),
    )),
    ('ARABIC LIGATURE HAH WITH YEH', (
        '\u062D\u064A', ('\uFD00', '', '', '\uFD1C'),
    )),
    ('ARABIC LIGATURE HEH WITH ALEF MAKSURA', (
        '\u0647\u0649', ('\uFC53', '', '', ''),
    )),
    ('ARABIC LIGATURE HEH WITH JEEM', (
        '\u0647\u062C', ('\uFC51', '\uFCD7', '', ''),
    )),
    ('ARABIC LIGATURE HEH WITH MEEM', (
        '\u0647\u0645', ('\uFC52', '\uFCD8', '', ''),
    )),
    ('ARABIC LIGATURE HEH WITH MEEM WITH JEEM', (
        '\u0647\u0645\u062C', ('', '\uFD93', '', ''),
    )),
    ('ARABIC LIGATURE HEH WITH MEEM WITH MEEM', (
        '\u0647\u0645\u0645', ('', '\uFD94', '', ''),
    )),
    ('ARABIC LIGATURE HEH WITH SUPERSCRIPT ALEF', (
        '\u0647\u0670', ('', '\uFCD9', '', ''),
    )),
    ('ARABIC LIGATURE HEH WITH YEH', (
        '\u0647\u064A', ('\uFC54', '', '', ''),
    )),
    ('ARABIC LIGATURE JEEM WITH ALEF MAKSURA', (
        '\u062C\u0649', ('\uFD01', '', '', '\uFD1D'),
    )),
    ('ARABIC LIGATURE JEEM WITH HAH', (
        '\u062C\u062D', ('\uFC15', '\uFCA7', '', ''),
    )),
    ('ARABIC LIGATURE JEEM WITH HAH WITH ALEF MAKSURA', (
        '\u062C\u062D\u0649', ('', '', '', '\uFDA6'),
    )),
    ('ARABIC LIGATURE JEEM WITH HAH WITH YEH', (
        '\u062C\u062D\u064A', ('', '', '', '\uFDBE'),
    )),
    ('ARABIC LIGATURE JEEM WITH MEEM', (
        '\u062C\u0645', ('\uFC16', '\uFCA8', '', ''),
    )),
    ('ARABIC LIGATURE JEEM WITH MEEM WITH ALEF MAKSURA', (
        '\u062C\u0645\u0649', ('', '', '', '\uFDA7'),
    )),
    ('ARABIC LIGATURE JEEM WITH MEEM WITH HAH', (
        '\u062C\u0645\u062D', ('', '\uFD59', '', '\uFD58'),
    )),
    ('ARABIC LIGATURE JEEM WITH MEEM WITH YEH', (
        '\u062C\u0645\u064A', ('', '', '', '\uFDA5'),
    )),
    ('ARABIC LIGATURE JEEM WITH YEH', (
        '\u062C\u064A', ('\uFD02', '', '', '\uFD1E'),
    )),
    ('ARABIC LIGATURE KAF WITH ALEF', (
        '\u0643\u0627', ('\uFC37', '', '', '\uFC80'),
    )),
    ('ARABIC LIGATURE KAF WITH ALEF MAKSURA', (
        '\u0643\u0649', ('\uFC3D', '', '', '\uFC83'),
    )),
    ('ARABIC LIGATURE KAF WITH HAH', (
        '\u0643\u062D', ('\uFC39', '\uFCC5', '', ''),
    )),
    ('ARABIC LIGATURE KAF WITH JEEM', (
        '\u0643\u062C', ('\uFC38', '\uFCC4', '', ''),
    )),
    ('ARABIC LIGATURE KAF WITH KHAH', (
        '\u0643\u062E', ('\uFC3A', '\uFCC6', '', ''),
    )),
    ('ARABIC LIGATURE KAF WITH LAM', (
        '\u0643\u0644', ('\uFC3B', '\uFCC7', '\uFCEB', '\uFC81'),
    )),
    ('ARABIC LIGATURE KAF WITH MEEM', (
        '\u0643\u0645', ('\uFC3C', '\uFCC8', '\uFCEC', '\uFC82'),
    )),
    ('ARABIC LIGATURE KAF WITH MEEM WITH MEEM', (
        '\u0643\u0645\u0645', ('', '\uFDC3', '', '\uFDBB'),
    )),
    ('ARABIC LIGATURE KAF WITH MEEM WITH YEH', (
        '\u0643\u0645\u064A', ('', '', '', '\uFDB7'),
    )),
    ('ARABIC LIGATURE KAF WITH YEH', (
        '\u0643\u064A', ('\uFC3E', '', '', '\uFC84'),
    )),
    ('ARABIC LIGATURE KHAH WITH ALEF MAKSURA', (
        '\u062E\u0649', ('\uFD03', '', '', '\uFD1F'),
    )),
    ('ARABIC LIGATURE KHAH WITH HAH', (
        '\u062E\u062D', ('\uFC1A', '', '', ''),
    )),
    ('ARABIC LIGATURE KHAH WITH JEEM', (
        '\u062E\u062C', ('\uFC19', '\uFCAB', '', ''),
    )),
    ('ARABIC LIGATURE KHAH WITH MEEM', (
        '\u062E\u0645', ('\uFC1B', '\uFCAC', '', ''),
    )),
    ('ARABIC LIGATURE KHAH WITH YEH', (
        '\u062E\u064A', ('\uFD04', '', '', '\uFD20'),
    )),
    ('ARABIC LIGATURE LAM WITH ALEF', (
        '\u0644\u0627', ('\uFEFB', '', '', '\uFEFC'),
    )),
    ('ARABIC LIGATURE LAM WITH ALEF MAKSURA', (
        '\u0644\u0649', ('\uFC43', '', '', '\uFC86'),
    )),
    ('ARABIC LIGATURE LAM WITH ALEF WITH HAMZA ABOVE', (
        '\u0644\u0623', ('\uFEF7', '', '', '\uFEF8'),
    )),
    ('ARABIC LIGATURE LAM WITH ALEF WITH HAMZA BELOW', (
        '\u0644\u0625', ('\uFEF9', '', '', '\uFEFA'),
    )),
    ('ARABIC LIGATURE LAM WITH ALEF WITH MADDA ABOVE', (
        '\u0644\u0622', ('\uFEF5', '', '', '\uFEF6'),
    )),
    ('ARABIC LIGATURE LAM WITH HAH', (
        '\u0644\u062D', ('\uFC40', '\uFCCA', '', ''),
    )),
    ('ARABIC LIGATURE LAM WITH HAH WITH ALEF MAKSURA', (
        '\u0644\u062D\u0649', ('', '', '', '\uFD82'),
    )),
    ('ARABIC LIGATURE LAM WITH HAH WITH MEEM', (
        '\u0644\u062D\u0645', ('', '\uFDB5', '', '\uFD80'),
    )),
    ('ARABIC LIGATURE LAM WITH HAH WITH YEH', (
        '\u0644\u062D\u064A', ('', '', '', '\uFD81'),
    )),
    ('ARABIC LIGATURE LAM WITH HEH', (
        '\u0644\u0647', ('', '\uFCCD', '', ''),
    )),
    ('ARABIC LIGATURE LAM WITH JEEM', (
        '\u0644\u062C', ('\uFC3F', '\uFCC9', '', ''),
    )),
    ('ARABIC LIGATURE LAM WITH JEEM WITH JEEM', (
        '\u0644\u062C\u062C', ('', '\uFD83', '', '\uFD84'),
    )),
    ('ARABIC LIGATURE LAM WITH JEEM WITH MEEM', (
        '\u0644\u062C\u0645', ('', '\uFDBA', '', '\uFDBC'),
    )),
    ('ARABIC LIGATURE LAM WITH JEEM WITH YEH', (
        '\u0644\u062C\u064A', ('', '', '', '\uFDAC'),
    )),
    ('ARABIC LIGATURE LAM WITH KHAH', (
        '\u0644\u062E', ('\uFC41', '\uFCCB', '', ''),
    )),
    ('ARABIC LIGATURE LAM WITH KHAH WITH MEEM', (
        '\u0644\u062E\u0645', ('', '\uFD86', '', '\uFD85'),
    )),
    ('ARABIC LIGATURE LAM WITH MEEM', (
        '\u0644\u0645', ('\uFC42', '\uFCCC', '\uFCED', '\uFC85'),
    )),
    ('ARABIC LIGATURE LAM WITH MEEM WITH HAH', (
        '\u0644\u0645\u062D', ('', '\uFD88', '', '\uFD87'),
    )),
    ('ARABIC LIGATURE LAM WITH MEEM WITH YEH', (
        '\u0644\u0645\u064A', ('', '', '', '\uFDAD'),
    )),
    ('ARABIC LIGATURE LAM WITH YEH', (
        '\u0644\u064A', ('\uFC44', '', '', '\uFC87'),
    )),
    ('ARABIC LIGATURE MEEM WITH ALEF', (
        '\u0645\u0627', ('', '', '', '\uFC88'),
    )),
    ('ARABIC LIGATURE MEEM WITH ALEF MAKSURA', (
        '\u0645\u0649', ('\uFC49', '', '', ''),
    )),
    ('ARABIC LIGATURE MEEM WITH HAH', (
        '\u0645\u062D', ('\uFC46', '\uFCCF', '', ''),
    )),
    ('ARABIC LIGATURE MEEM WITH HAH WITH JEEM', (
        '\u0645\u062D\u062C', ('', '\uFD89', '', ''),
    )),
    ('ARABIC LIGATURE MEEM WITH HAH WITH MEEM', (
        '\u0645\u062D\u0645', ('', '\uFD8A', '', ''),
    )),
    ('ARABIC LIGATURE MEEM WITH HAH WITH YEH', (
        '\u0645\u062D\u064A', ('', '', '', '\uFD8B'),
    )),
    ('ARABIC LIGATURE MEEM WITH JEEM', (
        '\u0645\u062C', ('\uFC45', '\uFCCE', '', ''),
    )),
    ('ARABIC LIGATURE MEEM WITH JEEM WITH HAH', (
        '\u0645\u062C\u062D', ('', '\uFD8C', '', ''),
    )),
    ('ARABIC LIGATURE MEEM WITH JEEM WITH KHAH', (
        '\u0645\u062C\u062E', ('', '\uFD92', '', ''),
    )),
    ('ARABIC LIGATURE MEEM WITH JEEM WITH MEEM', (
        '\u0645\u062C\u0645', ('', '\uFD8D', '', ''),
    )),
    ('ARABIC LIGATURE MEEM WITH JEEM WITH YEH', (
        '\u0645\u062C\u064A', ('', '', '', '\uFDC0'),
    )),
    ('ARABIC LIGATURE MEEM WITH KHAH', (
        '\u0645\u062E', ('\uFC47', '\uFCD0', '', ''),
    )),
    ('ARABIC LIGATURE MEEM WITH KHAH WITH JEEM', (
        '\u0645\u062E\u062C', ('', '\uFD8E', '', ''),
    )),
    ('ARABIC LIGATURE MEEM WITH KHAH WITH MEEM', (
        '\u0645\u062E\u0645', ('', '\uFD8F', '', ''),
    )),
    ('ARABIC LIGATURE MEEM WITH KHAH WITH YEH', (
        '\u0645\u062E\u064A', ('', '', '', '\uFDB9'),
    )),
    ('ARABIC LIGATURE MEEM WITH MEEM', (
        '\u0645\u0645', ('\uFC48', '\uFCD1', '', '\uFC89'),
    )),
    ('ARABIC LIGATURE MEEM WITH MEEM WITH YEH', (
        '\u0645\u0645\u064A', ('', '', '', '\uFDB1'),
    )),
    ('ARABIC LIGATURE MEEM WITH YEH', (
        '\u0645\u064A', ('\uFC4A', '', '', ''),
    )),
    ('ARABIC LIGATURE NOON WITH ALEF MAKSURA', (
        '\u0646\u0649', ('\uFC4F', '', '', '\uFC8E'),
    )),
    ('ARABIC LIGATURE NOON WITH HAH', (
        '\u0646\u062D', ('\uFC4C', '\uFCD3', '', ''),
    )),
    ('ARABIC LIGATURE NOON WITH HAH WITH ALEF MAKSURA', (
        '\u0646\u062D\u0649', ('', '', '', '\uFD96'),
    )),
    ('ARABIC LIGATURE NOON WITH HAH WITH MEEM', (
        '\u0646\u062D\u0645', ('', '\uFD95', '', ''),
    )),
    ('ARABIC LIGATURE NOON WITH HAH WITH YEH', (
        '\u0646\u062D\u064A', ('', '', '', '\uFDB3'),
    )),
    ('ARABIC LIGATURE NOON WITH HEH', (
        '\u0646\u0647', ('', '\uFCD6', '\uFCEF', ''),
    )),
    ('ARABIC LIGATURE NOON WITH JEEM', (
        '\u0646\u062C', ('\uFC4B', '\uFCD2', '', ''),
    )),
    ('ARABIC LIGATURE NOON WITH JEEM WITH ALEF MAKSURA', (
        '\u0646\u062C\u0649', ('', '', '', '\uFD99'),
    )),
    ('ARABIC LIGATURE NOON WITH JEEM WITH HAH', (
        '\u0646\u062C\u062D', ('', '\uFDB8', '', '\uFDBD'),
    )),
    ('ARABIC LIGATURE NOON WITH JEEM WITH MEEM', (
        '\u0646\u062C\u0645', ('', '\uFD98', '', '\uFD97'),
    )),
    ('ARABIC LIGATURE NOON WITH JEEM WITH YEH', (
        '\u0646\u062C\u064A', ('', '', '', '\uFDC7'),
    )),
    ('ARABIC LIGATURE NOON WITH KHAH', (
        '\u0646\u062E', ('\uFC4D', '\uFCD4', '', ''),
    )),
    ('ARABIC LIGATURE NOON WITH MEEM', (
        '\u0646\u0645', ('\uFC4E', '\uFCD5', '\uFCEE', '\uFC8C'),
    )),
    ('ARABIC LIGATURE NOON WITH MEEM WITH ALEF MAKSURA', (
        '\u0646\u0645\u0649', ('', '', '', '\uFD9B'),
    )),
    ('ARABIC LIGATURE NOON WITH MEEM WITH YEH', (
        '\u0646\u0645\u064A', ('', '', '', '\uFD9A'),
    )),
    ('ARABIC LIGATURE NOON WITH NOON', (
        '\u0646\u0646', ('', '', '', '\uFC8D'),
    )),
    ('ARABIC LIGATURE NOON WITH REH', (
        '\u0646\u0631', ('', '', '', '\uFC8A'),
    )),
    ('ARABIC LIGATURE NOON WITH YEH', (
        '\u0646\u064A', ('\uFC50', '', '', '\uFC8F'),
    )),
    ('ARABIC LIGATURE NOON WITH ZAIN', (
        '\u0646\u0632', ('', '', '', '\uFC8B'),
    )),
    ('ARABIC LIGATURE QAF WITH ALEF MAKSURA', (
        '\u0642\u0649', ('\uFC35', '', '', '\uFC7E'),
    )),
    ('ARABIC LIGATURE QAF WITH HAH', (
        '\u0642\u062D', ('\uFC33', '\uFCC2', '', ''),
    )),
    ('ARABIC LIGATURE QAF WITH MEEM', (
        '\u0642\u0645', ('\uFC34', '\uFCC3', '', ''),
    )),
    ('ARABIC LIGATURE QAF WITH MEEM WITH HAH', (
        '\u0642\u0645\u062D', ('', '\uFDB4', '', '\uFD7E'),
    )),
    ('ARABIC LIGATURE QAF WITH MEEM WITH MEEM', (
        '\u0642\u0645\u0645', ('', '', '', '\uFD7F'),
    )),
    ('ARABIC LIGATURE QAF WITH MEEM WITH YEH', (
        '\u0642\u0645\u064A', ('', '', '', '\uFDB2'),
    )),
    ('ARABIC LIGATURE QAF WITH YEH', (
        '\u0642\u064A', ('\uFC36', '', '', '\uFC7F'),
    )),
    ('ARABIC LIGATURE QALA USED AS KORANIC STOP SIGN', (
        '\u0642\u0644\u06D2', ('\uFDF1', '', '', ''),
    )),
    ('ARABIC LIGATURE REH WITH SUPERSCRIPT ALEF', (
        '\u0631\u0670', ('\uFC5C', '', '', ''),
    )),
    ('ARABIC LIGATURE SAD WITH ALEF MAKSURA', (
        '\u0635\u0649', ('\uFD05', '', '', '\uFD21'),
    )),
    ('ARABIC LIGATURE SAD WITH HAH', (
        '\u0635\u062D', ('\uFC20', '\uFCB1', '', ''),
    )),
    ('ARABIC LIGATURE SAD WITH HAH WITH HAH', (
        '\u0635\u062D\u062D', ('', '\uFD65', '', '\uFD64'),
    )),
    ('ARABIC LIGATURE SAD WITH HAH WITH YEH', (
        '\u0635\u062D\u064A', ('', '', '', '\uFDA9'),
    )),
    ('ARABIC LIGATURE SAD WITH KHAH', (
        '\u0635\u062E', ('', '\uFCB2', '', ''),
    )),
    ('ARABIC LIGATURE SAD WITH MEEM', (
        '\u0635\u0645', ('\uFC21', '\uFCB3', '', ''),
    )),
    ('ARABIC LIGATURE SAD WITH MEEM WITH MEEM', (
        '\u0635\u0645\u0645', ('', '\uFDC5', '', '\uFD66'),
    )),
    ('ARABIC LIGATURE SAD WITH REH', (
        '\u0635\u0631', ('\uFD0F', '', '', '\uFD2B'),
    )),
    ('ARABIC LIGATURE SAD WITH YEH', (
        '\u0635\u064A', ('\uFD06', '', '', '\uFD22'),
    )),
    ('ARABIC LIGATURE SALLA USED AS KORANIC STOP SIGN', (
        '\u0635\u0644\u06D2', ('\uFDF0', '', '', ''),
    )),
    ('ARABIC LIGATURE SEEN WITH ALEF MAKSURA', (
        '\u0633\u0649', ('\uFCFB', '', '', '\uFD17'),
    )),
    ('ARABIC LIGATURE SEEN WITH HAH', (
        '\u0633\u062D', ('\uFC1D', '\uFCAE', '\uFD35', ''),
    )),
    ('ARABIC LIGATURE SEEN WITH HAH WITH JEEM', (
        '\u0633\u062D\u062C', ('', '\uFD5C', '', ''),
    )),
    ('ARABIC LIGATURE SEEN WITH HEH', (
        '\u0633\u0647', ('', '\uFD31', '\uFCE8', ''),
    )),
    ('ARABIC LIGATURE SEEN WITH JEEM', (
        '\u0633\u062C', ('\uFC1C', '\uFCAD', '\uFD34', ''),
    )),
    ('ARABIC LIGATURE SEEN WITH JEEM WITH ALEF MAKSURA', (
        '\u0633\u062C\u0649', ('', '', '', '\uFD5E'),
    )),
    ('ARABIC LIGATURE SEEN WITH JEEM WITH HAH', (
        '\u0633\u062C\u062D', ('', '\uFD5D', '', ''),
    )),
    ('ARABIC LIGATURE SEEN WITH KHAH', (
        '\u0633\u062E', ('\uFC1E', '\uFCAF', '\uFD36', ''),
    )),
    ('ARABIC LIGATURE SEEN WITH KHAH WITH ALEF MAKSURA', (
        '\u0633\u062E\u0649', ('', '', '', '\uFDA8'),
    )),
    ('ARABIC LIGATURE SEEN WITH KHAH WITH YEH', (
        '\u0633\u062E\u064A', ('', '', '', '\uFDC6'),
    )),
    ('ARABIC LIGATURE SEEN WITH MEEM', (
        '\u0633\u0645', ('\uFC1F', '\uFCB0', '\uFCE7', ''),
    )),
    ('ARABIC LIGATURE SEEN WITH MEEM WITH HAH', (
        '\u0633\u0645\u062D', ('', '\uFD60', '', '\uFD5F'),
    )),
    ('ARABIC LIGATURE SEEN WITH MEEM WITH JEEM', (
        '\u0633\u0645\u062C', ('', '\uFD61', '', ''),
    )),
    ('ARABIC LIGATURE SEEN WITH MEEM WITH MEEM', (
        '\u0633\u0645\u0645', ('', '\uFD63', '', '\uFD62'),
    )),
    ('ARABIC LIGATURE SEEN WITH REH', (
        '\u0633\u0631', ('\uFD0E', '', '', '\uFD2A'),
    )),
    ('ARABIC LIGATURE SEEN WITH YEH', (
        '\u0633\u064A', ('\uFCFC', '', '', '\uFD18'),
    )),

    # Arabic ligatures with Shadda, the order of characters doesn't matter
    ('ARABIC LIGATURE SHADDA WITH DAMMATAN ISOLATED FORM', (
        '(?:\u064C\u0651|\u0651\u064C)',

        ('\uFC5E', '\uFC5E', '\uFC5E', '\uFC5E'),
    )),
    ('ARABIC LIGATURE SHADDA WITH KASRATAN ISOLATED FORM', (
        '(?:\u064D\u0651|\u0651\u064D)',

        ('\uFC5F', '\uFC5F', '\uFC5F', '\uFC5F'),
    )),
    ('ARABIC LIGATURE SHADDA WITH FATHA ISOLATED FORM', (
        '(?:\u064E\u0651|\u0651\u064E)',

        ('\uFC60', '\uFC60', '\uFC60', '\uFC60'),
    )),
    ('ARABIC LIGATURE SHADDA WITH DAMMA ISOLATED FORM', (
        '(?:\u064F\u0651|\u0651\u064F)',

        ('\uFC61', '\uFC61', '\uFC61', '\uFC61'),
    )),
    ('ARABIC LIGATURE SHADDA WITH KASRA ISOLATED FORM', (
        '(?:\u0650\u0651|\u0651\u0650)',

        ('\uFC62', '\uFC62', '\uFC62', '\uFC62'),
    )),
    ('ARABIC LIGATURE SHADDA WITH SUPERSCRIPT ALEF', (
        '(?:\u0651\u0670|\u0670\u0651)', ('\uFC63', '', '', ''),
    )),

    # There is a special case when they are with Tatweel
    ('ARABIC LIGATURE SHADDA WITH FATHA MEDIAL FORM', (
        '\u0640(?:\u064E\u0651|\u0651\u064E)',

        ('\uFCF2', '\uFCF2', '\uFCF2', '\uFCF2'),
    )),
    ('ARABIC LIGATURE SHADDA WITH DAMMA MEDIAL FORM', (
        '\u0640(?:\u064F\u0651|\u0651\u064F)',

        ('\uFCF3', '\uFCF3', '\uFCF3', '\uFCF3'),
    )),
    ('ARABIC LIGATURE SHADDA WITH KASRA MEDIAL FORM', (
        '\u0640(?:\u0650\u0651|\u0651\u0650)',

        ('\uFCF4', '\uFCF4', '\uFCF4', '\uFCF4'),
    )),

    # Repeated with different keys to be backward compatible
    ('ARABIC LIGATURE SHADDA WITH FATHA', (
        '\u0640(?:\u064E\u0651|\u0651\u064E)',

        ('\uFCF2', '\uFCF2', '\uFCF2', '\uFCF2'),
    )),
    ('ARABIC LIGATURE SHADDA WITH DAMMA', (
        '\u0640(?:\u064F\u0651|\u0651\u064F)',

        ('\uFCF3', '\uFCF3', '\uFCF3', '\uFCF3'),
    )),
    ('ARABIC LIGATURE SHADDA WITH KASRA', (
        '\u0640(?:\u0650\u0651|\u0651\u0650)',

        ('\uFCF4', '\uFCF4', '\uFCF4', '\uFCF4'),
    )),

    ('ARABIC LIGATURE SHEEN WITH ALEF MAKSURA', (
        '\u0634\u0649', ('\uFCFD', '', '', '\uFD19'),
    )),
    ('ARABIC LIGATURE SHEEN WITH HAH', (
        '\u0634\u062D', ('\uFD0A', '\uFD2E', '\uFD38', '\uFD26'),
    )),
    ('ARABIC LIGATURE SHEEN WITH HAH WITH MEEM', (
        '\u0634\u062D\u0645', ('', '\uFD68', '', '\uFD67'),
    )),
    ('ARABIC LIGATURE SHEEN WITH HAH WITH YEH', (
        '\u0634\u062D\u064A', ('', '', '', '\uFDAA'),
    )),
    ('ARABIC LIGATURE SHEEN WITH HEH', (
        '\u0634\u0647', ('', '\uFD32', '\uFCEA', ''),
    )),
    ('ARABIC LIGATURE SHEEN WITH JEEM', (
        '\u0634\u062C', ('\uFD09', '\uFD2D', '\uFD37', '\uFD25'),
    )),
    ('ARABIC LIGATURE SHEEN WITH JEEM WITH YEH', (
        '\u0634\u062C\u064A', ('', '', '', '\uFD69'),
    )),
    ('ARABIC LIGATURE SHEEN WITH KHAH', (
        '\u0634\u062E', ('\uFD0B', '\uFD2F', '\uFD39', '\uFD27'),
    )),
    ('ARABIC LIGATURE SHEEN WITH MEEM', (
        '\u0634\u0645', ('\uFD0C', '\uFD30', '\uFCE9', '\uFD28'),
    )),
    ('ARABIC LIGATURE SHEEN WITH MEEM WITH KHAH', (
        '\u0634\u0645\u062E', ('', '\uFD6B', '', '\uFD6A'),
    )),
    ('ARABIC LIGATURE SHEEN WITH MEEM WITH MEEM', (
        '\u0634\u0645\u0645', ('', '\uFD6D', '', '\uFD6C'),
    )),
    ('ARABIC LIGATURE SHEEN WITH REH', (
        '\u0634\u0631', ('\uFD0D', '', '', '\uFD29'),
    )),
    ('ARABIC LIGATURE SHEEN WITH YEH', (
        '\u0634\u064A', ('\uFCFE', '', '', '\uFD1A'),
    )),
    ('ARABIC LIGATURE TAH WITH ALEF MAKSURA', (
        '\u0637\u0649', ('\uFCF5', '', '', '\uFD11'),
    )),
    ('ARABIC LIGATURE TAH WITH HAH', (
        '\u0637\u062D', ('\uFC26', '\uFCB8', '', ''),
    )),
    ('ARABIC LIGATURE TAH WITH MEEM', (
        '\u0637\u0645', ('\uFC27', '\uFD33', '\uFD3A', ''),
    )),
    ('ARABIC LIGATURE TAH WITH MEEM WITH HAH', (
        '\u0637\u0645\u062D', ('', '\uFD72', '', '\uFD71'),
    )),
    ('ARABIC LIGATURE TAH WITH MEEM WITH MEEM', (
        '\u0637\u0645\u0645', ('', '\uFD73', '', ''),
    )),
    ('ARABIC LIGATURE TAH WITH MEEM WITH YEH', (
        '\u0637\u0645\u064A', ('', '', '', '\uFD74'),
    )),
    ('ARABIC LIGATURE TAH WITH YEH', (
        '\u0637\u064A', ('\uFCF6', '', '', '\uFD12'),
    )),
    ('ARABIC LIGATURE TEH WITH ALEF MAKSURA', (
        '\u062A\u0649', ('\uFC0F', '', '', '\uFC74'),
    )),
    ('ARABIC LIGATURE TEH WITH HAH', (
        '\u062A\u062D', ('\uFC0C', '\uFCA2', '', ''),
    )),
    ('ARABIC LIGATURE TEH WITH HAH WITH JEEM', (
        '\u062A\u062D\u062C', ('', '\uFD52', '', '\uFD51'),
    )),
    ('ARABIC LIGATURE TEH WITH HAH WITH MEEM', (
        '\u062A\u062D\u0645', ('', '\uFD53', '', ''),
    )),
    ('ARABIC LIGATURE TEH WITH HEH', (
        '\u062A\u0647', ('', '\uFCA5', '\uFCE4', ''),
    )),
    ('ARABIC LIGATURE TEH WITH JEEM', (
        '\u062A\u062C', ('\uFC0B', '\uFCA1', '', ''),
    )),
    ('ARABIC LIGATURE TEH WITH JEEM WITH ALEF MAKSURA', (
        '\u062A\u062C\u0649', ('', '', '', '\uFDA0'),
    )),
    ('ARABIC LIGATURE TEH WITH JEEM WITH MEEM', (
        '\u062A\u062C\u0645', ('', '\uFD50', '', ''),
    )),
    ('ARABIC LIGATURE TEH WITH JEEM WITH YEH', (
        '\u062A\u062C\u064A', ('', '', '', '\uFD9F'),
    )),
    ('ARABIC LIGATURE TEH WITH KHAH', (
        '\u062A\u062E', ('\uFC0D', '\uFCA3', '', ''),
    )),
    ('ARABIC LIGATURE TEH WITH KHAH WITH ALEF MAKSURA', (
        '\u062A\u062E\u0649', ('', '', '', '\uFDA2'),
    )),
    ('ARABIC LIGATURE TEH WITH KHAH WITH MEEM', (
        '\u062A\u062E\u0645', ('', '\uFD54', '', ''),
    )),
    ('ARABIC LIGATURE TEH WITH KHAH WITH YEH', (
        '\u062A\u062E\u064A', ('', '', '', '\uFDA1'),
    )),
    ('ARABIC LIGATURE TEH WITH MEEM', (
        '\u062A\u0645', ('\uFC0E', '\uFCA4', '\uFCE3', '\uFC72'),
    )),
    ('ARABIC LIGATURE TEH WITH MEEM WITH ALEF MAKSURA', (
        '\u062A\u0645\u0649', ('', '', '', '\uFDA4'),
    )),
    ('ARABIC LIGATURE TEH WITH MEEM WITH HAH', (
        '\u062A\u0645\u062D', ('', '\uFD56', '', ''),
    )),
    ('ARABIC LIGATURE TEH WITH MEEM WITH JEEM', (
        '\u062A\u0645\u062C', ('', '\uFD55', '', ''),
    )),
    ('ARABIC LIGATURE TEH WITH MEEM WITH KHAH', (
        '\u062A\u0645\u062E', ('', '\uFD57', '', ''),
    )),
    ('ARABIC LIGATURE TEH WITH MEEM WITH YEH', (
        '\u062A\u0645\u064A', ('', '', '', '\uFDA3'),
    )),
    ('ARABIC LIGATURE TEH WITH NOON', (
        '\u062A\u0646', ('', '', '', '\uFC73'),
    )),
    ('ARABIC LIGATURE TEH WITH REH', (
        '\u062A\u0631', ('', '', '', '\uFC70'),
    )),
    ('ARABIC LIGATURE TEH WITH YEH', (
        '\u062A\u064A', ('\uFC10', '', '', '\uFC75'),
    )),
    ('ARABIC LIGATURE TEH WITH ZAIN', (
        '\u062A\u0632', ('', '', '', '\uFC71'),
    )),
    ('ARABIC LIGATURE THAL WITH SUPERSCRIPT ALEF', (
        '\u0630\u0670', ('\uFC5B', '', '', ''),
    )),
    ('ARABIC LIGATURE THEH WITH ALEF MAKSURA', (
        '\u062B\u0649', ('\uFC13', '', '', '\uFC7A'),
    )),
    ('ARABIC LIGATURE THEH WITH HEH', (
        '\u062B\u0647', ('', '', '\uFCE6', ''),
    )),
    ('ARABIC LIGATURE THEH WITH JEEM', (
        '\u062B\u062C', ('\uFC11', '', '', ''),
    )),
    ('ARABIC LIGATURE THEH WITH MEEM', (
        '\u062B\u0645', ('\uFC12', '\uFCA6', '\uFCE5', '\uFC78'),
    )),
    ('ARABIC LIGATURE THEH WITH NOON', (
        '\u062B\u0646', ('', '', '', '\uFC79'),
    )),
    ('ARABIC LIGATURE THEH WITH REH', (
        '\u062B\u0631', ('', '', '', '\uFC76'),
    )),
    ('ARABIC LIGATURE THEH WITH YEH', (
        '\u062B\u064A', ('\uFC14', '', '', '\uFC7B'),
    )),
    ('ARABIC LIGATURE THEH WITH ZAIN', (
        '\u062B\u0632', ('', '', '', '\uFC77'),
    )),
    ('ARABIC LIGATURE UIGHUR KIRGHIZ YEH WITH HAMZA ABOVE WITH ALEF MAKSURA', (
        '\u0626\u0649', ('\uFBF9', '\uFBFB', '', '\uFBFA'),
    )),
    ('ARABIC LIGATURE YEH WITH ALEF MAKSURA', (
        '\u064A\u0649', ('\uFC59', '', '', '\uFC95'),
    )),
    ('ARABIC LIGATURE YEH WITH HAH', (
        '\u064A\u062D', ('\uFC56', '\uFCDB', '', ''),
    )),
    ('ARABIC LIGATURE YEH WITH HAH WITH YEH', (
        '\u064A\u062D\u064A', ('', '', '', '\uFDAE'),
    )),
    ('ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH AE', (
        '\u0626\u06D5', ('\uFBEC', '', '', '\uFBED'),
    )),
    ('ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH ALEF', (
        '\u0626\u0627', ('\uFBEA', '', '', '\uFBEB'),
    )),
    ('ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH ALEF MAKSURA', (
        '\u0626\u0649', ('\uFC03', '', '', '\uFC68'),
    )),
    ('ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH E', (
        '\u0626\u06D0', ('\uFBF6', '\uFBF8', '', '\uFBF7'),
    )),
    ('ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH HAH', (
        '\u0626\u062D', ('\uFC01', '\uFC98', '', ''),
    )),
    ('ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH HEH', (
        '\u0626\u0647', ('', '\uFC9B', '\uFCE0', ''),
    )),
    ('ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH JEEM', (
        '\u0626\u062C', ('\uFC00', '\uFC97', '', ''),
    )),
    ('ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH KHAH', (
        '\u0626\u062E', ('', '\uFC99', '', ''),
    )),
    ('ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH MEEM', (
        '\u0626\u0645', ('\uFC02', '\uFC9A', '\uFCDF', '\uFC66'),
    )),
    ('ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH NOON', (
        '\u0626\u0646', ('', '', '', '\uFC67'),
    )),
    ('ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH OE', (
        '\u0626\u06C6', ('\uFBF2', '', '', '\uFBF3'),
    )),
    ('ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH REH', (
        '\u0626\u0631', ('', '', '', '\uFC64'),
    )),
    ('ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH U', (
        '\u0626\u06C7', ('\uFBF0', '', '', '\uFBF1'),
    )),
    ('ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH WAW', (
        '\u0626\u0648', ('\uFBEE', '', '', '\uFBEF'),
    )),
    ('ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH YEH', (
        '\u0626\u064A', ('\uFC04', '', '', '\uFC69'),
    )),
    ('ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH YU', (
        '\u0626\u06C8', ('\uFBF4', '', '', '\uFBF5'),
    )),
    ('ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH ZAIN', (
        '\u0626\u0632', ('', '', '', '\uFC65'),
    )),
    ('ARABIC LIGATURE YEH WITH HEH', (
        '\u064A\u0647', ('', '\uFCDE', '\uFCF1', ''),
    )),
    ('ARABIC LIGATURE YEH WITH JEEM', (
        '\u064A\u062C', ('\uFC55', '\uFCDA', '', ''),
    )),
    ('ARABIC LIGATURE YEH WITH JEEM WITH YEH', (
        '\u064A\u062C\u064A', ('', '', '', '\uFDAF'),
    )),
    ('ARABIC LIGATURE YEH WITH KHAH', (
        '\u064A\u062E', ('\uFC57', '\uFCDC', '', ''),
    )),
    ('ARABIC LIGATURE YEH WITH MEEM', (
        '\u064A\u0645', ('\uFC58', '\uFCDD', '\uFCF0', '\uFC93'),
    )),
    ('ARABIC LIGATURE YEH WITH MEEM WITH MEEM', (
        '\u064A\u0645\u0645', ('', '\uFD9D', '', '\uFD9C'),
    )),
    ('ARABIC LIGATURE YEH WITH MEEM WITH YEH', (
        '\u064A\u0645\u064A', ('', '', '', '\uFDB0'),
    )),
    ('ARABIC LIGATURE YEH WITH NOON', (
        '\u064A\u0646', ('', '', '', '\uFC94'),
    )),
    ('ARABIC LIGATURE YEH WITH REH', (
        '\u064A\u0631', ('', '', '', '\uFC91'),
    )),
    ('ARABIC LIGATURE YEH WITH YEH', (
        '\u064A\u064A', ('\uFC5A', '', '', '\uFC96'),
    )),
    ('ARABIC LIGATURE YEH WITH ZAIN', (
        '\u064A\u0632', ('', '', '', '\uFC92'),
    )),
    ('ARABIC LIGATURE ZAH WITH MEEM', (
        '\u0638\u0645', ('\uFC28', '\uFCB9', '\uFD3B', ''),
    )),
)

LIGATURES = tuple(chain(SENTENCES_LIGATURES, WORDS_LIGATURES, LETTERS_LIGATURES))


# -*- coding: utf-8 -*-

# This work is licensed under the MIT License.
# To view a copy of this license, visit https://opensource.org/licenses/MIT

# Written by Abdullah Diab (mpcabd)
# Email: mpcabd@gmail.com
# Website: http://mpcabd.xyz

import os

from configparser import ConfigParser

# from .letters import (UNSHAPED, ISOLATED, LETTERS_ARABIC)
# from .ligatures import (SENTENCES_LIGATURES,
#                         WORDS_LIGATURES,
#                         LETTERS_LIGATURES)

try:
    from fontTools.ttLib import TTFont
    with_font_config = True
except ImportError:
    with_font_config = False

ENABLE_NO_LIGATURES = 0b000
ENABLE_SENTENCES_LIGATURES = 0b001
ENABLE_WORDS_LIGATURES = 0b010
ENABLE_LETTERS_LIGATURES = 0b100
ENABLE_ALL_LIGATURES = 0b111

default_config = {
    # Supported languages are: [Arabic, ArabicV2, Kurdish]
    # More languages might be supported soon.
    # `Arabic` is default and recommended to work in most of the cases and
    # supports (Arabic, Urdu and Farsi)
    # `ArabicV2` is only to be used with certain font that you run into missing
    # chars `Kurdish` if you are using Kurdish Sarchia font is recommended,
    # work with both unicode and classic Arabic-Kurdish keybouard
    'language': 'Arabic',

    # Whether to delete the Harakat (Tashkeel) before reshaping or not.
    'delete_harakat': True,

    # Whether to shift the Harakat (Tashkeel) one position so they appear
    # correctly when string is reversed
    'shift_harakat_position': False,

    # Whether to delete the Tatweel (U+0640) before reshaping or not.
    'delete_tatweel': False,

    # Whether to support ZWJ (U+200D) or not.
    'support_zwj': True,

    # Use unshaped form instead of isolated form.
    'use_unshaped_instead_of_isolated': False,

    # Whether to use ligatures or not.
    # Serves as a shortcut to disable all ligatures.
    'support_ligatures': True,

    # When `support_ligatures` is enabled.
    # Separate ligatures configuration take precedence over it.
    # When `support_ligatures` is disabled,
    # separate ligatures configurations are ignored.

    # ------------------- Begin: Ligatures Configurations ------------------ #

    # Sentences (Enabled on top)
    'ARABIC LIGATURE BISMILLAH AR-RAHMAN AR-RAHEEM': False,
    'ARABIC LIGATURE JALLAJALALOUHOU': False,
    'ARABIC LIGATURE SALLALLAHOU ALAYHE WASALLAM': False,

    # Words (Enabled on top)
    'ARABIC LIGATURE ALLAH': True,
    'ARABIC LIGATURE AKBAR': False,
    'ARABIC LIGATURE ALAYHE': False,
    'ARABIC LIGATURE MOHAMMAD': False,
    'ARABIC LIGATURE RASOUL': False,
    'ARABIC LIGATURE SALAM': False,
    'ARABIC LIGATURE SALLA': False,
    'ARABIC LIGATURE WASALLAM': False,
    'RIAL SIGN': False,

    # Letters (Enabled on top)
    'ARABIC LIGATURE LAM WITH ALEF': True,
    'ARABIC LIGATURE LAM WITH ALEF WITH HAMZA ABOVE': True,
    'ARABIC LIGATURE LAM WITH ALEF WITH HAMZA BELOW': True,
    'ARABIC LIGATURE LAM WITH ALEF WITH MADDA ABOVE': True,
    'ARABIC LIGATURE AIN WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE AIN WITH JEEM': False,
    'ARABIC LIGATURE AIN WITH JEEM WITH MEEM': False,
    'ARABIC LIGATURE AIN WITH MEEM': False,
    'ARABIC LIGATURE AIN WITH MEEM WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE AIN WITH MEEM WITH MEEM': False,
    'ARABIC LIGATURE AIN WITH MEEM WITH YEH': False,
    'ARABIC LIGATURE AIN WITH YEH': False,
    'ARABIC LIGATURE ALEF MAKSURA WITH SUPERSCRIPT ALEF': False,
    'ARABIC LIGATURE ALEF WITH FATHATAN': False,
    'ARABIC LIGATURE BEH WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE BEH WITH HAH': False,
    'ARABIC LIGATURE BEH WITH HAH WITH YEH': False,
    'ARABIC LIGATURE BEH WITH HEH': False,
    'ARABIC LIGATURE BEH WITH JEEM': False,
    'ARABIC LIGATURE BEH WITH KHAH': False,
    'ARABIC LIGATURE BEH WITH KHAH WITH YEH': False,
    'ARABIC LIGATURE BEH WITH MEEM': False,
    'ARABIC LIGATURE BEH WITH NOON': False,
    'ARABIC LIGATURE BEH WITH REH': False,
    'ARABIC LIGATURE BEH WITH YEH': False,
    'ARABIC LIGATURE BEH WITH ZAIN': False,
    'ARABIC LIGATURE DAD WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE DAD WITH HAH': False,
    'ARABIC LIGATURE DAD WITH HAH WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE DAD WITH HAH WITH YEH': False,
    'ARABIC LIGATURE DAD WITH JEEM': False,
    'ARABIC LIGATURE DAD WITH KHAH': False,
    'ARABIC LIGATURE DAD WITH KHAH WITH MEEM': False,
    'ARABIC LIGATURE DAD WITH MEEM': False,
    'ARABIC LIGATURE DAD WITH REH': False,
    'ARABIC LIGATURE DAD WITH YEH': False,
    'ARABIC LIGATURE FEH WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE FEH WITH HAH': False,
    'ARABIC LIGATURE FEH WITH JEEM': False,
    'ARABIC LIGATURE FEH WITH KHAH': False,
    'ARABIC LIGATURE FEH WITH KHAH WITH MEEM': False,
    'ARABIC LIGATURE FEH WITH MEEM': False,
    'ARABIC LIGATURE FEH WITH MEEM WITH YEH': False,
    'ARABIC LIGATURE FEH WITH YEH': False,
    'ARABIC LIGATURE GHAIN WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE GHAIN WITH JEEM': False,
    'ARABIC LIGATURE GHAIN WITH MEEM': False,
    'ARABIC LIGATURE GHAIN WITH MEEM WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE GHAIN WITH MEEM WITH MEEM': False,
    'ARABIC LIGATURE GHAIN WITH MEEM WITH YEH': False,
    'ARABIC LIGATURE GHAIN WITH YEH': False,
    'ARABIC LIGATURE HAH WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE HAH WITH JEEM': False,
    'ARABIC LIGATURE HAH WITH JEEM WITH YEH': False,
    'ARABIC LIGATURE HAH WITH MEEM': False,
    'ARABIC LIGATURE HAH WITH MEEM WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE HAH WITH MEEM WITH YEH': False,
    'ARABIC LIGATURE HAH WITH YEH': False,
    'ARABIC LIGATURE HEH WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE HEH WITH JEEM': False,
    'ARABIC LIGATURE HEH WITH MEEM': False,
    'ARABIC LIGATURE HEH WITH MEEM WITH JEEM': False,
    'ARABIC LIGATURE HEH WITH MEEM WITH MEEM': False,
    'ARABIC LIGATURE HEH WITH SUPERSCRIPT ALEF': False,
    'ARABIC LIGATURE HEH WITH YEH': False,
    'ARABIC LIGATURE JEEM WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE JEEM WITH HAH': False,
    'ARABIC LIGATURE JEEM WITH HAH WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE JEEM WITH HAH WITH YEH': False,
    'ARABIC LIGATURE JEEM WITH MEEM': False,
    'ARABIC LIGATURE JEEM WITH MEEM WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE JEEM WITH MEEM WITH HAH': False,
    'ARABIC LIGATURE JEEM WITH MEEM WITH YEH': False,
    'ARABIC LIGATURE JEEM WITH YEH': False,
    'ARABIC LIGATURE KAF WITH ALEF': False,
    'ARABIC LIGATURE KAF WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE KAF WITH HAH': False,
    'ARABIC LIGATURE KAF WITH JEEM': False,
    'ARABIC LIGATURE KAF WITH KHAH': False,
    'ARABIC LIGATURE KAF WITH LAM': False,
    'ARABIC LIGATURE KAF WITH MEEM': False,
    'ARABIC LIGATURE KAF WITH MEEM WITH MEEM': False,
    'ARABIC LIGATURE KAF WITH MEEM WITH YEH': False,
    'ARABIC LIGATURE KAF WITH YEH': False,
    'ARABIC LIGATURE KHAH WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE KHAH WITH HAH': False,
    'ARABIC LIGATURE KHAH WITH JEEM': False,
    'ARABIC LIGATURE KHAH WITH MEEM': False,
    'ARABIC LIGATURE KHAH WITH YEH': False,
    'ARABIC LIGATURE LAM WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE LAM WITH HAH': False,
    'ARABIC LIGATURE LAM WITH HAH WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE LAM WITH HAH WITH MEEM': False,
    'ARABIC LIGATURE LAM WITH HAH WITH YEH': False,
    'ARABIC LIGATURE LAM WITH HEH': False,
    'ARABIC LIGATURE LAM WITH JEEM': False,
    'ARABIC LIGATURE LAM WITH JEEM WITH JEEM': False,
    'ARABIC LIGATURE LAM WITH JEEM WITH MEEM': False,
    'ARABIC LIGATURE LAM WITH JEEM WITH YEH': False,
    'ARABIC LIGATURE LAM WITH KHAH': False,
    'ARABIC LIGATURE LAM WITH KHAH WITH MEEM': False,
    'ARABIC LIGATURE LAM WITH MEEM': False,
    'ARABIC LIGATURE LAM WITH MEEM WITH HAH': False,
    'ARABIC LIGATURE LAM WITH MEEM WITH YEH': False,
    'ARABIC LIGATURE LAM WITH YEH': False,
    'ARABIC LIGATURE MEEM WITH ALEF': False,
    'ARABIC LIGATURE MEEM WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE MEEM WITH HAH': False,
    'ARABIC LIGATURE MEEM WITH HAH WITH JEEM': False,
    'ARABIC LIGATURE MEEM WITH HAH WITH MEEM': False,
    'ARABIC LIGATURE MEEM WITH HAH WITH YEH': False,
    'ARABIC LIGATURE MEEM WITH JEEM': False,
    'ARABIC LIGATURE MEEM WITH JEEM WITH HAH': False,
    'ARABIC LIGATURE MEEM WITH JEEM WITH KHAH': False,
    'ARABIC LIGATURE MEEM WITH JEEM WITH MEEM': False,
    'ARABIC LIGATURE MEEM WITH JEEM WITH YEH': False,
    'ARABIC LIGATURE MEEM WITH KHAH': False,
    'ARABIC LIGATURE MEEM WITH KHAH WITH JEEM': False,
    'ARABIC LIGATURE MEEM WITH KHAH WITH MEEM': False,
    'ARABIC LIGATURE MEEM WITH KHAH WITH YEH': False,
    'ARABIC LIGATURE MEEM WITH MEEM': False,
    'ARABIC LIGATURE MEEM WITH MEEM WITH YEH': False,
    'ARABIC LIGATURE MEEM WITH YEH': False,
    'ARABIC LIGATURE NOON WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE NOON WITH HAH': False,
    'ARABIC LIGATURE NOON WITH HAH WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE NOON WITH HAH WITH MEEM': False,
    'ARABIC LIGATURE NOON WITH HAH WITH YEH': False,
    'ARABIC LIGATURE NOON WITH HEH': False,
    'ARABIC LIGATURE NOON WITH JEEM': False,
    'ARABIC LIGATURE NOON WITH JEEM WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE NOON WITH JEEM WITH HAH': False,
    'ARABIC LIGATURE NOON WITH JEEM WITH MEEM': False,
    'ARABIC LIGATURE NOON WITH JEEM WITH YEH': False,
    'ARABIC LIGATURE NOON WITH KHAH': False,
    'ARABIC LIGATURE NOON WITH MEEM': False,
    'ARABIC LIGATURE NOON WITH MEEM WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE NOON WITH MEEM WITH YEH': False,
    'ARABIC LIGATURE NOON WITH NOON': False,
    'ARABIC LIGATURE NOON WITH REH': False,
    'ARABIC LIGATURE NOON WITH YEH': False,
    'ARABIC LIGATURE NOON WITH ZAIN': False,
    'ARABIC LIGATURE QAF WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE QAF WITH HAH': False,
    'ARABIC LIGATURE QAF WITH MEEM': False,
    'ARABIC LIGATURE QAF WITH MEEM WITH HAH': False,
    'ARABIC LIGATURE QAF WITH MEEM WITH MEEM': False,
    'ARABIC LIGATURE QAF WITH MEEM WITH YEH': False,
    'ARABIC LIGATURE QAF WITH YEH': False,
    'ARABIC LIGATURE QALA USED AS KORANIC STOP SIGN': False,
    'ARABIC LIGATURE REH WITH SUPERSCRIPT ALEF': False,
    'ARABIC LIGATURE SAD WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE SAD WITH HAH': False,
    'ARABIC LIGATURE SAD WITH HAH WITH HAH': False,
    'ARABIC LIGATURE SAD WITH HAH WITH YEH': False,
    'ARABIC LIGATURE SAD WITH KHAH': False,
    'ARABIC LIGATURE SAD WITH MEEM': False,
    'ARABIC LIGATURE SAD WITH MEEM WITH MEEM': False,
    'ARABIC LIGATURE SAD WITH REH': False,
    'ARABIC LIGATURE SAD WITH YEH': False,
    'ARABIC LIGATURE SALLA USED AS KORANIC STOP SIGN': False,
    'ARABIC LIGATURE SEEN WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE SEEN WITH HAH': False,
    'ARABIC LIGATURE SEEN WITH HAH WITH JEEM': False,
    'ARABIC LIGATURE SEEN WITH HEH': False,
    'ARABIC LIGATURE SEEN WITH JEEM': False,
    'ARABIC LIGATURE SEEN WITH JEEM WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE SEEN WITH JEEM WITH HAH': False,
    'ARABIC LIGATURE SEEN WITH KHAH': False,
    'ARABIC LIGATURE SEEN WITH KHAH WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE SEEN WITH KHAH WITH YEH': False,
    'ARABIC LIGATURE SEEN WITH MEEM': False,
    'ARABIC LIGATURE SEEN WITH MEEM WITH HAH': False,
    'ARABIC LIGATURE SEEN WITH MEEM WITH JEEM': False,
    'ARABIC LIGATURE SEEN WITH MEEM WITH MEEM': False,
    'ARABIC LIGATURE SEEN WITH REH': False,
    'ARABIC LIGATURE SEEN WITH YEH': False,
    'ARABIC LIGATURE SHADDA WITH DAMMA': False,
    'ARABIC LIGATURE SHADDA WITH DAMMA ISOLATED FORM': False,
    'ARABIC LIGATURE SHADDA WITH DAMMA MEDIAL FORM': False,
    'ARABIC LIGATURE SHADDA WITH DAMMATAN ISOLATED FORM': False,
    'ARABIC LIGATURE SHADDA WITH FATHA': False,
    'ARABIC LIGATURE SHADDA WITH FATHA ISOLATED FORM': False,
    'ARABIC LIGATURE SHADDA WITH FATHA MEDIAL FORM': False,
    'ARABIC LIGATURE SHADDA WITH KASRA': False,
    'ARABIC LIGATURE SHADDA WITH KASRA ISOLATED FORM': False,
    'ARABIC LIGATURE SHADDA WITH KASRA MEDIAL FORM': False,
    'ARABIC LIGATURE SHADDA WITH KASRATAN ISOLATED FORM': False,
    'ARABIC LIGATURE SHADDA WITH SUPERSCRIPT ALEF': False,
    'ARABIC LIGATURE SHADDA WITH SUPERSCRIPT ALEF ISOLATED FORM': False,
    'ARABIC LIGATURE SHEEN WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE SHEEN WITH HAH': False,
    'ARABIC LIGATURE SHEEN WITH HAH WITH MEEM': False,
    'ARABIC LIGATURE SHEEN WITH HAH WITH YEH': False,
    'ARABIC LIGATURE SHEEN WITH HEH': False,
    'ARABIC LIGATURE SHEEN WITH JEEM': False,
    'ARABIC LIGATURE SHEEN WITH JEEM WITH YEH': False,
    'ARABIC LIGATURE SHEEN WITH KHAH': False,
    'ARABIC LIGATURE SHEEN WITH MEEM': False,
    'ARABIC LIGATURE SHEEN WITH MEEM WITH KHAH': False,
    'ARABIC LIGATURE SHEEN WITH MEEM WITH MEEM': False,
    'ARABIC LIGATURE SHEEN WITH REH': False,
    'ARABIC LIGATURE SHEEN WITH YEH': False,
    'ARABIC LIGATURE TAH WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE TAH WITH HAH': False,
    'ARABIC LIGATURE TAH WITH MEEM': False,
    'ARABIC LIGATURE TAH WITH MEEM WITH HAH': False,
    'ARABIC LIGATURE TAH WITH MEEM WITH MEEM': False,
    'ARABIC LIGATURE TAH WITH MEEM WITH YEH': False,
    'ARABIC LIGATURE TAH WITH YEH': False,
    'ARABIC LIGATURE TEH WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE TEH WITH HAH': False,
    'ARABIC LIGATURE TEH WITH HAH WITH JEEM': False,
    'ARABIC LIGATURE TEH WITH HAH WITH MEEM': False,
    'ARABIC LIGATURE TEH WITH HEH': False,
    'ARABIC LIGATURE TEH WITH JEEM': False,
    'ARABIC LIGATURE TEH WITH JEEM WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE TEH WITH JEEM WITH MEEM': False,
    'ARABIC LIGATURE TEH WITH JEEM WITH YEH': False,
    'ARABIC LIGATURE TEH WITH KHAH': False,
    'ARABIC LIGATURE TEH WITH KHAH WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE TEH WITH KHAH WITH MEEM': False,
    'ARABIC LIGATURE TEH WITH KHAH WITH YEH': False,
    'ARABIC LIGATURE TEH WITH MEEM': False,
    'ARABIC LIGATURE TEH WITH MEEM WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE TEH WITH MEEM WITH HAH': False,
    'ARABIC LIGATURE TEH WITH MEEM WITH JEEM': False,
    'ARABIC LIGATURE TEH WITH MEEM WITH KHAH': False,
    'ARABIC LIGATURE TEH WITH MEEM WITH YEH': False,
    'ARABIC LIGATURE TEH WITH NOON': False,
    'ARABIC LIGATURE TEH WITH REH': False,
    'ARABIC LIGATURE TEH WITH YEH': False,
    'ARABIC LIGATURE TEH WITH ZAIN': False,
    'ARABIC LIGATURE THAL WITH SUPERSCRIPT ALEF': False,
    'ARABIC LIGATURE THEH WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE THEH WITH HEH': False,
    'ARABIC LIGATURE THEH WITH JEEM': False,
    'ARABIC LIGATURE THEH WITH MEEM': False,
    'ARABIC LIGATURE THEH WITH NOON': False,
    'ARABIC LIGATURE THEH WITH REH': False,
    'ARABIC LIGATURE THEH WITH YEH': False,
    'ARABIC LIGATURE THEH WITH ZAIN': False,
    'ARABIC LIGATURE UIGHUR KIRGHIZ YEH WITH HAMZA ABOVE WITH ALEF MAKSURA': False,  # noqa
    'ARABIC LIGATURE YEH WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE YEH WITH HAH': False,
    'ARABIC LIGATURE YEH WITH HAH WITH YEH': False,
    'ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH AE': False,
    'ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH ALEF': False,
    'ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH ALEF MAKSURA': False,
    'ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH E': False,
    'ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH HAH': False,
    'ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH HEH': False,
    'ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH JEEM': False,
    'ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH KHAH': False,
    'ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH MEEM': False,
    'ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH NOON': False,
    'ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH OE': False,
    'ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH REH': False,
    'ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH U': False,
    'ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH WAW': False,
    'ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH YEH': False,
    'ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH YU': False,
    'ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH ZAIN': False,
    'ARABIC LIGATURE YEH WITH HEH': False,
    'ARABIC LIGATURE YEH WITH JEEM': False,
    'ARABIC LIGATURE YEH WITH JEEM WITH YEH': False,
    'ARABIC LIGATURE YEH WITH KHAH': False,
    'ARABIC LIGATURE YEH WITH MEEM': False,
    'ARABIC LIGATURE YEH WITH MEEM WITH MEEM': False,
    'ARABIC LIGATURE YEH WITH MEEM WITH YEH': False,
    'ARABIC LIGATURE YEH WITH NOON': False,
    'ARABIC LIGATURE YEH WITH REH': False,
    'ARABIC LIGATURE YEH WITH YEH': False,
    'ARABIC LIGATURE YEH WITH ZAIN': False,
    'ARABIC LIGATURE ZAH WITH MEEM': False,
    # -------------------- End: Ligatures Configurations ------------------- #
}


def auto_config(configuration=None, configuration_file=None):
    loaded_from_envvar = False

    configuration_parser = ConfigParser()
    configuration_parser.read_dict({
        'ArabicReshaper': default_config
    })

    if not configuration_file:
        configuration_file = os.getenv(
            'PYTHON_ARABIC_RESHAPER_CONFIGURATION_FILE'
        )
        if configuration_file:
            loaded_from_envvar = True

    if configuration_file:
        if not os.path.exists(configuration_file):
            raise Exception(
                'Configuration file {} not found{}.'.format(
                    configuration_file,
                    loaded_from_envvar and (
                        ' it is set in your environment variable ' +
                        'PYTHON_ARABIC_RESHAPER_CONFIGURATION_FILE'
                    ) or ''
                )
            )
        configuration_parser.read((configuration_file,))

    if configuration:
        configuration_parser.read_dict({
            'ArabicReshaper': configuration
        })

    if 'ArabicReshaper' not in configuration_parser:
        raise ValueError(
            'Invalid configuration: '
            'A section with the name ArabicReshaper was not found'
        )

    return configuration_parser['ArabicReshaper']


def config_for_true_type_font(font_file_path,
                              ligatures_config=ENABLE_ALL_LIGATURES):
    if not with_font_config:
        raise Exception('fonttools not installed, ' +
                        'install it then rerun this.\n' +
                        '$ pip install arabic-teshaper[with-fonttools]')
    if not font_file_path or not os.path.exists(font_file_path):
        raise Exception('Invalid path to font file')
    ttfont = TTFont(font_file_path)
    has_isolated = True
    for k, v in LETTERS_ARABIC.items():
        for table in ttfont['cmap'].tables:
            if ord(v[ISOLATED]) in table.cmap:
                break
        else:
            has_isolated = False
            break

    configuration = {
        'use_unshaped_instead_of_isolated': not has_isolated,
    }

    def process_ligatures(ligatures):
        for ligature in ligatures:
            forms = list(filter(lambda form: form != '', ligature[1][1]))
            n = len(forms)
            for form in forms:
                for table in ttfont['cmap'].tables:
                    if ord(form) in table.cmap:
                        n -= 1
                        break
            configuration[ligature[0]] = (n == 0)

    if ENABLE_SENTENCES_LIGATURES & ligatures_config:
        process_ligatures(SENTENCES_LIGATURES)

    if ENABLE_WORDS_LIGATURES & ligatures_config:
        process_ligatures(WORDS_LIGATURES)

    if ENABLE_LETTERS_LIGATURES & ligatures_config:
        process_ligatures(LETTERS_LIGATURES)

    return configuration

# -*- coding: utf-8 -*-

# This work is licensed under the MIT License.
# To view a copy of this license, visit https://opensource.org/licenses/MIT

# Written by Abdullah Diab (mpcabd)
# Email: mpcabd@gmail.com
# Website: http://mpcabd.xyz

import re

from itertools import repeat

# from .ligatures import LIGATURES
# from .reshaper_config import auto_config
# from .letters import (UNSHAPED, ISOLATED, TATWEEL, ZWJ, LETTERS_ARABIC,
#                       LETTERS_ARABIC_V2, LETTERS_KURDISH, FINAL,
#                       INITIAL, MEDIAL, connects_with_letters_before_and_after,
#                       connects_with_letter_before, connects_with_letter_after)

HARAKAT_RE = re.compile(
    '['
    '\u0610-\u061a'
    '\u064b-\u065f'
    '\u0670'
    '\u06d6-\u06dc'
    '\u06df-\u06e8'
    '\u06ea-\u06ed'
    '\u08d4-\u08e1'
    '\u08d4-\u08ed'
    '\u08e3-\u08ff'
    ']',

    re.UNICODE | re.X
)


class ArabicReshaper(object):
    """
    A class for Arabic reshaper, it allows for fine-tune configuration over the
    API.

    If no configuration is passed to the constructor, the class will check for
    an environment variable :envvar:`PYTHON_ARABIC_RESHAPER_CONFIGURATION_FILE`
    , if the variable is available, the class will load the file pointed to by
    the variable, and will read it as an ini file.
    If the variable doesn't exist, the class will load with the default
    configuration file :file:`default-config.ini`

    Check these links for information on the configuration files format:

    * Python 3: https://docs.python.org/3/library/configparser.html

    See the default configuration file :file:`default-config.ini` for details
    on how to configure your reshaper.
    """

    def __init__(self, configuration=None, configuration_file=None):
        super(ArabicReshaper, self).__init__()

        self.configuration = auto_config(configuration, configuration_file)
        self.language = self.configuration.get('language')

        if self.language == 'ArabicV2':
            self.letters = LETTERS_ARABIC_V2
        elif self.language == 'Kurdish':
            self.letters = LETTERS_KURDISH
        else:
            self.letters = LETTERS_ARABIC

    @property
    def _ligatures_re(self):
        if not hasattr(self, '__ligatures_re'):
            patterns = []
            re_group_index_to_ligature_forms = {}
            index = 0
            FORMS = 1
            MATCH = 0
            for ligature_record in LIGATURES:
                ligature, replacement = ligature_record
                if not self.configuration.getboolean(ligature):
                    continue
                re_group_index_to_ligature_forms[index] = replacement[FORMS]
                patterns.append('({})'.format(replacement[MATCH]))
                index += 1
            self._re_group_index_to_ligature_forms = (
                re_group_index_to_ligature_forms
            )
            self.__ligatures_re = re.compile('|'.join(patterns), re.UNICODE)
        return self.__ligatures_re

    def _get_ligature_forms_from_re_group_index(self, group_index):
        if not hasattr(self, '_re_group_index_to_ligature_forms'):
            return self._ligatures_re
        return self._re_group_index_to_ligature_forms[group_index]

    def reshape(self, text):
        if not text:
            return ''

        output = []

        LETTER = 0
        FORM = 1
        NOT_SUPPORTED = -1

        delete_harakat = self.configuration.getboolean('delete_harakat')
        delete_tatweel = self.configuration.getboolean('delete_tatweel')
        support_zwj = self.configuration.getboolean('support_zwj')
        shift_harakat_position = self.configuration.getboolean(
            'shift_harakat_position'
        )
        use_unshaped_instead_of_isolated = self.configuration.getboolean(
            'use_unshaped_instead_of_isolated'
        )

        positions_harakat = {}

        isolated_form = (UNSHAPED
                         if use_unshaped_instead_of_isolated else ISOLATED)

        for letter in text:
            if HARAKAT_RE.match(letter):
                if not delete_harakat:
                    position = len(output) - 1
                    if shift_harakat_position:
                        position -= 1
                    if position not in positions_harakat:
                        positions_harakat[position] = []
                    if shift_harakat_position:
                        positions_harakat[position].insert(0, letter)
                    else:
                        positions_harakat[position].append(letter)
            elif letter == TATWEEL and delete_tatweel:
                pass
            elif letter == ZWJ and not support_zwj:
                pass
            elif letter not in self.letters:
                output.append((letter, NOT_SUPPORTED))
            elif not output:  # first letter
                output.append((letter, isolated_form))
            else:
                previous_letter = output[-1]
                if previous_letter[FORM] == NOT_SUPPORTED:
                    output.append((letter, isolated_form))
                elif not connects_with_letter_before(letter, self.letters):
                    output.append((letter, isolated_form))
                elif not connects_with_letter_after(
                        previous_letter[LETTER], self.letters):
                    output.append((letter, isolated_form))
                elif (previous_letter[FORM] == FINAL and not
                      connects_with_letters_before_and_after(
                          previous_letter[LETTER], self.letters
                )):
                    output.append((letter, isolated_form))
                elif previous_letter[FORM] == isolated_form:
                    output[-1] = (
                        previous_letter[LETTER],
                        INITIAL
                    )
                    output.append((letter, FINAL))
                # Otherwise, we will change the previous letter to connect
                # to the current letter
                else:
                    output[-1] = (
                        previous_letter[LETTER],
                        MEDIAL
                    )
                    output.append((letter, FINAL))

            # Remove ZWJ if it's the second to last item as it won't be useful
            if support_zwj and len(output) > 1 and output[-2][LETTER] == ZWJ:
                output.pop(len(output) - 2)

        if support_zwj and output and output[-1][LETTER] == ZWJ:
            output.pop()

        if self.configuration.getboolean('support_ligatures'):
            # Clean text from Harakat to be able to find ligatures
            text = HARAKAT_RE.sub('', text)

            # Clean text from Tatweel to find ligatures if delete_tatweel
            if delete_tatweel:
                text = text.replace(TATWEEL, '')

            for match in re.finditer(self._ligatures_re, text):
                group_index = next((
                    i for i, group in enumerate(match.groups()) if group
                ), -1)
                forms = self._get_ligature_forms_from_re_group_index(
                    group_index
                )
                a, b = match.span()
                a_form = output[a][FORM]
                b_form = output[b - 1][FORM]
                ligature_form = None

                # +-----------+----------+---------+---------+----------+
                # | a   \   b | ISOLATED | INITIAL | MEDIAL  | FINAL    |
                # +-----------+----------+---------+---------+----------+
                # | ISOLATED  | ISOLATED | INITIAL | INITIAL | ISOLATED |
                # | INITIAL   | ISOLATED | INITIAL | INITIAL | ISOLATED |
                # | MEDIAL    | FINAL    | MEDIAL  | MEDIAL  | FINAL    |
                # | FINAL     | FINAL    | MEDIAL  | MEDIAL  | FINAL    |
                # +-----------+----------+---------+---------+----------+

                if a_form in (isolated_form, INITIAL):
                    if b_form in (isolated_form, FINAL):
                        ligature_form = ISOLATED
                    else:
                        ligature_form = INITIAL
                else:
                    if b_form in (isolated_form, FINAL):
                        ligature_form = FINAL
                    else:
                        ligature_form = MEDIAL
                if not forms[ligature_form]:
                    continue
                output[a] = (forms[ligature_form], NOT_SUPPORTED)
                output[a+1:b] = repeat(('', NOT_SUPPORTED), b - 1 - a)

        result = []
        if not delete_harakat and -1 in positions_harakat:
            result.extend(positions_harakat[-1])
        for i, o in enumerate(output):
            if o[LETTER]:
                if o[FORM] == NOT_SUPPORTED or o[FORM] == UNSHAPED:
                    result.append(o[LETTER])
                else:
                    result.append(self.letters[o[LETTER]][o[FORM]])

            if not delete_harakat:
                if i in positions_harakat:
                    result.extend(positions_harakat[i])

        return ''.join(result)


default_reshaper = ArabicReshaper()
reshape = default_reshaper.reshape



class Process:
    def process_before(self, text):
        # إعداد سياق المعالجة إذا لزم الأمر
        context = {}
        # تُرجع النص كما هو مع السياق
        return text, context

    def process_after(self, res, context):
        # إعادة تشكيل النص العربي ليظهر متصلاً بعد المعالجة
        reshaped_text = reshape(res)
        # عكس النص
        reversed_text = ''.join(reversed(reshaped_text))
        # يمكنك هنا إضافة تحويل النص إلى UTF-8 إذا لزم الأمر أو أية معالجات إضافية
        return reversed_text