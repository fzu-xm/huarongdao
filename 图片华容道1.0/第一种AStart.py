#coding:utf-8
import copy
import sys
import random
from PyQt5 import QtGui
import requestion
from enum import IntEnum
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QLabel, QWidget, QApplication, QGridLayout, QMessageBox, QMainWindow, QPushButton

class grid:
    def __init__(self, stat):
        self.pre = None
        # 目标状态
        # stat是一个二维列表
        self.stat = stat
        self.find0()
        self.update()

    # 更新启发函数的相关信息
    def update(self):
        self.fH()
        self.fG()
        self.fF()

    # G是深度，也就是走的步数
    def fG(self):
        if self.pre is not None:
            self.G = self.pre.G + 1
        else:
            self.G = 0

    # H是和目标状态距离之和
    def fH(self):
        self.H = 0
        for i in range(3):
            for j in range(3):
                targetX = target[i][j]
                nowP = self.findx(targetX)
                # 曼哈顿距离之和
                self.H += abs(nowP[0] - i) + abs(nowP[1] - j)

    # F是启发函数，F=G+H
    def fF(self):
        self.F = self.G + self.H

    # 查看找到的解是如何从头移动的
    def seeAns(self):
        global ans
        ans = ""
        p = self
        while p.pre:
            x1, y1 = p.find2()
            p = p.pre
            x2, y2 = p.find2()
            if x2 > x1:
                ans += "w"
            elif x2 < x1:
                ans += "s"
            elif x2 == x1:
                if y2 > y1:
                    ans += "a"
                elif y2 < y1:
                    ans += "d"
        listans = list(ans)
        listans.reverse()
        ans = "".join(listans)
        print(ans)

    def find2(self):
        for i in range(3):
            if 0 in self.stat[i]:
                j = self.stat[i].index(0)
                return i, j

    # 找到数字x的位置
    def findx(self, x):
        for i in range(3):
            if x in self.stat[i]:
                j = self.stat[i].index(x)
                return [i, j]

    # 找到0，也就是空白格的位置
    def find0(self):
        self.zero = self.findx(0)

    # 扩展当前状态，也就是上下左右移动。返回的是一个状态列表，也就是包含stat的列表
    def expand(self):
        i = self.zero[0]
        j = self.zero[1]
        gridList = []
        if j == 2 or j == 1:
            gridList.append(self.left())
        if i == 2 or i == 1:
            gridList.append(self.up())
        if i == 0 or i == 1:
            gridList.append(self.down())
        if j == 0 or j == 1:
            gridList.append(self.right())
        return gridList

    # deepcopy多维列表的复制，防止指针赋值将原列表改变
    # move只能移动行或列，即row和col必有一个为0
    # 向某个方向移动
    def move(self, row, col):
        newStat = copy.deepcopy(self.stat)
        tmp = self.stat[self.zero[0] + row][self.zero[1] + col]
        newStat[self.zero[0]][self.zero[1]] = tmp
        newStat[self.zero[0] + row][self.zero[1] + col] = 0
        return newStat

    def up(self):
        return self.move(-1, 0)

    def down(self):
        return self.move(1, 0)

    def left(self):
        return self.move(0, -1)

    def right(self):
        return self.move(0, 1)


# 判断状态g是否在状态集合中，g是对象，gList是对象列表
# 返回的结果是一个列表，第一个值是真假，如果是真则第二个值是g在gList中的位置索引
def isin(g, gList):
    gstat = g.stat
    statList = []
    for i in gList:
        statList.append(i.stat)
    if gstat in statList:
        res = [True, statList.index(gstat)]
    else:
        res = [False, 0]
    return res


# 计算不在位的个数
def getcost(alist):
    cost = 0
    for row in range(3):
        for column in range(3):
            if alist[row][column] == 0:
                pass
                # 值是否对应
            elif alist[row][column] != row * 3 + column + 1:
                cost = cost + 1
    return cost


# 计算逆序数之和
def N(nums):
    count = 0
    for i in range(len(nums)):
        if nums[i] != 0:
            for j in range(i):
                if nums[j] > nums[i]:
                    count += 1
    return count


# 根据逆序数之和判断所给八数码是否可解
def judge(src, target1):
    src = src[0] + src[1] + src[2]
    target1 = target1[0] + target1[1] + target1[2]
    N1 = N(src)
    N2 = N(target1)
    if N1 % 2 == N2 % 2:
        return True
    else:
        return False


