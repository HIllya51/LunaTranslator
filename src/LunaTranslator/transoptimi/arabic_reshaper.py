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

TATWEEL = "\u0640"
ZWJ = "\u200d"
LETTERS_ARABIC = {
    # ARABIC LETTER HAMZA
    "\u0621": ("\ufe80", "", "", ""),
    # ARABIC LETTER ALEF WITH MADDA ABOVE
    "\u0622": ("\ufe81", "", "", "\ufe82"),
    # ARABIC LETTER ALEF WITH HAMZA ABOVE
    "\u0623": ("\ufe83", "", "", "\ufe84"),
    # ARABIC LETTER WAW WITH HAMZA ABOVE
    "\u0624": ("\ufe85", "", "", "\ufe86"),
    # ARABIC LETTER ALEF WITH HAMZA BELOW
    "\u0625": ("\ufe87", "", "", "\ufe88"),
    # ARABIC LETTER YEH WITH HAMZA ABOVE
    "\u0626": ("\ufe89", "\ufe8b", "\ufe8c", "\ufe8a"),
    # ARABIC LETTER ALEF
    "\u0627": ("\ufe8d", "", "", "\ufe8e"),
    # ARABIC LETTER BEH
    "\u0628": ("\ufe8f", "\ufe91", "\ufe92", "\ufe90"),
    # ARABIC LETTER TEH MARBUTA
    "\u0629": ("\ufe93", "", "", "\ufe94"),
    # ARABIC LETTER TEH
    "\u062a": ("\ufe95", "\ufe97", "\ufe98", "\ufe96"),
    # ARABIC LETTER THEH
    "\u062b": ("\ufe99", "\ufe9b", "\ufe9c", "\ufe9a"),
    # ARABIC LETTER JEEM
    "\u062c": ("\ufe9d", "\ufe9f", "\ufea0", "\ufe9e"),
    # ARABIC LETTER HAH
    "\u062d": ("\ufea1", "\ufea3", "\ufea4", "\ufea2"),
    # ARABIC LETTER KHAH
    "\u062e": ("\ufea5", "\ufea7", "\ufea8", "\ufea6"),
    # ARABIC LETTER DAL
    "\u062f": ("\ufea9", "", "", "\ufeaa"),
    # ARABIC LETTER THAL
    "\u0630": ("\ufeab", "", "", "\ufeac"),
    # ARABIC LETTER REH
    "\u0631": ("\ufead", "", "", "\ufeae"),
    # ARABIC LETTER ZAIN
    "\u0632": ("\ufeaf", "", "", "\ufeb0"),
    # ARABIC LETTER SEEN
    "\u0633": ("\ufeb1", "\ufeb3", "\ufeb4", "\ufeb2"),
    # ARABIC LETTER SHEEN
    "\u0634": ("\ufeb5", "\ufeb7", "\ufeb8", "\ufeb6"),
    # ARABIC LETTER SAD
    "\u0635": ("\ufeb9", "\ufebb", "\ufebc", "\ufeba"),
    # ARABIC LETTER DAD
    "\u0636": ("\ufebd", "\ufebf", "\ufec0", "\ufebe"),
    # ARABIC LETTER TAH
    "\u0637": ("\ufec1", "\ufec3", "\ufec4", "\ufec2"),
    # ARABIC LETTER ZAH
    "\u0638": ("\ufec5", "\ufec7", "\ufec8", "\ufec6"),
    # ARABIC LETTER AIN
    "\u0639": ("\ufec9", "\ufecb", "\ufecc", "\ufeca"),
    # ARABIC LETTER GHAIN
    "\u063a": ("\ufecd", "\ufecf", "\ufed0", "\ufece"),
    # ARABIC TATWEEL
    TATWEEL: (TATWEEL, TATWEEL, TATWEEL, TATWEEL),
    # ARABIC LETTER FEH
    "\u0641": ("\ufed1", "\ufed3", "\ufed4", "\ufed2"),
    # ARABIC LETTER QAF
    "\u0642": ("\ufed5", "\ufed7", "\ufed8", "\ufed6"),
    # ARABIC LETTER KAF
    "\u0643": ("\ufed9", "\ufedb", "\ufedc", "\ufeda"),
    # ARABIC LETTER LAM
    "\u0644": ("\ufedd", "\ufedf", "\ufee0", "\ufede"),
    # ARABIC LETTER MEEM
    "\u0645": ("\ufee1", "\ufee3", "\ufee4", "\ufee2"),
    # ARABIC LETTER NOON
    "\u0646": ("\ufee5", "\ufee7", "\ufee8", "\ufee6"),
    # ARABIC LETTER HEH
    "\u0647": ("\ufee9", "\ufeeb", "\ufeec", "\ufeea"),
    # ARABIC LETTER WAW
    "\u0648": ("\ufeed", "", "", "\ufeee"),
    # ARABIC LETTER (UIGHUR KAZAKH KIRGHIZ)? ALEF MAKSURA
    "\u0649": ("\ufeef", "\ufbe8", "\ufbe9", "\ufef0"),
    # ARABIC LETTER YEH
    "\u064a": ("\ufef1", "\ufef3", "\ufef4", "\ufef2"),
    # ARABIC LETTER ALEF WASLA
    "\u0671": ("\ufb50", "", "", "\ufb51"),
    # ARABIC LETTER U WITH HAMZA ABOVE
    "\u0677": ("\ufbdd", "", "", ""),
    # ARABIC LETTER TTEH
    "\u0679": ("\ufb66", "\ufb68", "\ufb69", "\ufb67"),
    # ARABIC LETTER TTEHEH
    "\u067a": ("\ufb5e", "\ufb60", "\ufb61", "\ufb5f"),
    # ARABIC LETTER BEEH
    "\u067b": ("\ufb52", "\ufb54", "\ufb55", "\ufb53"),
    # ARABIC LETTER PEH
    "\u067e": ("\ufb56", "\ufb58", "\ufb59", "\ufb57"),
    # ARABIC LETTER TEHEH
    "\u067f": ("\ufb62", "\ufb64", "\ufb65", "\ufb63"),
    # ARABIC LETTER BEHEH
    "\u0680": ("\ufb5a", "\ufb5c", "\ufb5d", "\ufb5b"),
    # ARABIC LETTER NYEH
    "\u0683": ("\ufb76", "\ufb78", "\ufb79", "\ufb77"),
    # ARABIC LETTER DYEH
    "\u0684": ("\ufb72", "\ufb74", "\ufb75", "\ufb73"),
    # ARABIC LETTER TCHEH
    "\u0686": ("\ufb7a", "\ufb7c", "\ufb7d", "\ufb7b"),
    # ARABIC LETTER TCHEHEH
    "\u0687": ("\ufb7e", "\ufb80", "\ufb81", "\ufb7f"),
    # ARABIC LETTER DDAL
    "\u0688": ("\ufb88", "", "", "\ufb89"),
    # ARABIC LETTER DAHAL
    "\u068c": ("\ufb84", "", "", "\ufb85"),
    # ARABIC LETTER DDAHAL
    "\u068d": ("\ufb82", "", "", "\ufb83"),
    # ARABIC LETTER DUL
    "\u068e": ("\ufb86", "", "", "\ufb87"),
    # ARABIC LETTER RREH
    "\u0691": ("\ufb8c", "", "", "\ufb8d"),
    # ARABIC LETTER JEH
    "\u0698": ("\ufb8a", "", "", "\ufb8b"),
    # ARABIC LETTER VEH
    "\u06a4": ("\ufb6a", "\ufb6c", "\ufb6d", "\ufb6b"),
    # ARABIC LETTER PEHEH
    "\u06a6": ("\ufb6e", "\ufb70", "\ufb71", "\ufb6f"),
    # ARABIC LETTER KEHEH
    "\u06a9": ("\ufb8e", "\ufb90", "\ufb91", "\ufb8f"),
    # ARABIC LETTER NG
    "\u06ad": ("\ufbd3", "\ufbd5", "\ufbd6", "\ufbd4"),
    # ARABIC LETTER GAF
    "\u06af": ("\ufb92", "\ufb94", "\ufb95", "\ufb93"),
    # ARABIC LETTER NGOEH
    "\u06b1": ("\ufb9a", "\ufb9c", "\ufb9d", "\ufb9b"),
    # ARABIC LETTER GUEH
    "\u06b3": ("\ufb96", "\ufb98", "\ufb99", "\ufb97"),
    # ARABIC LETTER NOON GHUNNA
    "\u06ba": ("\ufb9e", "", "", "\ufb9f"),
    # ARABIC LETTER RNOON
    "\u06bb": ("\ufba0", "\ufba2", "\ufba3", "\ufba1"),
    # ARABIC LETTER HEH DOACHASHMEE
    "\u06be": ("\ufbaa", "\ufbac", "\ufbad", "\ufbab"),
    # ARABIC LETTER HEH WITH YEH ABOVE
    "\u06c0": ("\ufba4", "", "", "\ufba5"),
    # ARABIC LETTER HEH GOAL
    "\u06c1": ("\ufba6", "\ufba8", "\ufba9", "\ufba7"),
    # ARABIC LETTER KIRGHIZ OE
    "\u06c5": ("\ufbe0", "", "", "\ufbe1"),
    # ARABIC LETTER OE
    "\u06c6": ("\ufbd9", "", "", "\ufbda"),
    # ARABIC LETTER U
    "\u06c7": ("\ufbd7", "", "", "\ufbd8"),
    # ARABIC LETTER YU
    "\u06c8": ("\ufbdb", "", "", "\ufbdc"),
    # ARABIC LETTER KIRGHIZ YU
    "\u06c9": ("\ufbe2", "", "", "\ufbe3"),
    # ARABIC LETTER VE
    "\u06cb": ("\ufbde", "", "", "\ufbdf"),
    # ARABIC LETTER FARSI YEH
    "\u06cc": ("\ufbfc", "\ufbfe", "\ufbff", "\ufbfd"),
    # ARABIC LETTER E
    "\u06d0": ("\ufbe4", "\ufbe6", "\ufbe7", "\ufbe5"),
    # ARABIC LETTER YEH BARREE
    "\u06d2": ("\ufbae", "", "", "\ufbaf"),
    # ARABIC LETTER YEH BARREE WITH HAMZA ABOVE
    "\u06d3": ("\ufbb0", "", "", "\ufbb1"),
    # ZWJ
    ZWJ: (ZWJ, ZWJ, ZWJ, ZWJ),
}

