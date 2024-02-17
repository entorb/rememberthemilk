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
* count and sums per calender week

### Analyze tasks overdue

[3tasks_overdue.py](3tasks_overdue.py)

* HTML table of overdue tasks
* ranked by product of overdue days x priority to focus on most urgent ones
* display time estimation in minutes to motivate you for solving the minor ones right away
