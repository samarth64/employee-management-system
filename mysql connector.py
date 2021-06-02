import time
import mysql.connector
import colorama
from colorama import Fore, Back, Style


def database():
    global host
    global user
    global password
    host=input("\t\t\t\tenter host (generally localhost) -:")
    user=input("\t\t\t\tenter user (generally root) -:")
    password=input("\t\t\t\tenter password of MYSQL -:")
    con = mysql.connector.connect(host=host, user=user, password=password)
    mycursor = con.cursor()
    global data 
    data=input("\t\t\t\tenter database name")
    sql="CREATE DATABASE if not exists {}".format(data)
    mycursor.execute(sql)
    con.commit()
    con.close()
    

def createtable():
    con = mysql.connector.connect(host=host, user=user, password=password,database=data)
    mycursor = con.cursor()
    mycursor.execute("CREATE TABLE if not exists empl(empno char(3) primary key ,name varchar(20) not null, job varchar(14) ,age int(2),salary varchar("
                     "6),deptno varchar(5))")


def insert():
    con = mysql.connector.connect(host=host, user=user, password=password,database=data)
    mycursor = con.cursor()
    count = 0
    a = int(input("\n\t\t\t\thow many records you want to enter"))
    for i in range(a):
        empno = input("\n\t\t\t\tenter employe number -:")
        name = input("\n\t\t\t\tenter employe name -:")
        job=input("\n\t\t\t\tenter designation of employe -:")
        age = int(input("\n\t\t\t\tenter employe age -:"))
        salary = input("\n\t\t\t\tenter employe salary -:")
        deptno = input("\n\t\t\t\tenter employe department -:")
        val = (empno, name,job, age, salary, deptno)
        sql = "insert into empl values(%s,%s,%s,%s,%s,%s)"
        mycursor.execute(sql, val)
        count = count + 1
    con.commit()
    print("\t\t\t\t",count, "record inserted.")


def search():
    con = mysql.connector.connect(host=host, user=user, password=password,database=data)
    mycursor = con.cursor()
    a = input("\t\t\t\tenter empno which you want to search")
    sql = "SELECT * FROM empl where empno= %s"
    d = (a,)
    mycursor.execute(sql, d)
    z = mycursor.fetchall()
    for i in z:
        print("\t\t\t\t",i)
    con.commit()


def structure():
    con = mysql.connector.connect(host=host, user=user, password=password,database=data)
    mycursor = con.cursor()
    mycursor.execute("desc empl")
    for i in mycursor:
        print("\t\t\t\t",i)


def display():
    con = mysql.connector.connect(host=host, user=user, password=password,database=data)
    mycursor = con.cursor()
    sql = "SELECT * FROM empl "
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    count=0
    for z in myresult:
        print("\t\t\t\t",z)
        count+=1
    if count==0 :
        print("\t\t\t\tno records are available in table") 


def delete():
    con = mysql.connector.connect(host=host, user=user, password=password,database=data)
    mycursor = con.cursor()
    sql = "delete from empl where empno = %s"
    a = input("\t\t\t\tenter the empno you want to delete")
    u = (a,)
    mycursor.execute(sql, u)
    con.commit()
    print("\t\t\t\t",mycursor.rowcount, "record deleted")


def update():
    print("\t\t\t\tpress 1 to update employe name")
    time.sleep(0.3)
    print("\t\t\t\tpress 2 to update employe designation")
    time.sleep(0.3)
    print("\t\t\t\tpress 3 to update employe age")
    time.sleep(0.3)
    print("\t\t\t\tpress 4 to update employe salary")
    time.sleep(0.3)
    print("\t\t\t\tpress 5 to update employe department ")
    time.sleep(0.3)
    w=input("\t\t\t\tpress here")
    con = mysql.connector.connect(host=host, user=user, password=password,database=data)
    mycursor = con.cursor()
    z = input("\t\t\t\tenter the empno where you want to update")
    if w=="1":
        sql="update empl set name=%s where empno = %s"
        y=input("\t\t\t\tenter new name")
    elif w=="2":
        sql="update empl set job=%s where empno = %s"
        y=input("\t\t\t\tenter new job designation")
    elif w=="3":
        sql="update empl set age=%s where empno =%s"
        y=input("\t\t\t\tenter new age")
    elif w=="4" :
        sql = "UPDATE empl SET salary = %s WHERE empno = %s"
        y = input("\t\t\t\tenter the updated salary ")
    elif w=="5":
        sql="update empl set deptno = %s where empno =%s"
        y=input("\t\t\t\tenter new deptno")
    z = (y, z)
    mycursor.execute(sql, z)
    con.commit()
    print("\t\t\t\tupdated succesfully")

def menu():
    print(Fore.BLACK +"\t\t\t--------------------------Menu------------------------------------")
    time.sleep(1)
    print("\t\t\tThis is a menu driven program of MYSQL connectivity with Python")
    time.sleep(1)
    print(Fore.CYAN+"\t\t\t|\t\t\t\t 1: creating database employe\t\t\t\t\t|")
    time.sleep(0.5)
    print("\t\t\t|\t\t\t\t 2: creating table name as employe \t\t\t\t|")
    time.sleep(0.5)
    print("\t\t\t|\t\t\t\t 3: inserting a value \t\t\t\t\t\t\t|")
    time.sleep(0.5)
    print("\t\t\t|\t\t\t\t 4: display \t\t\t\t\t\t\t\t\t|")
    time.sleep(0.5)
    print("\t\t\t|\t\t\t\t 5: searching a value\t\t\t\t\t\t\t|")
    time.sleep(0.5)
    print("\t\t\t|\t\t\t\t 6: updation of salary \t\t\t\t\t\t\t|")
    time.sleep(0.5)
    print("\t\t\t|\t\t\t\t 7: deleting any empl details \t\t\t\t\t|")
    time.sleep(0.5)
    print("\t\t\t|\t\t\t\t 8: reprint the menu \t\t\t\t\t\t\t|")
    time.sleep(0.5)
    print("\t\t\t|\t\t\t\t q: quit \t\t\t\t\t\t\t\t\t\t|")
    time.sleep(0.5)
    global p
    p=input("\n\t\t\tpress here -:")
    p.lower()
menu()
x = "y"
while x == "y":
    if p == "1":
        database()
        print("\t\t\t\tsuccesfully created database named as employe")
        print()
    elif p == "2":
        createtable()
        print("\t\t\t\tsuccesfully created table named as empl")
        print()
    elif p == "3":
        insert()
        print()
    elif p == "4":
        display()
        print()
    elif p == "5":
        search()
        print()
    elif p == "6":
        update()
        print()
    elif p == "7":
        delete()
        print()
    elif p=="8":
        menu()
        print()
    elif p == "q":
        quit()
        print("\t\t\t\tThank You ")
        break
    

    x = input("\t\t\t\tpress y if you want to continue else any key other than y -: ")
    x = x.lower()
    print()
    if x=="y":
        p=input("\t\t\t\tpress the serial number as per the menu or press 8 to see menu -:")
        print()
        continue
    else:
        print("\t\t\t\tThank You ")
        break
    
