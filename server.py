from ast import Return
from crypt import methods
from itertools import product
import json
from pickle import APPEND
from pickletools import read_uint1
from unittest import result
from webbrowser import get
import mysql.connector
from flask import Flask, jsonify, request,render_template,redirect,request,session
from flaskext.mysql import MySQL
from flask_session import Session
from datetime import date

app = Flask(__name__)

#Database Connection
mydb = mysql.connector.connect(host="localhost",user="root",password="rudra123",database="sample1")
cursor=mydb.cursor()


@app.route('/', methods = ['GET'])
def home():
    if(request.method == 'GET'):
  
        data = "hello world"
        cursor.execute(''' select * from CUSTOMER''')
        result = cursor.fetchall()
        return jsonify({'data': result})



#Customer Login 
@app.route('/custlogin/<int:phone>/<password>', methods = ['GET'])
def custlogin(phone,password):
   
     
    if request.method == 'GET':
        

        cursor.execute("select * from CUSTOMER where C_PHNO='"+str(phone)+"' ")
        result = cursor.fetchall()
        print(result)
        
        if(len(result)>0): 
            if(result[0][6]==password):
                print(result)
                loginresult=jsonify({"id":result[0][0]},{"status":"Success"})
                return loginresult
            else:
                return "Fail"
        else:
            return "Fail"


#Customer Profile
@app.route('/custprofile/<userid>',methods = ['GET'])
def custprofile(userid):
    print(userid)
    
    cursor.execute("select * from CUSTOMER where C_ID='"+str(userid)+"' ")
    result = cursor.fetchall()
    cname=result[0][1]
    cphn=str(result[0][2])
    cemail=result[0][3]
    caddr=result[0][4]
    cpincode=str(result[0][5])
    custdata = jsonify({"custinfo":{"cname":cname,"cphn":cphn,"cemail":cemail,"caddr":caddr,"cpincode":cpincode}})
    return custdata


#Customer Order history
@app.route('/custorderhistory/<userid>',methods = ['GET'])
def custorderhistory(userid):
    print(userid)

    cursor.execute("SELECT O.CO_ID,B.B_NAME,P.P_NAME,P.P_PRICE,O.P_QUANTITY,O.CO_DELIVERYDATE FROM C_ORDER O,BOOTH B,ADD_PRODUCT P WHERE O.C_ID='"+str(userid)+"' and O.B_NAME=B.B_NAME and P.P_NAME=O.P_NAME and O.O_STATUS='SUCCESS'")
    result = cursor.fetchall()
   
    print(result)
    
    custorderh = []
    row_headers=[x[0] for x in cursor.description]
    for res in result:
        custorderh.append(dict(zip(row_headers,res)))
    
    finalRes=jsonify({"orders":custorderh})
    
    return finalRes


#
@app.route('/custproductname/', methods = ['GET'])
def custproductname():
    # print(productname)

    cursor.execute("select P_NAME from ADD_PRODUCT")
    result = cursor.fetchall()

    productname = []
    row_headers = [x[0] for x in cursor.description]
    for res in result:
        productname.append(dict(zip(row_headers,res)))
    
    finalRes = jsonify({"products":productname})
    return finalRes

@app.route('/custproducts/<productname>', methods = ['GET'])
def custproducts(productname):
    print(productname)

    cursor.execute("select P_PRICE from ADD_PRODUCT where P_NAME='"+productname+"'")
    result = cursor.fetchall()

    productname = []
    row_headers = [x[0] for x in cursor.description]
    for res in result:
        productname.append(dict(zip(row_headers,res)))
    
    finalRes = jsonify({"productdetails":productname})
    return finalRes

@app.route('/boothdet/', methods = ['GET'])
def boothdet():
    # print(productname)

    cursor.execute("select B_NAME from BOOTH ")
    result = cursor.fetchall()

    boothname = []
    row_headers = [x[0] for x in cursor.description]
    for res in result:
        boothname.append(dict(zip(row_headers,res)))
    
    finalRes = jsonify({"boothdetails":boothname})
    return finalRes


