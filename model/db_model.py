from flask_sqlalchemy import SQLAlchemy
mydb = SQLAlchemy()


class mac_record(mydb.Model):
    id = mydb.Column(mydb.Integer, primary_key=True)
    mac = mydb.Column(mydb.VARCHAR)
    isp = mydb.Column(mydb.VARCHAR)
    campus = mydb.Column(mydb.VARCHAR)
    payingCustomer = mydb.Column(mydb.VARCHAR)
    addTime = mydb.Column(mydb.DATETIME)
    lastTime = mydb.Column(mydb.DATETIME)
    count = mydb.Column(mydb.Integer)


class forward_device(mydb.Model):
    id = mydb.Column(mydb.Integer, primary_key=True)
    campus = mydb.Column(mydb.VARCHAR)
    ip = mydb.Column(mydb.VARCHAR)
    server_port = mydb.Column(mydb.VARCHAR)
    updateTime = mydb.Column(mydb.DATETIME)