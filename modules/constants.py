"""bikeparkingdb

Global constants

Copyright (c) 2024 Todd Glover
Derived from github.com/ironwoodcall/tagtracker (C) 2023-2024 Julias Hocking & Todd Glover

    Notwithstanding the licensing information below, this code may not
    be used in a commercial (for-profit, non-profit or government) setting
    without the copyright-holder's written consent.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import re


# Type aliases only to improve readability and IDE linting
MaybeTag = str
MaybeTime = str
MaybeDate = str

# Constants to use as dictionary keys.
# E.g. rather than something[this_time]["tag"] = "whatever",
# could instead be something[this_time][TAG_KEY] = "whatever"
# The values of these constants aren't important as long as they're unique.
# By using these rather than string values, the lint checker in the
# editor can pick up missing or misspelled items, as can Python itself.
# These all have a non-ASCII chr (→) at the beginning to make it unlikely
# that their values would ever get typed or otherwise be non-unique

TAG = chr(0x2192) + "tag"
BIKE_IN = chr(0x2192) + "bike_in"
BIKE_OUT = chr(0x2192) + "bike_out"
INOUT = chr(0x2192) + "inout"
NOTES = chr(0x2192) + "notes"
REGULAR = chr(0x2192) + "regular"
OVERSIZE = chr(0x2192) + "oversize"
MIXED = chr(0x2192) + "mixed"
RETIRED = chr(0x2192) + "retired"
USABLE = chr(0x2192) + "usable"
TOTAL = chr(0x2192) + "total"
COUNT = chr(0x2192) + "count"
TIME = chr(0x2192) + "time"
IGNORE = chr(0x2192) + "ignore"
NOT_A_LIST = chr(0x2192) + "not_a_list"
COLOURS = chr(0x2192) + "colours"
BADVALUE = chr(0x2192) + "badvalue"
UPPERCASE = chr(0x2192) + "uppercase"
LOWERCASE = chr(0x2192) + "lowercase"
UNKNOWN = chr(0x2192) + "unknown"
ON = chr(0x2192) + "on"
OFF = chr(0x2192) + "off"
ALERT = chr(0x2192) + "alert"
CHEER = chr(0x2192) + "cheer"

# Here's how I really want to do it, but then pylint won't know they're defined
# for keyword in [
#    "TAG", "TIME",
#    "BIKE_IN","BIKE_OUT","INOUT",
#    "REGULAR","OVERSIZE","RETIRED",
#    "TOTAL","COUNT",
#    "IGNORE",
#    "COLOURS",
#    "BADVALUE",
#    "UPPERCASE","LOWERCASE",
#   "UNKNOWN",
#    "ON","OFF"
# ]:
#   globals()[keyword] = chr(0x2192) + keyword.lower()

# Date re checks for date that might be in another string
_DATE_RE = r"(2[0-9][0-9][0-9])[/-]([01]?[0-9])[/-]([0123]?[0-9])"
# Match a date within another string
DATE_PART_RE = re.compile(r"(\b|[^a-zA-Z0-9])" + _DATE_RE + r"\b")
# Match a date as the whole string
DATE_FULL_RE = re.compile(r"^ *" + _DATE_RE + " *$")

# How long a single time block is (minutes) - for charts/stats etc
BLOCK_DURATION = 30




# Styles related to colour
STYLE = {}
PROMPT_STYLE = "prompt_style"
SUBPROMPT_STYLE = "subprompt_style"
ANSWER_STYLE = "answer_style"
TITLE_STYLE = "title_style"
SUBTITLE_STYLE = "subtitle_style"
NORMAL_STYLE = "normal_style"
RESET_STYLE = "reset_style"
HIGHLIGHT_STYLE = "highlight_style"
WARNING_STYLE = "warn_style"
ERROR_STYLE = "error_style"
ALERT_STYLE = "alert_style"
STRONG_ALERT_STYLE = "strong_alert_style"


def set_html_style():
    """Set STYLE values to work in an HTML doc."""
    global STYLE  # pylint:disable=global-statement
    STYLE = {
        PROMPT_STYLE: '<span style="color: green; background-color: black; font-weight: bold;">',
        SUBPROMPT_STYLE: '<span style="color: green; background-color: black; font-weight: bold;">',
        ANSWER_STYLE: '<span style="color: yellow; background-color: blue; font-weight: bold;">',
        TITLE_STYLE: '<span style="color: white; background-color: blue; font-weight: bold;">',
        SUBTITLE_STYLE: '<span style="color: cyan; background-color: black; font-weight: bold;">',
        RESET_STYLE: "</span>",  # Closes the style tag
        NORMAL_STYLE: '<span style="color:white;background-color:black;">',  # Nothing
        HIGHLIGHT_STYLE: '<span style="color: cyan; background-color: black; font-weight: bold;">',
        WARNING_STYLE: '<span style="color: red; background-color: black; font-weight: bold;">',
        ERROR_STYLE: '<span style="color: white; background-color: red; font-weight: bold;">',
        ALERT_STYLE: '<span style="color: white; background-color: blue; font-weight: bold;">',
        STRONG_ALERT_STYLE:
            '<span style="color: white; background-color: red; font-weight: bold;">',
    }


# Colour combinations.
set_html_style()

# These are the symbols & styles used in the tag inventory matrix.
# Each is a tuple of (symbol,style).
# Each symbol should be 2 characters wide.  Warning if using fancy unicode
# that those characters come in various widths, platform-dependent.
TAG_INV_UNKNOWN = ("  ", NORMAL_STYLE)
TAG_INV_AVAILABLE = (" -", NORMAL_STYLE)
TAG_INV_BIKE_IN = ("In", ANSWER_STYLE)
TAG_INV_BIKE_OUT = ("Ou", PROMPT_STYLE)
TAG_INV_RETIRED = ("Re", WARNING_STYLE)
TAG_INV_ERROR = ("!?", ERROR_STYLE)

