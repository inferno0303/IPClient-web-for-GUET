import os
import configparser


def get_config():
    # 路径
    pro_dir = os.path.split(os.path.realpath(__file__))[0]
    config_path = os.path.join(pro_dir, "config.ini")
    path = os.path.abspath(config_path)
    # 读配置
    conf = configparser.ConfigParser()
    print(path)
    conf.read(path)
    return conf
