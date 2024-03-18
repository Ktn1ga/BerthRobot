# from loguru import logger  # 日志
import time
import os
import sys
from bfs import robotToGoods,goodsToBerth,saveReDfs
from copy import deepcopy
import random
n = 200 # 地图大小
money = 0
boat_capacity = 0
# id = 0

robot_num = 10 # 机器人数量
boat_num = 5 # 船的数量
berth_num = 10 # 港口数量
cacheSize = 1000 # 机器人路径缓存大小

class Controller:
    def __init__(self):
        self.ch = [] # 地图
        self.timeID = 0 # 时间标号
        self.goodsID = 0 # 货物标号

        self.goodsMap =  {} # 货物字典  {货物编号，货物对象}
        self.goodsList = [] # 货物列表  (存放排序后索引)
        
        self.berthList = [i for i in range(berth_num)] # 港口列表

        self.AllStep = 0 # 总步数
        self.AllMoney = 0 # 总收益

        self.testvalue = 0

    def add_goods(self, x, y, value, zhenID):
        self.goodsMap[self.goodsID] = Goods(x, y, value, self.goodsID, zhenID)
        self.ch[x][y] = 'G'
        # self.goodsMap[self.goodsID].update() # 更新货物信息
        self.goodsList.append(self.goodsID)
        self.goodsID += 1

    def pick_goods(self,goodsID):
        self.ch[self.goodsMap[goodsID]._x][self.goodsMap[goodsID]._y] = 'X'
        self.goodsList.remove(goodsID)
        

    def del_goods(self,goodsID):
        if goodsID == -1:
            return 
        self.AllMoney -= controller.goodsMap[goodsID]._value
        self.AllStep -= controller.goodsMap[goodsID].minStep
        self.ch[self.goodsMap[goodsID]._x][self.goodsMap[goodsID]._y] = '.'
        # 防止还在列表中
        if(goodsID) in self.goodsList: self.goodsList.remove(goodsID)
        del self.goodsMap[goodsID]

controller = Controller()
class dog():
    def __init__(self):
        pass
    def say():
        print("wangwang")

# 港口
class Berth:
    def __init__(self, x=0, y=0, transport_time=0, loading_speed=0):
        self._x = x # 港口坐标
        self._y = y # 港口坐标
        self._transport_time = transport_time # 港口运输时间
        self._loading_speed = loading_speed # 港口装货速度
        
        self.score = 0 # 港口评分 评分越高越优先
        self.ability = 0 # 港口可达能力
        self.weightExpe = 0 # 港口预期装载重量
        self.weightReal = 0 # 港口实际装载重
        self.valueReal = 0 # 港口实际装载价值

        self.state = 0 # 港口状态 [0表示无船，1表示有船,2表示2艘船]

berth = [Berth() for _ in range(berth_num)]