@app.route('/orderfinal/<custid>/<productname>/<boothname>/<quantity>/<price>/', methods = ['GET'])
def orderfinal(custid,productname,boothname,quantity,price):
    print(productname)
    odate = date.today()
    cursor.execute("select CO_ID from C_ORDER order by(CO_ID) desc limit 1")
    result = cursor.fetchall()
    coid=result[0][0]
    count=int(coid[-1])+1
    newcoid=coid[0:3]+str(count)
    cursor.execute("insert into C_ORDER values('"+newcoid+"','"+custid+"','"+boothname+"','"+productname+"','"+quantity+"','"+price+"','"+str(odate)+"',null,'PENDING') ")
    mydb.commit()
    return "success"


@app.route('/custprofileupdate/<Name>/<Phonenumber>/<Email>/<Address>/<Pincode>/<custid>', methods =['Put'])
def custprofileupdate(Name,Phonenumber,Email,Address,Pincode,custid):
    

    cursor.execute("update CUSTOMER SET C_NAME='"+Name+"',C_PHNO='"+Phonenumber+"',C_EMAIL='"+Email+"',C_ADDRESS='"+Address+"',C_PINCODE='"+Pincode+"' where C_ID='"+custid+"'")
    # return "updated"
    mydb.commit()
    print(cursor.rowcount, "record(s) affected") 

    #print(Name,Phonenumber,Email,Address,Pincode,custid)
    return "done"



@app.route('/factlogin/<plantname>/<password>', methods = ['GET'])
def factlogin(plantname,password):
         
    if request.method == 'GET':
        

        cursor.execute("select * from PLANT where PLANT_NAME='"+plantname+"' ")
        result = cursor.fetchall()
        
        
        if(len(result)>0):  
            if(result[0][2]==password):
                
                loginresult=jsonify({"id":result[0][0]},{"status":"Success"})
                return loginresult
            else:
                return "Fail"
        else:
            return "Fail"

@app.route('/factaddproduct/<productname>/<productprice>/<plantname>', methods = ['GET'])
def factaddproduct(productname,productprice,plantname):
    cursor.execute("insert into ADD_PRODUCT values('"+productname+"','"+productprice+"','"+plantname+"')")
    mydb.commit()   
    return "success"

@app.route('/factboothlist/<plantname>', methods = ['GET'])
def factboothlist(plantname):
    cursor.execute("select * FROM BOOTH WHERE PLANT_NAME=('"+plantname+"')")
    result=cursor.fetchall()
    boothlist = []
    row_headers = [x[0] for x in cursor.description]
    for res in result:
        boothlist.append(dict(zip(row_headers,res)))
    
    finalRes = jsonify({"boothdetails":boothlist})
    return finalRes

@app.route('/boothorder/<plantis>', methods = ['GET'])
def boothorder(plantis):
    cursor.execute("select bo.* FROM B_ORDER bo,PLANT p,BOOTH b WHERE bo.PLANT_NAME=('"+plantis+"') and bo.PLANT_NAME=p.PLANT_NAME and bo.B_NAME=b.B_NAME ")
    result=cursor.fetchall()
    bootholist = []
    print(result)
    print(plantis)
    row_headers = [x[0] for x in cursor.description]
    for res in result:
        bootholist.append(dict(zip(row_headers,res)))
    
    finalRes = jsonify({"boothorder":bootholist})
    return finalRes

@app.route('/factprodlist/<plantname>', methods = ['GET'])
def factprodlist(plantname):
    cursor.execute("select * FROM ADD_PRODUCT WHERE PLANT_NAME=('"+plantname+"')")
    result=cursor.fetchall()
    prodlist = []
    row_headers = [x[0] for x in cursor.description]
    for res in result:
        prodlist.append(dict(zip(row_headers,res)))
    
    finalRes = jsonify({"prodlist":prodlist})
    return finalRes


@app.route('/factoryboothname/<plantname>', methods =['GET'])
def factoryboothname(plantname):
    cursor.execute("Select b.B_NAME from BOOTH b, PLANT p where b.PLANT_NAME='"+plantname+"' and b.PLANT_NAME=p.PLANT_NAME")
    result = cursor.fetchall()
    boothname=[]
    row_headers = [x[0] for x in cursor.description]
    for res in result:
        boothname.append(dict(zip(row_headers,res)))
    finalres = jsonify({'data':boothname})
    return finalres
    # return "hello"

