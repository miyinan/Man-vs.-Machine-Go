from tkinter import *
from tkinter.ttk import *
import copy
import tkinter.messagebox
import random
import time


# 从tk中派生出application类
class Application(Tk):
    def __init__(self):
        Tk.__init__(self)  # 调用父类Tk库的初始化函数
        self.mode = 7
        self.size = 2
        self.dd = 360 * self.size / (self.mode - 1)  # 7*7的棋盘，有7条线，6个方格
        self.p = 1
        # 初始化棋盘数组，共7*7,初始化都为零
        self.positions = [[0 for i in range(self.mode + 2)] for i in range(self.mode + 2)]
        # 将边界置为-1
        for i in range(self.mode + 2):
            for j in range(self.mode + 2):
                if (i * j == 0 or i == self.mode + 1 or j == self.mode + 1):
                    self.positions[i][j] = -1
        # 复制棋盘图层
        self.last_1_positions = copy.deepcopy(self.positions)
        self.last_2_positions = copy.deepcopy(self.positions)
        self.last_3_positions = copy.deepcopy(self.positions)
        # 记录光标情况
        self.cross_last = None
        # 记录玩家情况,0为黑子，1为白子
        self.player = 0
        # 游戏模式，0是停止运行，1是人人对战，2是人机对战
        self.play_mode = 0
        # 图片文件，W代表颜色；U代表up，没有落子含有阴影的；D代表down，已经落子了
        self.photoW = PhotoImage(file="./img/W.png")
        self.photoB = PhotoImage(file="./img/B.png")
        self.photoBD = PhotoImage(file="./img/BD.png")
        self.photoWD = PhotoImage(file="./img/WD.png")
        self.photoBU = PhotoImage(file="./img/BU.png")
        self.photoWU = PhotoImage(file="./img/WU.png")
        self.photo_title = PhotoImage(file="./img/title.png")
        # 用于黑白棋子图片切换的列表
        self.photoWBU_list = [self.photoBU, self.photoWU]
        self.photoWBD_list = [self.photoBD, self.photoWD]
        # 窗口大小
        self.geometry(str(int(600 * self.size)) + 'x' + str(int(400 * self.size)))
        # 画布控件，作为容器
        self.canvas_bottom = Canvas(self, bg='#8F2525', bd=0, width=600 * self.size, height=400 * self.size)
        self.canvas_bottom.place(x=0, y=0)
        # 几个功能按钮
        self.startButton = Button(self, text='人人对战', command=self.start)
        self.startButton.place(x=480 * self.size, y=250 * self.size)
        self.replayButton = Button(self, text='重新开始', command=self.reload)
        self.replayButton.place(x=480 * self.size, y=275 * self.size)
        self.quitButton = Button(self, text='人机对战', command=self.auto)
        self.quitButton.place(x=480 * self.size, y=300 * self.size)
        self.quitButton = Button(self, text='退出游戏', command=self.quit)
        self.quitButton.place(x=480 * self.size, y=325 * self.size)

        # 画棋盘，填充颜色
        self.canvas_bottom.create_rectangle(0 * self.size, 0 * self.size, 400 * self.size, 400 * self.size,
                                            fill='#F0D798')
        # 刻画棋盘线及九个点
        # 先画外框粗线
        self.canvas_bottom.create_rectangle(20 * self.size, 20 * self.size, 380 * self.size, 380 * self.size, width=3)
        # 棋盘上的九个定位点，以中点为模型，移动位置，以作出其余八个点
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                self.oringinal = self.canvas_bottom.create_oval(200 * self.size - self.size * 2,
                                                                200 * self.size - self.size * 2,
                                                                200 * self.size + self.size * 2,
                                                                200 * self.size + self.size * 2, fill='#000')
                self.canvas_bottom.move(self.oringinal,
                                        i * self.dd * 2,
                                        j * self.dd * 2)
        # 画中间的线条
        for i in range(1, self.mode - 1):
            self.canvas_bottom.create_line(20 * self.size, 20 * self.size + i * self.dd, 380 * self.size,
                                           20 * self.size + i * self.dd, width=2)
            self.canvas_bottom.create_line(20 * self.size + i * self.dd, 20 * self.size, 20 * self.size + i * self.dd,
                                           380 * self.size, width=2)
        # 放置右侧初始图片
        self.create_pB()
        self.create_pW()
        self.p_title = self.canvas_bottom.create_image(500 * self.size , 180 * self.size, image=self.photo_title)
        # 鼠标移动时，调用shadow函数，显示随鼠标移动的棋子，bind是事件绑定，事件对象 event 会传递给后面的函数，这里的event会传x、y坐标给回调函数
        self.canvas_bottom.bind('<Motion>', self.move)
        # 鼠标左键单击时，调用getdown函数，放下棋子，button-1是鼠标左键
        self.canvas_bottom.bind('<Button-1>', self.place_stone)

        # 以下四个函数实现了右侧太极图的动态创建与删除

    def create_pW(self):
        self.pW = self.canvas_bottom.create_image(500 * self.size - 22, 65 * self.size, image=self.photoW)
        self.canvas_bottom.addtag_withtag('image', self.pW)

    def create_pB(self):
        self.pB = self.canvas_bottom.create_image(500 * self.size + 17, 82 * self.size, image=self.photoB)
        self.canvas_bottom.addtag_withtag('image', self.pB)

    def del_pW(self):
        self.canvas_bottom.delete(self.pW)

    def del_pB(self):
        self.canvas_bottom.delete(self.pB)

    # 移动棋子
    def move(self,event):
        if self.play_mode:
            # 找到最近格点，在当前位置靠近的格点出显示棋子图片，并删除上一位置的棋子图片
            if (20 * self.size < event.x < 380 * self.size) and (20 * self.size < event.y < 380 * self.size):
                dx = (event.x - 20 * self.size) % self.dd
                dy = (event.y - 20 * self.size) % self.dd
                self.cross = self.canvas_bottom.create_image(event.x - dx + round(dx / self.dd) * self.dd + 22 * self.p,
                                                             event.y - dy + round(dy / self.dd) * self.dd - 27 * self.p,
                                                             image=self.photoWBU_list[self.player])
                self.canvas_bottom.addtag_withtag('image', self.cross)
                if self.cross_last != None:
                    self.canvas_bottom.delete(self.cross_last)
                self.cross_last = self.cross

    # 落子
    def place_stone(self,event):
        if  self.play_mode==1 or self.player==0:
            # 先找到最近格点
            if (20 * self.size - self.dd * 0.4 < event.x < self.dd * 0.4 + 380 * self.size) and (
                    20 * self.size - self.dd * 0.4 < event.y < self.dd * 0.4 + 380 * self.size):
                dx = (event.x - 20 * self.size) % self.dd
                dy = (event.y - 20 * self.size) % self.dd
                x = int((event.x - 20 * self.size - dx) / self.dd + round(dx / self.dd) + 1)
                y = int((event.y - 20 * self.size - dy) / self.dd + round(dy / self.dd) + 1)
                # 判断位置是否已经被占据
                if self.positions[y][x] == 0:
                    # 未被占据，则尝试占据，获得占据后能杀死的棋子列表
                    self.positions[y][x] = self.player + 1
                    self.image_added = self.canvas_bottom.create_image(
                        event.x - dx + round(dx / self.dd) * self.dd + 4 * self.p,
                        event.y - dy + round(dy / self.dd) * self.dd - 5 * self.p,
                        image=self.photoWBD_list[self.player])
                    self.canvas_bottom.addtag_withtag('image', self.image_added)
                    # 棋子与位置标签绑定，方便“杀死”
                    self.canvas_bottom.addtag_withtag('position' + str(x) + str(y), self.image_added)
                    deadlist = self.get_deadlist(x, y)
                    self.kill(deadlist)
                    # 判断是否重复棋局
                    if not self.last_2_positions == self.positions:
                        # 判断是否属于有气和杀死对方其中之一
                        if len(deadlist) > 0 or self.if_dead([[x, y]], self.player + 1, [x, y]) == False:
                            # 当不重复棋局，且属于有气和杀死对方其中之一时，落下棋子有效
                            self.last_3_positions = copy.deepcopy(self.last_2_positions)
                            self.last_2_positions = copy.deepcopy(self.last_1_positions)
                            self.last_1_positions = copy.deepcopy(self.positions)
                            # 删除上次的标记，重新创建标记
                            self.canvas_bottom.delete('image_added_sign')
                            self.image_added_sign = self.canvas_bottom.create_oval(
                                event.x - dx + round(dx / self.dd) * self.dd + 0.5 * self.dd,
                                event.y - dy + round(dy / self.dd) * self.dd + 0.5 * self.dd,
                                event.x - dx + round(dx / self.dd) * self.dd - 0.5 * self.dd,
                                event.y - dy + round(dy / self.dd) * self.dd - 0.5 * self.dd, width=3, outline='#3ae')
                            self.canvas_bottom.addtag_withtag('image', self.image_added_sign)
                            self.canvas_bottom.addtag_withtag('image_added_sign', self.image_added_sign)
                            if self.player == 0:
                                self.create_pW()
                                self.del_pB()
                                self.player = 1
                            else:
                                if self.play_mode==2:
                                    self.place_stone()
                                self.create_pB()
                                self.del_pW()
                                self.player = 0

                        else:
                            # 不属于杀死对方或有气，则判断为无气，警告并弹出警告框
                            self.positions[y][x] = 0
                            self.canvas_bottom.delete('position' + str(x) + str(y))
                            self.bell()
                            self.showwarningbox('无气', "你被包围了！")
                    else:
                        # 重复棋局，警告打劫
                        self.positions[y][x] = 0
                        self.canvas_bottom.delete('position' + str(x) + str(y))
                        self.recover(deadlist, (1 if self.player == 0 else 0))
                        self.bell()
                        self.showwarningbox("打劫", "据规则规定提一子后，对方在可以回提的情况下不能马上回提，要先在别处下一着，待对方应一手之后再回提")
                else:
                    # 覆盖，声音警告
                    self.bell()
            else:
                # 超出边界，声音警告
                self.bell()
            if self.play_mode == 2 and self.player==1:
                while 1:
                    x = random.randint(0, 6)
                    y = random.randint(0, 6)
                    if self.positions[y+1][x+1] == 0:
                        # 未被占据，则尝试占据，获得占据后能杀死的棋子列表
                        self.positions[y+1][x+1] = self.player + 1
                        self.image_added = self.canvas_bottom.create_image(
                            20 * self.size + x * self.dd,
                            20 * self.size + y * self.dd,
                            image=self.photoWBD_list[self.player])
                        self.canvas_bottom.addtag_withtag('image', self.image_added)
                        # 棋子与位置标签绑定，方便“杀死”
                        self.canvas_bottom.addtag_withtag('position' + str(x+1) + str(y+1), self.image_added)
                        deadlist = self.get_deadlist(x+1, y+1)
                        self.kill(deadlist)
                        # 判断是否重复棋局
                        if not self.last_2_positions == self.positions:
                            # 判断是否属于有气和杀死对方其中之一
                            if len(deadlist) > 0 or self.if_dead([[x+1, y+1]], self.player + 1, [x+1, y+1]) == False:
                                # 当不重复棋局，且属于有气和杀死对方其中之一时，落下棋子有效
                                self.last_3_positions = copy.deepcopy(self.last_2_positions)
                                self.last_2_positions = copy.deepcopy(self.last_1_positions)
                                self.last_1_positions = copy.deepcopy(self.positions)
                                # 删除上次的标记，重新创建标记
                                self.canvas_bottom.delete('image_added_sign')
                                self.image_added_sign = self.canvas_bottom.create_oval(
                                    20 * self.size + x * self.dd + 0.5 * self.dd,
                                    20 * self.size + y * self.dd + 0.5 * self.dd,
                                    20 * self.size + x * self.dd - 0.5 * self.dd,
                                    20 * self.size + y * self.dd - 0.5 * self.dd, width=3,
                                    outline='#3ae')
                                self.canvas_bottom.addtag_withtag('image', self.image_added_sign)
                                self.canvas_bottom.addtag_withtag('image_added_sign', self.image_added_sign)
                                self.create_pB()
                                self.del_pW()
                                self.player = 0
                                time.sleep(0.5)
                                return


    def if_dead(self, deadList, yourChessman, yourPosition):
        for i in [-1, 1]:
            if [yourPosition[0] + i, yourPosition[1]] not in deadList:
                if self.positions[yourPosition[1]][yourPosition[0] + i] == 0:
                    return False
            if [yourPosition[0], yourPosition[1] + i] not in deadList:
                if self.positions[yourPosition[1] + i][yourPosition[0]] == 0:
                    return False
        if ([yourPosition[0] + 1, yourPosition[1]] not in deadList) and (
                self.positions[yourPosition[1]][yourPosition[0] + 1] == yourChessman):
            midvar = self.if_dead(deadList + [[yourPosition[0] + 1, yourPosition[1]]], yourChessman,
                                  [yourPosition[0] + 1, yourPosition[1]])
            if not midvar:
                return False
            else:
                deadList += copy.deepcopy(midvar)
        if ([yourPosition[0] - 1, yourPosition[1]] not in deadList) and (
                self.positions[yourPosition[1]][yourPosition[0] - 1] == yourChessman):
            midvar = self.if_dead(deadList + [[yourPosition[0] - 1, yourPosition[1]]], yourChessman,
                                  [yourPosition[0] - 1, yourPosition[1]])
            if not midvar:
                return False
            else:
                deadList += copy.deepcopy(midvar)
        if ([yourPosition[0], yourPosition[1] + 1] not in deadList) and (
                self.positions[yourPosition[1] + 1][yourPosition[0]] == yourChessman):
            midvar = self.if_dead(deadList + [[yourPosition[0], yourPosition[1] + 1]], yourChessman,
                                  [yourPosition[0], yourPosition[1] + 1])
            if not midvar:
                return False
            else:
                deadList += copy.deepcopy(midvar)
        if ([yourPosition[0], yourPosition[1] - 1] not in deadList) and (
                self.positions[yourPosition[1] - 1][yourPosition[0]] == yourChessman):
            midvar = self.if_dead(deadList + [[yourPosition[0], yourPosition[1] - 1]], yourChessman,
                                  [yourPosition[0], yourPosition[1] - 1])
            if not midvar:
                return False
            else:
                deadList += copy.deepcopy(midvar)
        return deadList

    def get_deadlist(self, x, y):
        deadlist = []
        for i in [-1, 1]:
            if self.positions[y][x + i] == (2 if self.player == 0 else 1) and ([x + i, y] not in deadlist):
                killList = self.if_dead([[x + i, y]], (2 if self.player == 0 else 1), [x + i, y])
                if not killList == False:
                    deadlist += copy.deepcopy(killList)
            if self.positions[y + i][x] == (2 if self.player == 0 else 1) and ([x, y + i] not in deadlist):
                killList = self.if_dead([[x, y + i]], (2 if self.player == 0 else 1), [x, y + i])
                if not killList == False:
                    deadlist += copy.deepcopy(killList)
        return deadlist

        # 杀死位置列表killList中的棋子，即删除图片，位置值置0

    def kill(self, killList):
        if len(killList) > 0:
            for i in range(len(killList)):
                self.positions[killList[i][1]][killList[i][0]] = 0
                self.canvas_bottom.delete('position' + str(killList[i][0]) + str(killList[i][1]))

    def recover(self, list_to_recover, b_or_w):
        if len(list_to_recover) > 0:
            for i in range(len(list_to_recover)):
                self.positions[list_to_recover[i][1]][list_to_recover[i][0]] = b_or_w + 1
                self.image_added = self.canvas_bottom.create_image(
                    20 * self.size + (list_to_recover[i][0] - 1) * self.dd + 4 * self.p,
                    20 * self.size + (list_to_recover[i][1] - 1) * self.dd - 5 * self.p,
                    image=self.photoWBD_list[b_or_w])
                self.canvas_bottom.addtag_withtag('image', self.image_added)
                self.canvas_bottom.addtag_withtag('position' + str(list_to_recover[i][0]) + str(list_to_recover[i][1]),
                                                  self.image_added)

    # 开始游戏
    def start(self):
        self.canvas_bottom.delete(self.pW)
        self.canvas_bottom.delete(self.pB)
        if self.player == 0:
            self.create_pB()
            self.del_pW()
        else:
            self.create_pW()
            self.del_pB()
        self.play_mode = 1

    # 重新开始游戏
    def reload(self):
        if self.play_mode == 1:
            self.play_mode = 0
        self.canvas_bottom.delete('image')
        self.player = 0
        self.create_pB()
        for m in range(1, self.mode + 1):
            for n in range(1, self.mode + 1):
                self.positions[m][n] = 0
                self.last_3_positions[m][n] = 0
                self.last_2_positions[m][n] = 0
                self.last_1_positions[m][n] = 0

    # 人机对战模式
    def auto(self):
        self.canvas_bottom.delete(self.pW)
        self.canvas_bottom.delete(self.pB)
        if self.player == 0:
            self.create_pB()
            self.del_pW()
        else:
            self.create_pW()
            self.del_pB()
        self.play_mode = 2

    # 警告消息框，接受标题和警告信息
    def showwarningbox(self, title, message):
        self.canvas_bottom.delete(self.cross)
        tkinter.messagebox.showwarning(title, message)


global newApp
newApp = False
if __name__ == '__main__':
    # 循环，直到不切换游戏模式
    while True:
        newApp = False
        app = Application()
        app.title('围棋')
        app.mainloop()
        if newApp:
            app.destroy()
        else:
            break