# 机器人
class Robot:
    def __init__(self, id = 0, goods=0, startX=0, startY=0, status=0):
        self._id = 0 # 机器人编号
        self._goods = goods # 机器人是否携带物品[0无，1有]
        self._x = startX # 机器人坐标
        self._y = startY # 机器人坐标
        self._status = status # 机器人状态 [0表示回复中，1表示正常]
        
        self.last_x = startX
        self.last_y = startY
        self.goodID = -1 # 机器人携带的货物编号
        self.berthID = -1 # 机器人目标港口编号
        self.pathToget = [] # 机器人的取货路径规划
        self.pathTopull = [] # 机器人的卸货路径规划
        self.pathCache = [] # 机器人的历史路径缓存（预防碰撞）
        self.forceStop = 0 # 机器人停止计数

    def go(self):
        # if(self._id==7):
        #     logger.info(self._id)
        #     logger.info("({},{})".format(self._x,self._y))
        #     logger.info(self._goods)
        #     logger.info(self._status)
        #     logger.info(self.goodID)
        #     logger.info(self.pathToget)
        #     logger.info(self.pathTopull)
        
        # 强制休息
        if self.forceStop:
            self.forceStop = 0
            return 0
        
        #  不用去了 超时还没找到目标
        if(self._goods == 0 and self.goodID !=-1 and controller.timeID - controller.goodsMap[self.goodID]._zhenID>1500):
            if self.goodID in controller.goodsList:
                controller.del_goods(self.goodID) # 移除货物
            self.goodID = -1
            self.pathToget.clear()
            self.pathTopull.clear()
            return 0
        
        # 机器人取货
        if(self._goods == 0 and self.goodID != -1 and
           self._x == controller.goodsMap[self.goodID]._x and self._y == controller.goodsMap[self.goodID]._y
           and controller.ch[self._x][self._y] == 'X'):
            for berthNum in controller.goodsMap[self.goodID].pathToBerth.keys():
                self.berthID = berthNum
                self.pathTopull = controller.goodsMap[self.goodID].pathToBerth[berthNum]
                self.pathTopull.reverse()
                break
            print("get", self._id)
            sys.stdout.flush()
            berth[self.berthID].weightExpe += 1
            controller.ch[self._x][self._y] = '.' # 复原
            # return 0

        # 机器人卸货
        if (self._goods == 1 and self.goodID != -1 and
            (controller.ch[self._x][self._y] == 'B')
           ):
            print("pull", self._id)
            sys.stdout.flush()
            berth[self.berthID].weightReal += 1
            berth[self.berthID].weightExpe -= 1

            controller.testvalue +=  controller.goodsMap[self.goodID]._value
            controller.del_goods(self.goodID) # 移除货物
            self.goodID = -1
            self.pathToget.clear()
            self.pathTopull.clear()
            # 这里是不是就要找新物品了
            # return 0
        
        # 机器人移动取货
        if(self.pathToget is not None and len(self.pathToget) != 0):
            # 判断是否成功移动
            # if(self._x == self.last_x and self._y == self.last_y):
            #     if self.pathCache != []:
            #         last_pos = self.pathCache.pop()
            #     else:
            #         last_pos = (self._x, self._y)
            #     self.pathToget.append(last_pos)

            #更新缓存
            if (self.last_x,self.last_y)!= (self._x,self._y):
               self.pathCache.append((self.last_x,self.last_y))
            if(len(self.pathCache)>cacheSize):
                del self.pathCache[0]
            self.last_x = self._x
            self.last_y = self._y

            self.nextpos = self.pathToget.pop()
            while(self.nextpos == (self._x,self._y) and len(self.pathToget) != 0):
                self.nextpos = self.pathToget.pop()

            fx = 0 # 方向 0右 1左 2上 3下.左边是题目说的，xy反了，看了好久 好坑
            # 路重新寻址
            # 路重新寻址
            if(self.nextpos[0]-self._x != 0 and self.nextpos[1]-self._y != 0):
                self.pathTopull = saveReDfs(controller.ch, self._x, self._y, self.pathTopull, set())
                if(len(self.pathTopull)!=0): self.nextpos = self.pathTopull.pop()
            if(self.nextpos[0] > self._x):
                print("move", self._id, 3)
                sys.stdout.flush()
            if(self.nextpos[0] < self._x):
                print("move", self._id, 2)
                sys.stdout.flush()
            if(self.nextpos[1] < self._y):
                print("move", self._id, 1)
                sys.stdout.flush()
            if(self.nextpos[1] > self._y):
                print("move", self._id, 0)
                sys.stdout.flush()
            return 0
        # 机器人移动卸货
        if(self.pathTopull is not None and len(self.pathTopull) != 0):
            # 判断是否成功移动
            if(self._x == self.last_x and self._y == self.last_y):
                if self.pathCache != []:
                    last_pos = self.pathCache.pop()
                else:
                    last_pos = (self._x, self._y)
                # self.pathToget.append(last_pos)     ####get???
                self.pathTopull.append(last_pos)

            #更新缓存
            if (self.last_x,self.last_y)!= (self._x,self._y):
               self.pathCache.append((self.last_x,self.last_y))
            if(len(self.pathCache)>cacheSize):
                del self.pathCache[0]
            self.last_x = self._x
            self.last_y = self._y

            self.nextpos = self.pathTopull.pop()
            while(self.nextpos == (self._x,self._y) and len(self.pathTopull) != 0):
                self.nextpos = self.pathTopull.pop()

            # 路重新寻址
            if(self.nextpos[0]-self._x != 0 and self.nextpos[1]-self._y != 0):
                self.pathTopull = saveReDfs(controller.ch, self._x, self._y, self.pathTopull, set())
                if(len(self.pathTopull)!=0): self.nextpos = self.pathTopull.pop()
            fx = 0 # 方向 0右 1左 2上 3下

            if (self.nextpos[0] > self._x):
                print("move", self._id, 3)
                sys.stdout.flush()
            if (self.nextpos[0] < self._x):
                print("move", self._id, 2)
                sys.stdout.flush()
            if (self.nextpos[1] < self._y):
                print("move", self._id, 1)
                sys.stdout.flush()
            if (self.nextpos[1] > self._y):
                print("move", self._id, 0)
                sys.stdout.flush()
            return 0

        
        if self._goods == 0 and self.pathToget==[]:
            self.goodID = -1 # 刷新