# Astar算法的函数
def Astar(startStat):
    # open和closed存的是grid对象
    openlist = []
    closed = []
    # 初始化状态
    g = grid(startStat)
    # 检查是否有解
    if not judge(startStat, target):
        print("无解")
        exit(1)

    openlist.append(g)
    # time变量用于记录遍历次数
    time = 0
    # 当open表非空时进行遍历
    while openlist:
        # 根据启发函数值对open进行排序，默认升序
        openlist.sort(key=lambda G: G.F)
        # 找出启发函数值最小的进行扩展
        minFStat = openlist[0]
        # 检查是否找到解，如果找到则从头输出移动步骤
        if minFStat.H == 0:
            print("found and times:", time, "moves:", minFStat.G)
            minFStat.seeAns()
            break

        # 走到这里证明还没有找到解，对启发函数值最小的进行扩展
        openlist.pop(0)
        closed.append(minFStat)
        expandStats = minFStat.expand()
        # 遍历扩展出来的状态
        for stat in expandStats:
            # 将扩展出来的状态（二维列表）实例化为grid对象
            tmpG = grid(stat)
            # 指针指向父节点
            tmpG.pre = minFStat
            # 初始化时没有pre，所以G初始化时都是0
            # 在设置pre之后应该更新G和F
            tmpG.update()
            # 查看扩展出的状态是否已经存在与open或closed中
            findstat = isin(tmpG, openlist)
            findstat2 = isin(tmpG, closed)
            # 在closed中,判断是否更新
            if findstat2[0] == True and tmpG.F < closed[findstat2[1]].F:
                closed[findstat2[1]] = tmpG
                openlist.append(tmpG)
                time += 1
            # 在open中，判断是否更新
            if findstat[0] == True and tmpG.F < openlist[findstat[1]].F:
                openlist[findstat[1]] = tmpG
                time += 1
            # tmpG状态不在open中，也不在closed中
            if findstat[0] == False and findstat2[0] == False:
                openlist.append(tmpG)
                time += 1


