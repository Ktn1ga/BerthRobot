import sys
import queue
import random
from bfs import bfsToBerth

N = 210 

n = 200 # 地图大小
money = 0
boat_capacity = 0
id = 0
ch = [] # 地图

robot_num = 10 # 机器人数量
boat_num = 5 # 船的数量
berth_num = 10 # 港口数量

goodList = []
goodID = 0 # 货物编号
goodNum = 0 # 货物总数

AllStep = 0 # 总步数
AllMoney = 0 # 总收益

cacheSize = 10 # 机器人路径缓存大小

# 港口
class Berth:
    def __init__(self, x=0, y=0, transport_time=0, loading_speed=0):
        self.x = x # 港口坐标
        self.y = y # 港口坐标
        self.transport_time = transport_time # 港口运输时间
        self.loading_speed = loading_speed # 港口装货速度
        
        self.score = 0 # 港口评分
        self.state = 0 # 港口状态
berth = [Berth() for _ in range(berth_num)]

# 机器人
class Robot:
    def __init__(self, id = 0, goods=0, startX=0, startY=0, status=0):
        self.id = 0 # 机器人编号
        self.goods = goods # 机器人是否携带物品[0无，1有]
        self.x = startX # 机器人坐标
        self.y = startY # 机器人坐标
        self.status = status # 机器人状态 [0表示回复中，1表示正常]

        self.goodID = -1 # 机器人携带的货物编号
        self.pathToget = [] # 机器人的取货路径规划
        self.pathTopull = [] # 机器人的卸货路径规划
        self.pathCache = [] # 机器人的历史路径缓存（预防碰撞）

    def go(self):
        # 机器人取货
        if(self.goods ==0 and self.x == goodList[self.goodID].x and self.y == goodList[self.goodID].y):
            print("get", self.id)
            sys.stdout.flush()
            return 0
        # 机器人卸货
        if(self.goods ==1 and 
           self.x == berth[goodList[self.goodID].stepToBerth[0][0]].x and self.y == berth[goodList[self.goodID].stepToBerth[0][0]].y):
            print("pull", self.id)
            sys.stdout.flush()
            return 0
        # 机器人移动
        if(len(self.pathToget) != 0):
            self.nextpos = self.pathToget.pop()
            self.pathCache.append(self.nextpos)
            if(len(self.pathCache)>cacheSize):
                del self.pathCache[0]
            print("move", self.id, 1)
            sys.stdout.flush()
           
robot = [Robot() for _ in range(robot_num)]

# 船
class Boat:
    def __init__(self, num=0, status=0):
        self.num = num # 船的编号
        self.status = status # 船的状态
        self.pos = 0 # 船的泊位编号
        self.capacity = 0 # 船的载货量
boat = [Boat() for _ in range(boat_num)]


# 货物（100帧15个,150*15)
class Goods:
    def __init__(self, x=0, y=0, value=0,id = 0):
        self.x = x # 货物坐标
        self.y = y # 货物坐标
        self.value = value # 货物价值
        self.id = id # 货物编号

        # 以下信息需要更新
        self.goalBerth = -1
        self.goalRobot = -1
        self.stepToBerth = [] # 到各个港口的最短步数 {i,path}
        self.stepToRobot = [] # 最近机器人的最短步数
        self.score = 0 # 收益评分

    def update(self):
        # 到最近港口的路径规划
        ans_berch,ans_robot = bfsToBerth(ch, self.x, self.y, berth,robot)
        # 更新到港口的最短路径
        self.goalBerth = ans_berch[0][0]
        MinNumStepToBerch = len(ans_berch[0][1])
        # 更新到所有机器人的最短路径
        self.goalRobot = ans_robot[0][0]
        MinNumStepToRobot = len(ans_robot[0][1])
        # 更新货物评分
        global AllMoney, AllStep
        AllMoney = AllMoney + self.value
        AllStep = AllStep + MinNumStepToBerch + MinNumStepToRobot
        self.score = self.value
        # self.score = self.value - (self.stepToBerth.size() + 1)*(AllMoney/AllStep)


# 初始化
def Init():
    # 读取地图
    for i in range(0, n):
        line = input()
        ch.append([c for c in line.split(sep=" ")]) 
    # 读取港口信息
    for i in range(berth_num):
        line = input()
        berth_list = [int(c) for c in line.split(sep=" ")]
        id = berth_list[0]
        berth[id].x = berth_list[1]
        berth[id].y = berth_list[2]
        berth[id].transport_time = berth_list[3]
        berth[id].loading_speed = berth_list[4]
    boat_capacity = int(input()) # 读取船的载货量
    okk = input() # 读取OK
    print("OK") # 输出OK
    sys.stdout.flush()

def Input():
    zhenID, money = map(int, input().split(" "))
    num = int(input())
    for i in range(num):
        x, y, val = map(int, input().split())
        goodList.append(Goods(x, y, val,goodID))
        goodID += 1
        goodNum = goodNum+1 # 货物总数
    for i in range(robot_num):
        robot[i].id = i
        robot[i].goods, robot[i].x, robot[i].y, robot[i].status = map(int, input().split())
    for i in range(boat_num):
        boat[i].status, boat[i].pos = map(int, input().split())
    okk = input()
    return zhenID


LastflushGoodNum = 0 # 上一次刷新货物的标号

def Update():
    global LastflushGoodNum
    # 刷新货物排序
    if LastflushGoodNum != goodNum:
        for i in range(LastflushGoodNum,goodNum):
            goodList[i].update()
        goodList.sort(key=lambda x: x.score, reverse=True)
    LastflushGoodNum = goodNum
    # 刷新机器人状态
    for i in range(robot_num):
        if robot[i].status == 1:
            robot[i].status = 0
            robot[i].goods = 0
    pass

def Safe():
    # 安全检测
    pass

def Output():
    # 输出
    for i in range(robot_num):
        robot[i].go()
    print("OK")
    sys.stdout.flush()


if __name__ == "__main__":
    Init()
    for zhen in range(1, 15001):
        zhenID = Input()
        # Update()
        # Safe()
        # Output()
