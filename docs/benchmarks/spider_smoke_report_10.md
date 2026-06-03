# Spider Small Smoke Test Report

| Metric | Result |
| --- | --- |
| Cases | 10 |
| Databases | concert_singer |
| SQL+ valid | 10/10 |
| SQL executable | 10/10 |
| Execution match | 10/10 |

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
