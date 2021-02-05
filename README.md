# nearprog

Scripts for the management and data analysis of the [r/nearprog](https://www.reddit.com/r/nearprog) subreddit.

> User privacy is our #1 priority -- no files here include any user-specific information (outside of possibly the mods) or any raw traffic or post data. Additionally, note that we don't have access to any data which isn't already publicly available on Reddit -- PRAW just makes it easier to gather and analyse this information.

---

## automatic traffic scraping (mods only)

Reddit maintains recent traffic stats for each subreddit, at hourly, daily, and monthly intervals.

Unfortunately (from a data analysis perspective), only the past few days of hourly data are maintained.

If more than a few days worth of hourly data are desired, you'll need to set up a `cron` or similar script to scrape data on regular intervals (or do it yourself manually).

### macOS

On macOS, you can configure `launchd` to automatically scrape new traffic stats on regular intervals, using the included `com.nearprog.daily_traffic.plist` configuration file, with the following steps. (Note that this guide assumes your current working directory is the location of this `README.md` file.)

1. In the file `com.nearprog.daily_traffic.plist`, change `<string>awwsmm</string>` to reflect your username on your computer (instead of mine), which you can find with the terminal command `echo $USER`.

2. Similarly, change `<string>/usr/local/bin/python3</string>` to reflect the path to your local installation of `python3` (required). If you have `python3` installed, you can find its installation path with the terminal command `which python3`.

3. Finally, change `<string>/Users/awwsmm/Git/nearprog/scripts/pull_data.py</string>` to reflect the path to your clone of the nearprog Git repo. With these three changes in place, we can set up a recurring task in macOS. You should now run the following commands in your terminal...

4. `$ sudo ln -s $PWD/com.nearprog.daily_traffic.plist /Library/LaunchDaemons/com.nearprog.daily_traffic.plist`

5. `$ sudo chown root:wheel com.nearprog.daily_traffic.plist`

6. `$ sudo launchctl load /Library/LaunchDaemons/com.nearprog.daily_traffic.plist`

You can verify that the script has been loaded correctly with

```
$ sudo launchctl list | grep nearprog
```

As the `.plist` file has `RunAtLoad` set to `true`, the script should immediately run once after the last (`load`) command above is entered. Note that the file will initially be empty while Reddit is queried... give it a few seconds.

The above commands set the `pull_data.py` script to run every day at 10:45am local time, with the arguments `traffic save`. This will query and save the most recent traffic data to the `scripts/data` directory. To cancel this automatically-running job, you can do:

```
$ sudo launchctl remove com.nearprog.daily_traffic.plist
```

and verify that the job has been removed with, again

```
$ sudo launchctl list | grep nearprog
```

#### Related Reading

- https://superuser.com/a/546353/728488
- https://stackoverflow.com/a/133425/2925434
- https://superuser.com/a/126928/728488
- https://osxdaily.com/2011/03/08/remove-an-agent-from-launchd/