# 用枚举类表示方向
class Direction(IntEnum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

class NumberHuaRong2(QWidget):
    """ 华容道主体 """

    def __init__(self):
        super().__init__()
        self.numbers = list(range(1, 10))
        self.blocks = []
        # 0的坐标
        self.zero_row = 0
        self.zero_column = 0
        self.disnum = 0  # 缺的数字位置
        self.gltMain = QGridLayout()
        self.cost = 0
        self.mylist = []
        self.goal = []
        self.initUI()
        self.ans = ""
        self.count = 0

    def initUI(self):
        # 设置方块间隔
        self.gltMain.setSpacing(10)

        self.onInit()

        # 设置布局
        self.setLayout(self.gltMain)
        # 设置宽和高
        self.setFixedSize(950, 950)
        # 设置标题和图标
        self.setWindowTitle('图片华容道          WASD：移动白块   R:返回   Z：解题   C:演示')
        self.setWindowIcon(QIcon("图标.png"))
        # 设置背景颜色
        self.setStyleSheet("background-color:gray;")
        self.show()

    # 初始化布局
    def onInit(self):
        # 产生顺序数组
        self.ans = ""
        self.count = 0
        self.score = 0
        self.rand = random.randint(1, 9)  # 缺的数字
        self.numbers = list(range(1, 10))
        self.numbers[self.rand - 1] = 0
        # 将数字添加到二维数组
        self.blocks = []
        for row in range(3):
            self.blocks.append([])
            for column in range(3):
                temp = self.numbers[row * 3 + column]
                # print(temp)
                if temp == 0:
                    self.zero_row = row
                    self.zero_column = column

                self.blocks[row].append(temp)
        for i in range(500):
            random_num = random.randint(0, 3)
            self.move(Direction(random_num))
        self.mylist = self.blocks.copy()
        self.updatePanel()
    # 检测按键
    def keyPressEvent(self, event):
        global ans
        key = event.key()
        if key == Qt.Key_Up or key == Qt.Key_W:
            self.move(Direction.DOWN)
            self.score += 1
        if key == Qt.Key_Down or key == Qt.Key_S:
            self.move(Direction.UP)
            self.score += 1
        if key == Qt.Key_Left or key == Qt.Key_A:
            self.move(Direction.RIGHT)
            self.score += 1
        if key == Qt.Key_Right or key == Qt.Key_D:
            self.move(Direction.LEFT)
            self.score += 1
        if key == Qt.Key_Z:
            self.solve()
            self.ans = ans
        if key == Qt.Key_C:
            mm = self.ans[self.count]
            if mm == 'w':
                self.move(Direction.DOWN)
                self.score += 1
            elif mm == 's':
                self.move(Direction.UP)
                self.score += 1
            elif mm == 'a':
                self.move(Direction.RIGHT)
                self.score += 1
            elif mm == 'd':
                self.move(Direction.LEFT)
                self.score += 1
            self.updatePanel()
            self.count += 1

        if key == Qt.Key_R:
            self.close()
            # self.f = FirstUi()
            self.f.show()
        self.updatePanel()
        if self.checkResult():
            if QMessageBox.Ok == QMessageBox.information(self, '挑战结果', '恭喜您完成挑战！\n本次挑战得分:'+str(self.score)):
                #写入得分
                with open("score.txt","a+",encoding="utf-8") as fp:
                    fp.write(str(self.score)+'\n')
                print(self.score)
                self.onInit()  # 结束后重新开始


    # 方块移动算法
    def move(self, direction):
        if direction == Direction.UP:  # 上
            if self.zero_row != 2:
                self.blocks[self.zero_row][self.zero_column] = self.blocks[self.zero_row + 1][self.zero_column]
                self.blocks[self.zero_row + 1][self.zero_column] = 0
                self.zero_row += 1
        if direction == Direction.DOWN:  # 下
            if self.zero_row != 0:
                self.blocks[self.zero_row][self.zero_column] = self.blocks[self.zero_row - 1][self.zero_column]
                self.blocks[self.zero_row - 1][self.zero_column] = 0
                self.zero_row -= 1
        if direction == Direction.LEFT:  # 左
            if self.zero_column != 2:
                self.blocks[self.zero_row][self.zero_column] = self.blocks[self.zero_row][self.zero_column + 1]
                self.blocks[self.zero_row][self.zero_column + 1] = 0
                self.zero_column += 1
        if direction == Direction.RIGHT:  # 右
            if self.zero_column != 0:
                self.blocks[self.zero_row][self.zero_column] = self.blocks[self.zero_row][self.zero_column - 1]
                self.blocks[self.zero_row][self.zero_column - 1] = 0
                self.zero_column -= 1

    def updatePanel(self):
        for row in range(3):
            for column in range(3):
                self.gltMain.addWidget(Block2(self.blocks[row][column]), row, column)
        self.setLayout(self.gltMain)

    # 检测是否完成
    def checkResult(self):
        for row in range(3):
            for column in range(3):
                if row == self.zero_row and column == self.zero_column:
                    pass
                # 值是否对应
                elif self.blocks[row][column] != row * 3 + column + 1:
                    return False

        return True

    def solve(self):
        self.goal = []
        for row in range(3):
            self.goal.append([])
            for column in range(3):
                temp = self.numbers[row * 3 + column]
                self.goal[row].append(temp)
        global target
        target = self.goal.copy()
        stat = self.mylist
        global operations
        Astar(stat)


class Block(QLabel):
    """ 数字方块 """

    def __init__(self, number):
        super().__init__()
        self.imgPath = ["D://0作业/软工实践/hrd/确定序列/" + str(zuhao) + "_" + str(i) + ".jpg" for i in range(1, 10)]
        self.number = number
        self.setFixedSize(300, 300)  # 控制窗体大小
        if self.number > 0:
            # 导入图片
            imgName = self.imgPath[number - 1]
            pix = QPixmap(imgName)
            lb1 = QLabel(self)
            lb1.setPixmap(pix)

        if self.number == 0:
            self.setStyleSheet("background-color:white;border-radius:10px;")

class Block2(QLabel):
    """ 数字方块 """

    def __init__(self, number):
        super().__init__()
        self.imgPath = ["sub" + str(i) + ".png" for i in range(1, 10)]
        self.number = number
        self.setFixedSize(300, 300)  # 控制窗体大小
        if self.number > 0:
            # 导入图片
            imgName = self.imgPath[number - 1]
            pix = QPixmap(imgName)
            lb1 = QLabel(self)
            lb1.setPixmap(pix)

        if self.number == 0:
            self.setStyleSheet("background-color:white;border-radius:10px;")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = NumberHuaRong2()
    w.show()
    sys.exit(app.exec_())