robot = [Robot() for _ in range(robot_num)]

# 船
class Boat:
    def __init__(self, num=0, status=0):
        self._num = num # 船的编号
        self._status = status # 船的状态
        self._pos = -1 # 船的泊位编号
        self._capacity = 0 # 船的最大承重量

        self.goalPos = -1 # 船的目标泊位编号
        self.weight = 0    # 船的载货重量
        self.berthTime = 0 # 船的停泊时间
    def go(self):
        # logger.info("boat:{}".format(self._num))
        # logger.info("status:{}".format(self._status))
        # logger.info("pos:{}".format(self._pos))
        # logger.info("boat:{}  status:{}  pos:{}".format(self._num,self._status,self._pos))
        if self._status == 0: # 在路上
            return 0
        elif self._status == 1 and self._pos!=-1: # 在码头装货
            # 输出 berth[self._pos]._loading_speed
            self.weight = min(berth[self._pos].weightReal,(controller.timeID - self.berthTime) * berth[self._pos]._loading_speed)
            if(self.weight>= self._capacity or controller.timeID + berth[self._pos]._transport_time>= 14900
                or self._pos not in controller.berthList[0:5] ):
                berth[self._pos].weightReal -= self.weight
                berth[self._pos].state -= 1
                print("go",self._num)
                sys.stdout.flush()

        elif self._status == 1 and self._pos== -1 or self._status== 2 :  #在虚拟点
            for i in controller.berthList: # 选择最优港口
                if(berth[i].score >= 0.2 * boat_capacity and berth[i].state < 1
                   # or berth[i].score >= 1.8 * boat_capacity and berth[i].state < 2
                ) :
                    self.goalPos = i
                    berth[self.goalPos].state +=1
                    print("ship",self._num,self.goalPos)
                    sys.stdout.flush()
                    self.berthTime = controller.timeID + berth[self.goalPos]._transport_time  # 记录停泊时间
                    return 0
        return 0

boat = [Boat(i) for i in range(boat_num)]


# 货物（100帧15个,150*15)
class Goods:
    def __init__(self, x=0, y=0, value=0, id = 0,zhenID=0):
        self._x = x # 货物坐标
        self._y = y # 货物坐标
        self._value = value # 货物价值
        self._id = id # 货物编号
        self._zhenID = zhenID # 货物生成时间

        # 以下信息需要更新
        self.pathToBerth = {} # 到各个港口的最短路径 (i,path)
        self.minStep = 0
        self.score = 0 # 收益评分

    def update(self):
        # 到最近N个港口的路径规划
        ans_berch = goodsToBerth(controller.ch, self._x, self._y, berth, N = 1)
        # 如果没有可达的港口
        if(ans_berch == []):
            if controller.goodsList !=[] and self._id in controller.goodsList:
                controller.del_goods(self._id)
            return
        
        # 更新货物-码头路由表
        for i in range(len(ans_berch)):
            self.pathToBerth[ans_berch[i][0]] = ans_berch[i][1] # 更新路径
        
        self.minStep = len(ans_berch[0][1]) # 最短路径

        # 更新港口得分
        for i in range(len(ans_berch)):
            berth[ans_berch[i][0]].ability += 1/len(ans_berch[i][1]) # 只要可达就加分，但路程越长加的越少
        
        # 更新总体货物评分
        controller.AllMoney = controller.AllMoney + self._value 
        controller.AllStep = controller.AllStep + len(ans_berch[0][1])
        
        # 更新该货物评分
        # self.score = 1/len(ans_berch[0][1])
        # self.score = self._value
        self.score = self._value - (len(ans_berch[0][1]))*(controller.AllMoney/controller.AllStep)



