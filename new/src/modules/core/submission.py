from collections.abc import Callable
import json
import praw.models
import re
from typing import Any, Iterator, List, Optional

class Submission:
    """A Submission can be a PRAW Submission or any other kind of Submission representation."""

    def __init__(self, timestamp: int, flair: str = 'N/A', raw_title: str = 'N/A') -> None:
        """Create a Submission object by directly defining its fields."""

        self.timestamp = timestamp
        self.flair = flair
        self.raw_title = raw_title

    __processed = False

    def process(self):
        """Parse this Submission's title, extracting artist, song, subgenre, and other information."""

        if (self.is_song()):
            parsed: Title = Title.parse(self.raw_title)

            self.artist = parsed.artist
            self.song_title = parsed.song_title
            self.featuring = parsed.featuring
            self.subgenre = parsed.subgenre
            self.year = parsed.year

            self.__processed = True

    @staticmethod
    def wrap(submission: praw.models.Submission) -> None:
        """Create a Submission object from a PRAW Submission."""

        return Submission(int(submission.created_utc), submission.link_flair_text, submission.title)

    def is_song(self) -> bool:
        """Returns True if this Submission is a song (and not a contest, etc.)."""

        return ((self.flair != 'Discussion') and
                (self.flair != 'Contest') and
                (self.flair != 'Announcement') and
                ('[Discussion]' not in self.raw_title))

    def as_JSON(self) -> str:
        if (self.is_song()):
            if (not self.__processed):
                self.process()
            return (
                '{'
                f'\n  "timestamp"  : {self.timestamp},'
                f'\n  "flair"      : {json.dumps(self.flair, ensure_ascii=False)},'
                f'\n  "raw_title"  : {json.dumps(self.raw_title, ensure_ascii=False)},'
                f'\n  "artist"     : {json.dumps(self.artist, ensure_ascii=False)},'
                f'\n  "song_title" : {json.dumps(self.song_title, ensure_ascii=False)},'
                f'\n  "featuring"  : {json.dumps(self.featuring, ensure_ascii=False)},'
                f'\n  "subgenre"   : {json.dumps(self.subgenre, ensure_ascii=False)},'
                f'\n  "year"       : {self.year or "null"}'
                '\n}'
            )
        else:
            return (
                '{'
                f'\n  "timestamp"  : {self.timestamp},'
                f'\n  "flair"      : {json.dumps(self.flair, ensure_ascii=False)},'
                f'\n  "raw_title"  : {json.dumps(self.raw_title, ensure_ascii=False)}'
                '\n}'
            )