@app.route('/boothmodify/<boothname>', methods = ['GET'])
def boothmodify(boothname):
    cursor.execute("Select B_NAME,B_PHNO,B_EMAIL,B_ADDRESS,B_PINCODE FROM BOOTH where B_NAME='"+boothname+"'")
    result = cursor.fetchall()
    boothmodify=[]
    row_headers = [x[0] for x in cursor.description]
    for res in result:
        boothmodify.append(dict(zip(row_headers,res)))
    finalres = jsonify({"boothdetails":boothmodify})
    return finalres
    # return "one"
@app.route('/updateboothdata/<bname>/<bphno>/<bemail>/<baddr>/<pin>/<plantname>')
def boothUpdate(bname,bphno,bemail,baddr,pin,plantname):
    cursor.execute("update BOOTH set B_NAME='"+bname+"' , B_PHNO = '"+bphno+"' , B_EMAIL ='"+bemail+"' , B_ADDRESS = '"+baddr+"' , B_PINCODE ='"+pin+"' where B_NAME='"+bname+"'  ")
    mydb.commit()
    return "success"



#Delivery Person login
@app.route('/deliverylogin/<phone>/<password>', methods = ['GET'])
def deliverylogin(phone,password):
        cursor.execute("select * from D_BOYS where DB_PHNO='"+str(phone)+"' ")
        result = cursor.fetchall()
        print(result)
        
        if(len(result)>0): 
            if(result[0][4]==password):
                print(result)
                loginresult=jsonify({"id":result[0][0]},{"status":"Success"})
                return loginresult
            else:
                return "Fail"
        else:
            return "Fail"
        

#BoothLogin
@app.route('/boothlogin/<bname>/<password>', methods = ['GET'])
def boothlogin(bname,password):
        cursor.execute("select * from BOOTH where B_NAME='"+str(bname)+"' ")
        result = cursor.fetchall()
        print(result)
        print(bname,password)
        
        if(len(result)>0): 
            if(result[0][5]==password):
                print(result)
                loginresult=jsonify({"id":result[0][0]},{"status":"Success"})
                return loginresult
            else:
                return "Fail"
        else:
            return "Fail"
        




#Booth order details
'''@app.route('/boothdeliveries/<custid>', methods =[''])
def boothdeliveries(productname):
    cursor.execute("SELECT D.*,CO.CO_PRICE FROM DBOYS_DELIVERY D,C_ORDER CO WHERE CO.C_ID='"+custid+"' and D.C_ID=CO.C_ID")
    result = cursor.fetchall()
    boothdeliveries = []
    row_headers = [x[0] for x in cursor.description]
    for res in result:
        boothdeliveries.append(dict(zip(row_headers,res)))
    finalres = jsonify({"BoothDeliveries":boothdeliveries})
    return finalres
'''

#Add Delivery person

@app.route('/boothdeliveryboy/<db_id>/<db_name>/<db_phno>/<db_email>/<db_password>', methods =['GET'])
def boothdeliveryboy(db_id,db_name,db_phno,db_email,db_password):
    

    query = cursor.execute("insert into D_BOYS(DB_ID,DB_NAME,DB_PHNO,DB_EMAIL,PASSWORD) values('"+db_id+"','"+db_name+"','"+db_phno+"','"+db_email+"','"+db_password+"')")
    # val = (db_id,db_name,db_phno,db_email,db_password)
    # return "updated"
    result = cursor.execute(query)
    mydb.commit()
    print(cursor.rowcount, "record(s) affected") 

    #print(Name,Phonenumber,Email,Address,Pincode,custid)
    return "SUCCCESS"




#Update Delivery boy profile Details

@app.route('/boothdeliveryboyupdate/<db_name>/<db_phno>/<db_email>', methods =['Put'])
def boothdeliveryboyupdate(db_name,db_phno,db_email):


    cursor.execute("update D_BOYS SET DB_PHNO = '"+db_phno+"',DB_EMAIL = '"+db_email+"' WHERE DB_NAME = '"+db_name+"'")
    
    mydb.commit()
    print(cursor.rowcount, "record(s) affected") 

    
    return "success"

#Display delivery boy deatiles
@app.route('/deliveryboydetails/<boothid>', methods = ['GET'])
def deliveryboydetails(boothid):
    cursor.execute("select DB_NAME from D_BOYS where B_NAME='"+boothid+"' " )
    result=cursor.fetchall()
    print(result)
    deliveryboydetails = []
    row_headers = [x[0] for x in cursor.description]
    for res in result:
        deliveryboydetails.append(dict(zip(row_headers,res)))
    finalres = jsonify({"deliveryboydetails":deliveryboydetails})
    return finalres


