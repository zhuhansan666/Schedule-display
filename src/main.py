from src.Show import ShowUI
from src.g import app_config, global_obj
from src.pkg.staticTools import ThreadErr

from src.Version import VERSION

from time import sleep, time
from logging import getLogger
from traceback import format_exception
import sys

logger = getLogger("main")


class Main:
    def __init__(self, app_config_obj, _global, show_ui_obj):
        self.__app_config = app_config_obj
        self.__global = _global
        self.__show_ui = show_ui_obj

        self.exit = False

    def __reload(self):
        while not self.exit:
            try:
                low_time = time()
                self.__global.update_config()
                sleep_time = self.__app_config.reload_interval - (time() - low_time)
                sleep(sleep_time if sleep_time > 0 else 0)
            except Exception as e:
                logger.error("重新加载内部发生错误:", exc_info=e)

    def main(self):
        ThreadErr(self.__reload, logger.error, errorfunc_argvs=("重新加载发生错误:", ), daemon=True).start()
        self.__show_ui.mainloop(True)
        self.exit = True


def error(t, value, trace_back):
    traceback_info = ""
    for line in format_exception(t, value, trace_back):
        traceback_info += str(line)
    logger.error("主程序发生错误(sys.excepthook): {}".format(traceback_info))
    sys.exit(-1)


sys.excepthook = error

if __name__ == '__main__':
    str_version = (str(n) for n in VERSION)
    print("Welcome to ues the 日程显示 by 爱喝牛奶 (Ver={})".format(".".join(str_version)))
    show_ui = ShowUI(app_config, global_obj, r"./static/MiSans-Bold.ttf")
    main = Main(app_config, global_obj, show_ui)
    main.main()
