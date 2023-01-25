import sqlite3
bd = sqlite3.connect("the_best_player.sqlite3")
cur = bd.cursor()
cur.execute("""
create table if not exists RECORDS (
    name text, 
    score time
)""")
cur.execute("""
SELECT name, max(score) score from RECORDS
GROUP by name
ORDER by score
limit 3
""")
result = cur.fetchall()
print(result)
cur.close()