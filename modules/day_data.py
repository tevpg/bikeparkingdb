"""TagTracker by Julias Hocking.

DayData class for tagtracker.

DayData holds all the state information about a single day at the bike
parking service. It is a generic structure that knows nothing that is specific
to a single source type.


General flow:
- a source-specific reader populates a DayData with the day summary (if present)
  and the visits (if present)
- use DayData (& Visit & Block) methods to calculate the day summary info,
  and the Block info
- at which point the DayData object is complete (& ready to write to the database)


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

import modules.constants as k
from modules.tt_time import BTime

## import modules.tt_util as ut


class DayData:
    """One day of bike parking data.

    This is made up of summary information about the day, and if
    there is information about visits, includes the visits and the
    distribution of visits through blocks of time in the day.

    These structures should have a high degree of local match to the
    bikeparkingdatabase structure.
    """

    def __init__(self) -> None:
        """Initialize blank."""
        self.org_code = ""
        self.site_code = ""
        self.date = ""

        self.opening_time = BTime("")
        self.closing_time = BTime("")
        self.registrations = 0

        self.visits:list[Visit] = []
        self.blocks:dict[BTime:Block] = {}

    # pylint:disable-next=pointless-string-statement
    '''
    def lint_check(self, strict_datetimes: bool = False) -> list[str]:
        """Generate a list of logic error messages for DayData object.

        If no errors found returns []
        If errors, returns list of error message strings.

        Check for:
        - bikes checked out but not in
        - checked out before in
        - multiple check-ins, multiple check-outs
        - unrecognized tag in check-ins & check-outs
        - poorly formed Tag
        - poorly formed Time
        - use of a tag that is retired (to do later)
        If strict_datetimes then checks:
        - valet date, opening and closing are well-formed
        - valet opening time < closing time
        """

        def bad_times(timesdict: dict[str, BTime], listname: str) -> list[str]:
            """Get list of errors about mal-formed time values in timesdict."""
            msgs = []
            for key, atime in timesdict.items():
                if not isinstance(atime, BTime) or not atime:
                    msgs.append(
                        f"Bad time '{atime}' in " f"{listname} with key '{key}'"
                    )
            return msgs

        errors = []
        # Look for missing or bad times and dates
        if strict_datetimes:
            if not self.date or ut.date_str(self.date) != self.date:
                errors.append(f"Bad or missing date {self.date}")
            if not self.opening_time or not isinstance(self.opening_time, BTime):
                errors.append(f"Bad or missing opening time {self.opening_time}")
            if not self.closing_time or not isinstance(self.closing_time, BTime):
                errors.append(f"Bad or missing closing time {self.closing_time}")
            if (
                self.opening_time
                and self.closing_time
                and self.opening_time >= self.closing_time
            ):
                errors.append(
                    f"Opening time '{self.opening_time}' is not "
                    f"earlier then closing time '{self.closing_time}'"
                )
        # Look for poorly formed times and tags
        errors += bad_tags(self.regular, "regular-tags")
        errors += bad_tags(self.oversize, "oversize-tags")
        errors += bad_tags(self.bikes_in.keys(), "bikes-checked-in")
        errors += bad_tags(self.bikes_out.keys(), "bikes-checked-out")
        errors += bad_times(self.bikes_in, "bikes-checked-in")
        errors += bad_times(self.bikes_out, "bikes-checked-out")
        # Look for duplicates in regular and oversize tags lists
        if len(self.regular | self.oversize) != len(self.regular) + len(self.oversize):
            errors.append("Size mismatch between regular+oversize tags and their union")
        # Look for bike checked out but not in, or check-in later than check-out
        for tag, atime in self.bikes_out.items():
            if tag not in self.bikes_in:
                errors.append(f"Bike {tag} checked in but not out")
            elif atime < self.bikes_in[tag]:
                errors.append(f"Bike {tag} check-out earlier than check-in")
        # Bikes that are not in the list of allowed bikes
        _allowed_tags = self.regular | self.oversize
        _used_tags = self.bikes_in.keys() | self.bikes_out.keys()
        for tag in _used_tags:
            if tag not in _allowed_tags:
                errors.append(f"Tag {tag} not in use (not regular nor oversized)")
            if tag in self.retired:
                errors.append(f"Tag {tag} is marked as retired")
        return errors
    '''

    def earliest_event(self) -> BTime:
        """Return the earliest event of the day as HH:MM (or "" if none)."""
        events = [x.time_in for x in self.visits] + [x.time_out for x in self.visits]
        # Find earliest event of the day
        return min(events,default="")

    def latest_event(self, as_of_when: BTime | int | None = None) -> BTime:
        """Return the latest event of the day at or before as_of_when.

        If no events in the time period, return "".
        If as_of_when is blank or None, then this will use the whole day.
        """
        if not as_of_when:
            as_of_when = BTime("24:00")
        else:
            as_of_when = BTime(as_of_when)
            if not as_of_when:
                return ""
        events = [x.time_in for x in self.visits] + [x.time_out for x in self.visits]
        # Find latest event of the day
        return max(events,default="")

    def num_later_events(self, after_when: BTime | int | None = None) -> int:
        """Get count of events that are later than after_when."""
        if not after_when:
            after_when = BTime("now")
        else:
            after_when = BTime(after_when)
            if not after_when:
                return ""
        events = [x.time_in for x in self.visits] + [x.time_out for x in self.visits]
        events = [x for x in events if x > after_when]
        return len(events)

    def _get_timeblock_starts(self, as_of_when: str) -> list[BTime]:
        """Build a list of timeblocks from beg of day until as_of_when.

        Latest block of the day will be the latest timeblock that
        had any transactions at or before as_of_when.
        """

        as_of_when = as_of_when if as_of_when else "now"
        as_of_when = BTime(as_of_when)
        # Make list of transactions <= as_of_when
        events = [x.time_in for x in self.visits] + [x.time_out for x in self.visits]
        events = [x for x in events if x <= as_of_when]
        # Anything?
        if not events:
            return []
        # Find earliest and latest block of the day
        min_block_min:BTime = Block.block_start(min(events))
        max_block_min:BTime = Block.block_start(max(events))
        # Create list of timeblock starts for the the whole day.
        timeblocks = []
        for t in range(
            min_block_min, max_block_min + k.BLOCK_DURATION, k.BLOCK_DURATION
        ):
            timeblocks.append(BTime(t))
        return timeblocks

    def calc_blocks(self, as_of_when: str = None) -> dict[BTime, object]:
        """Create a dictionary of Blocks {start:Block} for whole day."""
        if not as_of_when:
            as_of_when = self.latest_event("24:00")
            if as_of_when < self.closing_time:
                as_of_when = self.closing_time
        as_of_when = BTime(as_of_when)
        # Create dict with all the blocktimes as keys (None as values)
        blocktimes = self._get_timeblock_starts(as_of_when=as_of_when)
        if not blocktimes:
            return {}
        blocks = {}
        for t in blocktimes:
            blocks[t] = Block(t)
        # latest_time is the end of the latest block that interests us
        latest_time = Block.block_end(max(blocktimes))
        # Load check-ins & check-outs into the blocks to which they belong
        # This has to happen carefully, in the order in which they occurred,
        # thus processing as Events rather than reading check_ins & _outs
        # FIXME : below here need to rewrite; but only care about totals not list of bikes in
        events = Event.calc_events(day, as_of_when=as_of_when)
        for evtime in sorted(events.keys()):
            ev: Event
            ev = events[evtime]
            bstart = block_start(ev.event_time)
            blk: Block
            blk = blocks[bstart]
            if ev.event_time > latest_time:
                continue
            blk.ins_list += ev.bikes_in
            blk.outs_list += ev.bikes_out
            # Watch for highwater-mark *within* the block
            if ev.num_here_total > blk.max_here:
                blk.max_here = ev.num_here_total
                blk.max_here_list = ev.bikes_here
        # For each block, see what bikes are present at the end of the block
        # Use a set to be able to find the set difference (ie list that's here)
        here_set = set()
        for blk in blocks.values():
            blk.num_ins = len(blk.ins_list)
            blk.num_outs = len(blk.outs_list)
            here_set = (here_set | set(blk.ins_list)) - set(blk.outs_list)
            blk.here_list = here_set
            blk.num_here = len(here_set)
        # Calculate the ins/outs and bikes here categorized by regular/oversize.
        for blk in blocks.values():
            for tag in blk.ins_list:
                if tag in day.regular:
                    blk.num_ins_regular += 1
                elif tag in day.oversize:
                    blk.num_ins_oversize += 1
            for tag in blk.outs_list:
                if tag in day.regular:
                    blk.num_outs_regular += 1
                elif tag in day.oversize:
                    blk.num_outs_oversize += 1
            for tag in blk.here_list:
                if tag in day.regular:
                    blk.num_here_regular += 1
                elif tag in day.oversize:
                    blk.num_here_oversize += 1
            # Categorize the tag lists & counts at peak within the block
            for tag in blk.max_here_list:
                if tag in day.regular:
                    blk.max_here_regular += 1
                elif tag in day.oversize:
                    blk.max_here_oversize += 1

        return blocks


    def calc_summaries(self):
        """Calculate/check day summaries from visit info (if available)."""
        # FIXME



class Visit:
    """All needed data about a single visit."""
    def __init__(self) -> None:
        self.time_in = ""
        self.time_out = ""
        self.duration = 0
        self.bike_id = ""
        self.bike_type = ""

class Block:
    """Summary of what toook place in a single block of time."""

    def __init__(self, start_time:BTime|int) -> None:
        self.time_start = BTime(start_time)
        self.time_end = ""
        self.regular_at_start = 0
        self.oversize_at_start = 0
        self.bikes_at_start = 0
        self.regular_at_end = 0
        self.oversize_at_end = 0
        self.bikes_at_end = 0
        self.most_full = 0
        self.most_full_time = ""

    @staticmethod
    def block_start(atime: int|str) -> BTime:
        """Return the start time of the block that contains time 'atime'.

        'atime' can be minutes since midnight or HHMM.
        """
        # Get time in minutes
        atime = BTime(atime)
        if atime is None:
            return ""
        # which block of time does it fall in?
        block_start_min = (atime.num // k.BLOCK_DURATION) * k.BLOCK_DURATION
        return BTime(block_start_min)

    @classmethod
    def block_end(cls,atime: int|str) -> BTime:
        """Return the last minute of the timeblock that contains time 'atime'.

        'atime' can be minutes since midnight or HHMM.
        """
        # Get block start
        start = cls.block_start(atime)
        # Calculate block end
        end = start.num + k.BLOCK_DURATION - 1
        # Return as minutes or HHMM
        return BTime(end)
