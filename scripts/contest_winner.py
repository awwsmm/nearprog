import sys
from collections import defaultdict
from statistics import mean, stdev

from tools import reddit

#===============================================================================
#
#  method to determine contest winner(s) despite Reddit's score fuzzing
#
#-------------------------------------------------------------------------------
#
#  run with
#    $ python3 path/to/contest_winner.py <term> [N]
#
#  this script will search the r/nearprog subreddit for a post with a title that
#  matches the search <term>, which is mandatory. Note that you can enter
#  multiple words as a search term by "surrounding them with quotes".
#
#  If only a single post is found which matches the search term, the script will
#  continue running by itself. If none are found, it will quit. If multiple
#  matching posts are found, the script will ask for user clarification.
#
#  The number of iterations N is optional and set to 5 by default, with an
#  enforced minimum of 2 iterations. 10-100 iterations are suggested.
#
#===============================================================================

def findAndEvaluate (search_term, iterations = 5):

    if (iterations < 2):
        print(f"  Note: 'iterations' must be >= 2 at minimum. Set to 2.")
        iterations = 2

    search_result = list(reddit.nearprog().search(search_term))
    n_results = len(search_result)

    if (n_results < 1):
        print(f"\nNo posts found matching \"{search_term}\"")
        print(f"    Try again with a different search term.")
        sys.exit(1)

    elif (n_results > 1):
        print(f"\nMultiple posts found matching \"{search_term}\"")
        print(f"    Please choose one by entering a number (q to quit):")
        for index in range(n_results):
            submission = search_result[index]
            print(f"      [{index}]: \"{submission.title}\"")
        print("------------------------------------------------------------")
        decision = ''
        while (True):
            decision = input("     > ")
            if (decision.lower() == 'q'):
                sys.exit(0)
            elif (decision.isdigit()):
                number = int(decision)
                if (number > 0 and number < n_results):
                    submission_index = number
                    break

    else:
        submission_index = 0

    submission = search_result[submission_index]
    print(f"\nFound submission with id \"{submission.id}\" and title:")
    print(f"    \"{submission.title}\"\n")

    # info is a dictionary of (permalink, [comment score]) values
    # where [comment score] is an array
    info = defaultdict(list)

    print(f"Collecting data (x{iterations})...\n")
    for i in range(iterations):
        print(f"Loop {i+1} / {iterations}")

        # pull the submission in every loop so Reddit refreshes the fuzzed votes
        contest = reddit.connect().submission(url=submission.url)

        # remove second-level comments and "More Comments" messages
        contest.comments.replace_more(limit=None)

        # loop over all top-level comments
        for comment in contest.comments:
            id = comment.permalink
            info[id].append(comment.score)

    # get average
    print("")
    def average_and_stdev(permalink_and_values):
        return (permalink_and_values[0], (mean(permalink_and_values[1]), stdev(permalink_and_values[1])))

    # get values as list and sort by mean
    tuples = list(map(average_and_stdev, info.items()))
    ranked = sorted(tuples, key = lambda x: x[1][0], reverse = True)

    for link, (avg, dev) in ranked:
        print(f"{avg:.2f} w/ {dev:.2f} => {link}")

# to do: add functionality to automatically determine winner,
#        and randomly choose a winner if there is a tie

# command-line testing
if (len(sys.argv) > 1 and "contest_winner.py" in sys.argv[0]):

    # set limit on number of posts to fetch / parse
    if (len(sys.argv) == 3 and sys.argv[2].isdigit()):
        findAndEvaluate(sys.argv[1], int(sys.argv[2]))
    else:
        findAndEvaluate(sys.argv[1])