LETTERS_ARABIC_V2 = {
    # ARABIC LETTER HAMZA
    "\u0621": ("\ufe80", "", "", ""),
    # ARABIC LETTER ALEF WITH MADDA ABOVE
    "\u0622": ("\u0622", "", "", "\ufe82"),
    # ARABIC LETTER ALEF WITH HAMZA ABOVE
    "\u0623": ("\u0623", "", "", "\ufe84"),
    # ARABIC LETTER WAW WITH HAMZA ABOVE
    "\u0624": ("\u0624", "", "", "\ufe86"),
    # ARABIC LETTER ALEF WITH HAMZA BELOW
    "\u0625": ("\u0625", "", "", "\ufe88"),
    # ARABIC LETTER YEH WITH HAMZA ABOVE
    "\u0626": ("\u0626", "\ufe8b", "\ufe8c", "\ufe8a"),
    # ARABIC LETTER ALEF
    "\u0627": ("\u0627", "", "", "\ufe8e"),
    # ARABIC LETTER BEH
    "\u0628": ("\u0628", "\ufe91", "\ufe92", "\ufe90"),
    # ARABIC LETTER TEH MARBUTA
    "\u0629": ("\u0629", "", "", "\ufe94"),
    # ARABIC LETTER TEH
    "\u062a": ("\u062a", "\ufe97", "\ufe98", "\ufe96"),
    # ARABIC LETTER THEH
    "\u062b": ("\u062b", "\ufe9b", "\ufe9c", "\ufe9a"),
    # ARABIC LETTER JEEM
    "\u062c": ("\u062c", "\ufe9f", "\ufea0", "\ufe9e"),
    # ARABIC LETTER HAH
    "\u062d": ("\ufea1", "\ufea3", "\ufea4", "\ufea2"),
    # ARABIC LETTER KHAH
    "\u062e": ("\u062e", "\ufea7", "\ufea8", "\ufea6"),
    # ARABIC LETTER DAL
    "\u062f": ("\u062f", "", "", "\ufeaa"),
    # ARABIC LETTER THAL
    "\u0630": ("\u0630", "", "", "\ufeac"),
    # ARABIC LETTER REH
    "\u0631": ("\u0631", "", "", "\ufeae"),
    # ARABIC LETTER ZAIN
    "\u0632": ("\u0632", "", "", "\ufeb0"),
    # ARABIC LETTER SEEN
    "\u0633": ("\u0633", "\ufeb3", "\ufeb4", "\ufeb2"),
    # ARABIC LETTER SHEEN
    "\u0634": ("\u0634", "\ufeb7", "\ufeb8", "\ufeb6"),
    # ARABIC LETTER SAD
    "\u0635": ("\u0635", "\ufebb", "\ufebc", "\ufeba"),
    # ARABIC LETTER DAD
    "\u0636": ("\u0636", "\ufebf", "\ufec0", "\ufebe"),
    # ARABIC LETTER TAH
    "\u0637": ("\u0637", "\ufec3", "\ufec4", "\ufec2"),
    # ARABIC LETTER ZAH
    "\u0638": ("\u0638", "\ufec7", "\ufec8", "\ufec6"),
    # ARABIC LETTER AIN
    "\u0639": ("\u0639", "\ufecb", "\ufecc", "\ufeca"),
    # ARABIC LETTER GHAIN
    "\u063a": ("\u063a", "\ufecf", "\ufed0", "\ufece"),
    # ARABIC TATWEEL
    TATWEEL: (TATWEEL, TATWEEL, TATWEEL, TATWEEL),
    # ARABIC LETTER FEH
    "\u0641": ("\u0641", "\ufed3", "\ufed4", "\ufed2"),
    # ARABIC LETTER QAF
    "\u0642": ("\u0642", "\ufed7", "\ufed8", "\ufed6"),
    # ARABIC LETTER KAF
    "\u0643": ("\u0643", "\ufedb", "\ufedc", "\ufeda"),
    # ARABIC LETTER LAM
    "\u0644": ("\u0644", "\ufedf", "\ufee0", "\ufede"),
    # ARABIC LETTER MEEM
    "\u0645": ("\u0645", "\ufee3", "\ufee4", "\ufee2"),
    # ARABIC LETTER NOON
    "\u0646": ("\u0646", "\ufee7", "\ufee8", "\ufee6"),
    # ARABIC LETTER HEH
    "\u0647": ("\u0647", "\ufeeb", "\ufeec", "\ufeea"),
    # ARABIC LETTER WAW
    "\u0648": ("\u0648", "", "", "\ufeee"),
    # ARABIC LETTER (UIGHUR KAZAKH KIRGHIZ)? ALEF MAKSURA
    "\u0649": ("\u0649", "\ufbe8", "\ufbe9", "\ufef0"),
    # ARABIC LETTER YEH
    "\u064a": ("\u064a", "\ufef3", "\ufef4", "\ufef2"),
    # ARABIC LETTER ALEF WASLA
    "\u0671": ("\u0671", "", "", "\ufb51"),
    # ARABIC LETTER U WITH HAMZA ABOVE
    "\u0677": ("\u0677", "", "", ""),
    # ARABIC LETTER TTEH
    "\u0679": ("\u0679", "\ufb68", "\ufb69", "\ufb67"),
    # ARABIC LETTER TTEHEH
    "\u067a": ("\u067a", "\ufb60", "\ufb61", "\ufb5f"),
    # ARABIC LETTER BEEH
    "\u067b": ("\u067b", "\ufb54", "\ufb55", "\ufb53"),
    # ARABIC LETTER PEH
    "\u067e": ("\u067e", "\ufb58", "\ufb59", "\ufb57"),
    # ARABIC LETTER TEHEH
    "\u067f": ("\u067f", "\ufb64", "\ufb65", "\ufb63"),
    # ARABIC LETTER BEHEH
    "\u0680": ("\u0680", "\ufb5c", "\ufb5d", "\ufb5b"),
    # ARABIC LETTER NYEH
    "\u0683": ("\u0683", "\ufb78", "\ufb79", "\ufb77"),
    # ARABIC LETTER DYEH
    "\u0684": ("\u0684", "\ufb74", "\ufb75", "\ufb73"),
    # ARABIC LETTER TCHEH
    "\u0686": ("\u0686", "\ufb7c", "\ufb7d", "\ufb7b"),
    # ARABIC LETTER TCHEHEH
    "\u0687": ("\u0687", "\ufb80", "\ufb81", "\ufb7f"),
    # ARABIC LETTER DDAL
    "\u0688": ("\u0688", "", "", "\ufb89"),
    # ARABIC LETTER DAHAL
    "\u068c": ("\u068c", "", "", "\ufb85"),
    # ARABIC LETTER DDAHAL
    "\u068d": ("\u068d", "", "", "\ufb83"),
    # ARABIC LETTER DUL
    "\u068e": ("\u068e", "", "", "\ufb87"),
    # ARABIC LETTER RREH
    "\u0691": ("\u0691", "", "", "\ufb8d"),
    # ARABIC LETTER JEH
    "\u0698": ("\u0698", "", "", "\ufb8b"),
    # ARABIC LETTER VEH
    "\u06a4": ("\u06a4", "\ufb6c", "\ufb6d", "\ufb6b"),
    # ARABIC LETTER PEHEH
    "\u06a6": ("\u06a6", "\ufb70", "\ufb71", "\ufb6f"),
    # ARABIC LETTER KEHEH
    "\u06a9": ("\u06a9", "\ufb90", "\ufb91", "\ufb8f"),
    # ARABIC LETTER NG
    "\u06ad": ("\u06ad", "\ufbd5", "\ufbd6", "\ufbd4"),
    # ARABIC LETTER GAF
    "\u06af": ("\u06af", "\ufb94", "\ufb95", "\ufb93"),
    # ARABIC LETTER NGOEH
    "\u06b1": ("\u06b1", "\ufb9c", "\ufb9d", "\ufb9b"),
    # ARABIC LETTER GUEH
    "\u06b3": ("\u06b3", "\ufb98", "\ufb99", "\ufb97"),
    # ARABIC LETTER NOON GHUNNA
    "\u06ba": ("\u06ba", "", "", "\ufb9f"),
    # ARABIC LETTER RNOON
    "\u06bb": ("\u06bb", "\ufba2", "\ufba3", "\ufba1"),
    # ARABIC LETTER HEH DOACHASHMEE
    "\u06be": ("\u06be", "\ufbac", "\ufbad", "\ufbab"),
    # ARABIC LETTER HEH WITH YEH ABOVE
    "\u06c0": ("\u06c0", "", "", "\ufba5"),
    # ARABIC LETTER HEH GOAL
    "\u06c1": ("\u06c1", "\ufba8", "\ufba9", "\ufba7"),
    # ARABIC LETTER KIRGHIZ OE
    "\u06c5": ("\u06c5", "", "", "\ufbe1"),
    # ARABIC LETTER OE
    "\u06c6": ("\u06c6", "", "", "\ufbda"),
    # ARABIC LETTER U
    "\u06c7": ("\u06c7", "", "", "\ufbd8"),
    # ARABIC LETTER YU
    "\u06c8": ("\u06c8", "", "", "\ufbdc"),
    # ARABIC LETTER KIRGHIZ YU
    "\u06c9": ("\u06c9", "", "", "\ufbe3"),
    # ARABIC LETTER VE
    "\u06cb": ("\u06cb", "", "", "\ufbdf"),
    # ARABIC LETTER FARSI YEH
    "\u06cc": ("\u06cc", "\ufbfe", "\ufbff", "\ufbfd"),
    # ARABIC LETTER E
    "\u06d0": ("\u06d0", "\ufbe6", "\ufbe7", "\ufbe5"),
    # ARABIC LETTER YEH BARREE
    "\u06d2": ("\u06d2", "", "", "\ufbaf"),
    # ARABIC LETTER YEH BARREE WITH HAMZA ABOVE
    "\u06d3": ("\u06d3", "", "", "\ufbb1"),
    # Kurdish letter YEAH
    "\u06ce": ("\ue004", "\ue005", "\ue006", "\ue004"),
    # Kurdish letter Hamza same as arabic Teh without the point
    "\u06d5": ("\u06d5", "", "", "\ue000"),
    # ZWJ
    ZWJ: (ZWJ, ZWJ, ZWJ, ZWJ),
}
LETTERS_KURDISH = {
    # ARABIC LETTER HAMZA
    "\u0621": ("\ufe80", "", "", ""),
    # ARABIC LETTER ALEF WITH MADDA ABOVE
    "\u0622": ("\u0622", "", "", "\ufe82"),
    # ARABIC LETTER ALEF WITH HAMZA ABOVE
    "\u0623": ("\u0623", "", "", "\ufe84"),
    # ARABIC LETTER WAW WITH HAMZA ABOVE
    "\u0624": ("\u0624", "", "", "\ufe86"),
    # ARABIC LETTER ALEF WITH HAMZA BELOW
    "\u0625": ("\u0625", "", "", "\ufe88"),
    # ARABIC LETTER YEH WITH HAMZA ABOVE
    "\u0626": ("\u0626", "\ufe8b", "\ufe8c", "\ufe8a"),
    # ARABIC LETTER ALEF
    "\u0627": ("\u0627", "", "", "\ufe8e"),
    # ARABIC LETTER BEH
    "\u0628": ("\u0628", "\ufe91", "\ufe92", "\ufe90"),
    # ARABIC LETTER TEH MARBUTA
    "\u0629": ("\u0629", "", "", "\ufe94"),
    # ARABIC LETTER TEH
    "\u062a": ("\u062a", "\ufe97", "\ufe98", "\ufe96"),
    # ARABIC LETTER THEH
    "\u062b": ("\u062b", "\ufe9b", "\ufe9c", "\ufe9a"),
    # ARABIC LETTER JEEM
    "\u062c": ("\u062c", "\ufe9f", "\ufea0", "\ufe9e"),
    # ARABIC LETTER HAH
    "\u062d": ("\ufea1", "\ufea3", "\ufea4", "\ufea2"),
    # ARABIC LETTER KHAH
    "\u062e": ("\u062e", "\ufea7", "\ufea8", "\ufea6"),
    # ARABIC LETTER DAL
    "\u062f": ("\u062f", "", "", "\ufeaa"),
    # ARABIC LETTER THAL
    "\u0630": ("\u0630", "", "", "\ufeac"),
    # ARABIC LETTER REH
    "\u0631": ("\u0631", "", "", "\ufeae"),
    # ARABIC LETTER ZAIN
    "\u0632": ("\u0632", "", "", "\ufeb0"),
    # ARABIC LETTER SEEN
    "\u0633": ("\u0633", "\ufeb3", "\ufeb4", "\ufeb2"),
    # ARABIC LETTER SHEEN
    "\u0634": ("\u0634", "\ufeb7", "\ufeb8", "\ufeb6"),
    # ARABIC LETTER SAD
    "\u0635": ("\u0635", "\ufebb", "\ufebc", "\ufeba"),
    # ARABIC LETTER DAD
    "\u0636": ("\u0636", "\ufebf", "\ufec0", "\ufebe"),
    # ARABIC LETTER TAH
    "\u0637": ("\u0637", "\ufec3", "\ufec4", "\ufec2"),
    # ARABIC LETTER ZAH
    "\u0638": ("\u0638", "\ufec7", "\ufec8", "\ufec6"),
    # ARABIC LETTER AIN
    "\u0639": ("\u0639", "\ufecb", "\ufecc", "\ufeca"),
    # ARABIC LETTER GHAIN
    "\u063a": ("\u063a", "\ufecf", "\ufed0", "\ufece"),
    # ARABIC TATWEEL
    TATWEEL: (TATWEEL, TATWEEL, TATWEEL, TATWEEL),
    # ARABIC LETTER FEH
    "\u0641": ("\u0641", "\ufed3", "\ufed4", "\ufed2"),
    # ARABIC LETTER QAF
    "\u0642": ("\u0642", "\ufed7", "\ufed8", "\ufed6"),
    # ARABIC LETTER KAF
    "\u0643": ("\u0643", "\ufedb", "\ufedc", "\ufeda"),
    # ARABIC LETTER LAM
    "\u0644": ("\u0644", "\ufedf", "\ufee0", "\ufede"),
    # ARABIC LETTER MEEM
    "\u0645": ("\u0645", "\ufee3", "\ufee4", "\ufee2"),
    # ARABIC LETTER NOON
    "\u0646": ("\u0646", "\ufee7", "\ufee8", "\ufee6"),
    # ARABIC LETTER HEH
    "\u0647": ("\ufbab", "\ufbab", "\ufbab", "\ufbab"),
    # ARABIC LETTER WAW
    "\u0648": ("\u0648", "", "", "\ufeee"),
    # ARABIC LETTER (UIGHUR KAZAKH KIRGHIZ)? ALEF MAKSURA
    "\u0649": ("\u0649", "\ufbe8", "\ufbe9", "\ufef0"),
    # ARABIC LETTER YEH
    "\u064a": ("\u064a", "\ufef3", "\ufef4", "\ufef2"),
    # ARABIC LETTER ALEF WASLA
    "\u0671": ("\u0671", "", "", "\ufb51"),
    # ARABIC LETTER U WITH HAMZA ABOVE
    "\u0677": ("\u0677", "", "", ""),
    # ARABIC LETTER TTEH
    "\u0679": ("\u0679", "\ufb68", "\ufb69", "\ufb67"),
    # ARABIC LETTER TTEHEH
    "\u067a": ("\u067a", "\ufb60", "\ufb61", "\ufb5f"),
    # ARABIC LETTER BEEH
    "\u067b": ("\u067b", "\ufb54", "\ufb55", "\ufb53"),
    # ARABIC LETTER PEH
    "\u067e": ("\u067e", "\ufb58", "\ufb59", "\ufb57"),
    # ARABIC LETTER TEHEH
    "\u067f": ("\u067f", "\ufb64", "\ufb65", "\ufb63"),
    # ARABIC LETTER BEHEH
    "\u0680": ("\u0680", "\ufb5c", "\ufb5d", "\ufb5b"),
    # ARABIC LETTER NYEH
    "\u0683": ("\u0683", "\ufb78", "\ufb79", "\ufb77"),
    # ARABIC LETTER DYEH
    "\u0684": ("\u0684", "\ufb74", "\ufb75", "\ufb73"),
    # ARABIC LETTER TCHEH
    "\u0686": ("\u0686", "\ufb7c", "\ufb7d", "\ufb7b"),
    # ARABIC LETTER TCHEHEH
    "\u0687": ("\u0687", "\ufb80", "\ufb81", "\ufb7f"),
    # ARABIC LETTER DDAL
    "\u0688": ("\u0688", "", "", "\ufb89"),
    # ARABIC LETTER DAHAL
    "\u068c": ("\u068c", "", "", "\ufb85"),
    # ARABIC LETTER DDAHAL
    "\u068d": ("\u068d", "", "", "\ufb83"),
    # ARABIC LETTER DUL
    "\u068e": ("\u068e", "", "", "\ufb87"),
    # ARABIC LETTER RREH
    "\u0691": ("\u0691", "", "", "\ufb8d"),
    # ARABIC LETTER JEH
    "\u0698": ("\u0698", "", "", "\ufb8b"),
    # ARABIC LETTER VEH
    "\u06a4": ("\u06a4", "\ufb6c", "\ufb6d", "\ufb6b"),
    # ARABIC LETTER PEHEH
    "\u06a6": ("\u06a6", "\ufb70", "\ufb71", "\ufb6f"),
    # ARABIC LETTER KEHEH
    "\u06a9": ("\u06a9", "\ufb90", "\ufb91", "\ufb8f"),
    # ARABIC LETTER NG
    "\u06ad": ("\u06ad", "\ufbd5", "\ufbd6", "\ufbd4"),
    # ARABIC LETTER GAF
    "\u06af": ("\u06af", "\ufb94", "\ufb95", "\ufb93"),
    # ARABIC LETTER NGOEH
    "\u06b1": ("\u06b1", "\ufb9c", "\ufb9d", "\ufb9b"),
    # ARABIC LETTER GUEH
    "\u06b3": ("\u06b3", "\ufb98", "\ufb99", "\ufb97"),
    # ARABIC LETTER NOON GHUNNA
    "\u06ba": ("\u06ba", "", "", "\ufb9f"),
    # ARABIC LETTER RNOON
    "\u06bb": ("\u06bb", "\ufba2", "\ufba3", "\ufba1"),
    # ARABIC LETTER HEH DOACHASHMEE
    "\u06be": ("\u06be", "\ufbac", "\ufbad", "\ufbab"),
    # ARABIC LETTER HEH WITH YEH ABOVE
    "\u06c0": ("\u06c0", "", "", "\ufba5"),
    # ARABIC LETTER HEH GOAL
    "\u06c1": ("\u06c1", "\ufba8", "\ufba9", "\ufba7"),
    # ARABIC LETTER KIRGHIZ OE
    "\u06c5": ("\u06c5", "", "", "\ufbe1"),
    # ARABIC LETTER OE
    "\u06c6": ("\u06c6", "", "", "\ufbda"),
    # ARABIC LETTER U
    "\u06c7": ("\u06c7", "", "", "\ufbd8"),
    # ARABIC LETTER YU
    "\u06c8": ("\u06c8", "", "", "\ufbdc"),
    # ARABIC LETTER KIRGHIZ YU
    "\u06c9": ("\u06c9", "", "", "\ufbe3"),
    # ARABIC LETTER VE
    "\u06cb": ("\u06cb", "", "", "\ufbdf"),
    # ARABIC LETTER FARSI YEH
    "\u06cc": ("\u06cc", "\ufbfe", "\ufbff", "\ufbfd"),
    # ARABIC LETTER E
    "\u06d0": ("\u06d0", "\ufbe6", "\ufbe7", "\ufbe5"),
    # ARABIC LETTER YEH BARREE
    "\u06d2": ("\u06d2", "", "", "\ufbaf"),
    # ARABIC LETTER YEH BARREE WITH HAMZA ABOVE
    "\u06d3": ("\u06d3", "", "", "\ufbb1"),
    # Kurdish letter YEAH
    "\u06ce": ("\ue004", "\ue005", "\ue006", "\ue004"),
    # Kurdish letter Hamza same as arabic Teh without the point
    "\u06d5": ("\u06d5", "", "", "\ue000"),
    # ZWJ
    ZWJ: (ZWJ, ZWJ, ZWJ, ZWJ),
}


