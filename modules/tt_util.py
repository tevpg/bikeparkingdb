"""TagTracker by Julias Hocking.

Utility functions & constants for TagTracker suite.

Copyright (C) 2023-2024 Julias Hocking & Todd Glover

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

import os
import sys
import datetime
import re
import collections
import random
import string

from tt_time import BTime
from tt_tag import TagID


def find_on_path(filename):
    """Check if filename exists, including anywhere in system PATH.

    Returns the absolute filepath if it exists, otherwise "".
    """
    # Check if the filename contains '/' indicating it's a relative or absolute path
    if "/" in filename:
        if os.path.exists(filename):
            return os.path.abspath(filename)
        else:
            return None  # File doesn't exist
    else:
        # Iterate through each directory in the system path
        for directory in os.environ["PATH"].split(os.pathsep):
            # What would the absolute filepath be if it were present?
            abs_path = os.path.join(directory, filename)
            if os.path.exists(abs_path):
                return abs_path
        # Return None if the file is not found on the system path
        return None


def top_level_script() -> str:
    """Return filename of highest-level calling script.

    This is specifically intended to let a module determine
    whether or not it is being called by the tagtracker desktop
    (data entry) script."""

    frame = sys._getframe()
    while frame.f_back:
        frame = frame.f_back
    top = frame.f_globals.get("__file__", None)
    top = top if top else ""
    return top


def squawk(whatever: str = "") -> None:
    """Print whatever with file & linenumber in front of it.

    This is intended for programming errors not prettiness.

    Additional caller info:
        caller_path = f.f_globals['__file__'] (though fails if squawk()
            called from interpreter, as __file__ not in globals at that point)
        caller_file = os.path.basename(caller_path)
    """
    f = sys._getframe(1)  # pylint:disable=protected-access
    caller_module = f.f_globals["__name__"]
    caller_function = f.f_code.co_name
    caller_line_no = f.f_lineno
    print(f"{caller_module}:{caller_function}():{caller_line_no}: {whatever}")


def decomment(string: str) -> str:
    """Remove any part of the string that starts with '#'."""
    r = re.match(r"^([^#]*) *#", string)
    if r:
        return r.group(1)
    return string


def date_str(
    maybe_date: str,
    dow_str_len: int = None,
    long_date: bool = False,
    strict: bool = False,
) -> str:
    """Return maybe_date in the form of YYYY-MM-DD (or "").

    Optional flags will return it in a variety of str or int
    formats:
        dow_str_len: if set, returns the date as day of week
            of given length (up to day of week's full length)
        long_date: if True, returns str as a long date
        strict: if set, only accepts exact "YYYY-MM-DD";
            otherwise accepts "now", "today" "tomorrow" and
            "yesterday"; strips whitespace; and accepts
            "" or "/" as separators

    """
    if not maybe_date or not isinstance(maybe_date, str) or maybe_date.isspace():
        return ""
    thisday = None
    if not strict:
        maybe_date = maybe_date.lower().strip()
        if maybe_date in ["now", "today"]:
            thisday = datetime.datetime.today()
        elif maybe_date == "yesterday":
            thisday = datetime.datetime.today() - datetime.timedelta(1)
        elif maybe_date == "tomorrow":
            thisday = datetime.datetime.today() + datetime.timedelta(1)
        else:
            # Allow YYYYMMDD or YYYY/MM/DD
            r = re.fullmatch(r"(\d\d\d\d)[-/]?(\d\d)[-/]?(\d\d)", maybe_date)
            if not r:
                return ""
            try:
                thisday = datetime.datetime.strptime(
                    f"{r.group(1)}-{r.group(2)}-{r.group(3)}", "%Y-%m-%d"
                )
            except ValueError:
                return ""
    if not thisday:
        try:
            thisday = datetime.datetime.strptime(maybe_date, "%Y-%m-%d")
        except ValueError:
            return ""
    if not thisday:
        return ""
    # Now have thisday (a datetime object), convert to str
    # Format as a day of the week?
    if dow_str_len:
        return thisday.strftime("%A")[0:dow_str_len]
    if long_date:
        return thisday.strftime("%A %B %d (%Y-%m-%d)")
    return thisday.strftime("%Y-%m-%d")


def date_offset(start_date: str, offset: int) -> str:
    """Return a day some number of days before or after a date.

    start_date: is any date string that date_str() will recognize
    offset: is the number of days later(+) or earlier(-)
    Returns:
        YYYY-MM-DD of date which is offset from start_date
        "" if start_date is bad
    """
    start_date = date_str(start_date)
    if not start_date:
        return ""
    offset_day = datetime.datetime.strptime(
        start_date, "%Y-%m-%d"
    ) + datetime.timedelta(offset)
    return offset_day.strftime("%Y-%m-%d")


def dow_int(date_or_dayname: str) -> int:
    """Get ISO day of week from a date or weekday name."""
    date = date_str(date_or_dayname)
    if date:
        d = datetime.datetime.strptime(date, "%Y-%m-%d")
        return int(d.strftime("%u"))
    # Try to match to a dow.
    dow_ints = {
        1: ["m", "mo", "mon", "monday"],
        2: ["tu", "tue", "tues", "tuesday"],
        3: ["w", "we", "wed", "wednesday"],
        4: ["th", "thu", "thurs", "thursday"],
        5: ["f", "fr", "fri", "friday"],
        6: ["sa", "sat", "saturday"],
        7: ["su", "sun", "sunday"],
    }
    for num, name_list in dow_ints.items():
        if str(date_or_dayname).strip().lower() in name_list:
            return num
    return None


def dow_str(iso_dow: int, dow_str_len: int = 0) -> str:
    """Return int ISO day of week as a str of length dow_str_len.

    If dow_len is not specified then returns whole dow name.
    """
    iso_dow = str(iso_dow)
    dow_str_len = dow_str_len if dow_str_len else 99
    d = datetime.datetime.strptime(f"2023-1-{iso_dow}", "%Y-%W-%u")
    return date_str(d.strftime("%Y-%m-%d"), dow_str_len=dow_str_len)


def most_recent_dow(iso_day) -> str:
    """Return most recent date that falls on day of week iso_day."""
    if isinstance(iso_day, str) and iso_day.isdigit():
        iso_day = int(iso_day)
    elif isinstance(iso_day, float):
        iso_day = round(iso_day)
    elif not isinstance(iso_day, int):
        return None

    # Get the current date
    current_date = datetime.date.today()
    # Calculate the difference between the current day of the week and the target ISO day
    day_difference = current_date.isoweekday() - iso_day
    # Calculate the most recent date by subtracting the day difference from the current date
    most_recent_date = current_date - datetime.timedelta(days=day_difference)
    return most_recent_date.strftime("%Y-%m-%d")


def get_time() -> BTime:
    """Return current time as string: HH:MM."""
    # FIXME: get_time() deprecated, use BTime("now") instead
    return BTime(datetime.datetime.today().strftime("%H:%M"))


def time_int(maybe_time: str | int | float | None) -> int | None:
    """Return maybe_time (str or int) to number of minutes since midnight or "".

        Input can be int (minutes since midnight) or a string
    that might be a time in HH:MM.

    Return is either None (doesn't look like a valid time) or
    will be an integer between 0 and 1440.

    Warning: edge case: if given "00:00" or 0, this will return 0,
    which can test as False in a boolean argument.  In cases where 0
    might be a legitimate time, test for the type of the return or
    test whether "is None".
    """
    # FIXME: time_int() deprecated, use BTime() instead
    if isinstance(maybe_time, float):
        maybe_time = round(maybe_time)
    if isinstance(maybe_time, str):
        r = re.match(r"^ *([012]*[0-9]):?([0-5][0-9]) *$", maybe_time)
        if not (r):
            return None
        h = int(r.group(1))
        m = int(r.group(2))
        # Test for an impossible time
        if h > 24 or m > 59 or (h * 60 + m) > 1440:
            return None
        return h * 60 + m
    if isinstance(maybe_time, int):
        # Test for impossible time.
        if not (0 <= maybe_time <= 1440):
            return None
        return maybe_time
    if maybe_time is None:
        return None
    # Not an int, not a str, not None.
    squawk(f"PROGRAM ERROR: called time_int({maybe_time=})")
    return None


def iso_timestamp() -> str:
    """Get ISO8601 timestamp of current local time."""
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def time_str(
    maybe_time: int | str | float | None,
    allow_now: bool = False,
    default_now: bool = False,
) -> BTime:
    """Return maybe_time as HH:MM (or "").

    Input can be int/float (duration or minutes since midnight),
    or a string that *might* be a time in [H]H[:]MM.

    Special case: "now" will return current time if allowed
    by flag "allow_now".

    If default_now is True, then will return current time when input is blank.

    Return is either "" (doesn't look like a valid time) or
    will be HH:MM, always length 5 (i.e. 09:00 not 9:00)
    """
    # FIXME: time_str() deprecated, use BTime() object
    if not maybe_time and default_now:
        return BTime("now")
    if isinstance(maybe_time, float):
        maybe_time = round(maybe_time)
    if isinstance(maybe_time, str):
        if maybe_time.lower() == "now" and allow_now:
            return BTime("now")
        r = re.match(r"^ *([012]*[0-9]):?([0-5][0-9]) *$", maybe_time)
        if not (r):
            return BTime("")
        h = int(r.group(1))
        m = int(r.group(2))
        # Test for an impossible time
        if h > 24 or m > 59 or (h * 60 + m) > 1440:
            return BTime("")
    elif maybe_time is None:
        return BTime("")
    elif not isinstance(maybe_time, int):
        squawk(f"PROGRAM ERROR: called time_str({maybe_time=})")
        return BTime("")
    elif isinstance(maybe_time, int):
        # Test for impossible time.
        if not (0 <= maybe_time <= 1440):
            return BTime("")
        h = maybe_time // 60
        m = maybe_time % 60
    # Return 5-digit time string
    return BTime(f"{h:02d}:{m:02d}")


def taglists_by_prefix(unsorted: tuple[TagID]) -> list[list[TagID]]:
    """Get tags sorted into lists by their prefix.

    Return a list of lists of tags, sorted and de-duped. E.g.
        taglists_by_prefix(['wa5','be1','be1', 'wa12','wd15','be1','be10','be9'])
        --> [['be1','be9','be10],['wa5','wa12'],['wd15']]

    Preconditions:
        - tags are either all uppercase or all lowercase
        - all tags are syntactically valid
    """

    # Make a dictionary of all tags keyed by their prefixes
    prefixed_tags = dict(
        zip([tag.prefix for tag in unsorted], [[] for _ in range(0, 100)])
    )
    for tag in unsorted:
        prefixed_tags[tag.prefix].append(tag)
    outerlist = []
    for prefix in sorted(prefixed_tags.keys()):
        outerlist.append(sorted(prefixed_tags[prefix]))
    return outerlist


def tagnums_by_prefix(tags: list[TagID]) -> dict[str, list[int]]:
    """Return a dict of tag prefixes with lists of associated tag numbers."""
    prefixes = {}
    for tag in tags:
        if tag.prefix not in prefixes:
            prefixes[tag.prefix] = []
        prefixes[tag.prefix].append(tag.number)
    for numbers in prefixes.values():
        numbers.sort()
    return prefixes


def splitline(inp: str) -> list[str]:
    """Split input on commas & whitespace into list of non-blank strs."""
    # Start by splitting on commas
    tokens = inp.split(",")
    # Split on whitespace.  This makes a list of lists.
    tokens = [item.split() for item in tokens]
    # Flatten the list of lists into a single list.
    tokens = [item for sublist in tokens for item in sublist]
    # Reject any blank members of the list.
    tokens = [x for x in tokens if x]
    return tokens


def get_version() -> str:
    """Return system version number from changelog.txt.

    If it looks like a git repo, will also try to include a ref from that.
    """
    version_str = ""

    # Git ref
    git_head = os.path.join(".git", "HEAD")
    if not os.path.exists(git_head):
        return "?"
    # .git/HEAD points to the file that contains the version
    with open(git_head, "r", encoding="utf-8") as f:
        ref_path = ""
        for line in f:
            r = re.match(r"^ref: *(refs.*)", line)
            if r:
                ref_path = r.group(1)
        if not ref_path:
            return version_str
    ref_full_path = os.path.join(".git", ref_path)
    if not os.path.exists(ref_full_path):
        return version_str
    git_str = ""
    with open(ref_full_path, "r", encoding="utf-8") as f:
        for line in f:
            if line:
                git_str = line.strip()[:7]
                break
    # get just the feature portion of the git ref_path
    r = re.match(r"^refs/heads/(.*)", ref_path)
    if r:
        git_str = f"{git_str} '{r.group(1)}'"
    # Full version string now
    # version_str = f"{version_str} ({git_str})"
    return git_str


def OLD_plural(count: int) -> str:
    """Get an "s" if count indicates one is needed."""
    if isinstance(count, (int, float)) and count == 1:
        return ""
    else:
        return "s"


def untaint(tainted: str) -> str:
    """Remove any suspicious characters from a possibly tainted string."""
    return "".join(c for c in tainted if c.isprintable())


def plural(count: int, singluar_form: str, plural_form: str = "") -> str:
    """Choose correct singlur/pliral form of a word."""
    if count == 1:
        return singluar_form
    plural_form = plural_form if plural_form else f"{singluar_form}s"
    return plural_form


def line_wrapper(
    input_string, width: int = 80, print_handler=None, print_handler_args=None
) -> list[str]:
    """Split and maybe print input_string to a given width.

    print_handler is an optional print handler function (e.g. print,iprint,squawk)
        if None, then no printing takes place
    print_handler_args is a dict of named arguments for print_handler
        (e.g. {"num_indents":2})
    Returns a list of strings of width width or less.

    Thanks ChatGPT for the basic code and especially for the tricky syntax
    forwarding optional args to the print hander.
    """
    # If no print handler args just make an empty dict.
    print_handler_args = print_handler_args if print_handler_args else {}

    lines = []
    while len(input_string) > width:
        last_space_index = input_string.rfind(" ", 0, width + 1)

        if last_space_index == -1:
            last_space_index = width

        line = input_string[:last_space_index]
        lines.append(line)

        if print_handler:
            print_handler(line, **print_handler_args)

        input_string = input_string[last_space_index + 1 :]

    lines.append(input_string)

    if print_handler:
        print_handler(input_string, **print_handler_args)

    return lines


def calculate_visit_frequencies(
    durations_list: list, category_width: int = 30
) -> collections.Counter:
    durations = []
    for d in durations_list:
        if isinstance(d, int):
            durations.append(d)
        else:
            durations.append(BTime(d).num)
    durations = [d for d in durations if isinstance(d, int)]

    # Make a new list of the durations, categorized
    categorized = [(d // category_width) * category_width for d in durations]

    # Count how many are in each category
    return collections.Counter(categorized)


def calculate_visit_modes(
    durations_list: list, category_width: int = 30
) -> tuple[list[BTime], int]:
    """Calculate the mode(s) for the list of durations.

    The elements in durations can be BTime, str, or int,
    as long as they all evaluate to a BTime.

    For purposes of determining mode, times within one
    block of time of length category_width are
    considered identical.  Defaulit 30 (1/2 hour)

    Returns a list of sorted BTimes().tidy of all the centre times of
    the modes and the number of times it/they occurred.
    """
    freq_list = calculate_visit_frequencies(durations_list, category_width)
    mosts = freq_list.most_common()
    occurences = mosts[0][1]
    modes_numeric = sorted([element for element, count in mosts if count == occurences])
    modes_list = [f"{BTime(x+category_width/2).tidy}" for x in modes_numeric]
    # modes_list = []
    # modes_list = [x.tidy for x in modes_list]

    return modes_list, occurences


def time_distribution(
    times_list: list[str],
    start_time: str = None,
    end_time: str = None,
    category_width: int = 30,
) -> dict[str, int]:
    """Make frequency distribution for list of HH:MM strings."""
    # make a list of categorized times_list
    categorized = [
        str(BTime((BTime(t).num // category_width) * category_width))
        for t in times_list
    ]
    categorized = [t for t in categorized if t]  # remove any nulls
    freq = dict(collections.Counter(categorized))
    start_time = BTime(start_time) if start_time else BTime(min(freq))
    end_time = BTime(end_time) if end_time else BTime(max(freq))
    # make a target list of categories (maybe different from the natural list)
    categories = {
        BTime(t): 0 for t in range(start_time.num, end_time.num + 1, category_width)
    }
    have_overs = have_unders = False
    for cat_start, cat_count in freq.items():
        if cat_start in categories:
            categories[cat_start] = cat_count
        elif cat_start < start_time:
            categories[start_time] += cat_count
            have_unders = True
        elif cat_start > end_time:
            categories[end_time] += cat_count
            have_overs = True
    # if there were items outside our target range, decorate the category names
    # i.e., "12:00" becomes "12:00+"; "01:00" becomes "01:00-"
    categories = {str(BTime(key).tidy): value for key, value in categories.items()}
    if have_unders:
        categories[f"{BTime(start_time).tidy}-"] = categories.pop(
            BTime(start_time).tidy
        )
    if have_overs:
        categories[f"{BTime(end_time).tidy}+"] = categories.pop(BTime(end_time).tidy)
    ##categories = {str(key):value for key,value in categories.items()}
    categories = {str(key): categories[key] for key in sorted(categories.keys())}

    return categories


def random_string(length):
    """Create a random alphaetic string of a given length."""
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def greatest_tagnum(
    prefix: str, regular_tags: list[TagID], oversize_tags: list[TagID]
) -> int:
    """Returns the number of the greatest-numbered tag *available* in a prefix."""
    if not regular_tags and not oversize_tags:
        return None
    # print(f"{prefix=},{len(regular_tags)=},{len(oversize_tags)=}")
    all_tags = list(regular_tags) + list(oversize_tags)
    this_group = [t for t in all_tags if t.prefix == prefix]
    # print(f"{this_group=}")
    if this_group:
        return max([TagID(t).number for t in this_group])
    else:
        return None


def writable_dir(filepath: str) -> bool:
    """Test if filepath is a folder and writeable."""
    if os.path.isdir(filepath):
        if os.access(filepath, os.W_OK):
            return True
        else:
            return False
    else:
        return False