# 初始化
def Init():
    # 读取地图
    for i in range(0, n):
        line = input()
        line = line.replace('A', '.') # 将A替换为 “.”
        controller.ch.append(list(line))
    
    # 读取港口信息
    for i in range(berth_num):
        line = input()
        berth_list = [int(c) for c in line.split(sep=" ")]
        id = berth_list[0]
        berth[id]._x = berth_list[1]
        berth[id]._y = berth_list[2]
        berth[id]._transport_time = berth_list[3]
        berth[id]._loading_speed = berth_list[4]
    
        # logger.info("transport_time:{}".format(berth[id]._transport_time))
    
    global boat_capacity
    boat_capacity = int(input()) # 读取船的载货量
    for bo in boat:
        bo._capacity = boat_capacity
    okk = input() # 读取OK
    print("OK") # 输出OK
    sys.stdout.flush()


def Input():
    zhenID, money = map(int, input().split(" "))
    controller.timeID = zhenID
    num = int(input())
    for i in range(num):
        x, y, val = map(int, input().split())
        controller.add_goods(x,y,val,zhenID)
    for i in range(robot_num):
        robot[i]._id = i
        robot[i]._goods, robot[i]._x, robot[i]._y, robot[i]._status = map(int, input().split())
    for i in range(boat_num):
        boat[i]._status, boat[i]._pos = map(int, input().split())
    okk = input()
    return zhenID

def Update():
    # 更新货物地图，删除超时货物
    # logging.info("goodsList:{}".format(len(controller.goodsList)))
    for goodsId in controller.goodsList:
        if controller.timeID - controller.goodsMap[goodsId]._zhenID > 1000: # 超时货物
            controller.del_goods(goodsId)
    # 更新港口排序
    for id in range(berth_num):    
        berth[id].score = berth[id].weightExpe + berth[id].weightReal
        # berth[id].score = berth[id].ability + berth[id].weightExpe + 10 * berth[id].weightReal
    
    controller.berthList.sort(key=lambda id: berth[id].score,reverse=True) # 港口评分排序(从大到小)

    # logger.info("timeID:{}".format(controller.timeID))
    # logger.info("berthList:{}".format(controller.berthList))
    # boat_poslist = [boat[i]._pos for i in range(boat_num)]
    # logger.info("boat_poslist:{}".format(boat_poslist))
    # for id in range(berth_num):
    #     logger.info("berth:{} score:{} ability:{}  weightExpe:{} weightReal:{}".format(id,berth[id].score,berth[id].ability,berth[id].weightExpe,berth[id].weightReal))

    # 刷新机器人目标
    for id in range(robot_num):
        # 如果机器人有任务或状态异常，就不寻找目标
        if robot[id].goodID != -1 or robot[id]._status == 0: continue
        # if  robot[id]._status == 0: continue

        # 寻找距离机器人最近的N个货物
        search_num = len(controller.goodsList)/10
    
        ans = robotToGoods(controller,robot[id]._x,robot[id]._y,N = search_num)
        # logger.info(ans)
        if ans == []: continue
        # 解析答案，选择N个货物中路径（取货+送货）最小的一个
        maxScore = -100000
        choiceGoodsID = -1
        choicePath = []
        for oneAns in ans: # pos:货物坐标 path:路径
            currentID = oneAns[0]
            currentPath = oneAns[1]
            currentScore = controller.goodsMap[currentID].score
            # 选择最短的路径 or 最高的价值？
            if currentScore > maxScore:
                maxScore = currentScore
                choiceGoodsID = currentID
                choicePath = currentPath
        # 更新机器人目标
        robot[id].goodID = choiceGoodsID
        controller.goodsMap[robot[id].goodID].update() # 更新货物信息
        # 机器人取货路径规划
        robot[id].pathToget = choicePath
        robot[id].pathToget.reverse()
        controller.pick_goods(choiceGoodsID) # 移除货物

        # # # 重新规划送货路径
        # if robot[id].goodID != -1 and robot[id]._goods == 1 :
        # # 到最近N个港口的路径规划
        #     robot[id].pathTopull = goodsToBerth(controller.ch, robot[id]._x,robot[id]._y, berth, N=1)


