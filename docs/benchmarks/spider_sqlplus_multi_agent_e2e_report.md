# Spider SQL+ Multi-Agent End-to-End Report

This is an end-to-end generation experiment on the Spider `concert_singer` smoke-test subset.
Gold SQL is used only for offline execution-match evaluation, not for generation or repair.

| Metric | Result |
| --- | --- |
| Model | gpt-5-mini |
| Repair rounds | 1 |
| Cases | 20 |
| SQL+ valid | 3/20 |
| SQL executable | 2/20 |
| Execution match | 2/20 |
| Avg total tokens | 1229.05 |
| Avg latency seconds | 18.412 |

## Details

| ID | SQL+ valid | SQL executable | Match | Latency | Tokens | Question | Error |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
| spider_001 | False | False | False | 17.6993 | 1229 | How many singers do we have? | SQL+ output must start with FROM and use SQL+ step syntax, not standard SQL. |
| spider_002 | False | False | False | 15.8976 | 1377 | What is the total number of singers? | SQL+ output must start with FROM and use SQL+ step syntax, not standard SQL. |
| spider_003 | False | False | False | 4.7254 | 506 | Show name, country, age for all singers ordered by age from the oldest to the youngest. | SQL+ output must start with FROM and use SQL+ step syntax, not standard SQL. |
| spider_004 | False | False | False | 7.295 | 785 | What are the names, countries, and ages for every singer in descending order of age? | SQL+ output must start with FROM and use SQL+ step syntax, not standard SQL. |
| spider_005 | False | False | False | 6.6768 | 714 | What is the average, minimum, and maximum age of all singers from France? | SQL+ output must start with FROM and use SQL+ step syntax, not standard SQL. |
| spider_006 | False | False | False | 6.6612 | 755 | What is the average, minimum, and maximum age for all French singers? | SQL+ output must start with FROM and use SQL+ step syntax, not standard SQL. |
| spider_007 | False | False | False | 5.8845 | 671 | Show the name and the release year of the song by the youngest singer. | SQL+ output must start with FROM and use SQL+ step syntax, not standard SQL. |
| spider_008 | False | False | False | 22.3097 | 2078 | What are the names and release years for all the songs of the youngest singer? | SQL+ output must start with FROM and use SQL+ step syntax, not standard SQL. |
| spider_009 | False | False | False | 11.3162 | 1123 | Show all countries and the number of singers in each country. | SQL+ output must start with FROM and use SQL+ step syntax, not standard SQL. |
| spider_010 | False | False | False | 14.898 | 1568 | How many singers are from each country? | SQL+ output must start with FROM and use SQL+ step syntax, not standard SQL. |
| spider_011 | False | False | False | 71.3492 | 1683 | What is the maximum capacity and the average of all stadiums ? | SQL+ output must start with FROM and use SQL+ step syntax, not standard SQL. |
| spider_012 | True | True | True | 5.4836 | 676 | What is the average and maximum capacities for all stadiums ? |  |
| spider_013 | True | True | True | 10.5167 | 1097 | What is the name and capacity for the stadium with highest average attendance? |  |
| spider_014 | False | False | False | 8.2653 | 911 | What is the name and capacity for the stadium with the highest average attendance? | SQL+ output must start with FROM and use SQL+ step syntax, not standard SQL. |
| spider_015 | False | False | False | 74.2604 | 1595 | Show the stadium name and the number of concerts in each stadium. | SQL+ output must start with FROM and use SQL+ step syntax, not standard SQL. |
| spider_016 | False | False | False | 10.1878 | 982 | For each stadium, how many concerts play there? | SQL+ output must start with FROM and use SQL+ step syntax, not standard SQL. |
| spider_017 | False | False | False | 23.6628 | 2105 | Show the stadium name and capacity with most number of concerts in year 2014 or after. | SQL+ output must start with FROM and use SQL+ step syntax, not standard SQL. |
| spider_018 | False | False | False | 17.2411 | 1671 | What is the name and capacity of the stadium with the most concerts after 2013 ? | SQL+ output must start with FROM and use SQL+ step syntax, not standard SQL. |
| spider_019 | True | False | False | 15.9415 | 1458 | Which year has most number of concerts? | no such column: Year |
| spider_020 | False | False | False | 17.9686 | 1597 | What is the year that had the most concerts? | SQL+ output must start with FROM and use SQL+ step syntax, not standard SQL. |
