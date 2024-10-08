# 软件工具箱
一个基于PyQt5开发的，支持自定义配置实现多个程序统一到一个程序来控制启动的工具箱。

# 前言

程序读取配置中的程序名和路径，自动生成按钮添加到UI中，点击按钮即可启动对应程序。  

## 运行环境

操作系统：win7及以上  
编程语言：python3.8+（python版本过高时会不兼容win7，推荐用py38）  


# 使用

安装依赖库 `pip install -r requirements.txt`  

根据需求，修改 `配置.ini` 文件中的配置信息，即追加程序名和程序相对或绝对路径即可。

运行程序 `python main.py`

程序运行中的日志直接输出在控制台中，由于子程序自己会维护日志，所以不做重复记录

# 开发

打开设计师 `pyqt5-tools designer`  

生成UI代码 `pyuic5 -o UI_main.py main.ui`  

打包程序 `auto-py-to-exe` 加载 `package.json` 进行打包。  

# 许可证

本项目采用MIT许可证。请查看LICENSE文件了解更多信息。  

# 更新日志

- 2024-10-08
    - v0.1.0 初版发布