class Title:
    """Helper class for parsing Submission titles.
    
    A (song) Submission title looks like

        Bob Marley feat. Bob Dylan, Bob Barker - We're All Named Bob [rap metal] [1972]
        |-- (1) -|       |------- (2) -------|   |------ (3) ------| |-- (4) --| |(5)-|

    1. Artist name (mandatory)
    2. Additional / featured artist name(s) (optional)
    3. Song name (mandatory)
    4. Subgenre (optional)
    5. Year (optional)

    ...but we also need to handle cases where users accidentally use parentheses () instead of
    square brackets [] for tags after the song name. Additionally, we need to parse a variety
    of "additional artists" formats, including things like:

    - Eminem ft. Juice WRLD
    - Korn feat. Ice Cube
    - Flight Facilities feat. Broods, Reggie Watts, and Saro
    - David Bowie feat. Maynard James Keenan and John Frusciante
    - Dave Grohl, Trent Reznor, Josh Homme
    - Yuki Koshimoto & Liam Tillyer
    - Yussef Dayes X Alfa Mist
    - Jeremy Flower with Carla Kihlstedt

    ...but we need to make exceptions for compound single-artist names, like

    - Jess & the Ancient Ones
    - Black Country, New Road
    - King Gizzard And The Lizard Wizard
    - Simon and Garfunkel

    All of this parsing / interpretation is handled in this class.
    """

    def __init__(self, artist: str, song_title: str, featuring: List[str] = [], subgenre: Optional[str] = None, year: Optional[str] = None) -> None:
        self.artist = artist
        self.song_title = song_title
        self.featuring = featuring
        self.subgenre = subgenre
        self.year = year

    def __eq__(self, obj: Any) -> bool:
        return (isinstance(obj, Title)
            and obj.artist == self.artist
            and obj.song_title == self.song_title
            and obj.featuring == self.featuring
            and obj.subgenre == self.subgenre
            and obj.year == self.year
        )

    @staticmethod
    def parse(raw: str) -> None:

        # At this point, we have a raw title like
        #     Bob Marley feat. Bob Dylan, Bob Barker - We're All Named Bob [rap metal] [1972]
        # ...with no sections parsed / extracted at all.

        # STEP 1: First, we split the title on the mandatory " - " separator.

        re_dash = r"\s+[—-]+\s+"

        rawartists_rawsong = re.split(re_dash, raw)

        if len(rawartists_rawsong) < 2:
            raise ValueError(f'Error parsing title: missing mandatory " - " separator between artist(s) and song:\n  > {raw}')
        
        raw_artists = rawartists_rawsong[0]
        raw_song = rawartists_rawsong[1]

        # At this point, we have
        #     raw_artists: "Bob Marley feat. Bob Dylan, Bob Barker"
        #     raw_song:    "We're All Named Bob [rap metal] [1972]"

        # STEP 2: Next, we split the raw_artist into the primary (first) and secondary (additional) artists

        re_feat = r"\s*feat\.?\s*|\s*ft\.?\s*"
        re_comma = r"\s*,\s*"
        re_and = r'\s*&\s*'

        artists = re.split(f'{re_feat}|{re_comma}|{re_and}', raw_artists)

        # "paste together" compound artist names which should not have been separated
        compound_artists = [
            (["Stephen Malkmus", "The Jicks"], "Stephen Malkmus and the Jicks")
        ]

        for separate, together in compound_artists:
            if all(map(lambda pair: pair[0] == pair[1], zip(separate, artists))):
                artists = artists[len(separate):]
                artists.insert(0, together)
                break

        artist = artists[0]
        featuring = artists[1:]

        # At this point, we have
        #     artist:             "Bob Marley"
        #     featuring: ["Bob Dylan", "Bob Barker"]
        #     raw_song:           "We're All Named Bob [rap metal] [1972]"

        # STEP 3: Lastly, we parse any [tags] from raw_song and categorise the tags

        re_tag = r"\[([^\[\]]+)\]"

        tags = re.compile(re_tag).findall(raw_song)

        # print(f'"{artist}"')
        # print(", ".join(featuring))
        # print(", ".join(tags))

        # if there are any tags at all...
        if len(tags) > 0:

            # ...then the final title is everything before the first tag
            song_title = raw_song.split(f'[{tags[0]}]')[0].strip()

            # if any tag matches a year 1900-2021, consider that a 'year' tag

            re_year = re.compile(r'19[0-9]{2}|20[01][0-9]|202[01]')
            years = list(filter(lambda tag: re_year.match(tag), tags))

            if len(years) > 0:
                year = int(years[0])
                tags.remove(years[0])
            else:
                year = None
            
            # if there is any remaining tag, it must be the subgenre

            if len(tags) > 0:
                subgenre = str(tags[0])
            else:
                subgenre = None

            # print(f'"{song_title}"')
            # print(f'"{year}"')
            # print(f'"{subgenre}"')

            return Title(artist, song_title, featuring, subgenre, year)

        # if there are no tags, the raw_song is the song_title and the subgenre and year are None
        else:
            return Title(artist, raw_song, featuring, None, None)

class Fetcher:
    """Fetches up to 'limit' Submissions, posted 'since' the given UTC UNIX timestamp."""

    def __init__(self, fetcher: Callable[[int], Iterator[Submission]]):
        self.fetcher = fetcher

    def fetch(self, since: int, limit: int) -> Iterator[Submission]:
        return filter(lambda s: s.timestamp >= since, self.fetcher(limit))