def Safe():
    # 碰撞检测
    occupied_points = set()
    # 添加所有机器人现在坐标
    for robot_id in range(robot_num):
        occupied_points.add((robot[robot_id]._x, robot[robot_id]._y))

    for robot_id in range(robot_num):
        # 移除上一个机器人上一时刻的状态
        if( robot_id > 0 and robot[robot_id-1].forceStop != 1
           and (robot[robot_id-1]._x, robot[robot_id-1]._y) != (robot[robot_id-1].last_x, robot[robot_id-1].last_y)
           and (robot[robot_id-1]._x, robot[robot_id-1]._y) in occupied_points
           ):
            occupied_points.remove((robot[robot_id-1]._x, robot[robot_id-1]._y))
        # 选择路径属性和目标路径
        if robot[robot_id]._goods == 0:
            path_attr_name = 'pathToget'
        elif robot[robot_id]._goods == 1:
            path_attr_name = 'pathTopull'
        else:
            return
        # 获取当前目标位置
        current_path = getattr(robot[robot_id], path_attr_name)
        if current_path:  # 如果路径非空
            pos = current_path[-1]  # 获取路径上最后一个位置
            # 路径规划是当前位置
            while(pos == (robot[robot_id]._x,robot[robot_id]._y) and len(current_path) != 0):
                pos = current_path.pop()
        else:
            continue  # 如果没有路径，则跳过当前机器人

        # 检查是否已经被占用
        if pos not in occupied_points: # 如果没有碰撞
            occupied_points.add(pos)
            continue
        else: # 如果有碰撞
            new_path = saveReDfs(controller.ch, robot[robot_id]._x, robot[robot_id]._y, getattr(robot[robot_id], path_attr_name), occupied_points)
            # 如果新路径为空，说明没有找到新路径
            if new_path == []:
                # robot[robot_id].forceStop = 1
                # # 先找缓存，回退
                if(robot[robot_id].pathCache!=[]):
                    pos = robot[robot_id].pathCache.pop()
                    pos1 = robot[robot_id].pathCache.pop()
                    if(robot[robot_id]._goods==0):
                        robot[robot_id].pathToget.append(pos)
                        robot[robot_id].pathToget.append(pos1)
                    else:
                        robot[robot_id].pathTopull.append(pos)
                        robot[robot_id].pathTopull.append(pos1)

                new_path = saveReDfs(controller.ch, pos1[0], pos1[1],
                                     getattr(robot[robot_id], path_attr_name), occupied_points)
                setattr(robot[robot_id], path_attr_name, deepcopy(new_path))  # 更新路径

            else:
                setattr(robot[robot_id], path_attr_name, deepcopy(new_path))  # 更新路径
            # 获取当前目标位置
            current_path = getattr(robot[robot_id], path_attr_name)
            if current_path:  # 如果路径非空
                pos = current_path[-1]  # 获取路径上最后一个位置
            else:
                continue  # 如果没有路径，则跳过当前机器人
            occupied_points.add(pos)

def Output():
    # 输出
    for i in range(robot_num):
        robot[i].go()
    for i in range(boat_num):
        boat[i].go()
    print("OK")
    sys.stdout.flush()

if __name__ == "__main__":
    Init()

    for k in range(1, 15001):
        id = Input()
        # logger.info("id:{}   testvalue:{}".format(id,controller.testvalue))
        Update()
        Safe()
        Output()