from src.g import app_config, global_obj


class Manager:
    def __init__(self, _app_config, _global):
        self.__app_config = _app_config
        self.__global = _global

    def add(self, name: str, time: str):
        """
        新增项
        :param name: 名称
        :param time: 格式化后的时间字符串
        :return: list[True / False, err / None, err / None]
        """
        result = [True, None, None]
        try:
            self.__global.config_dict["__events"]["names"].append(name)
        except Exception as e:
            result[0] = False
            result[1] = e
        try:
            self.__global.config_dict["__events"]["times"].append(time)
        except Exception as e:
            result[0] = False
            result[2] = e
        return result

    def delete(self, index: int):
        """
        删除
        :param index: 索引值
        :return: True / False, None / err
        """
        try:
            del self.__global.config_dict["__events"]["names"][index]
            del self.__global.config_dict["__events"]["times"][index]
            return True, None
        except Exception as e:
            return False, e

    def update(self, index: int, name: str=None, time: str=None):
        """
        更改
        :param index: 索引值
        :param name: 名称 (为None不变)
        :param time: 格式化后的时间字符串 (为None不变)
        :return: True / False, None / err
        """
        try:
            if name is not None:
                self.__global.config_dict["__events"]["names"][index] = name
            if time is not None:
                self.__global.config_dict["__events"]["times"][index] = time
            return True, None
        except Exception as e:
            return False, e


if __name__ == '__main__':
    test = Manager(app_config, global_obj)

    print(global_obj.config_dict)
