import sys
import os
import subprocess
from threading import Thread
from queue import Queue, Empty
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QScrollArea, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from UI_main import Ui_MainWindow

class ProcessManager:
    def __init__(self):
        self.processes = {}

    def start_process(self, name, path, working_dir):
        try:
            if name in self.processes and self.processes[name]['process'].poll() is None:
                print(f"进程 {name} 已经在运行。")
                return
            
            print(f"启动进程: {name}, 路径: {path}, 工作目录: {working_dir}")

            # 启动进程
            process = subprocess.Popen(
                [path],
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # 使用线程异步读取输出和错误
            output_queue = Queue()
            error_queue = Queue()
            
            Thread(target=self._enqueue_output, args=(process.stdout, output_queue), daemon=True).start()
            Thread(target=self._enqueue_output, args=(process.stderr, error_queue), daemon=True).start()
            
            self.processes[name] = {
                'process': process,
                'output_queue': output_queue,
                'error_queue': error_queue
            }
        except Exception as e:
            print(f"启动进程 {name} 失败: {e}")
        
    def stop_process(self, name):
        if name not in self.processes or self.processes[name]['process'].poll() is not None:
            print(f"进程 {name} 没有运行。")
            return
        
        process = self.processes[name]['process']
        
        print(f"强制终止进程: {name}")
        process.kill()  # 强制终止
        process.wait()  # 等待进程结束
        
        del self.processes[name]
        print(f"进程 {name} 已终止。")


    def read_output(self, name):
        if name not in self.processes:
            print(f"进程 {name} 没有运行。")
            return
        
        try:
            output = self.processes[name]['output_queue'].get_nowait()
            if output:
                print(f"[{name}] {output.strip()}")
        except Empty:
            pass

        try:
            error = self.processes[name]['error_queue'].get_nowait()
            if error:
                print(f"[{name}] {error.strip()}")
        except Empty:
            pass
    
    def _enqueue_output(self, out, queue):
        for line in iter(out.readline, ''):
            queue.put(line)
        out.close()

class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, exe_paths):
        super(MyWindow, self).__init__()
        self.setupUi(self)
        
        self.setWindowIcon(QIcon("icon.ico"))

        self.manager = ProcessManager()

        # 创建按钮布局
        button_layout = QVBoxLayout()

        try:
            for name, (path, working_dir) in exe_paths.items():
                start_button = QPushButton(f'启动 {name}')
                start_button.clicked.connect(lambda _, n=name, p=path, wd=working_dir: self.manager.start_process(n, p, wd))
                button_layout.addWidget(start_button)
        except Exception as e:
            print(f"读取exe_paths时出错: {e}")

        # 增加空白空间，优化排版
        button_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        container = QWidget()
        container.setLayout(button_layout)
        self.scrollArea.setWidget(container)
        self.scrollArea.setWidgetResizable(True)

        # 设置滚动区域作为主窗口的中央组件
        # self.setCentralWidget(self.scrollArea)

        # 设置窗口大小，并允许用户调整窗口大小
        self.resize(600, 400)
        
        # 定时器用于定期读取子进程的输出和错误
        self.timer = self.startTimer(500)

    def timerEvent(self, event):
        for name in self.manager.processes.keys():
            self.manager.read_output(name)

def load_config(file_path):
    import configparser
    config = configparser.ConfigParser()
    config.read(file_path, encoding='utf-8')
    exe_paths = {}
    if '程序' in config:
        for key, value in config['程序'].items():
            exe_path = os.path.abspath(os.path.join(os.path.dirname(file_path), value))
            working_dir = os.path.dirname(exe_path)
            exe_paths[key] = (exe_path, working_dir)
    return exe_paths

if __name__ == "__main__":
    try:
        from qt_material import apply_stylesheet
        
        app = QApplication(sys.argv)
        
        # 判断配置文件是否存在，不存在则创建一个默认的配置文件
        config_file = '配置.ini'
        if not os.path.exists(config_file):
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write('[程序]\n')
                f.write('程序名 = 程序相关路径/程序完整名称含有拓展名.exe\n')
        
        # 读取配置文件
        exe_paths = load_config(config_file)
        
        window = MyWindow(exe_paths)
        
        apply_stylesheet(app, theme='light_blue.xml', css_file='ui/custom.css')
        
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"配置文件加载失败！{str(e)}")
        print("按任意键退出...")
        input()  # 这会暂停程序直到用户输入并按回车键
