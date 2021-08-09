from submission import Title

def test_title_parsing():
    """Test the title parser with a variety of test cases."""

    test_cases = [
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
        # ...

        # add older submissions at the bottom (above this line)        
        ("Bob Marley feat. Bob Dylan, Bob Barker - We're All Named Bob [rap metal] [1972]", Title("Bob Marley", "We're All Named Bob", ["Bob Dylan", "Bob Barker"], "rap metal", 1972))
    ]

    for actual, expected in test_cases:
        assert Title.parse(actual) == expected