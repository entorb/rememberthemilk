# RememberTheMilk

* access to <https://www.rememberthemilk.com> todo lists via their API
* analyze done and pending tasks
* caching to reduce API usage

## Setup

### Register for API usage

register for using the Remember The Milk API here: <https://www.rememberthemilk.com/services/api/> and obtain

* `api_key`
* `shared_secret`

store these info in [rememberthemilk.ini](rememberthemilk.ini) (see [rememberthemilk.ini.example](rememberthemilk.ini.example))

### Install required Python packages

```sh
pip install -r requirements.txt
```

### Obtain API token

run [1auth.py](1auth.py) once and add the resulting `token` to [rememberthemilk.ini](rememberthemilk.ini)

## Playing with the API

### Analyze tasks completed

[2tasks_completed.py](2tasks_completed.py)

* HTML table of completed tasks
* appreciate what you have achieved
* count and sums per calendar week

### Analyze tasks overdue

[3tasks_overdue.py](3tasks_overdue.py)

* HTML table of overdue tasks
* ranked by product of overdue days x priority, to focus on most urgent ones
* display time estimation in minutes to motivate you for solving the minor ones right away

## My RTM lifehacks

see original post at <https://www.rememberthemilk.com/forums/tips/31034/>

I use RTM for several years now, mostly for keeping track of periodic todos, e.g. maintenance, backups, doc appointments, cleaning my home, ... and also for one-timers I tend to postpone.

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

Smart lists that remind me of adding missing date, prio and estimate

* no Date -> `due:never`
* no Prio -> `priority:none`
* no Estimate -> `hasTimeEstimate:false`
* no List -> `list:Inbox`
* no Tag -> `isTagged:false`

### Goal setting and tracking

* I use one list for my goals
* each goal has a prio (= short, medium, far)
* I do not use tags to categorize, but simple prefix in the title, e.g. "JOB", "SPORT"
* to sort the goals by category, I just sort the list by task name (thanks to prefix)
* I usually sort the list by prio
* once a month I check the medium prio goals
* once a quarter I check the low prio goals
* to work towards a goal, I create small repetitive tasks (using after, not every), that use the url field to link to the goal.
