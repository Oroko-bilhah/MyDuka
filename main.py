from cProfile import label
from flask import Flask, render_template,request,url_for,redirect
import psycopg2
from datetime import datetime

conn = psycopg2.connect(user="egrygupakzeqkd",
                       password="34dd2aaf584e7c9048faf6b6a470f38c8d7452fbff11739570d25e855272aeae",
                       host="ec2-54-246-185-161.eu-west-1.compute.amazonaws.com",
                       port="5432", 
                       database="myduka") 

cur=conn.cursor()

app= Flask(__name__)
cur.execute("CREATE TABLE IF NOT EXISTS products(id SERIAL PRIMARY KEY, name VARCHAR(50),buying_price INT NOT NULL, selling_price INT NOT NULL,stock_quantity INT NOT NULL)")


cur.execute("CREATE TABLE IF NOT EXISTS sales(id SERIAL PRIMARY KEY ,pid FOREIGN KEY ,quantity INT,created_at DATE NOT NULL DEFAULT NOW())")



@app.route('/inventories',methods=['POST','GET'])
def inventories():
  cur=conn.cursor()
  if request.method=="POST":
    name=request.form['p_name']
    bp=request.form['bp']
    sp=request.form['sp']
    sq=request.form['sq']
    cur.execute("INSERT INTO products(name,buying_price,selling_price,stock_quantity)VALUES(%s,%s,%s,%s)",(name,bp,sp,sq))
    conn.commit()
    
    return redirect('/inventories')
  else:
    cur.execute("SELECT* FROM products;")
    records=cur.fetchall()
    
    return render_template("inventories.html",records=records)

@app.route('/sales',methods=['GET', 'POST'])
def sales():
  cur=conn.cursor()
  if request.method=="POST":
    pid = request.form['pid']
    quantity = request.form['quantity']
    created_at=datetime.now()
    print(pid,quantity)
    cur.execute("UPDATE products SET stock_quantity=(stock_quantity-%s) WHERE id=%s;", (quantity, pid))
    cur.execute("INSERT INTO sales (pid, quantity,created_at) VALUES (%s, %s,%s);",(pid,quantity,created_at))
    conn.commit()
    
    return redirect('/sales')
  else:
     cur.execute("SELECT * FROM sales;")
     rows=cur.fetchall()
     print(rows)
     return render_template("sales.html",rows=rows)

@app.route("/inventories/<int:x>")
def view_item(x):
  cur=conn.cursor()
  cur.execute("select * from products where id=%(id)s;",{"id":x})
  x=cur.fetchall()
  print(x)
  return render_template("inventories.html",records=x)

@app.route("/sales/<int:y>")
def view_sales(y):
  cur=conn.cursor()
  cur.execute("select * from sales where id=%(id)s;",{"id":y})
  y=cur.fetchall()
  print(y)
  return render_template("sales.html",rows=y)


@app.route("/edit_products", methods=['POST','GET'])
def edit_products() :
  cur=conn.cursor()
  if request.method=="POST":
    pid=request.form['pid']
    names=str(request.form['p_name'])
    bp=request.form['bp']
    sp=request.form['sp']
    sq=request.form['sq']
    
    cur.execute("SELECT name FROM products where id=%s;",pid)
    name= cur.fetchone()
    if name!=names:
        cur.execute("UPDATE products SET name=%s WHERE id=%s;", (names,pid))
   
        cur.execute("UPDATE products SET buying_price=%s where id=%s;",(bp,pid))
        cur.execute("UPDATE products SET selling_price=%s where id=%s;",(sp,pid))
        cur.execute("UPDATE products SET stock_quantity=%s where id=%s;",(sq,pid))

   # cur.execute("INSERT INTO products(name,buying_price,selling_price,stock_quantity)VALUES(%s,%s,%s,%s)",(name,bp,sp,sq))

        conn.commit()
        return redirect("/inventories")

@app.route("/dashboard")
def dashboard():
  cur=conn.cursor()
  cur.execute("SELECT name,stock_quantity FROM products")
  data = cur.fetchall()
  print (data)
  labels=[row[0] for row in data]
  values=[row[1] for row in data]

  cur.execute("SELECT quantity.sales,products.name FROM sales join products on products.id=sales.pid")
  data = cur.fetchall()
  print (data)
  x=[row[0] for row in data]
  y=[row[1] for row in data]
  return render_template('dashboard.html',label=labels,values=values,x=x,y=y)
  
     


@app.route("/")
def home():
  return render_template("index.html")

@app.route("/about")
def about():
  return render_template("about.html")

# @app.route('/make_sale', methods=['GET', 'POST'])
# def make_sale():
#             if request.method == "POST":
#                 pid = request.form['pid']
#                 quantity = request.form['qty']
#                 created_at = datetime.now()
#                 # # # from datetime import datetime
#                 cur.execute(
#                     "UPDATE products SET stock_quantity=(stock_quantity-%s) WHERE id=%s;", (quantity, pid))
#                 cur.execute("INSERT INTO Sales (pid, quantity, created_at) VALUES (%s, %s, %s)",(pid,quantity,created_at))

        
#                 conn.commit()
        
#                 return redirect('/inventorie')
        

if __name__=="__main__":
  app.run()


  
 