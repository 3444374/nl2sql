# Spider Small Smoke Test Report

| Metric | Result |
| --- | --- |
| Cases | 20 |
| Databases | concert_singer |
| SQL+ valid | 20/20 |
| SQL executable | 20/20 |
| Execution match | 20/20 |

## Details

| ID | DB | Match | Question | SQL+ |
| --- | --- | --- | --- | --- |
| spider_001 | concert_singer | True | How many singers do we have? | FROM singer<br>\| AGG count(*) AS count_value |
| spider_002 | concert_singer | True | What is the total number of singers? | FROM singer<br>\| AGG count(*) AS count_value |
| spider_003 | concert_singer | True | Show name, country, age for all singers ordered by age from the oldest to the youngest. | FROM singer<br>\| SELECT name , country , age<br>\| ORDER age DESC |
| spider_004 | concert_singer | True | What are the names, countries, and ages for every singer in descending order of age? | FROM singer<br>\| SELECT name , country , age<br>\| ORDER age DESC |
| spider_005 | concert_singer | True | What is the average, minimum, and maximum age of all singers from France? | FROM singer<br>\| WHERE country = 'France'<br>\| AGG avg(age) AS avg_value, min(age) AS min_value_2, max(age) AS max_value_3 |
| spider_006 | concert_singer | True | What is the average, minimum, and maximum age for all French singers? | FROM singer<br>\| WHERE country = 'France'<br>\| AGG avg(age) AS avg_value, min(age) AS min_value_2, max(age) AS max_value_3 |
| spider_007 | concert_singer | True | Show the name and the release year of the song by the youngest singer. | FROM singer<br>\| SELECT song_name , song_release_year<br>\| ORDER age<br>\| LIMIT 1 |
| spider_008 | concert_singer | True | What are the names and release years for all the songs of the youngest singer? | FROM singer<br>\| SELECT song_name , song_release_year<br>\| ORDER age<br>\| LIMIT 1 |
| spider_009 | concert_singer | True | Show all countries and the number of singers in each country. | FROM singer<br>\| GROUP country<br>\| AGG country, count(*) AS count_value_2 |
| spider_010 | concert_singer | True | How many singers are from each country? | FROM singer<br>\| GROUP country<br>\| AGG country, count(*) AS count_value_2 |
| spider_011 | concert_singer | True | What is the maximum capacity and the average of all stadiums ? | FROM stadium<br>\| AGG max(capacity) AS max_value, average |
| spider_012 | concert_singer | True | What is the average and maximum capacities for all stadiums ? | FROM stadium<br>\| AGG avg(capacity) AS avg_value, max(capacity) AS max_value_2 |
| spider_013 | concert_singer | True | What is the name and capacity for the stadium with highest average attendance? | FROM stadium<br>\| SELECT name , capacity<br>\| ORDER average DESC<br>\| LIMIT 1 |
| spider_014 | concert_singer | True | What is the name and capacity for the stadium with the highest average attendance? | FROM stadium<br>\| SELECT name , capacity<br>\| ORDER average DESC<br>\| LIMIT 1 |
| spider_015 | concert_singer | True | Show the stadium name and the number of concerts in each stadium. | FROM concert AS T1<br>\| JOIN stadium AS T2 ON T1.stadium_id = T2.stadium_id<br>\| GROUP T1.stadium_id<br>\| AGG T2.name, count(*) AS count_value_2 |
| spider_016 | concert_singer | True | For each stadium, how many concerts play there? | FROM concert AS T1<br>\| JOIN stadium AS T2 ON T1.stadium_id = T2.stadium_id<br>\| GROUP T1.stadium_id<br>\| AGG T2.name, count(*) AS count_value_2 |
| spider_017 | concert_singer | True | Show the stadium name and capacity with most number of concerts in year 2014 or after. | FROM concert AS T1<br>\| JOIN stadium AS T2 ON T1.stadium_id = T2.stadium_id<br>\| WHERE T1.year >= 2014<br>\| GROUP T2.stadium_id<br>\| SELECT T2.name , T2.capacity<br>\| ORDER count(*) DESC<br>\| LIMIT 1 |
| spider_018 | concert_singer | True | What is the name and capacity of the stadium with the most concerts after 2013 ? | FROM concert as t1<br>\| JOIN stadium as t2 on t1.stadium_id = t2.stadium_id<br>\| WHERE t1.year > 2013<br>\| GROUP t2.stadium_id<br>\| SELECT t2.name , t2.capacity<br>\| ORDER count(*) desc<br>\| LIMIT 1 |
| spider_019 | concert_singer | True | Which year has most number of concerts? | FROM concert<br>\| GROUP YEAR<br>\| SELECT YEAR<br>\| ORDER count(*) DESC<br>\| LIMIT 1 |
| spider_020 | concert_singer | True | What is the year that had the most concerts? | FROM concert<br>\| GROUP YEAR<br>\| SELECT YEAR<br>\| ORDER count(*) DESC<br>\| LIMIT 1 |
