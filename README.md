# rememberthemilk

access to <https://www.rememberthemilk.com> tasks via their API

## Register your API app

register your Remember the Milk app here: <https://www.rememberthemilk.com/services/api/> and  obtain

* api_key
* shared_secret

store these info in [rememberthemilk.ini](rememberthemilk.ini) (see [rememberthemilk.ini.example](rememberthemilk.ini.example))

## Obtain API token

run [1auth.py](1auth.py) once and add the resulting token to [rememberthemilk.ini](rememberthemilk.ini)

## Playing with the API

[2tasks_completed.py](2tasks_completed.py) analyzes the completed tasks of this year

* HTML table of completed tasks
* count and sums per calender week

[3tasks_overdue.py](3tasks_overdue.py) analyzes the overdue tasks

* HTML table of overdue tasks
* ranked by product of overdue days x priority
