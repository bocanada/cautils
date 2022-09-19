# cautils

cautils is a python library that allows you to run a n/sql query on a Clarity PPM env from the command line.

# Examples

- Creating a new environment
```console
foo@bar:~$ cautils credentials new env-name http://env.url username password
[11:02:41] Saved env env-name -> http://env.url. 🚀
```

- Running a query from a file
```console
foo@bar:~$ cautils query run file ./files/dwh_audit.nsql --env ppm-dev --db Datawarehouse
                                                             query.runner
┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ row_num ┃ table_name               ┃ dw_updated_date     ┃ dw_load_start_date  ┃ dw_load_end_date    ┃ load_duration ┃ table_count ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ 1       │ DWH_CMN_EXCHANGE_RATE    │ 2022-09-11T05:53:06 │ 2022-09-11T05:53:14 │ 2022-09-11T05:53:14 │ 0             │ 0           │
├─────────┼──────────────────────────┼─────────────────────┼─────────────────────┼─────────────────────┼───────────────┼─────────────┤
│ 2       │ DWH_CMN_EXCHANGE_RATE_LN │ 2022-09-11T05:53:06 │ 2022-09-11T05:54:19 │ 2022-09-11T05:54:19 │ 0             │ 0           │
└─────────┴──────────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┴───────────────┴─────────────┘
                                                            Got n records.
```

- Running an existing query on Clarity PPM
```console
foo@bar:~$ cautils query run id cop.admDWHAudit -e ppm-dev -n 2
                                                              cop.admDWHAudit
┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ row_num ┃ table_name               ┃ dw_updated_date     ┃ dw_load_start_date  ┃ dw_load_end_date    ┃ load_duration ┃ table_count ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ 1       │ DWH_CMN_EXCHANGE_RATE    │ 2022-09-11T05:53:06 │ 2022-09-11T05:53:14 │ 2022-09-11T05:53:14 │ 0             │ 0           │
├─────────┼──────────────────────────┼─────────────────────┼─────────────────────┼─────────────────────┼───────────────┼─────────────┤
│ 2       │ DWH_CMN_EXCHANGE_RATE_LN │ 2022-09-11T05:53:06 │ 2022-09-11T05:54:19 │ 2022-09-11T05:54:19 │ 0             │ 0           │
└─────────┴──────────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┴───────────────┴─────────────┘
                                                            Got 2 records.
```

- Getting the result on a different format
```console
foo@bar:~$ cautils run file ./files/dwh_audit.nsql -e ppm-dev -f json --limit 2
```
Yields the result:
```json
{
    "records": [
        {
            "row_num": "1",
            "table_name": "DWH_CMN_EXCHANGE_RATE",
            "dw_updated_date": "2022-09-11T05:53:06",
            "dw_load_start_date": "2022-09-11T05:53:14",
            "dw_load_end_date": "2022-09-11T05:53:14",
            "load_duration": "0",
            "table_count": "0"
        },
        {
            "row_num": "2",
            "table_name": "DWH_CMN_EXCHANGE_RATE_LN",
            "dw_updated_date": "2022-09-11T05:53:06",
            "dw_load_start_date": "2022-09-11T05:54:19",
            "dw_load_end_date": "2022-09-11T05:54:19",
            "load_duration": "0",
            "table_count": "0"
        }
    ]
}
```

- Output the result to a file instead of stdout
```console
foo@bar:~$ cautils query run id cop.dwh_audit -e ppm-dev -f csv -o dwh_audit.csv
```
