# Config.json 参数

* `font` (str, 可被设置) 显示的字符字体 <br>
* `wininfo` (list, 不可设置) 窗口弹出的位置和大小 (为空默认) [x, y, w, h] <br>
* `wintype` (int, 可设置) 窗口是否置顶 (0 否, 1 是)  <br>
* `events` (dict, 可设置内部项) 事件 (names为空字符则为空白项, 用于添加事件间隔) {"names": [<name1>, <name2>, ...], "times": [<name1_time>, <name2_time>, ...]} <br>
* 