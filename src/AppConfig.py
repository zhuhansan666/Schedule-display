import win32api, win32con


class AppConfig:
    def __init__(self):
        # g.py
        self.log_file = "latest.log"
        # self.log_file = None

        self.config_file = "config.json"
        self.default_config = {
            "font": "",
            "wininfo": [],
            "wintype": 1,
            "__events": {
                "names": [],
                "times": []
            }
        }

        # Show.py
        screen_size = win32api.GetSystemMetrics(win32con.SM_CXSCREEN), win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        self.default_wininfo = (0, screen_size[1] // 2, screen_size[0], screen_size[1] // 2)
        # self.screen_color = (21, 148, 33)

        self.date_format = "%Y-%m-%d %H:%M:%S"
        self.time_format = "%H:%M:%S"

        self.win_title = "日程显示 by 爱喝牛奶"

        self.error_interval = 1  # 错误打印间隔, 秒
        self.max_error = 2  # 连续错误日志输出最大值
        self.resort_interval = 1  # 重新加载并排序间隔, 秒
        self.reset_pos_interval = 0.01  # 重新更改窗口位置间隔, 秒

        self.time_units = {
            "日": 3600 * 24, "时": 3600, "分": 60, "秒": 1, "毫秒": 0.001
        }

        # main.py
        self.reload_interval = 1  # 重新加载(读取文件)间隔, 秒
