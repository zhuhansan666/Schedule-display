import logging
from time import time
from src.AppConfig import AppConfig
from src.pkg import staticTools

from os import path as os_path, chdir

chdir(staticTools.get_current_path())  # change to work path


class Global:
    def __init__(self, app_config_obj):
        self.__app_config = app_config_obj

        self.__config_dict = self.__app_config.default_config

    def update_config(self):
        run_type = staticTools.read_json(app_config.config_file)
        if run_type[0] != 0:
            logger.error("读取配置发生错误:", exc_info=run_type[1])  # 失败
        else:
            self.__config_dict.update(run_type[1])

    def write_config(self):
        run_type = staticTools.write_json(app_config.config_file, self.__config_dict)
        if run_type[0] != 0:
            logger.error("写入配置发生错误:", exc_info=run_type[1])

    @property
    def config_dict(self):
        return self.__config_dict

    @config_dict.setter
    def config_dict(self, value):
        self.__config_dict = staticTools.merge_dict(value, self.__app_config.default_config)


app_config = AppConfig()
global_obj = Global(app_config)

logging.basicConfig(
    filename=app_config.log_file,
    encoding="u8",
    level=logging.INFO,
    style='{',
    format='[{asctime}:%03d] [{levelname}] In {filename} At PID: {process}'
           ' threadName: {threadName} Line {lineno}:\n{message}' % (time() % 1 * 1000),
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger("g")

# init #

# 读取配置文件
if os_path.exists(app_config.config_file) and not os_path.isdir(app_config.config_file):  # 存在配置文件
    result = staticTools.read_json(app_config.config_file)
    if result[0] != 0:
        logger.error("Read {} error:".format(app_config.config_file), exc_info=result[1])  # 失败
    else:
        global_obj.config_dict = result[1]  # 成功设置为内容
else:
    return_code = staticTools.write_json(app_config.config_file, app_config.default_config)  # 不存在配置文件创建
    if return_code[0] != 0:
        logger.error("Write {} error:".format(app_config.config_file), exc_info=return_code[1])  # 写入失败
    else:
        global_obj.config_dict = app_config.default_config  # 成功设置为默认

# end init #