@app.route('/deliveryboy/<dbname>',methods = ['GET'])
def deliveryboy(dbname):
    cursor.execute("select DB_NAME,DB_PHNO,DB_EMAIL from D_BOYS WHERE DB_NAME='"+dbname+"' ")
    result = cursor.fetchall()
    print(result)
    
    deliveryboy = []
    row_headers = [x[0] for x in cursor.description]
    for res in result:
        deliveryboy.append(dict(zip(row_headers,res)))
    finalres = jsonify({"details":deliveryboy})
    return finalres


@app.route('/orderidlist/<boothid>', methods = ['GET'])
def orderids(boothid):
    cursor.execute("select CO_ID from C_ORDER where B_NAME='"+boothid+"' " )
    result=cursor.fetchall()
    print(result)
    orderids = []
    row_headers = [x[0] for x in cursor.description]
    for res in result:
        orderids.append(dict(zip(row_headers,res)))
    finalres = jsonify({"orderids":orderids})
    return finalres


#Customer Order Detailes Display

@app.route('/custordertobooth/<odrid>/<boothid>',methods = ['GET'])
def odrlist(odrid,boothid):
    cursor.execute("select CO.C_ID,C.C_NAME,CO.P_NAME,CO.P_QUANTITY,(CO.P_QUANTITY*CO.P_PRICE) AS PRICE FROM C_ORDER CO,CUSTOMER C WHERE CO.CO_ID='"+odrid+"' AND CO.B_NAME='"+boothid+"' AND CO.C_ID=C.C_ID AND CO.O_STATUS='PENDING'")
    result = cursor.fetchall()
   # select CO.C_ID,C.C_NAME,CO.P_NAME,CO.P_QUANTITY,(CO.P_QUANTITY*CO.P_PRICE) FROM C_ORDER CO,CUSTOMER C WHERE CO_ID='CO001' AND CO.C_ID=C.C_ID;

    ordrlist1= []
    print(result)
    row_headers = [x[0] for x in cursor.description]
    for res in result:
        ordrlist1.append(dict(zip(row_headers,res)))
    finalres = jsonify({"details":ordrlist1})
    return finalres

#ASSIGN ORDER TO DBOYS
@app.route('/assignorder/<bname>/<coid>/<dbid>',methods = ['GET'])
def asignorder(bname,coid,dbid):
    cursor.execute("select DB_ID from D_BOYS where DB_NAME='"+dbid+"'" )
    id=cursor.fetchall()
    # print(id)
    cursor.execute(" INSERT INTO B_ASSIGN_DELIVERY VALUES('"+bname+"','"+coid+"','"+id[0][0]+"','PENDING')")
    # print(result)
    mydb.commit()

    # print(bname,coid,dbid)
    return "success"


#Store custid in BOOTH
@app.route('/boothcustid/<boothname>', methods=['Get'])
def boothcustid(boothname):
    cursor.execute("select C_ID,CO_ID from C_ORDER WHERE B_NAME = '"+boothname+"'")
    result = cursor.fetchall()
    custid = []
    row_headers = [x[0] for x in cursor.description]
    for res in result:
        custid.append(dict(zip(row_headers,res)))
    finalres = jsonify({'custid':custid})

    return finalres

#Customer payments history in Booth
@app.route('/boothcustpayments/<custname>', methods = ['GET'])
def boothcustpayments(custname):
    cursor.execute("SELECT C.C_ID,C.C_NAME,COUNT(CO.CO_ID) AS ORDERCOUNT ,SUM(CO.P_QUANTITY*CO.P_PRICE) AS TOTAL FROM CUSTOMER C,C_ORDER CO WHERE C.C_ID='"+custname+"' AND C.C_ID=CO.C_ID GROUP BY C_ID")
    result = cursor.fetchall()
    boothcustpayments = []
    row_headers = [x[0] for x in cursor.description]
    for res in result:
        boothcustpayments.append(dict(zip(row_headers,res)))
    finalres = jsonify({"Boothcustpay":boothcustpayments})
    return finalres

