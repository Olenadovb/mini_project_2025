Web-app for Ukrainian Army

reload main.py:
uvicorn main:app --reload

server:
http://127.0.0.1:8000/

cliend ID:
530210287714-hrog583ugo4tt5rk6dk1rfcbcm11p8n0.apps.googleusercontent.com


render start:
uvicorn main:app --host=0.0.0.0 --port=$PORT




import mysql.connector
db=mysql.connector.connect(host="your host", user="your username", password="your
password",database="database_name")

cursor=db.cursor()

query="UPDATE Students SET City='Kolkata' WHERE Name='Kriti'"
cursor.execute(query)
db.commit()

query="SELECT * FROM Students"
cursor.execute(query)

for row in cursor:
   print(row)
db.close()