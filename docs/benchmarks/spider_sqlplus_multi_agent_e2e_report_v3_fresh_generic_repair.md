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
| Avg total tokens | 1160.3 |
| Avg latency seconds | 8.7563 |

## Details

| ID | SQL+ valid | SQL executable | Match | Latency | Tokens | Question | Error |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
| spider_001 | True | True | True | 5.0825 | 850 | How many singers do we have? |  |
| spider_002 | True | True | True | 6.0328 | 922 | What is the total number of singers? |  |
| spider_003 | True | True | True | 4.2752 | 961 | Show name, country, age for all singers ordered by age from the oldest to the youngest. |  |
| spider_004 | True | True | True | 4.4241 | 947 | What are the names, countries, and ages for every singer in descending order of age? |  |
| spider_005 | True | True | True | 7.2705 | 1110 | What is the average, minimum, and maximum age of all singers from France? |  |
| spider_006 | True | True | True | 11.716 | 1340 | What is the average, minimum, and maximum age for all French singers? |  |
| spider_007 | True | True | True | 3.8373 | 898 | Show the name and the release year of the song by the youngest singer. |  |
| spider_008 | True | True | True | 36.0399 | 2964 | What are the names and release years for all the songs of the youngest singer? |  |
| spider_009 | True | True | True | 5.9062 | 1074 | Show all countries and the number of singers in each country. |  |
| spider_010 | True | True | True | 6.0855 | 1059 | How many singers are from each country? |  |
| spider_011 | True | True | True | 6.1126 | 1089 | What is the maximum capacity and the average of all stadiums ? |  |
| spider_012 | True | True | True | 6.8577 | 1141 | What is the average and maximum capacities for all stadiums ? |  |
| spider_013 | True | True | True | 5.8967 | 965 | What is the name and capacity for the stadium with highest average attendance? |  |
| spider_014 | True | True | True | 5.3121 | 1011 | What is the name and capacity for the stadium with the highest average attendance? |  |
| spider_015 | True | True | True | 6.5112 | 1107 | Show the stadium name and the number of concerts in each stadium. |  |
| spider_016 | True | True | True | 8.0454 | 1317 | For each stadium, how many concerts play there? |  |
| spider_017 | True | True | True | 24.3263 | 1306 | Show the stadium name and capacity with most number of concerts in year 2014 or after. |  |
| spider_018 | True | True | True | 10.3974 | 1225 | What is the name and capacity of the stadium with the most concerts after 2013 ? |  |
| spider_019 | True | True | True | 6.4813 | 957 | Which year has most number of concerts? |  |
| spider_020 | True | True | True | 4.5159 | 963 | What is the year that had the most concerts? |  |
