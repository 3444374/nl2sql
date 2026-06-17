# Spider SQL+ Multi-Agent End-to-End Report

This is an end-to-end generation experiment on the Spider `concert_singer` smoke-test subset.
Gold SQL is used only for offline execution-match evaluation, not for generation or repair.
Generic semantic repair uses question wording, schema columns, SQL+ structure, and execution/parser feedback only.
It does not use Spider case IDs, database-specific hard-coded rules, or gold SQL for repair.

| Metric | Result |
| --- | --- |
| Model | gpt-5-mini |
| Repair rounds | 1 |
| Generic semantic repair | enabled |
| Cases | 20 |
| SQL+ valid | 20/20 |
| SQL executable | 20/20 |
| Execution match | 20/20 |
| Avg total tokens | 1297.5 |
| Avg latency seconds | 11.7367 |

## Details

| ID | SQL+ valid | SQL executable | Match | Latency | Tokens | Question | Error |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
| spider_001 | True | True | True | 3.246 | 523 | How many singers do we have? |  |
| spider_002 | True | True | True | 3.3076 | 608 | What is the total number of singers? |  |
| spider_003 | True | True | True | 18.3993 | 1593 | Show name, country, age for all singers ordered by age from the oldest to the youngest. |  |
| spider_004 | True | True | True | 10.9117 | 1178 | What are the names, countries, and ages for every singer in descending order of age? |  |
| spider_005 | True | True | True | 7.8601 | 713 | What is the average, minimum, and maximum age of all singers from France? |  |
| spider_006 | True | True | True | 5.5654 | 783 | What is the average, minimum, and maximum age for all French singers? |  |
| spider_007 | True | True | True | 22.7107 | 2361 | Show the name and the release year of the song by the youngest singer. |  |
| spider_008 | True | True | True | 27.3429 | 2569 | What are the names and release years for all the songs of the youngest singer? |  |
| spider_009 | True | True | True | 4.6536 | 595 | Show all countries and the number of singers in each country. |  |
| spider_010 | True | True | True | 3.497 | 582 | How many singers are from each country? |  |
| spider_011 | True | True | True | 4.3525 | 654 | What is the maximum capacity and the average of all stadiums ? |  |
| spider_012 | True | True | True | 5.9576 | 659 | What is the average and maximum capacities for all stadiums ? |  |
| spider_013 | True | True | True | 14.0026 | 1705 | What is the name and capacity for the stadium with highest average attendance? |  |
| spider_014 | True | True | True | 17.881 | 2153 | What is the name and capacity for the stadium with the highest average attendance? |  |
| spider_015 | True | True | True | 5.7052 | 780 | Show the stadium name and the number of concerts in each stadium. |  |
| spider_016 | True | True | True | 7.2704 | 780 | For each stadium, how many concerts play there? |  |
| spider_017 | True | True | True | 19.3592 | 2259 | Show the stadium name and capacity with most number of concerts in year 2014 or after. |  |
| spider_018 | True | True | True | 26.4536 | 2447 | What is the name and capacity of the stadium with the most concerts after 2013 ? |  |
| spider_019 | True | True | True | 13.1404 | 1432 | Which year has most number of concerts? |  |
| spider_020 | True | True | True | 13.1172 | 1576 | What is the year that had the most concerts? |  |
