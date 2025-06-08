# RememberTheMilk

* access to <https://www.rememberthemilk.com> todo lists via their API
* analyze done and pending tasks
* caching to reduce API usage

Disclaimer: This code uses the Remember The Milk API but is not endorsed or certified by Remember The Milk.

## Setup

### Register for API usage

register for using the Remember The Milk API here: <https://www.rememberthemilk.com/services/api/> and obtain

* `api_key`
* `shared_secret`

store these info in [rememberthemilk.ini](src/rememberthemilk.ini) (see [rememberthemilk.ini.example](src/rememberthemilk.ini.example))

### Install required Python packages

```sh
pip install -r requirements.txt
```

#### Dev Tools

optionally: ruff and pre-commit

```sh
pip install ruff pre-commit
```

optionally: pytest coverage report

```sh
pip install pytest-cov
pytest --cov
# or
pytest --cov --cov-report=html:coverage_report
```

### Obtain API token

run [auth.py](src/auth.py) once and add the resulting `token` to [rememberthemilk.ini](src/rememberthemilk.ini)

## Playing with the API

### Analyze tasks completed

[tasks_completed.py](src/tasks_completed.py)

* HTML table of completed tasks
* appreciate what you have achieved
* count and sums per calendar week

### Analyze tasks overdue

[tasks_overdue.py](src/tasks_overdue.py)

* HTML table of overdue tasks
* ranked by product of overdue days x priority, to focus on most urgent ones
* display time estimation in minutes to motivate you for solving the minor ones right away

## Streamlit for interactive data analysis

```sh
pip install streamlit watchdog
```

```sh
streamlit run src/app.py
```

## My RTM lifehacks

see original post at <https://www.rememberthemilk.com/forums/tips/31034/>

I use RTM for several years now, mostly for keeping track of periodic todos, e.g. maintenance, backups, doc appointments, cleaning my home, ... and also for one-timers I tend to postpone.

See the [RTM forum](https://www.rememberthemilk.com/forums/) for other tips.

### My RTM setup for tasks

* I use some different lists to group tasks
* I use only few tags, mostly lists instead
* I do not set locations, lists instead
* I set date, prio and estimate to all tasks, especially to periodic tasks, to empower nice smart lists
* for most repetitive tasks I use *after* instead of *each* (e.g. watering the flowers)
* for once-a-year tasks I add notes for the details I tend to forget until its due next time

### Smart list examples

What I love most of RTM are the dynamic smart lists. Here some examples:

* big Projects -> `timeEstimate:">1 hour"`
* high Prio -> `priority:1`
* one-timers -> `isRepeating:false`
* series -> `isRepeating:true AND NOT list:MyListToExclude`
* minor (low handing fruits) -> `dueBefore:"1 week" and timeEstimate:"<15 minutes" AND NOT list:MyListToExclude`
* done 7d (to celebrate what I accomplished) -> `completedWithin:"7 day of today"`
* created more than a week ago -> `NOT addedWithin:"1 week of today"`

Smart lists that remind me of adding missing date, prio and estimate

* no Date -> `due:never AND NOT addedWithin:"1 week of today"`
* no Prio -> `priority:none AND NOT addedWithin:"1 week of today"`
* no Estimate -> `hasTimeEstimate:false AND NOT addedWithin:"1 week of today"`
* no List -> `list:Inbox`
* no Tag -> `isTagged:false`

see <https://www.rememberthemilk.com/help/?ctx=basics.search.advanced>

### Goal setting and tracking

* I use one list for my goals
* each goal has a prio (= short, medium, far)
* I do not use tags to categorize, but simple prefix in the title, e.g. "JOB", "SPORT"
* to sort the goals by category, I just sort the list by task name (thanks to prefix)
* I usually sort the list by prio
* once a month I check the medium prio goals
* once a quarter I check the low prio goals
* to work towards a goal, I create small repetitive tasks (using after, not every), that use the url field to link to the goal.

## SonarQube Code Analysis

At [sonarcloud.io](https://sonarcloud.io/summary/overall?id=entorb_rememberthemilk&branch=main)