#Customer order details in BOOTH
@app.route('/custboothdeliverydetails/<boothid>',methods = ['GET'])
def custboothdeliverydetails(boothid):
    cursor.execute("select CO.P_NAME,CO.C_ID,CO.CO_ID,CO.CO_DELIVERYDATE,(CO.P_QUANTITY*CO.P_PRICE) AS PRICE FROM C_ORDER CO,BOOTH B ,CUSTOMER C WHERE CO.B_NAME='"+boothid+"' AND CO.C_ID=C.C_ID AND CO.B_NAME=B.B_NAME AND CO.O_STATUS='SUCCESS'")
    result = cursor.fetchall()
    
   # select CO.C_ID,C.C_NAME,CO.P_NAME,CO.P_QUANTITY,(CO.P_QUANTITY*CO.P_PRICE) FROM C_ORDER CO,CUSTOMER C WHERE CO_ID='CO001' AND CO.C_ID=C.C_ID;

    ordrlist1= []
    print(result)
    row_headers = [x[0] for x in cursor.description]
    for res in result:
        ordrlist1.append(dict(zip(row_headers,res)))
    finalres = jsonify({"details":ordrlist1})
    return finalres

@app.route('/newdeliverydetails/<delboyid>',methods = ['GET'])
def newdeliverydetails(delboyid):
    cursor.execute("select b.B_NAME,b.CO_ID,co.CO_DELIVERYDATE from B_ASSIGN_DELIVERY b,C_ORDER co where b.DB_ID='"+delboyid+"' and b.CO_ID=co.CO_ID and co.O_STATUS='SUCCESS'")
    result = cursor.fetchall()
    
   # select CO.C_ID,C.C_NAME,CO.P_NAME,CO.P_QUANTITY,(CO.P_QUANTITY*CO.P_PRICE) FROM C_ORDER CO,CUSTOMER C WHERE CO_ID='CO001' AND CO.C_ID=C.C_ID;

    ordrlist1= []
    print(result)
    row_headers = [x[0] for x in cursor.description]
    for res in result:
        ordrlist1.append(dict(zip(row_headers,res)))
    finalres = jsonify({"details":ordrlist1})
    return finalres

@app.route('/assignnewdelivery/<delboyid>',methods = ['GET'])
def assignnewdelivery(delboyid):
    cursor.execute("select co.CO_ID,co.B_NAME,c.C_ADDRESS from C_ORDER co,CUSTOMER c,D_BOYS d,BOOTH b where d.DB_ID='"+delboyid+"' and d.B_NAME=b.B_NAME and co.C_ID=c.C_ID and co.O_STATUS='PENDING' order by(co.CO_DATE) limit 1")
    result = cursor.fetchall()
    
    ordrlist1= []
    print(result)
    row_headers = [x[0] for x in cursor.description]
    for res in result:
        ordrlist1.append(dict(zip(row_headers,res)))
    finalres = jsonify({"details":ordrlist1})
    return finalres

@app.route('/updatedeliverystatus/<orderid>',methods = ['GET'])
def updatedeliverystatus(orderid):
    deldate = date.today()
    print(deldate)
    cursor.execute("update C_ORDER set CO_DELIVERYDATE='"+str(deldate)+"',O_STATUS='SUCCESS' where CO_ID='"+orderid+"'")
   
    cursor.execute("update B_ASSIGN_DELIVERY set STATUS='SUCCESS' where CO_ID='"+orderid+"'")
    mydb.commit()

    return "success"


@app.route('/deliveryboylist/<delboyid>',methods = ['GET'])
def deliveryboylist(delboyid):
    cursor.execute("select DB_NAME,DB_PHNO,DB_EMAIL from D_BOYS where DB_ID='"+delboyid+"'")
    result = cursor.fetchall()
    
    ordrlist1= []
    print(result)
    row_headers = [x[0] for x in cursor.description]
    for res in result:
        ordrlist1.append(dict(zip(row_headers,res)))
    finalres = jsonify({"details":ordrlist1})
    return finalres

@app.route('/delboydetailsupdate/<delboyid>/<delboyname>/<delboyphno>/<delboymail>',methods = ['GET'])
def delboydetailsupdate(delboyid,delboyname,delboyphno,delboymail):
    cursor.execute("update D_BOYS set DB_NAME='"+delboyname+"',DB_PHNO='"+delboyphno+"',DB_EMAIL='"+delboymail+"' where DB_ID='"+delboyid+"'")
   
    mydb.commit()

    return "success"

if __name__ == '__main__':
   
    app.run('0.0.0.0',8000,debug ="False")