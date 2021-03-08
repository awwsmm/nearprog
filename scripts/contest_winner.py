import sys, argparse
from collections import defaultdict
from statistics import mean, stdev
from random import randrange, random

from tools import reddit

#===============================================================================
#
#  method to determine contest winner(s) despite Reddit's score fuzzing
#
#-------------------------------------------------------------------------------
#
#  run with
#    $ python3 path/to/contest_winner.py <term>
#
#  optional flags (can appear anywhere)
#    -n <N>   number of iterations; 5 by default; minimum 2
#    -m       multi-comment mode: all of the user's comments' scores are summed
#             and then the number of posts is subtracted from that value; in
#             contrast to the default ranking, which is the top comment score
#
#  This script will search the r/nearprog subreddit for a post with a title that
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

def findAndEvaluate (search_term, multi_comment_mode = False, iterations = 5):

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
                if (number >= 0 and number < n_results):
                    submission_index = number
                    break

    else:
        submission_index = 0

    submission = search_result[submission_index]
    print(f"\nFound submission with id \"{submission.id}\" and title:")
    print(f"    \"{submission.title}\"\n")

    scores = defaultdict(list) # {commend_id: [score]} for each comment
    username = {}              # {commend_id: username} for each comment

    # remove mods from the running
    mods = ["MysteriousGear", "_awwsmm", "yyogo"]

    connection = reddit.connect()
    for i in range(iterations):
        print(f"Collecting data ({i+1}/{iterations})...", end="\r")

        # pull the submission in every loop so Reddit refreshes the fuzzed votes
        contest = connection.submission(url=submission.url)

        # remove second-level comments and "More Comments" messages
        contest.comments.replace_more(limit=None)

        # loop over all top-level comments
        for comment in contest.comments:
            author = str(comment.author)
            if (author not in mods):
                id = comment.permalink.split('/')[-2]
                username.setdefault(id, author)
                scores[id].append(comment.score)

    # clear the "Collecting data" line
    print("                                                         ", end="\r")

    def average_and_stdev(permalink_and_values):
        return (permalink_and_values[0], (mean(permalink_and_values[1]), stdev(permalink_and_values[1])))

    # {permalink: (average, stdev)} for each comment -- "defuzzed"
    tuples = dict(map(average_and_stdev, scores.items()))

    # if using multi-comment mode, scores are grouped by user
    if multi_comment_mode:
        user_scores = defaultdict(list) # {username: [(avg, stdev)]} for each participant

        # collect all (avg, stdev) upvote tuples for each user
        for cid in username.keys():
            user = username[cid]
            user_scores[user].append(tuples[cid])

        final_scores = {} # {username: overall_score} for each participant

        # calculate overall score for each user
        for user, scores in user_scores.items():
            n_submissions = len(scores)
            total_upvotes = sum(map(lambda x: x[0], scores))
            total_score = total_upvotes - n_submissions
            final_scores.setdefault(user, (n_submissions, total_upvotes, total_score))

        # sort users by final_score, then randomly (if rounded scores are equal)
        ranked = sorted(final_scores.items(), key = lambda x: (round(x[1][2]), random()), reverse = True)

        # print out the rankings
        rank = 1
        for user, (n, upvotes, score) in ranked:
            print(f"  {rank:2d} @ {score:2.2f} (== {upvotes:2.2f} - {n:2d}) | {user}")
            rank += 1

    # single-comment ("normal") mode
    else:
        # sort comments by rounding (mean+stdev) value, then randomly (if rounded scores are equal)
        ranked = sorted(tuples.items(), key = lambda x: (round(x[1][0] + x[1][1]), random()), reverse = True)

        # print out the rankings
        rank = 1
        for comment_id, (avg, dev) in ranked:
            print(f"  {rank:2d} @ {avg:.2f} ± {dev:.2f} | {submission.url}{comment_id}")
            rank += 1

# command-line testing
if (len(sys.argv) > 1 and "contest_winner.py" in sys.argv[0]):

    desc = "Method to determine contest winner(s) despite Reddit's score fuzzing."
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("term",
        help="term or phrase to search for in contest post title")

    parser.add_argument('-n', dest="num", type=int, default=5,
        help="number of iterations: default 5, minimum 2")

    parser.add_argument('-m', dest="multi", action='store_true',
        help="enable multi-comment mode (see comments in source)")

    args = parser.parse_args()
    findAndEvaluate(args.term, args.multi, max(2, args.num))