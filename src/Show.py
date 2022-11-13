from os import environ, path as os_path
from sys import exit as sys_exit
from time import strptime, mktime, time, strftime, localtime

import pygame
import win32con
import win32gui
from win32api import RGB

from src.pkg.staticTools import get_index, format_unit, ThreadErr
from src.pkg.pygameTools import PygameTools

from src.g import app_config, global_obj

from logging import getLogger

pygame.init()
logger = getLogger("Show")


class Format:
    _app_config = app_config

    @classmethod
    def sort(cls, events: dict, target_time: float | int = 0, mate_date: bool = False):
        """
        排序events, 直接作用于原字典
        :param events: dict {"names": [str, ...], "times": [timeFormatStr, ...]}
        :param target_time: 当前的目标项的时间戳 要设置的值 大于等于 此项时 才会被设置
        :param mate_date: 是否匹配日期
        :return: True / False, 当前的目标项的index (float / int) [-1为未找到]/ Errors (list), -1(错误) / 目标项时间戳
        """

        errors = []
        time_format = cls._app_config.time_format
        date_format = cls._app_config.date_format
        names: list = events.get("names", None)
        times: list = events.get("times", None)
        if names is None or times is None:
            return False, [ValueError("list is empty")], -1

        low_timestamp = -1
        result_index = -1
        for index in range(min(len(names), len(times))):  # 为了时间戳在只有一个项获取正常, 此处不减一
            time_stamp2 = -1
            try:
                if mate_date:
                    time_stamp = mktime(strptime(times[index], date_format))
                else:
                    time_stamp = mktime(strptime(f"{strftime('%Y-%m-%d ', localtime())}{times[index]}",
                                                 f"%Y-%m-%d {time_format}"))
                for index2 in range(1, min(len(names), len(times))):
                    try:
                        if mate_date:
                            time_stamp2 = mktime(strptime(times[index2], date_format))
                        else:
                            time_stamp2 = mktime(strptime(f"{strftime('%Y-%m-%d ', localtime())}{times[index2]}",
                                                          f"%Y-%m-%d {time_format}"))
                        if time_stamp2 < time_stamp:
                            names[index2], times[index2], names[index], times[index] = \
                                names[index], times[index], names[index2], times[index2]  # 交换前后位置
                        if time_stamp2 >= target_time and (time_stamp2 < low_timestamp or low_timestamp < 0):
                            low_timestamp = time_stamp2
                            result_index = index2
                    except IndexError as err:
                        item2 = get_index(names, index, "")
                        e = IndexError(f"{index} ({item2}) in 2nd for not found: {err}")
                        if e not in errors:
                            errors.append(e)
                    except Exception as e:
                        if e not in errors:
                            errors.append(e)
                if time_stamp >= target_time and (time_stamp < low_timestamp or low_timestamp < 0):
                    low_timestamp = time_stamp
                    result_index = index
            except IndexError:
                item = get_index(names, index, "")
                e = IndexError(f"{index} ({item}) not found.")
                if e not in errors:
                    errors.append(e)
            except Exception as e:
                if e not in errors:
                    errors.append(e)

        if not errors:
            lens = min(len(names), len(times))
            events["names"] = names[:lens]
            events["times"] = times[:lens]
            if len(events["names"]) > 0:
                if len(events["names"][result_index]) <= 0:
                    low_timestamp = -1
            else:
                low_timestamp = -1
            return True, result_index, low_timestamp
        else:
            return False, errors, low_timestamp


