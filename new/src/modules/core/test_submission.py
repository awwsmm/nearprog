from submission import Title
from typing import List, Tuple

def test_title_parsing():
    """Test the title parser with a variety of test cases."""

    test_cases: List[Tuple[str, Title]] = [
        # add newer submissions at top (below this line)

        # ...
        ("Alien Alarms - Polygon Sea", Title("Alien Alarms", "Polygon Sea")),
        ("Stephen Malkmus & The Jicks - (Do Not Feed The) Oyster [freak folk / garage rock]", Title("Stephen Malkmus and the Jicks", "(Do Not Feed The) Oyster", [], "freak folk / garage rock")),
        ("John Cale & Terry Riley - The Hall of Mirrors in the Palace of Versailles", Title("John Cale", "The Hall of Mirrors in the Palace of Versailles", ["Terry Riley"])),
        ("LITE, DÉ DÉ Mouse - Minatsuki Sunset", Title("LITE", "Minatsuki Sunset", ["DÉ DÉ Mouse"])),
        ("Estradasphere - The Bounty Hunter [jazz / avant-garde metal] [2001]", Title("Estradasphere", "The Bounty Hunter", [], "jazz / avant-garde metal", 2001)),
        ("Bicurious - T.O.I [indie / math rock]", Title("Bicurious", "T.O.I", [], "indie / math rock")),
        ("August Burns Red - Internal Cannon", Title("August Burns Red", "Internal Cannon")),
        ("Stellar Circuits - Nocturnal Visitor", Title("Stellar Circuits", "Nocturnal Visitor")),
        ("Al Di Meola - Egyptian Danza [oriental jazz-rock]", Title("Al Di Meola", "Egyptian Danza", [], "oriental jazz-rock")),
        ("Art of Noise - Yebo", Title("Art of Noise", "Yebo")),
        ("Other Animals - Grand Departure", Title("Other Animals", "Grand Departure")),
        ("Biréli Lagrène - Lullaby of Birdland [acoustic jazz guitar]", Title("Biréli Lagrène", "Lullaby of Birdland", [], "acoustic jazz guitar")),
        ("Sunset Mission - Writer's Block", Title("Sunset Mission", "Writer's Block")),
        ("Unc D - Stress Yeeting", Title("Unc D", "Stress Yeeting")),
        ("Nobekazu Takemura - On a Balloon [Experimental Electronic/Ambient]", Title("Nobekazu Takemura", "On a Balloon", [], "Experimental Electronic/Ambient")),
        ("Lama - More Than You Are", Title("Lama", "More Than You Are")),
        # add older submissions at the bottom (above this line)

        # ... below here are weirder cases
        ("Amnoliac Teastone - Timeline [progressive pop, art pop]", Title("Amnoliac Teastone", "Timeline", [], "progressive pop, art pop")),
#       ("Steven Bryant - Concerto for Wind Ensemble: V (UT Wind Ensemble, Jerry Junkin)", Title()), # special case
        ("Melt-Banana - Lost Parts Stinging Me so Cold", Title("Melt-Banana", "Lost Parts Stinging Me so Cold")),
        ("ÄTNA - Won't Stop [Avantgarde/Pop] (2020)", Title("ÄTNA", "Won't Stop", [], "Avantgarde/Pop", 2020)),
        # ... above here are weirder cases

        # documentation test case
        ("Bob Marley feat. Bob Dylan, Bob Barker - We're All Named Bob [rap metal] [1972]", Title("Bob Marley", "We're All Named Bob", ["Bob Dylan", "Bob Barker"], "rap metal", 1972))
    ]

    for actual, expected in test_cases:
        parsed: Title = Title.parse(actual)

        assert parsed.artist == expected.artist
        assert parsed.song_title == expected.song_title
        assert parsed.featuring == expected.featuring
        assert parsed.subgenre == expected.subgenre
        assert parsed.year == expected.year

        assert Title.parse(actual) == expected