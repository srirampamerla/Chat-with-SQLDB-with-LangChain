import sqlite3

## COnnect to SQL lite

connection=sqlite3.connect("student.db")

## create a cursor object to insert record,create table

cursor=connection.cursor()

# Create the Table

table_info="""
create table STUDENT(NAME VARCHAR(25),CLASS VARCHAR(25),
SECTION VARCHAR(25), MARKS INT)
"""

cursor.execute(table_info)
## Insert Some more records


cursor.execute('''Insert into STUDENT values('Krish','Data Science','A',90)''')
cursor.execute('''Insert into STUDENT values('Sai','AI','B',95)''')
cursor.execute('''Insert into STUDENT values('Kumar','NLP','A',92)''')
cursor.execute('''Insert into STUDENT values('Sasi','ML','B',91)''')
cursor.execute('''Insert into STUDENT values('Jacob','Data Science','A',80)''')
cursor.execute('''Insert into STUDENT values('Dipesh','AI','B',95)''')

## Display all the records
print("The inserted records are")
data=cursor.execute('''Select * from STUDENT''')

for row in data:
    print(row)

## Commit the changes in the database
connection.commit()
connection.close()