class ShowUI:
    def __init__(self, app_config_obj, _global_obj, font_name="Microsoft Yahei"):
        self.__clock = None
        self.screen_hwnd = 0
        self.__ui_config = [
            pygame.NOFRAME,
        ]

        self.screen = None
        self.__app_config = app_config_obj
        self.__global = _global_obj
        self.__low_config = self.__config = _global_obj.config_dict
        self.__errors = {
            "format": [False, time(), 0]  # 是否错误, 上一次错误时间, 错误连续的次数
        }

        self.stopped = False

        self.__font_name = font_name
        self.__fonts = {}
        self.__default_font_name = "Microsoft Yahei"

        self.__fonts_size = []
        self.__fonts_size_config = {
            "title": 30,
            "title_bg": 30,
        }

        self.control_power = 0  # 控制权, 0自己控制self.now_event, 1其他控制
        self.now_event = ["", -1]  # 事件名, 事件时间戳
        self.pos = (0, 0)

        self.init()

        fonts_lst = list(self.__fonts.values())
        if len(fonts_lst) > 0:
            self.__default_font_obj = fonts_lst[0]
        else:
            self.__default_font_obj = pygame.font.SysFont("Microsoft Yahei", self.__fonts_size_config.get("title", 30))

    @staticmethod
    def set_alpha_win(hwnd: int, alpha_color, alpha=255):
        """
        透明窗口
        :param hwnd: 句柄
        :param alpha_color: 需要透明的颜色
        :param alpha: 透明的颜色值 (0-255)
        :return: True/ 0, False/ error
        """
        try:
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                                   win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
            result = win32gui.SetLayeredWindowAttributes(hwnd, RGB(*alpha_color), alpha, win32con.LWA_COLORKEY)
            if result is not False:
                return True, None
            else:
                return result
        except Exception as e:
            return False, e

    @staticmethod
    def set_top(hwnd: int, top: bool = True):
        """
        置顶窗口c
        :param hwnd: 句柄
        :param top: 是否置顶(True->置顶; False->取消置顶)
        :return: True/ False, None / error
        """
        try:
            result = win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST if top else win32con.win32con.HWND_NOTOPMOST,
                                           0, 0, 0, 0,
                                           win32con.SWP_SHOWWINDOW | win32con.SWP_NOSIZE | win32con.SWP_NOMOVE
                                           | win32con.SWP_NOACTIVATE)
            """win32con.SWP_NOSIZE -> 忽略更改的窗口大小;  win32con.SWP_NOMOVE -> 忽略更改的窗口位置;
            win32con.SWP_NOACTIVATE -> 默认不激活窗口"""
            if result != 0:
                return True, None
            else:
                return False, RuntimeError("Unknown Error")
        except Exception as e:
            return False, e

    @staticmethod
    def set_pos(hwnd: int, pos: list | tuple):
        try:
            result = win32gui.SetWindowPos(hwnd, None,
                                           *pos, 0, 0,
                                           win32con.SWP_SHOWWINDOW | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
            """win32con.SWP_NOSIZE -> 忽略更改的窗口大小;  win32con.SWP_NOMOVE -> 忽略更改的窗口位置;
            win32con.SWP_NOACTIVATE -> 默认不激活窗口"""
            if result != 0:
                return True, None
            else:
                return False, RuntimeError("Unknown Error")
        except Exception as e:
            return False, e

    # @staticmethod
    # def hide_background(hwnd: int):
    #     """
    #     使窗口在 Win+Tab & Alt+Tab 不显示
    #     :param hwnd:
    #     :return:
    #     """
    #     try:
    #         win32gui.ShowWindow(hwnd)
    #     except Exception as e:
    #         return False, e

    def init(self):
        self.stopped = False
        self.screen = None

        self.__set_font()

        self.__clock = pygame.time.Clock()

        icon_tuple = PygameTools.load_image("static/images/icon.png")
        if icon_tuple[0]:
            pygame.display.set_icon(icon_tuple[1])
        else:
            logger.error("加载icon.png错误:", exc_info=icon_tuple[1])

        pygame.display.set_caption(self.__app_config.win_title, self.__app_config.win_title)  # 设置窗口标题

        # environ["SDL_VIDEO_WINDOW_POS"]
        wininfo: list = self.__config.get("wininfo", [])
        if not len(wininfo) <= 0:
            x, y, w, h = get_index(wininfo, 0, None), get_index(wininfo, 1, None), get_index(wininfo, 2, None), \
                         get_index(wininfo, 3, None)
        else:
            x, y, w, h = app_config.default_wininfo

        if all((x is not None, y is not None)):
            environ["SDL_VIDEO_WINDOW_POS"] = f"{x},{y}"  # 设置弹出位置

        if all((w is not None, h is not None)):
            try:
                self.screen = pygame.display.set_mode((w, h), flags=self.__ui_config[0])
            except Exception as e:
                logger.error("Create pygame window error:", exc_info=e)
                self.screen = pygame.display.set_mode((x, y), flags=self.__ui_config[0])

        if self.screen is None:
            self.screen = pygame.display.set_mode(flags=self.__ui_config[0])

        self.screen_hwnd = pygame.display.get_wm_info().get("window", 0)
        result = self.set_alpha_win(self.screen_hwnd, (0, 0, 0))
        if not result[0]:
            logger.error("Set AlphaWin error:", exc_info=result[1])
        if self.__global.config_dict.get("wintype", 1) == 1:
            result = self.set_top(self.screen_hwnd)
            if result[0] is not True:
                logger.error("设置置顶发生错误:", exc_info=result[1])

        pygame.display.flip()

    def __set_font(self):
        lst = self.__fonts_size + list(self.__fonts_size_config.values())
        if os_path.splitext(self.__font_name)[1].lower() == ".ttf":  # 如果是.ttf文件
            for size in lst:
                try:
                    self.__fonts[size] = pygame.font.Font(self.__font_name, size)
                except Exception as e:
                    logger.error(f"加载字体文件 (大小: {size}) 发生错误:", exc_info=e)
        else:
            for size in lst:
                try:
                    self.__fonts[size] = pygame.font.SysFont([self.__font_name, self.__default_font_name], size)
                except Exception as e:
                    logger.error(f"加载系统字体 (大小: {size}) 发生错误:", exc_info=e)

    def __redraw(self):
        time_differ = get_index(self.now_event, 1, 0) - time()
        name = get_index(self.now_event, 0, "")
        if self.now_event[1] > 0 and time_differ >= 0 and len(name) > 0:
            info = f"距离 {name} 剩余 {format_unit(units=self.__app_config.time_units, num=time_differ, sep='')[1]}"
            font_surface = PygameTools.font_surface(
                self.__fonts.get(self.__fonts_size_config["title"], self.__default_font_obj),
                info,
                (255, 255, 255),
            )

            bg_font = PygameTools.font_surface(
                self.__fonts.get(self.__fonts_size_config["title_bg"], self.__default_font_obj),
                info,
                (1, 1, 1),
            )
        elif len(name) <= 0:
            font_surface = bg_font = None
        else:
            info = f"未找到任何项"
            font_surface = PygameTools.font_surface(
                self.__fonts.get(self.__fonts_size_config["title"], self.__default_font_obj),
                info,
                (255, 255, 255),
            )

            bg_font = PygameTools.font_surface(
                self.__fonts.get(self.__fonts_size_config["title_bg"], self.__default_font_obj),
                info,
                (1, 1, 1),
            )

        if font_surface is not None and bg_font is not None:
            self.screen.blit(bg_font[0], (14 + self.pos[0], self.pos[1] + self.screen.get_size()[1] - 40 -
                                          font_surface[1][1] + 4))
            self.screen.blit(font_surface[0], (10 + self.pos[0], self.pos[1] + self.screen.get_size()[1] - 40 -
                                               font_surface[1][1]))

    def __resort(self):
        if self.control_power == 0:
            result = Format.sort(self.__global.config_dict.get("events", {"names": [], "times": []}), time())
            if result[0] is not True:
                low_err = self.__errors.get("format", [False, -1, 0])

                if low_err[0] is True and time() - low_err[1] > self.__app_config.error_interval and \
                        low_err[2] > self.__app_config.max_error:  # 错误未连贯则重置内容
                    # 错误内容重设
                    low_err[0] = False
                    low_err[2] = 0
                    self.__errors["format"] = low_err
                if low_err[2] <= self.__app_config.max_error:  # 如果不大于最大错误次数
                    i = 0
                    for err in result[1]:
                        i += 1
                        logger.error(f"格式化事件字典发生错误({i}):", exc_info=err)  # 写入日志
                self.__errors["format"] = [True, time(), low_err[2] + 1]
            if type(result[1]) == int and result[1] >= 0:
                try:
                    self.now_event = [
                        get_index(self.__global.config_dict["events"].get("names", []), result[1], ""),  # 名称
                        result[2]  # 时间戳
                    ]  # 事件名, 事件时间戳
                except IndexError as e:
                    pass
                except Exception as e:
                    logger.error("读取配置发生错误:", exc_info=e)

    def __events(self, events_list: list):
        for e in events_list:
            if e.type == pygame.QUIT:
                self.stopped = True
                pygame.quit()
                sys_exit(0)

    def __reset_pos(self):
        wininfo: list = self.__config.get("wininfo", [])
        if not len(wininfo) <= 0:
            x, y, w, h = get_index(wininfo, 0, None), get_index(wininfo, 1, None), get_index(wininfo, 2, None), \
                         get_index(wininfo, 3, None)
        else:
            x, y, w, h = app_config.default_wininfo

        if all((x is not None, y is not None)):
            environ["SDL_VIDEO_WINDOW_POS"] = f"{x},{y}"  # 设置弹出位置
        result = self.set_pos(self.screen_hwnd, (x, y))
        if result[0] is not True:
            logger.error("重设置窗口位置发生错误:", exc_info=result[1])

    def mainloop(self, auto_exit: bool = False):
        ThreadErr(self.__resort, logger.error, errorfunc_argvs=("重新排序发生错误:",)).start()
        resort_time = time() - self.__app_config.resort_interval
        reset_pos_time = time() - self.__app_config.reset_pos_interval

        while not self.stopped:
            self.__clock.tick(144)
            # print(self.__clock.get_fps())

            if abs(time() - resort_time) >= self.__app_config.resort_interval:
                ThreadErr(self.__resort, logger.error, errorfunc_argvs=("重新排序发生错误:",)).start()
                resort_time = time()
            if abs(time() - reset_pos_time) >= self.__app_config.reset_pos_interval:
                ThreadErr(self.__reset_pos, logger.error, errorfunc_argvs=("重新设置窗口位置发生错误:",)).start()
                reset_pos_time = time()

            self.screen.fill((0, 0, 0))

            self.__redraw()

            pygame.display.update()
            if not auto_exit:
                pygame.event.get()
            else:
                # ThreadErr(lambda: self.__events(pygame.event.get()),
                #           logger.error, errorfunc_argvs=("读取事件/处理发生错误:", )).start()
                try:
                    self.__events(pygame.event.get())
                except Exception as e:
                    logger.error("读取事件/处理发生错误:", exc_info=e)


# test
if __name__ == '__main__':
    # dic = {
    #     "names": ["awa", "a", "", "测试"],
    #     "times": ["18:00:03", "18:00:00", "18:17:50", "23:59:59"]
    # }
    # # print(Format.sort(dic, 0))
    # # print(dic)
    # global_obj.config_dict["events"] = dic

    test = ShowUI(app_config, global_obj, r"./static/MiSans-Bold.ttf")
    test.mainloop(True)
