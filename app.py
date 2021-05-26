from flask import *
import pymysql
import flask_redis
import datetime
# 配置
from config.read_config import get_config
# 验证合法性函数
from services.make_package import MakePackage
from services.send_package import SendPackage
from services.verify_string import verify_mac_address, verify_isp, verify_campus
# ORM
from model.db_model import mydb, mac_record, forward_device


app = Flask(__name__)  # 实例化flask_app

# 配置数据库
db_config = get_config()
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://' + db_config.get('DB', 'DB_USER') + ':' + db_config.get('DB', 'DB_PASSWORD') + '@' + db_config.get('DB', 'DB_HOST') + '/' + db_config.get('DB', 'DB_DB')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config["SQLALCHEMY_ECHO"] = False
mydb.init_app(app)
# MySQLdb不兼容py3，使用pymysql代替
pymysql.install_as_MySQLdb()

# 配置Redis
app.config['REDIS'] = {"CACHE_TYPE": "redis", "CACHE_REDIS_HOST": "127.0.0.1", "CACHE_REDIS_PORT": 6379, "CACHE_REDIS_DB": 1, "CACHE_REDIS_PASSWORD": ""}  # 配置Redis ORM
r = flask_redis.FlaskRedis()
r.init_app(app)

# 实例化私有类
make_package = MakePackage()
send_package = SendPackage()

host = db_config.get('HOST', 'HOST')

"""
修改请求头允许跨域请求
param: data
return: response obj
"""


def response(data):
    data = make_response(data)
    data.headers['Access-Control-Allow-Origin'] = '*'
    return data


@app.route('/')
def index_page():
    return send_file('static/html/index.html')


@app.route('/history')
def history_page():
    return send_file('static/html/history.html')


@app.route('/api/send_package', methods=['POST'])
def send_package_api():
    try:
        param = request.form.to_dict()
        mac = param['mac']
        isp = param['isp']
        campus = param['campus']
        print('\n\n')
        print('[start]', isp, campus, mac)

        # 合法性校验
        mac = verify_mac_address(mac)
        isp = verify_isp(isp)
        campus = verify_campus(campus)
        if mac and isp and campus:
            campus_device = get_campus_ip_and_port(campus)  # 查数据库，得到不同校区转发设备的ip和port(frp)
            campus_ip, campus_port = campus_device[0], campus_device[1]
        else:
            return abort(404)

        package = make_package.do(ip=campus_ip, mac=mac, isp=isp)  # 生成数据包
        if package:
            recv_package = send_package.send_udp(host=host, port=int(campus_port), package=package)  # 发送数据包
        else:
            return abort(404)

        # 判断返回udp报文，回复前端
        if recv_package:
            if '0a153' in recv_package:
                write_to_db(mac=mac, isp=isp, campus=campus)  # 记录到数据库
                return response('success')
            else:
                return response('error')
        else:
            return response('false')

    except Exception as e:
        print(e)
        abort(404)


@app.route('/api/history')
def history_api():
    result = get_all_record()
    return response(jsonify(data=result))


def get_campus_ip_and_port(id):
    result = forward_device.query.filter(forward_device.campus == id).values(forward_device.ip, forward_device.server_port)
    return [i for i in result][0]


def write_to_db(mac, isp, campus):
    result = mac_record.query.filter(mac_record.mac == mac).first()  # 查询是否有这条记录
    now_time = datetime.datetime.now()
    if result is None:
        new_record = mac_record(mac=mac, isp=isp, campus=campus, addTime=now_time, lastTime=now_time, count=1)
        mydb.session.add(new_record)
    else:
        result.mac = mac
        result.isp = isp
        result.campus = campus
        result.lastTime = now_time
        result.count = int(result.count) + 1
    mydb.session.commit()


def get_all_record():
    start_time = datetime.datetime.today() + datetime.timedelta(-3000)
    end_time = datetime.datetime.today()
    result = mydb.session.query(mac_record).filter(mydb.or_(mac_record.addTime.between(start_time, end_time), mac_record.lastTime.between(start_time, end_time))).all()
    print(result)
    result = [(i.id, i.mac, i.isp, '花江校区' if i.campus == '1' else '东区', '' if i.payingCustomer is None else '是的', datetime.datetime.strftime(i.addTime, "%Y-%m-%d_%H:%M:%S"), datetime.datetime.strftime(i.lastTime, "%Y-%m-%d_%H:%M:%S") if i.lastTime else None, i.count) for i in result]
    return result


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=False, threaded=True)