def connects_with_letter_before(letter, LETTERS):
    if letter not in LETTERS:
        return False
    forms = LETTERS[letter]
    return forms[FINAL] or forms[MEDIAL]


def connects_with_letter_after(letter, LETTERS):
    if letter not in LETTERS:
        return False
    forms = LETTERS[letter]
    return forms[INITIAL] or forms[MEDIAL]


def connects_with_letters_before_and_after(letter, LETTERS):
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
    (
        "ARABIC LIGATURE BISMILLAH AR-RAHMAN AR-RAHEEM",
        (
            "\u0628\u0633\u0645\u0020"
            "\u0627\u0644\u0644\u0647\u0020"
            "\u0627\u0644\u0631\u062d\u0645\u0646\u0020"
            "\u0627\u0644\u0631\u062d\u064a\u0645",
            ("\ufdfd", "", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE JALLAJALALOUHOU",
        ("\u062c\u0644\u0020\u062c\u0644\u0627\u0644\u0647", ("\ufdfb", "", "", "")),
    ),
    (
        "ARABIC LIGATURE SALLALLAHOU ALAYHE WASALLAM",
        (
            "\u0635\u0644\u0649\u0020"
            "\u0627\u0644\u0644\u0647\u0020"
            "\u0639\u0644\u064a\u0647\u0020"
            "\u0648\u0633\u0644\u0645",
            ("\ufdfa", "", "", ""),
        ),
    ),
)

WORDS_LIGATURES = (
    (
        "ARABIC LIGATURE ALLAH",
        (
            "\u0627\u0644\u0644\u0647",
            ("\ufdf2", "", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE AKBAR",
        (
            "\u0623\u0643\u0628\u0631",
            ("\ufdf3", "", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE ALAYHE",
        (
            "\u0639\u0644\u064a\u0647",
            ("\ufdf7", "", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE MOHAMMAD",
        (
            "\u0645\u062d\u0645\u062f",
            ("\ufdf4", "", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE RASOUL",
        (
            "\u0631\u0633\u0648\u0644",
            ("\ufdf6", "", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE SALAM",
        (
            "\u0635\u0644\u0639\u0645",
            ("\ufdf5", "", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE SALLA",
        (
            "\u0635\u0644\u0649",
            ("\ufdf9", "", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE WASALLAM",
        (
            "\u0648\u0633\u0644\u0645",
            ("\ufdf8", "", "", ""),
        ),
    ),
    (
        "RIAL SIGN",
        (
            "\u0631[\u06cc\u064a]\u0627\u0644",
            ("\ufdfc", "", "", ""),
        ),
    ),
)

LETTERS_LIGATURES = (
    (
        "ARABIC LIGATURE AIN WITH ALEF MAKSURA",
        (
            "\u0639\u0649",
            ("\ufcf7", "", "", "\ufd13"),
        ),
    ),
    (
        "ARABIC LIGATURE AIN WITH JEEM",
        (
            "\u0639\u062c",
            ("\ufc29", "\ufcba", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE AIN WITH JEEM WITH MEEM",
        (
            "\u0639\u062c\u0645",
            ("", "\ufdc4", "", "\ufd75"),
        ),
    ),
    (
        "ARABIC LIGATURE AIN WITH MEEM",
        (
            "\u0639\u0645",
            ("\ufc2a", "\ufcbb", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE AIN WITH MEEM WITH ALEF MAKSURA",
        (
            "\u0639\u0645\u0649",
            ("", "", "", "\ufd78"),
        ),
    ),
    (
        "ARABIC LIGATURE AIN WITH MEEM WITH MEEM",
        (
            "\u0639\u0645\u0645",
            ("", "\ufd77", "", "\ufd76"),
        ),
    ),
    (
        "ARABIC LIGATURE AIN WITH MEEM WITH YEH",
        (
            "\u0639\u0645\u064a",
            ("", "", "", "\ufdb6"),
        ),
    ),
    (
        "ARABIC LIGATURE AIN WITH YEH",
        (
            "\u0639\u064a",
            ("\ufcf8", "", "", "\ufd14"),
        ),
    ),
    (
        "ARABIC LIGATURE ALEF MAKSURA WITH SUPERSCRIPT ALEF",
        (
            "\u0649\u0670",
            ("\ufc5d", "", "", "\ufc90"),
        ),
    ),
    (
        "ARABIC LIGATURE ALEF WITH FATHATAN",
        (
            "\u0627\u064b",
            ("\ufd3d", "", "", "\ufd3c"),
        ),
    ),
    (
        "ARABIC LIGATURE BEH WITH ALEF MAKSURA",
        (
            "\u0628\u0649",
            ("\ufc09", "", "", "\ufc6e"),
        ),
    ),
    (
        "ARABIC LIGATURE BEH WITH HAH",
        (
            "\u0628\u062d",
            ("\ufc06", "\ufc9d", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE BEH WITH HAH WITH YEH",
        (
            "\u0628\u062d\u064a",
            ("", "", "", "\ufdc2"),
        ),
    ),
    (
        "ARABIC LIGATURE BEH WITH HEH",
        (
            "\u0628\u0647",
            ("", "\ufca0", "\ufce2", ""),
        ),
    ),
    (
        "ARABIC LIGATURE BEH WITH JEEM",
        (
            "\u0628\u062c",
            ("\ufc05", "\ufc9c", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE BEH WITH KHAH",
        (
            "\u0628\u062e",
            ("\ufc07", "\ufc9e", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE BEH WITH KHAH WITH YEH",
        (
            "\u0628\u062e\u064a",
            ("", "", "", "\ufd9e"),
        ),
    ),
    (
        "ARABIC LIGATURE BEH WITH MEEM",
        (
            "\u0628\u0645",
            ("\ufc08", "\ufc9f", "\ufce1", "\ufc6c"),
        ),
    ),
    (
        "ARABIC LIGATURE BEH WITH NOON",
        (
            "\u0628\u0646",
            ("", "", "", "\ufc6d"),
        ),
    ),
    (
        "ARABIC LIGATURE BEH WITH REH",
        (
            "\u0628\u0631",
            ("", "", "", "\ufc6a"),
        ),
    ),
    (
        "ARABIC LIGATURE BEH WITH YEH",
        (
            "\u0628\u064a",
            ("\ufc0a", "", "", "\ufc6f"),
        ),
    ),
    (
        "ARABIC LIGATURE BEH WITH ZAIN",
        (
            "\u0628\u0632",
            ("", "", "", "\ufc6b"),
        ),
    ),
    (
        "ARABIC LIGATURE DAD WITH ALEF MAKSURA",
        (
            "\u0636\u0649",
            ("\ufd07", "", "", "\ufd23"),
        ),
    ),
    (
        "ARABIC LIGATURE DAD WITH HAH",
        (
            "\u0636\u062d",
            ("\ufc23", "\ufcb5", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE DAD WITH HAH WITH ALEF MAKSURA",
        (
            "\u0636\u062d\u0649",
            ("", "", "", "\ufd6e"),
        ),
    ),
    (
        "ARABIC LIGATURE DAD WITH HAH WITH YEH",
        (
            "\u0636\u062d\u064a",
            ("", "", "", "\ufdab"),
        ),
    ),
    (
        "ARABIC LIGATURE DAD WITH JEEM",
        (
            "\u0636\u062c",
            ("\ufc22", "\ufcb4", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE DAD WITH KHAH",
        (
            "\u0636\u062e",
            ("\ufc24", "\ufcb6", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE DAD WITH KHAH WITH MEEM",
        (
            "\u0636\u062e\u0645",
            ("", "\ufd70", "", "\ufd6f"),
        ),
    ),
    (
        "ARABIC LIGATURE DAD WITH MEEM",
        (
            "\u0636\u0645",
            ("\ufc25", "\ufcb7", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE DAD WITH REH",
        (
            "\u0636\u0631",
            ("\ufd10", "", "", "\ufd2c"),
        ),
    ),
    (
        "ARABIC LIGATURE DAD WITH YEH",
        (
            "\u0636\u064a",
            ("\ufd08", "", "", "\ufd24"),
        ),
    ),
    (
        "ARABIC LIGATURE FEH WITH ALEF MAKSURA",
        (
            "\u0641\u0649",
            ("\ufc31", "", "", "\ufc7c"),
        ),
    ),
    (
        "ARABIC LIGATURE FEH WITH HAH",
        (
            "\u0641\u062d",
            ("\ufc2e", "\ufcbf", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE FEH WITH JEEM",
        (
            "\u0641\u062c",
            ("\ufc2d", "\ufcbe", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE FEH WITH KHAH",
        (
            "\u0641\u062e",
            ("\ufc2f", "\ufcc0", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE FEH WITH KHAH WITH MEEM",
        (
            "\u0641\u062e\u0645",
            ("", "\ufd7d", "", "\ufd7c"),
        ),
    ),
    (
        "ARABIC LIGATURE FEH WITH MEEM",
        (
            "\u0641\u0645",
            ("\ufc30", "\ufcc1", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE FEH WITH MEEM WITH YEH",
        (
            "\u0641\u0645\u064a",
            ("", "", "", "\ufdc1"),
        ),
    ),
    (
        "ARABIC LIGATURE FEH WITH YEH",
        (
            "\u0641\u064a",
            ("\ufc32", "", "", "\ufc7d"),
        ),
    ),
    (
        "ARABIC LIGATURE GHAIN WITH ALEF MAKSURA",
        (
            "\u063a\u0649",
            ("\ufcf9", "", "", "\ufd15"),
        ),
    ),
    (
        "ARABIC LIGATURE GHAIN WITH JEEM",
        (
            "\u063a\u062c",
            ("\ufc2b", "\ufcbc", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE GHAIN WITH MEEM",
        (
            "\u063a\u0645",
            ("\ufc2c", "\ufcbd", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE GHAIN WITH MEEM WITH ALEF MAKSURA",
        (
            "\u063a\u0645\u0649",
            ("", "", "", "\ufd7b"),
        ),
    ),
    (
        "ARABIC LIGATURE GHAIN WITH MEEM WITH MEEM",
        (
            "\u063a\u0645\u0645",
            ("", "", "", "\ufd79"),
        ),
    ),
    (
        "ARABIC LIGATURE GHAIN WITH MEEM WITH YEH",
        (
            "\u063a\u0645\u064a",
            ("", "", "", "\ufd7a"),
        ),
    ),
    (
        "ARABIC LIGATURE GHAIN WITH YEH",
        (
            "\u063a\u064a",
            ("\ufcfa", "", "", "\ufd16"),
        ),
    ),
    (
        "ARABIC LIGATURE HAH WITH ALEF MAKSURA",
        (
            "\u062d\u0649",
            ("\ufcff", "", "", "\ufd1b"),
        ),
    ),
    (
        "ARABIC LIGATURE HAH WITH JEEM",
        (
            "\u062d\u062c",
            ("\ufc17", "\ufca9", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE HAH WITH JEEM WITH YEH",
        (
            "\u062d\u062c\u064a",
            ("", "", "", "\ufdbf"),
        ),
    ),
    (
        "ARABIC LIGATURE HAH WITH MEEM",
        (
            "\u062d\u0645",
            ("\ufc18", "\ufcaa", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE HAH WITH MEEM WITH ALEF MAKSURA",
        (
            "\u062d\u0645\u0649",
            ("", "", "", "\ufd5b"),
        ),
    ),
    (
        "ARABIC LIGATURE HAH WITH MEEM WITH YEH",
        (
            "\u062d\u0645\u064a",
            ("", "", "", "\ufd5a"),
        ),
    ),
    (
        "ARABIC LIGATURE HAH WITH YEH",
        (
            "\u062d\u064a",
            ("\ufd00", "", "", "\ufd1c"),
        ),
    ),
    (
        "ARABIC LIGATURE HEH WITH ALEF MAKSURA",
        (
            "\u0647\u0649",
            ("\ufc53", "", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE HEH WITH JEEM",
        (
            "\u0647\u062c",
            ("\ufc51", "\ufcd7", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE HEH WITH MEEM",
        (
            "\u0647\u0645",
            ("\ufc52", "\ufcd8", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE HEH WITH MEEM WITH JEEM",
        (
            "\u0647\u0645\u062c",
            ("", "\ufd93", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE HEH WITH MEEM WITH MEEM",
        (
            "\u0647\u0645\u0645",
            ("", "\ufd94", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE HEH WITH SUPERSCRIPT ALEF",
        (
            "\u0647\u0670",
            ("", "\ufcd9", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE HEH WITH YEH",
        (
            "\u0647\u064a",
            ("\ufc54", "", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE JEEM WITH ALEF MAKSURA",
        (
            "\u062c\u0649",
            ("\ufd01", "", "", "\ufd1d"),
        ),
    ),
    (
        "ARABIC LIGATURE JEEM WITH HAH",
        (
            "\u062c\u062d",
            ("\ufc15", "\ufca7", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE JEEM WITH HAH WITH ALEF MAKSURA",
        (
            "\u062c\u062d\u0649",
            ("", "", "", "\ufda6"),
        ),
    ),
    (
        "ARABIC LIGATURE JEEM WITH HAH WITH YEH",
        (
            "\u062c\u062d\u064a",
            ("", "", "", "\ufdbe"),
        ),
    ),
    (
        "ARABIC LIGATURE JEEM WITH MEEM",
        (
            "\u062c\u0645",
            ("\ufc16", "\ufca8", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE JEEM WITH MEEM WITH ALEF MAKSURA",
        (
            "\u062c\u0645\u0649",
            ("", "", "", "\ufda7"),
        ),
    ),
    (
        "ARABIC LIGATURE JEEM WITH MEEM WITH HAH",
        (
            "\u062c\u0645\u062d",
            ("", "\ufd59", "", "\ufd58"),
        ),
    ),
    (
        "ARABIC LIGATURE JEEM WITH MEEM WITH YEH",
        (
            "\u062c\u0645\u064a",
            ("", "", "", "\ufda5"),
        ),
    ),
    (
        "ARABIC LIGATURE JEEM WITH YEH",
        (
            "\u062c\u064a",
            ("\ufd02", "", "", "\ufd1e"),
        ),
    ),
    (
        "ARABIC LIGATURE KAF WITH ALEF",
        (
            "\u0643\u0627",
            ("\ufc37", "", "", "\ufc80"),
        ),
    ),
    (
        "ARABIC LIGATURE KAF WITH ALEF MAKSURA",
        (
            "\u0643\u0649",
            ("\ufc3d", "", "", "\ufc83"),
        ),
    ),
    (
        "ARABIC LIGATURE KAF WITH HAH",
        (
            "\u0643\u062d",
            ("\ufc39", "\ufcc5", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE KAF WITH JEEM",
        (
            "\u0643\u062c",
            ("\ufc38", "\ufcc4", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE KAF WITH KHAH",
        (
            "\u0643\u062e",
            ("\ufc3a", "\ufcc6", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE KAF WITH LAM",
        (
            "\u0643\u0644",
            ("\ufc3b", "\ufcc7", "\ufceb", "\ufc81"),
        ),
    ),
    (
        "ARABIC LIGATURE KAF WITH MEEM",
        (
            "\u0643\u0645",
            ("\ufc3c", "\ufcc8", "\ufcec", "\ufc82"),
        ),
    ),
    (
        "ARABIC LIGATURE KAF WITH MEEM WITH MEEM",
        (
            "\u0643\u0645\u0645",
            ("", "\ufdc3", "", "\ufdbb"),
        ),
    ),
    (
        "ARABIC LIGATURE KAF WITH MEEM WITH YEH",
        (
            "\u0643\u0645\u064a",
            ("", "", "", "\ufdb7"),
        ),
    ),
    (
        "ARABIC LIGATURE KAF WITH YEH",
        (
            "\u0643\u064a",
            ("\ufc3e", "", "", "\ufc84"),
        ),
    ),
    (
        "ARABIC LIGATURE KHAH WITH ALEF MAKSURA",
        (
            "\u062e\u0649",
            ("\ufd03", "", "", "\ufd1f"),
        ),
    ),
    (
        "ARABIC LIGATURE KHAH WITH HAH",
        (
            "\u062e\u062d",
            ("\ufc1a", "", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE KHAH WITH JEEM",
        (
            "\u062e\u062c",
            ("\ufc19", "\ufcab", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE KHAH WITH MEEM",
        (
            "\u062e\u0645",
            ("\ufc1b", "\ufcac", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE KHAH WITH YEH",
        (
            "\u062e\u064a",
            ("\ufd04", "", "", "\ufd20"),
        ),
    ),
    (
        "ARABIC LIGATURE LAM WITH ALEF",
        (
            "\u0644\u0627",
            ("\ufefb", "", "", "\ufefc"),
        ),
    ),
    (
        "ARABIC LIGATURE LAM WITH ALEF MAKSURA",
        (
            "\u0644\u0649",
            ("\ufc43", "", "", "\ufc86"),
        ),
    ),
    (
        "ARABIC LIGATURE LAM WITH ALEF WITH HAMZA ABOVE",
        (
            "\u0644\u0623",
            ("\ufef7", "", "", "\ufef8"),
        ),
    ),
    (
        "ARABIC LIGATURE LAM WITH ALEF WITH HAMZA BELOW",
        (
            "\u0644\u0625",
            ("\ufef9", "", "", "\ufefa"),
        ),
    ),
    (
        "ARABIC LIGATURE LAM WITH ALEF WITH MADDA ABOVE",
        (
            "\u0644\u0622",
            ("\ufef5", "", "", "\ufef6"),
        ),
    ),
    (
        "ARABIC LIGATURE LAM WITH HAH",
        (
            "\u0644\u062d",
            ("\ufc40", "\ufcca", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE LAM WITH HAH WITH ALEF MAKSURA",
        (
            "\u0644\u062d\u0649",
            ("", "", "", "\ufd82"),
        ),
    ),
    (
        "ARABIC LIGATURE LAM WITH HAH WITH MEEM",
        (
            "\u0644\u062d\u0645",
            ("", "\ufdb5", "", "\ufd80"),
        ),
    ),
    (
        "ARABIC LIGATURE LAM WITH HAH WITH YEH",
        (
            "\u0644\u062d\u064a",
            ("", "", "", "\ufd81"),
        ),
    ),
    (
        "ARABIC LIGATURE LAM WITH HEH",
        (
            "\u0644\u0647",
            ("", "\ufccd", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE LAM WITH JEEM",
        (
            "\u0644\u062c",
            ("\ufc3f", "\ufcc9", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE LAM WITH JEEM WITH JEEM",
        (
            "\u0644\u062c\u062c",
            ("", "\ufd83", "", "\ufd84"),
        ),
    ),
    (
        "ARABIC LIGATURE LAM WITH JEEM WITH MEEM",
        (
            "\u0644\u062c\u0645",
            ("", "\ufdba", "", "\ufdbc"),
        ),
    ),
    (
        "ARABIC LIGATURE LAM WITH JEEM WITH YEH",
        (
            "\u0644\u062c\u064a",
            ("", "", "", "\ufdac"),
        ),
    ),
    (
        "ARABIC LIGATURE LAM WITH KHAH",
        (
            "\u0644\u062e",
            ("\ufc41", "\ufccb", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE LAM WITH KHAH WITH MEEM",
        (
            "\u0644\u062e\u0645",
            ("", "\ufd86", "", "\ufd85"),
        ),
    ),
    (
        "ARABIC LIGATURE LAM WITH MEEM",
        (
            "\u0644\u0645",
            ("\ufc42", "\ufccc", "\ufced", "\ufc85"),
        ),
    ),
    (
        "ARABIC LIGATURE LAM WITH MEEM WITH HAH",
        (
            "\u0644\u0645\u062d",
            ("", "\ufd88", "", "\ufd87"),
        ),
    ),
    (
        "ARABIC LIGATURE LAM WITH MEEM WITH YEH",
        (
            "\u0644\u0645\u064a",
            ("", "", "", "\ufdad"),
        ),
    ),
    (
        "ARABIC LIGATURE LAM WITH YEH",
        (
            "\u0644\u064a",
            ("\ufc44", "", "", "\ufc87"),
        ),
    ),
    (
        "ARABIC LIGATURE MEEM WITH ALEF",
        (
            "\u0645\u0627",
            ("", "", "", "\ufc88"),
        ),
    ),
    (
        "ARABIC LIGATURE MEEM WITH ALEF MAKSURA",
        (
            "\u0645\u0649",
            ("\ufc49", "", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE MEEM WITH HAH",
        (
            "\u0645\u062d",
            ("\ufc46", "\ufccf", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE MEEM WITH HAH WITH JEEM",
        (
            "\u0645\u062d\u062c",
            ("", "\ufd89", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE MEEM WITH HAH WITH MEEM",
        (
            "\u0645\u062d\u0645",
            ("", "\ufd8a", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE MEEM WITH HAH WITH YEH",
        (
            "\u0645\u062d\u064a",
            ("", "", "", "\ufd8b"),
        ),
    ),
    (
        "ARABIC LIGATURE MEEM WITH JEEM",
        (
            "\u0645\u062c",
            ("\ufc45", "\ufcce", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE MEEM WITH JEEM WITH HAH",
        (
            "\u0645\u062c\u062d",
            ("", "\ufd8c", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE MEEM WITH JEEM WITH KHAH",
        (
            "\u0645\u062c\u062e",
            ("", "\ufd92", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE MEEM WITH JEEM WITH MEEM",
        (
            "\u0645\u062c\u0645",
            ("", "\ufd8d", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE MEEM WITH JEEM WITH YEH",
        (
            "\u0645\u062c\u064a",
            ("", "", "", "\ufdc0"),
        ),
    ),
    (
        "ARABIC LIGATURE MEEM WITH KHAH",
        (
            "\u0645\u062e",
            ("\ufc47", "\ufcd0", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE MEEM WITH KHAH WITH JEEM",
        (
            "\u0645\u062e\u062c",
            ("", "\ufd8e", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE MEEM WITH KHAH WITH MEEM",
        (
            "\u0645\u062e\u0645",
            ("", "\ufd8f", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE MEEM WITH KHAH WITH YEH",
        (
            "\u0645\u062e\u064a",
            ("", "", "", "\ufdb9"),
        ),
    ),
    (
        "ARABIC LIGATURE MEEM WITH MEEM",
        (
            "\u0645\u0645",
            ("\ufc48", "\ufcd1", "", "\ufc89"),
        ),
    ),
    (
        "ARABIC LIGATURE MEEM WITH MEEM WITH YEH",
        (
            "\u0645\u0645\u064a",
            ("", "", "", "\ufdb1"),
        ),
    ),
    (
        "ARABIC LIGATURE MEEM WITH YEH",
        (
            "\u0645\u064a",
            ("\ufc4a", "", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE NOON WITH ALEF MAKSURA",
        (
            "\u0646\u0649",
            ("\ufc4f", "", "", "\ufc8e"),
        ),
    ),
    (
        "ARABIC LIGATURE NOON WITH HAH",
        (
            "\u0646\u062d",
            ("\ufc4c", "\ufcd3", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE NOON WITH HAH WITH ALEF MAKSURA",
        (
            "\u0646\u062d\u0649",
            ("", "", "", "\ufd96"),
        ),
    ),
    (
        "ARABIC LIGATURE NOON WITH HAH WITH MEEM",
        (
            "\u0646\u062d\u0645",
            ("", "\ufd95", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE NOON WITH HAH WITH YEH",
        (
            "\u0646\u062d\u064a",
            ("", "", "", "\ufdb3"),
        ),
    ),
    (
        "ARABIC LIGATURE NOON WITH HEH",
        (
            "\u0646\u0647",
            ("", "\ufcd6", "\ufcef", ""),
        ),
    ),
    (
        "ARABIC LIGATURE NOON WITH JEEM",
        (
            "\u0646\u062c",
            ("\ufc4b", "\ufcd2", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE NOON WITH JEEM WITH ALEF MAKSURA",
        (
            "\u0646\u062c\u0649",
            ("", "", "", "\ufd99"),
        ),
    ),
    (
        "ARABIC LIGATURE NOON WITH JEEM WITH HAH",
        (
            "\u0646\u062c\u062d",
            ("", "\ufdb8", "", "\ufdbd"),
        ),
    ),
    (
        "ARABIC LIGATURE NOON WITH JEEM WITH MEEM",
        (
            "\u0646\u062c\u0645",
            ("", "\ufd98", "", "\ufd97"),
        ),
    ),
    (
        "ARABIC LIGATURE NOON WITH JEEM WITH YEH",
        (
            "\u0646\u062c\u064a",
            ("", "", "", "\ufdc7"),
        ),
    ),
    (
        "ARABIC LIGATURE NOON WITH KHAH",
        (
            "\u0646\u062e",
            ("\ufc4d", "\ufcd4", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE NOON WITH MEEM",
        (
            "\u0646\u0645",
            ("\ufc4e", "\ufcd5", "\ufcee", "\ufc8c"),
        ),
    ),
    (
        "ARABIC LIGATURE NOON WITH MEEM WITH ALEF MAKSURA",
        (
            "\u0646\u0645\u0649",
            ("", "", "", "\ufd9b"),
        ),
    ),
    (
        "ARABIC LIGATURE NOON WITH MEEM WITH YEH",
        (
            "\u0646\u0645\u064a",
            ("", "", "", "\ufd9a"),
        ),
    ),
    (
        "ARABIC LIGATURE NOON WITH NOON",
        (
            "\u0646\u0646",
            ("", "", "", "\ufc8d"),
        ),
    ),
    (
        "ARABIC LIGATURE NOON WITH REH",
        (
            "\u0646\u0631",
            ("", "", "", "\ufc8a"),
        ),
    ),
    (
        "ARABIC LIGATURE NOON WITH YEH",
        (
            "\u0646\u064a",
            ("\ufc50", "", "", "\ufc8f"),
        ),
    ),
    (
        "ARABIC LIGATURE NOON WITH ZAIN",
        (
            "\u0646\u0632",
            ("", "", "", "\ufc8b"),
        ),
    ),
    (
        "ARABIC LIGATURE QAF WITH ALEF MAKSURA",
        (
            "\u0642\u0649",
            ("\ufc35", "", "", "\ufc7e"),
        ),
    ),
    (
        "ARABIC LIGATURE QAF WITH HAH",
        (
            "\u0642\u062d",
            ("\ufc33", "\ufcc2", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE QAF WITH MEEM",
        (
            "\u0642\u0645",
            ("\ufc34", "\ufcc3", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE QAF WITH MEEM WITH HAH",
        (
            "\u0642\u0645\u062d",
            ("", "\ufdb4", "", "\ufd7e"),
        ),
    ),
    (
        "ARABIC LIGATURE QAF WITH MEEM WITH MEEM",
        (
            "\u0642\u0645\u0645",
            ("", "", "", "\ufd7f"),
        ),
    ),
    (
        "ARABIC LIGATURE QAF WITH MEEM WITH YEH",
        (
            "\u0642\u0645\u064a",
            ("", "", "", "\ufdb2"),
        ),
    ),
    (
        "ARABIC LIGATURE QAF WITH YEH",
        (
            "\u0642\u064a",
            ("\ufc36", "", "", "\ufc7f"),
        ),
    ),
    (
        "ARABIC LIGATURE QALA USED AS KORANIC STOP SIGN",
        (
            "\u0642\u0644\u06d2",
            ("\ufdf1", "", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE REH WITH SUPERSCRIPT ALEF",
        (
            "\u0631\u0670",
            ("\ufc5c", "", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE SAD WITH ALEF MAKSURA",
        (
            "\u0635\u0649",
            ("\ufd05", "", "", "\ufd21"),
        ),
    ),
    (
        "ARABIC LIGATURE SAD WITH HAH",
        (
            "\u0635\u062d",
            ("\ufc20", "\ufcb1", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE SAD WITH HAH WITH HAH",
        (
            "\u0635\u062d\u062d",
            ("", "\ufd65", "", "\ufd64"),
        ),
    ),
    (
        "ARABIC LIGATURE SAD WITH HAH WITH YEH",
        (
            "\u0635\u062d\u064a",
            ("", "", "", "\ufda9"),
        ),
    ),
    (
        "ARABIC LIGATURE SAD WITH KHAH",
        (
            "\u0635\u062e",
            ("", "\ufcb2", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE SAD WITH MEEM",
        (
            "\u0635\u0645",
            ("\ufc21", "\ufcb3", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE SAD WITH MEEM WITH MEEM",
        (
            "\u0635\u0645\u0645",
            ("", "\ufdc5", "", "\ufd66"),
        ),
    ),
    (
        "ARABIC LIGATURE SAD WITH REH",
        (
            "\u0635\u0631",
            ("\ufd0f", "", "", "\ufd2b"),
        ),
    ),
    (
        "ARABIC LIGATURE SAD WITH YEH",
        (
            "\u0635\u064a",
            ("\ufd06", "", "", "\ufd22"),
        ),
    ),
    (
        "ARABIC LIGATURE SALLA USED AS KORANIC STOP SIGN",
        (
            "\u0635\u0644\u06d2",
            ("\ufdf0", "", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE SEEN WITH ALEF MAKSURA",
        (
            "\u0633\u0649",
            ("\ufcfb", "", "", "\ufd17"),
        ),
    ),
    (
        "ARABIC LIGATURE SEEN WITH HAH",
        (
            "\u0633\u062d",
            ("\ufc1d", "\ufcae", "\ufd35", ""),
        ),
    ),
    (
        "ARABIC LIGATURE SEEN WITH HAH WITH JEEM",
        (
            "\u0633\u062d\u062c",
            ("", "\ufd5c", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE SEEN WITH HEH",
        (
            "\u0633\u0647",
            ("", "\ufd31", "\ufce8", ""),
        ),
    ),
    (
        "ARABIC LIGATURE SEEN WITH JEEM",
        (
            "\u0633\u062c",
            ("\ufc1c", "\ufcad", "\ufd34", ""),
        ),
    ),
    (
        "ARABIC LIGATURE SEEN WITH JEEM WITH ALEF MAKSURA",
        (
            "\u0633\u062c\u0649",
            ("", "", "", "\ufd5e"),
        ),
    ),
    (
        "ARABIC LIGATURE SEEN WITH JEEM WITH HAH",
        (
            "\u0633\u062c\u062d",
            ("", "\ufd5d", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE SEEN WITH KHAH",
        (
            "\u0633\u062e",
            ("\ufc1e", "\ufcaf", "\ufd36", ""),
        ),
    ),
    (
        "ARABIC LIGATURE SEEN WITH KHAH WITH ALEF MAKSURA",
        (
            "\u0633\u062e\u0649",
            ("", "", "", "\ufda8"),
        ),
    ),
    (
        "ARABIC LIGATURE SEEN WITH KHAH WITH YEH",
        (
            "\u0633\u062e\u064a",
            ("", "", "", "\ufdc6"),
        ),
    ),
    (
        "ARABIC LIGATURE SEEN WITH MEEM",
        (
            "\u0633\u0645",
            ("\ufc1f", "\ufcb0", "\ufce7", ""),
        ),
    ),
    (
        "ARABIC LIGATURE SEEN WITH MEEM WITH HAH",
        (
            "\u0633\u0645\u062d",
            ("", "\ufd60", "", "\ufd5f"),
        ),
    ),
    (
        "ARABIC LIGATURE SEEN WITH MEEM WITH JEEM",
        (
            "\u0633\u0645\u062c",
            ("", "\ufd61", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE SEEN WITH MEEM WITH MEEM",
        (
            "\u0633\u0645\u0645",
            ("", "\ufd63", "", "\ufd62"),
        ),
    ),
    (
        "ARABIC LIGATURE SEEN WITH REH",
        (
            "\u0633\u0631",
            ("\ufd0e", "", "", "\ufd2a"),
        ),
    ),
    (
        "ARABIC LIGATURE SEEN WITH YEH",
        (
            "\u0633\u064a",
            ("\ufcfc", "", "", "\ufd18"),
        ),
    ),
    # Arabic ligatures with Shadda, the order of characters doesn't matter
    (
        "ARABIC LIGATURE SHADDA WITH DAMMATAN ISOLATED FORM",
        (
            "(?:\u064c\u0651|\u0651\u064c)",
            ("\ufc5e", "\ufc5e", "\ufc5e", "\ufc5e"),
        ),
    ),
    (
        "ARABIC LIGATURE SHADDA WITH KASRATAN ISOLATED FORM",
        (
            "(?:\u064d\u0651|\u0651\u064d)",
            ("\ufc5f", "\ufc5f", "\ufc5f", "\ufc5f"),
        ),
    ),
    (
        "ARABIC LIGATURE SHADDA WITH FATHA ISOLATED FORM",
        (
            "(?:\u064e\u0651|\u0651\u064e)",
            ("\ufc60", "\ufc60", "\ufc60", "\ufc60"),
        ),
    ),
    (
        "ARABIC LIGATURE SHADDA WITH DAMMA ISOLATED FORM",
        (
            "(?:\u064f\u0651|\u0651\u064f)",
            ("\ufc61", "\ufc61", "\ufc61", "\ufc61"),
        ),
    ),
    (
        "ARABIC LIGATURE SHADDA WITH KASRA ISOLATED FORM",
        (
            "(?:\u0650\u0651|\u0651\u0650)",
            ("\ufc62", "\ufc62", "\ufc62", "\ufc62"),
        ),
    ),
    (
        "ARABIC LIGATURE SHADDA WITH SUPERSCRIPT ALEF",
        (
            "(?:\u0651\u0670|\u0670\u0651)",
            ("\ufc63", "", "", ""),
        ),
    ),
    # There is a special case when they are with Tatweel
    (
        "ARABIC LIGATURE SHADDA WITH FATHA MEDIAL FORM",
        (
            "\u0640(?:\u064e\u0651|\u0651\u064e)",
            ("\ufcf2", "\ufcf2", "\ufcf2", "\ufcf2"),
        ),
    ),
    (
        "ARABIC LIGATURE SHADDA WITH DAMMA MEDIAL FORM",
        (
            "\u0640(?:\u064f\u0651|\u0651\u064f)",
            ("\ufcf3", "\ufcf3", "\ufcf3", "\ufcf3"),
        ),
    ),
    (
        "ARABIC LIGATURE SHADDA WITH KASRA MEDIAL FORM",
        (
            "\u0640(?:\u0650\u0651|\u0651\u0650)",
            ("\ufcf4", "\ufcf4", "\ufcf4", "\ufcf4"),
        ),
    ),
    # Repeated with different keys to be backward compatible
    (
        "ARABIC LIGATURE SHADDA WITH FATHA",
        (
            "\u0640(?:\u064e\u0651|\u0651\u064e)",
            ("\ufcf2", "\ufcf2", "\ufcf2", "\ufcf2"),
        ),
    ),
    (
        "ARABIC LIGATURE SHADDA WITH DAMMA",
        (
            "\u0640(?:\u064f\u0651|\u0651\u064f)",
            ("\ufcf3", "\ufcf3", "\ufcf3", "\ufcf3"),
        ),
    ),
    (
        "ARABIC LIGATURE SHADDA WITH KASRA",
        (
            "\u0640(?:\u0650\u0651|\u0651\u0650)",
            ("\ufcf4", "\ufcf4", "\ufcf4", "\ufcf4"),
        ),
    ),
    (
        "ARABIC LIGATURE SHEEN WITH ALEF MAKSURA",
        (
            "\u0634\u0649",
            ("\ufcfd", "", "", "\ufd19"),
        ),
    ),
    (
        "ARABIC LIGATURE SHEEN WITH HAH",
        (
            "\u0634\u062d",
            ("\ufd0a", "\ufd2e", "\ufd38", "\ufd26"),
        ),
    ),
    (
        "ARABIC LIGATURE SHEEN WITH HAH WITH MEEM",
        (
            "\u0634\u062d\u0645",
            ("", "\ufd68", "", "\ufd67"),
        ),
    ),
    (
        "ARABIC LIGATURE SHEEN WITH HAH WITH YEH",
        (
            "\u0634\u062d\u064a",
            ("", "", "", "\ufdaa"),
        ),
    ),
    (
        "ARABIC LIGATURE SHEEN WITH HEH",
        (
            "\u0634\u0647",
            ("", "\ufd32", "\ufcea", ""),
        ),
    ),
    (
        "ARABIC LIGATURE SHEEN WITH JEEM",
        (
            "\u0634\u062c",
            ("\ufd09", "\ufd2d", "\ufd37", "\ufd25"),
        ),
    ),
    (
        "ARABIC LIGATURE SHEEN WITH JEEM WITH YEH",
        (
            "\u0634\u062c\u064a",
            ("", "", "", "\ufd69"),
        ),
    ),
    (
        "ARABIC LIGATURE SHEEN WITH KHAH",
        (
            "\u0634\u062e",
            ("\ufd0b", "\ufd2f", "\ufd39", "\ufd27"),
        ),
    ),
    (
        "ARABIC LIGATURE SHEEN WITH MEEM",
        (
            "\u0634\u0645",
            ("\ufd0c", "\ufd30", "\ufce9", "\ufd28"),
        ),
    ),
    (
        "ARABIC LIGATURE SHEEN WITH MEEM WITH KHAH",
        (
            "\u0634\u0645\u062e",
            ("", "\ufd6b", "", "\ufd6a"),
        ),
    ),
    (
        "ARABIC LIGATURE SHEEN WITH MEEM WITH MEEM",
        (
            "\u0634\u0645\u0645",
            ("", "\ufd6d", "", "\ufd6c"),
        ),
    ),
    (
        "ARABIC LIGATURE SHEEN WITH REH",
        (
            "\u0634\u0631",
            ("\ufd0d", "", "", "\ufd29"),
        ),
    ),
    (
        "ARABIC LIGATURE SHEEN WITH YEH",
        (
            "\u0634\u064a",
            ("\ufcfe", "", "", "\ufd1a"),
        ),
    ),
    (
        "ARABIC LIGATURE TAH WITH ALEF MAKSURA",
        (
            "\u0637\u0649",
            ("\ufcf5", "", "", "\ufd11"),
        ),
    ),
    (
        "ARABIC LIGATURE TAH WITH HAH",
        (
            "\u0637\u062d",
            ("\ufc26", "\ufcb8", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE TAH WITH MEEM",
        (
            "\u0637\u0645",
            ("\ufc27", "\ufd33", "\ufd3a", ""),
        ),
    ),
    (
        "ARABIC LIGATURE TAH WITH MEEM WITH HAH",
        (
            "\u0637\u0645\u062d",
            ("", "\ufd72", "", "\ufd71"),
        ),
    ),
    (
        "ARABIC LIGATURE TAH WITH MEEM WITH MEEM",
        (
            "\u0637\u0645\u0645",
            ("", "\ufd73", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE TAH WITH MEEM WITH YEH",
        (
            "\u0637\u0645\u064a",
            ("", "", "", "\ufd74"),
        ),
    ),
    (
        "ARABIC LIGATURE TAH WITH YEH",
        (
            "\u0637\u064a",
            ("\ufcf6", "", "", "\ufd12"),
        ),
    ),
    (
        "ARABIC LIGATURE TEH WITH ALEF MAKSURA",
        (
            "\u062a\u0649",
            ("\ufc0f", "", "", "\ufc74"),
        ),
    ),
    (
        "ARABIC LIGATURE TEH WITH HAH",
        (
            "\u062a\u062d",
            ("\ufc0c", "\ufca2", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE TEH WITH HAH WITH JEEM",
        (
            "\u062a\u062d\u062c",
            ("", "\ufd52", "", "\ufd51"),
        ),
    ),
    (
        "ARABIC LIGATURE TEH WITH HAH WITH MEEM",
        (
            "\u062a\u062d\u0645",
            ("", "\ufd53", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE TEH WITH HEH",
        (
            "\u062a\u0647",
            ("", "\ufca5", "\ufce4", ""),
        ),
    ),
    (
        "ARABIC LIGATURE TEH WITH JEEM",
        (
            "\u062a\u062c",
            ("\ufc0b", "\ufca1", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE TEH WITH JEEM WITH ALEF MAKSURA",
        (
            "\u062a\u062c\u0649",
            ("", "", "", "\ufda0"),
        ),
    ),
    (
        "ARABIC LIGATURE TEH WITH JEEM WITH MEEM",
        (
            "\u062a\u062c\u0645",
            ("", "\ufd50", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE TEH WITH JEEM WITH YEH",
        (
            "\u062a\u062c\u064a",
            ("", "", "", "\ufd9f"),
        ),
    ),
    (
        "ARABIC LIGATURE TEH WITH KHAH",
        (
            "\u062a\u062e",
            ("\ufc0d", "\ufca3", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE TEH WITH KHAH WITH ALEF MAKSURA",
        (
            "\u062a\u062e\u0649",
            ("", "", "", "\ufda2"),
        ),
    ),
    (
        "ARABIC LIGATURE TEH WITH KHAH WITH MEEM",
        (
            "\u062a\u062e\u0645",
            ("", "\ufd54", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE TEH WITH KHAH WITH YEH",
        (
            "\u062a\u062e\u064a",
            ("", "", "", "\ufda1"),
        ),
    ),
    (
        "ARABIC LIGATURE TEH WITH MEEM",
        (
            "\u062a\u0645",
            ("\ufc0e", "\ufca4", "\ufce3", "\ufc72"),
        ),
    ),
    (
        "ARABIC LIGATURE TEH WITH MEEM WITH ALEF MAKSURA",
        (
            "\u062a\u0645\u0649",
            ("", "", "", "\ufda4"),
        ),
    ),
    (
        "ARABIC LIGATURE TEH WITH MEEM WITH HAH",
        (
            "\u062a\u0645\u062d",
            ("", "\ufd56", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE TEH WITH MEEM WITH JEEM",
        (
            "\u062a\u0645\u062c",
            ("", "\ufd55", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE TEH WITH MEEM WITH KHAH",
        (
            "\u062a\u0645\u062e",
            ("", "\ufd57", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE TEH WITH MEEM WITH YEH",
        (
            "\u062a\u0645\u064a",
            ("", "", "", "\ufda3"),
        ),
    ),
    (
        "ARABIC LIGATURE TEH WITH NOON",
        (
            "\u062a\u0646",
            ("", "", "", "\ufc73"),
        ),
    ),
    (
        "ARABIC LIGATURE TEH WITH REH",
        (
            "\u062a\u0631",
            ("", "", "", "\ufc70"),
        ),
    ),
    (
        "ARABIC LIGATURE TEH WITH YEH",
        (
            "\u062a\u064a",
            ("\ufc10", "", "", "\ufc75"),
        ),
    ),
    (
        "ARABIC LIGATURE TEH WITH ZAIN",
        (
            "\u062a\u0632",
            ("", "", "", "\ufc71"),
        ),
    ),
    (
        "ARABIC LIGATURE THAL WITH SUPERSCRIPT ALEF",
        (
            "\u0630\u0670",
            ("\ufc5b", "", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE THEH WITH ALEF MAKSURA",
        (
            "\u062b\u0649",
            ("\ufc13", "", "", "\ufc7a"),
        ),
    ),
    (
        "ARABIC LIGATURE THEH WITH HEH",
        (
            "\u062b\u0647",
            ("", "", "\ufce6", ""),
        ),
    ),
    (
        "ARABIC LIGATURE THEH WITH JEEM",
        (
            "\u062b\u062c",
            ("\ufc11", "", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE THEH WITH MEEM",
        (
            "\u062b\u0645",
            ("\ufc12", "\ufca6", "\ufce5", "\ufc78"),
        ),
    ),
    (
        "ARABIC LIGATURE THEH WITH NOON",
        (
            "\u062b\u0646",
            ("", "", "", "\ufc79"),
        ),
    ),
    (
        "ARABIC LIGATURE THEH WITH REH",
        (
            "\u062b\u0631",
            ("", "", "", "\ufc76"),
        ),
    ),
    (
        "ARABIC LIGATURE THEH WITH YEH",
        (
            "\u062b\u064a",
            ("\ufc14", "", "", "\ufc7b"),
        ),
    ),
    (
        "ARABIC LIGATURE THEH WITH ZAIN",
        (
            "\u062b\u0632",
            ("", "", "", "\ufc77"),
        ),
    ),
    (
        "ARABIC LIGATURE UIGHUR KIRGHIZ YEH WITH HAMZA ABOVE WITH ALEF MAKSURA",
        (
            "\u0626\u0649",
            ("\ufbf9", "\ufbfb", "", "\ufbfa"),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH ALEF MAKSURA",
        (
            "\u064a\u0649",
            ("\ufc59", "", "", "\ufc95"),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH HAH",
        (
            "\u064a\u062d",
            ("\ufc56", "\ufcdb", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH HAH WITH YEH",
        (
            "\u064a\u062d\u064a",
            ("", "", "", "\ufdae"),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH AE",
        (
            "\u0626\u06d5",
            ("\ufbec", "", "", "\ufbed"),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH ALEF",
        (
            "\u0626\u0627",
            ("\ufbea", "", "", "\ufbeb"),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH ALEF MAKSURA",
        (
            "\u0626\u0649",
            ("\ufc03", "", "", "\ufc68"),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH E",
        (
            "\u0626\u06d0",
            ("\ufbf6", "\ufbf8", "", "\ufbf7"),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH HAH",
        (
            "\u0626\u062d",
            ("\ufc01", "\ufc98", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH HEH",
        (
            "\u0626\u0647",
            ("", "\ufc9b", "\ufce0", ""),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH JEEM",
        (
            "\u0626\u062c",
            ("\ufc00", "\ufc97", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH KHAH",
        (
            "\u0626\u062e",
            ("", "\ufc99", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH MEEM",
        (
            "\u0626\u0645",
            ("\ufc02", "\ufc9a", "\ufcdf", "\ufc66"),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH NOON",
        (
            "\u0626\u0646",
            ("", "", "", "\ufc67"),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH OE",
        (
            "\u0626\u06c6",
            ("\ufbf2", "", "", "\ufbf3"),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH REH",
        (
            "\u0626\u0631",
            ("", "", "", "\ufc64"),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH U",
        (
            "\u0626\u06c7",
            ("\ufbf0", "", "", "\ufbf1"),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH WAW",
        (
            "\u0626\u0648",
            ("\ufbee", "", "", "\ufbef"),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH YEH",
        (
            "\u0626\u064a",
            ("\ufc04", "", "", "\ufc69"),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH YU",
        (
            "\u0626\u06c8",
            ("\ufbf4", "", "", "\ufbf5"),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH ZAIN",
        (
            "\u0626\u0632",
            ("", "", "", "\ufc65"),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH HEH",
        (
            "\u064a\u0647",
            ("", "\ufcde", "\ufcf1", ""),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH JEEM",
        (
            "\u064a\u062c",
            ("\ufc55", "\ufcda", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH JEEM WITH YEH",
        (
            "\u064a\u062c\u064a",
            ("", "", "", "\ufdaf"),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH KHAH",
        (
            "\u064a\u062e",
            ("\ufc57", "\ufcdc", "", ""),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH MEEM",
        (
            "\u064a\u0645",
            ("\ufc58", "\ufcdd", "\ufcf0", "\ufc93"),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH MEEM WITH MEEM",
        (
            "\u064a\u0645\u0645",
            ("", "\ufd9d", "", "\ufd9c"),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH MEEM WITH YEH",
        (
            "\u064a\u0645\u064a",
            ("", "", "", "\ufdb0"),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH NOON",
        (
            "\u064a\u0646",
            ("", "", "", "\ufc94"),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH REH",
        (
            "\u064a\u0631",
            ("", "", "", "\ufc91"),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH YEH",
        (
            "\u064a\u064a",
            ("\ufc5a", "", "", "\ufc96"),
        ),
    ),
    (
        "ARABIC LIGATURE YEH WITH ZAIN",
        (
            "\u064a\u0632",
            ("", "", "", "\ufc92"),
        ),
    ),
    (
        "ARABIC LIGATURE ZAH WITH MEEM",
        (
            "\u0638\u0645",
            ("\ufc28", "\ufcb9", "\ufd3b", ""),
        ),
    ),
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
    "language": "Arabic",
    # Whether to delete the Harakat (Tashkeel) before reshaping or not.
    "delete_harakat": True,
    # Whether to shift the Harakat (Tashkeel) one position so they appear
    # correctly when string is reversed
    "shift_harakat_position": False,
    # Whether to delete the Tatweel (U+0640) before reshaping or not.
    "delete_tatweel": False,
    # Whether to support ZWJ (U+200D) or not.
    "support_zwj": True,
    # Use unshaped form instead of isolated form.
    "use_unshaped_instead_of_isolated": False,
    # Whether to use ligatures or not.
    # Serves as a shortcut to disable all ligatures.
    "support_ligatures": True,
    # When `support_ligatures` is enabled.
    # Separate ligatures configuration take precedence over it.
    # When `support_ligatures` is disabled,
    # separate ligatures configurations are ignored.
    # ------------------- Begin: Ligatures Configurations ------------------ #
    # Sentences (Enabled on top)
    "ARABIC LIGATURE BISMILLAH AR-RAHMAN AR-RAHEEM": False,
    "ARABIC LIGATURE JALLAJALALOUHOU": False,
    "ARABIC LIGATURE SALLALLAHOU ALAYHE WASALLAM": False,
    # Words (Enabled on top)
    "ARABIC LIGATURE ALLAH": True,
    "ARABIC LIGATURE AKBAR": False,
    "ARABIC LIGATURE ALAYHE": False,
    "ARABIC LIGATURE MOHAMMAD": False,
    "ARABIC LIGATURE RASOUL": False,
    "ARABIC LIGATURE SALAM": False,
    "ARABIC LIGATURE SALLA": False,
    "ARABIC LIGATURE WASALLAM": False,
    "RIAL SIGN": False,
    # Letters (Enabled on top)
    "ARABIC LIGATURE LAM WITH ALEF": True,
    "ARABIC LIGATURE LAM WITH ALEF WITH HAMZA ABOVE": True,
    "ARABIC LIGATURE LAM WITH ALEF WITH HAMZA BELOW": True,
    "ARABIC LIGATURE LAM WITH ALEF WITH MADDA ABOVE": True,
    "ARABIC LIGATURE AIN WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE AIN WITH JEEM": False,
    "ARABIC LIGATURE AIN WITH JEEM WITH MEEM": False,
    "ARABIC LIGATURE AIN WITH MEEM": False,
    "ARABIC LIGATURE AIN WITH MEEM WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE AIN WITH MEEM WITH MEEM": False,
    "ARABIC LIGATURE AIN WITH MEEM WITH YEH": False,
    "ARABIC LIGATURE AIN WITH YEH": False,
    "ARABIC LIGATURE ALEF MAKSURA WITH SUPERSCRIPT ALEF": False,
    "ARABIC LIGATURE ALEF WITH FATHATAN": False,
    "ARABIC LIGATURE BEH WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE BEH WITH HAH": False,
    "ARABIC LIGATURE BEH WITH HAH WITH YEH": False,
    "ARABIC LIGATURE BEH WITH HEH": False,
    "ARABIC LIGATURE BEH WITH JEEM": False,
    "ARABIC LIGATURE BEH WITH KHAH": False,
    "ARABIC LIGATURE BEH WITH KHAH WITH YEH": False,
    "ARABIC LIGATURE BEH WITH MEEM": False,
    "ARABIC LIGATURE BEH WITH NOON": False,
    "ARABIC LIGATURE BEH WITH REH": False,
    "ARABIC LIGATURE BEH WITH YEH": False,
    "ARABIC LIGATURE BEH WITH ZAIN": False,
    "ARABIC LIGATURE DAD WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE DAD WITH HAH": False,
    "ARABIC LIGATURE DAD WITH HAH WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE DAD WITH HAH WITH YEH": False,
    "ARABIC LIGATURE DAD WITH JEEM": False,
    "ARABIC LIGATURE DAD WITH KHAH": False,
    "ARABIC LIGATURE DAD WITH KHAH WITH MEEM": False,
    "ARABIC LIGATURE DAD WITH MEEM": False,
    "ARABIC LIGATURE DAD WITH REH": False,
    "ARABIC LIGATURE DAD WITH YEH": False,
    "ARABIC LIGATURE FEH WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE FEH WITH HAH": False,
    "ARABIC LIGATURE FEH WITH JEEM": False,
    "ARABIC LIGATURE FEH WITH KHAH": False,
    "ARABIC LIGATURE FEH WITH KHAH WITH MEEM": False,
    "ARABIC LIGATURE FEH WITH MEEM": False,
    "ARABIC LIGATURE FEH WITH MEEM WITH YEH": False,
    "ARABIC LIGATURE FEH WITH YEH": False,
    "ARABIC LIGATURE GHAIN WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE GHAIN WITH JEEM": False,
    "ARABIC LIGATURE GHAIN WITH MEEM": False,
    "ARABIC LIGATURE GHAIN WITH MEEM WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE GHAIN WITH MEEM WITH MEEM": False,
    "ARABIC LIGATURE GHAIN WITH MEEM WITH YEH": False,
    "ARABIC LIGATURE GHAIN WITH YEH": False,
    "ARABIC LIGATURE HAH WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE HAH WITH JEEM": False,
    "ARABIC LIGATURE HAH WITH JEEM WITH YEH": False,
    "ARABIC LIGATURE HAH WITH MEEM": False,
    "ARABIC LIGATURE HAH WITH MEEM WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE HAH WITH MEEM WITH YEH": False,
    "ARABIC LIGATURE HAH WITH YEH": False,
    "ARABIC LIGATURE HEH WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE HEH WITH JEEM": False,
    "ARABIC LIGATURE HEH WITH MEEM": False,
    "ARABIC LIGATURE HEH WITH MEEM WITH JEEM": False,
    "ARABIC LIGATURE HEH WITH MEEM WITH MEEM": False,
    "ARABIC LIGATURE HEH WITH SUPERSCRIPT ALEF": False,
    "ARABIC LIGATURE HEH WITH YEH": False,
    "ARABIC LIGATURE JEEM WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE JEEM WITH HAH": False,
    "ARABIC LIGATURE JEEM WITH HAH WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE JEEM WITH HAH WITH YEH": False,
    "ARABIC LIGATURE JEEM WITH MEEM": False,
    "ARABIC LIGATURE JEEM WITH MEEM WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE JEEM WITH MEEM WITH HAH": False,
    "ARABIC LIGATURE JEEM WITH MEEM WITH YEH": False,
    "ARABIC LIGATURE JEEM WITH YEH": False,
    "ARABIC LIGATURE KAF WITH ALEF": False,
    "ARABIC LIGATURE KAF WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE KAF WITH HAH": False,
    "ARABIC LIGATURE KAF WITH JEEM": False,
    "ARABIC LIGATURE KAF WITH KHAH": False,
    "ARABIC LIGATURE KAF WITH LAM": False,
    "ARABIC LIGATURE KAF WITH MEEM": False,
    "ARABIC LIGATURE KAF WITH MEEM WITH MEEM": False,
    "ARABIC LIGATURE KAF WITH MEEM WITH YEH": False,
    "ARABIC LIGATURE KAF WITH YEH": False,
    "ARABIC LIGATURE KHAH WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE KHAH WITH HAH": False,
    "ARABIC LIGATURE KHAH WITH JEEM": False,
    "ARABIC LIGATURE KHAH WITH MEEM": False,
    "ARABIC LIGATURE KHAH WITH YEH": False,
    "ARABIC LIGATURE LAM WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE LAM WITH HAH": False,
    "ARABIC LIGATURE LAM WITH HAH WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE LAM WITH HAH WITH MEEM": False,
    "ARABIC LIGATURE LAM WITH HAH WITH YEH": False,
    "ARABIC LIGATURE LAM WITH HEH": False,
    "ARABIC LIGATURE LAM WITH JEEM": False,
    "ARABIC LIGATURE LAM WITH JEEM WITH JEEM": False,
    "ARABIC LIGATURE LAM WITH JEEM WITH MEEM": False,
    "ARABIC LIGATURE LAM WITH JEEM WITH YEH": False,
    "ARABIC LIGATURE LAM WITH KHAH": False,
    "ARABIC LIGATURE LAM WITH KHAH WITH MEEM": False,
    "ARABIC LIGATURE LAM WITH MEEM": False,
    "ARABIC LIGATURE LAM WITH MEEM WITH HAH": False,
    "ARABIC LIGATURE LAM WITH MEEM WITH YEH": False,
    "ARABIC LIGATURE LAM WITH YEH": False,
    "ARABIC LIGATURE MEEM WITH ALEF": False,
    "ARABIC LIGATURE MEEM WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE MEEM WITH HAH": False,
    "ARABIC LIGATURE MEEM WITH HAH WITH JEEM": False,
    "ARABIC LIGATURE MEEM WITH HAH WITH MEEM": False,
    "ARABIC LIGATURE MEEM WITH HAH WITH YEH": False,
    "ARABIC LIGATURE MEEM WITH JEEM": False,
    "ARABIC LIGATURE MEEM WITH JEEM WITH HAH": False,
    "ARABIC LIGATURE MEEM WITH JEEM WITH KHAH": False,
    "ARABIC LIGATURE MEEM WITH JEEM WITH MEEM": False,
    "ARABIC LIGATURE MEEM WITH JEEM WITH YEH": False,
    "ARABIC LIGATURE MEEM WITH KHAH": False,
    "ARABIC LIGATURE MEEM WITH KHAH WITH JEEM": False,
    "ARABIC LIGATURE MEEM WITH KHAH WITH MEEM": False,
    "ARABIC LIGATURE MEEM WITH KHAH WITH YEH": False,
    "ARABIC LIGATURE MEEM WITH MEEM": False,
    "ARABIC LIGATURE MEEM WITH MEEM WITH YEH": False,
    "ARABIC LIGATURE MEEM WITH YEH": False,
    "ARABIC LIGATURE NOON WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE NOON WITH HAH": False,
    "ARABIC LIGATURE NOON WITH HAH WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE NOON WITH HAH WITH MEEM": False,
    "ARABIC LIGATURE NOON WITH HAH WITH YEH": False,
    "ARABIC LIGATURE NOON WITH HEH": False,
    "ARABIC LIGATURE NOON WITH JEEM": False,
    "ARABIC LIGATURE NOON WITH JEEM WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE NOON WITH JEEM WITH HAH": False,
    "ARABIC LIGATURE NOON WITH JEEM WITH MEEM": False,
    "ARABIC LIGATURE NOON WITH JEEM WITH YEH": False,
    "ARABIC LIGATURE NOON WITH KHAH": False,
    "ARABIC LIGATURE NOON WITH MEEM": False,
    "ARABIC LIGATURE NOON WITH MEEM WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE NOON WITH MEEM WITH YEH": False,
    "ARABIC LIGATURE NOON WITH NOON": False,
    "ARABIC LIGATURE NOON WITH REH": False,
    "ARABIC LIGATURE NOON WITH YEH": False,
    "ARABIC LIGATURE NOON WITH ZAIN": False,
    "ARABIC LIGATURE QAF WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE QAF WITH HAH": False,
    "ARABIC LIGATURE QAF WITH MEEM": False,
    "ARABIC LIGATURE QAF WITH MEEM WITH HAH": False,
    "ARABIC LIGATURE QAF WITH MEEM WITH MEEM": False,
    "ARABIC LIGATURE QAF WITH MEEM WITH YEH": False,
    "ARABIC LIGATURE QAF WITH YEH": False,
    "ARABIC LIGATURE QALA USED AS KORANIC STOP SIGN": False,
    "ARABIC LIGATURE REH WITH SUPERSCRIPT ALEF": False,
    "ARABIC LIGATURE SAD WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE SAD WITH HAH": False,
    "ARABIC LIGATURE SAD WITH HAH WITH HAH": False,
    "ARABIC LIGATURE SAD WITH HAH WITH YEH": False,
    "ARABIC LIGATURE SAD WITH KHAH": False,
    "ARABIC LIGATURE SAD WITH MEEM": False,
    "ARABIC LIGATURE SAD WITH MEEM WITH MEEM": False,
    "ARABIC LIGATURE SAD WITH REH": False,
    "ARABIC LIGATURE SAD WITH YEH": False,
    "ARABIC LIGATURE SALLA USED AS KORANIC STOP SIGN": False,
    "ARABIC LIGATURE SEEN WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE SEEN WITH HAH": False,
    "ARABIC LIGATURE SEEN WITH HAH WITH JEEM": False,
    "ARABIC LIGATURE SEEN WITH HEH": False,
    "ARABIC LIGATURE SEEN WITH JEEM": False,
    "ARABIC LIGATURE SEEN WITH JEEM WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE SEEN WITH JEEM WITH HAH": False,
    "ARABIC LIGATURE SEEN WITH KHAH": False,
    "ARABIC LIGATURE SEEN WITH KHAH WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE SEEN WITH KHAH WITH YEH": False,
    "ARABIC LIGATURE SEEN WITH MEEM": False,
    "ARABIC LIGATURE SEEN WITH MEEM WITH HAH": False,
    "ARABIC LIGATURE SEEN WITH MEEM WITH JEEM": False,
    "ARABIC LIGATURE SEEN WITH MEEM WITH MEEM": False,
    "ARABIC LIGATURE SEEN WITH REH": False,
    "ARABIC LIGATURE SEEN WITH YEH": False,
    "ARABIC LIGATURE SHADDA WITH DAMMA": False,
    "ARABIC LIGATURE SHADDA WITH DAMMA ISOLATED FORM": False,
    "ARABIC LIGATURE SHADDA WITH DAMMA MEDIAL FORM": False,
    "ARABIC LIGATURE SHADDA WITH DAMMATAN ISOLATED FORM": False,
    "ARABIC LIGATURE SHADDA WITH FATHA": False,
    "ARABIC LIGATURE SHADDA WITH FATHA ISOLATED FORM": False,
    "ARABIC LIGATURE SHADDA WITH FATHA MEDIAL FORM": False,
    "ARABIC LIGATURE SHADDA WITH KASRA": False,
    "ARABIC LIGATURE SHADDA WITH KASRA ISOLATED FORM": False,
    "ARABIC LIGATURE SHADDA WITH KASRA MEDIAL FORM": False,
    "ARABIC LIGATURE SHADDA WITH KASRATAN ISOLATED FORM": False,
    "ARABIC LIGATURE SHADDA WITH SUPERSCRIPT ALEF": False,
    "ARABIC LIGATURE SHADDA WITH SUPERSCRIPT ALEF ISOLATED FORM": False,
    "ARABIC LIGATURE SHEEN WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE SHEEN WITH HAH": False,
    "ARABIC LIGATURE SHEEN WITH HAH WITH MEEM": False,
    "ARABIC LIGATURE SHEEN WITH HAH WITH YEH": False,
    "ARABIC LIGATURE SHEEN WITH HEH": False,
    "ARABIC LIGATURE SHEEN WITH JEEM": False,
    "ARABIC LIGATURE SHEEN WITH JEEM WITH YEH": False,
    "ARABIC LIGATURE SHEEN WITH KHAH": False,
    "ARABIC LIGATURE SHEEN WITH MEEM": False,
    "ARABIC LIGATURE SHEEN WITH MEEM WITH KHAH": False,
    "ARABIC LIGATURE SHEEN WITH MEEM WITH MEEM": False,
    "ARABIC LIGATURE SHEEN WITH REH": False,
    "ARABIC LIGATURE SHEEN WITH YEH": False,
    "ARABIC LIGATURE TAH WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE TAH WITH HAH": False,
    "ARABIC LIGATURE TAH WITH MEEM": False,
    "ARABIC LIGATURE TAH WITH MEEM WITH HAH": False,
    "ARABIC LIGATURE TAH WITH MEEM WITH MEEM": False,
    "ARABIC LIGATURE TAH WITH MEEM WITH YEH": False,
    "ARABIC LIGATURE TAH WITH YEH": False,
    "ARABIC LIGATURE TEH WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE TEH WITH HAH": False,
    "ARABIC LIGATURE TEH WITH HAH WITH JEEM": False,
    "ARABIC LIGATURE TEH WITH HAH WITH MEEM": False,
    "ARABIC LIGATURE TEH WITH HEH": False,
    "ARABIC LIGATURE TEH WITH JEEM": False,
    "ARABIC LIGATURE TEH WITH JEEM WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE TEH WITH JEEM WITH MEEM": False,
    "ARABIC LIGATURE TEH WITH JEEM WITH YEH": False,
    "ARABIC LIGATURE TEH WITH KHAH": False,
    "ARABIC LIGATURE TEH WITH KHAH WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE TEH WITH KHAH WITH MEEM": False,
    "ARABIC LIGATURE TEH WITH KHAH WITH YEH": False,
    "ARABIC LIGATURE TEH WITH MEEM": False,
    "ARABIC LIGATURE TEH WITH MEEM WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE TEH WITH MEEM WITH HAH": False,
    "ARABIC LIGATURE TEH WITH MEEM WITH JEEM": False,
    "ARABIC LIGATURE TEH WITH MEEM WITH KHAH": False,
    "ARABIC LIGATURE TEH WITH MEEM WITH YEH": False,
    "ARABIC LIGATURE TEH WITH NOON": False,
    "ARABIC LIGATURE TEH WITH REH": False,
    "ARABIC LIGATURE TEH WITH YEH": False,
    "ARABIC LIGATURE TEH WITH ZAIN": False,
    "ARABIC LIGATURE THAL WITH SUPERSCRIPT ALEF": False,
    "ARABIC LIGATURE THEH WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE THEH WITH HEH": False,
    "ARABIC LIGATURE THEH WITH JEEM": False,
    "ARABIC LIGATURE THEH WITH MEEM": False,
    "ARABIC LIGATURE THEH WITH NOON": False,
    "ARABIC LIGATURE THEH WITH REH": False,
    "ARABIC LIGATURE THEH WITH YEH": False,
    "ARABIC LIGATURE THEH WITH ZAIN": False,
    "ARABIC LIGATURE UIGHUR KIRGHIZ YEH WITH HAMZA ABOVE WITH ALEF MAKSURA": False,  # noqa
    "ARABIC LIGATURE YEH WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE YEH WITH HAH": False,
    "ARABIC LIGATURE YEH WITH HAH WITH YEH": False,
    "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH AE": False,
    "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH ALEF": False,
    "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH ALEF MAKSURA": False,
    "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH E": False,
    "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH HAH": False,
    "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH HEH": False,
    "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH JEEM": False,
    "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH KHAH": False,
    "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH MEEM": False,
    "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH NOON": False,
    "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH OE": False,
    "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH REH": False,
    "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH U": False,
    "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH WAW": False,
    "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH YEH": False,
    "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH YU": False,
    "ARABIC LIGATURE YEH WITH HAMZA ABOVE WITH ZAIN": False,
    "ARABIC LIGATURE YEH WITH HEH": False,
    "ARABIC LIGATURE YEH WITH JEEM": False,
    "ARABIC LIGATURE YEH WITH JEEM WITH YEH": False,
    "ARABIC LIGATURE YEH WITH KHAH": False,
    "ARABIC LIGATURE YEH WITH MEEM": False,
    "ARABIC LIGATURE YEH WITH MEEM WITH MEEM": False,
    "ARABIC LIGATURE YEH WITH MEEM WITH YEH": False,
    "ARABIC LIGATURE YEH WITH NOON": False,
    "ARABIC LIGATURE YEH WITH REH": False,
    "ARABIC LIGATURE YEH WITH YEH": False,
    "ARABIC LIGATURE YEH WITH ZAIN": False,
    "ARABIC LIGATURE ZAH WITH MEEM": False,
    # -------------------- End: Ligatures Configurations ------------------- #
}


def auto_config(configuration=None, configuration_file=None):
    loaded_from_envvar = False

    configuration_parser = ConfigParser()
    configuration_parser.read_dict({"ArabicReshaper": default_config})

    if not configuration_file:
        configuration_file = os.getenv("PYTHON_ARABIC_RESHAPER_CONFIGURATION_FILE")
        if configuration_file:
            loaded_from_envvar = True

    if configuration_file:
        if not os.path.exists(configuration_file):
            raise Exception(
                "Configuration file {} not found{}.".format(
                    configuration_file,
                    loaded_from_envvar
                    and (
                        " it is set in your environment variable "
                        + "PYTHON_ARABIC_RESHAPER_CONFIGURATION_FILE"
                    )
                    or "",
                )
            )
        configuration_parser.read((configuration_file,))

    if configuration:
        configuration_parser.read_dict({"ArabicReshaper": configuration})

    if "ArabicReshaper" not in configuration_parser:
        raise ValueError(
            "Invalid configuration: "
            "A section with the name ArabicReshaper was not found"
        )

    return configuration_parser["ArabicReshaper"]


def config_for_true_type_font(font_file_path, ligatures_config=ENABLE_ALL_LIGATURES):
    if not with_font_config:
        raise Exception(
            "fonttools not installed, "
            + "install it then rerun this.\n"
            + "$ pip install arabic-teshaper[with-fonttools]"
        )
    if not font_file_path or not os.path.exists(font_file_path):
        raise Exception("Invalid path to font file")
    ttfont = TTFont(font_file_path)
    has_isolated = True
    for k, v in LETTERS_ARABIC.items():
        for table in ttfont["cmap"].tables:
            if ord(v[ISOLATED]) in table.cmap:
                break
        else:
            has_isolated = False
            break

    configuration = {
        "use_unshaped_instead_of_isolated": not has_isolated,
    }

    def process_ligatures(ligatures):
        for ligature in ligatures:
            forms = list(filter(lambda form: form != "", ligature[1][1]))
            n = len(forms)
            for form in forms:
                for table in ttfont["cmap"].tables:
                    if ord(form) in table.cmap:
                        n -= 1
                        break
            configuration[ligature[0]] = n == 0

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
    "["
    "\u0610-\u061a"
    "\u064b-\u065f"
    "\u0670"
    "\u06d6-\u06dc"
    "\u06df-\u06e8"
    "\u06ea-\u06ed"
    "\u08d4-\u08e1"
    "\u08d4-\u08ed"
    "\u08e3-\u08ff"
    "]",
    re.UNICODE | re.X,
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
        self.language = self.configuration.get("language")

        if self.language == "ArabicV2":
            self.letters = LETTERS_ARABIC_V2
        elif self.language == "Kurdish":
            self.letters = LETTERS_KURDISH
        else:
            self.letters = LETTERS_ARABIC

    @property
    def _ligatures_re(self):
        if not hasattr(self, "__ligatures_re"):
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
                patterns.append("({})".format(replacement[MATCH]))
                index += 1
            self._re_group_index_to_ligature_forms = re_group_index_to_ligature_forms
            self.__ligatures_re = re.compile("|".join(patterns), re.UNICODE)
        return self.__ligatures_re

    def _get_ligature_forms_from_re_group_index(self, group_index):
        if not hasattr(self, "_re_group_index_to_ligature_forms"):
            return self._ligatures_re
        return self._re_group_index_to_ligature_forms[group_index]

    def reshape(self, text):
        if not text:
            return ""

        output = []

        LETTER = 0
        FORM = 1
        NOT_SUPPORTED = -1

        delete_harakat = self.configuration.getboolean("delete_harakat")
        delete_tatweel = self.configuration.getboolean("delete_tatweel")
        support_zwj = self.configuration.getboolean("support_zwj")
        shift_harakat_position = self.configuration.getboolean("shift_harakat_position")
        use_unshaped_instead_of_isolated = self.configuration.getboolean(
            "use_unshaped_instead_of_isolated"
        )

        positions_harakat = {}

        isolated_form = UNSHAPED if use_unshaped_instead_of_isolated else ISOLATED

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
                    previous_letter[LETTER], self.letters
                ):
                    output.append((letter, isolated_form))
                elif previous_letter[
                    FORM
                ] == FINAL and not connects_with_letters_before_and_after(
                    previous_letter[LETTER], self.letters
                ):
                    output.append((letter, isolated_form))
                elif previous_letter[FORM] == isolated_form:
                    output[-1] = (previous_letter[LETTER], INITIAL)
                    output.append((letter, FINAL))
                # Otherwise, we will change the previous letter to connect
                # to the current letter
                else:
                    output[-1] = (previous_letter[LETTER], MEDIAL)
                    output.append((letter, FINAL))

            # Remove ZWJ if it's the second to last item as it won't be useful
            if support_zwj and len(output) > 1 and output[-2][LETTER] == ZWJ:
                output.pop(len(output) - 2)

        if support_zwj and output and output[-1][LETTER] == ZWJ:
            output.pop()

        if self.configuration.getboolean("support_ligatures"):
            # Clean text from Harakat to be able to find ligatures
            text = HARAKAT_RE.sub("", text)

            # Clean text from Tatweel to find ligatures if delete_tatweel
            if delete_tatweel:
                text = text.replace(TATWEEL, "")

            for match in re.finditer(self._ligatures_re, text):
                group_index = next(
                    (i for i, group in enumerate(match.groups()) if group), -1
                )
                forms = self._get_ligature_forms_from_re_group_index(group_index)
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
                output[a + 1 : b] = repeat(("", NOT_SUPPORTED), b - 1 - a)

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

        return "".join(result)


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
        reversed_text = "".join(reversed(reshaped_text))
        # يمكنك هنا إضافة تحويل النص إلى UTF-8 إذا لزم الأمر أو أية معالجات إضافية
        return reversed_text
