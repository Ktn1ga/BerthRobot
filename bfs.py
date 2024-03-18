# bfs
# from loguru import logger  # 日志
from collections import deque
import random
# 路径规划: 机器人到货物
def robotToGoods(controller, i, j, N):
    ch = controller.ch
    count = 0
    # 初始化队列，用于存储待探索的位置及其路径
    queue = deque([((i, j), [(i, j)])]) # (最后位置，历史路径)
    # # 记录已访问的位置
    visited = set([(i, j)])
    # 定义移动方向（上，下，左，右）
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    path_list_goods = []
    while queue:
        # count += 1
        # if(count > 2000*200): #截至搜索的条件
        #     return []
        # 从队列中取出当前位置和到达当前位置的路径
        (x, y), path = queue.popleft()
        # 找货物
        if ch[x][y] == 'G':
            # 如果当前位置是货物，先确认货物ID
            goodsIdForRobot = -1
            for itr_goodsId in controller.goodsList:
                if(controller.goodsMap[itr_goodsId]._x == x and controller.goodsMap[itr_goodsId]._y == y):
                    goodsIdForRobot = itr_goodsId
                    break
            # 如果货物不能及时获取，不加入
            if(controller.timeID - controller.goodsMap[goodsIdForRobot]._zhenID + len(path) > 1000):
                continue
            path.pop(0)
            path_list_goods.append([goodsIdForRobot,path])
        # 如果找到了目标位置，返回路径
        if len(path_list_goods) >= N:
            return path_list_goods
        # 探索当前位置的所有相邻位置
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            # 检查新位置是否在ch内部并且没有被访问过
            if (0 <= nx < len(ch) and 0 <= ny < len(ch[0]) 
                and (ch[nx][ny] == '.' or ch[nx][ny] == 'B' or ch[nx][ny] == 'G' or ch[nx][ny] == 'X')
                and ((nx, ny) not in visited)
                ):
                visited.add((nx, ny))
                # 将新位置和到达新位置的路径加入队列
                queue.append(((nx, ny), path + [(nx, ny)]))
    return []

# 路径规划: 货物到港口
def goodsToBerth(ch, i, j, berth,N):
    # 初始化队列，用于存储待探索的位置及其路径
    queue = deque([((i, j), [(i, j)])]) # (最后位置，历史路径)
    # # 记录已访问的位置
    visited = set([(i, j)])
    # 定义移动方向（上，下，左，右）
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    path_list_berch = []
    while queue:
        # 从队列中取出当前位置和到达当前位置的路径
        (x, y), path = queue.popleft()
        # 找港口 
        for i in range(len(berth)):
            targetx, targety = berth[i]._x, berth[i]._y
            # 如果当前位置是目标位置，返回路径
            if (x, y) == (targetx, targety):
                path.pop(0)
                path_list_berch.append([i,path])
        # 如果找到了目标位置，返回路径
        if len(path_list_berch) >= N:
            return path_list_berch
        # 探索当前位置的所有相邻位置
        for dx, dy in directions:
            nx, ny = x + dx, y + dy            
            # 检查新位置是否在ch内部并且没有被访问过
            if (0 <= nx < len(ch) and 0 <= ny < len(ch[0]) 
                and (ch[nx][ny] == '.' or ch[nx][ny] == 'B' or ch[nx][ny] == 'G' or ch[nx][ny] == 'X')
                and ((nx, ny) not in visited)
                ):
                visited.add((nx, ny))
                # 将新位置和到达新位置的路径加入队列
                queue.append(((nx, ny), path + [(nx, ny)]))
    return []

# 路径规划: 碰撞时绕路
def saveReDfs(ch, i, j, ori_list, occupied_points):
    # 初始化队列，用于存储待探索的位置及其路径
    queue = deque([((i, j), [(i, j)])]) # (最后位置，历史路径)
    # # 记录已访问的位置
    visited = set([(i, j)])
    visited.update(occupied_points)

    #  判断机器人的初始位置，选择不同的方向
    directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]

    while queue:
        # 从队列中取出当前位置和到达当前位置的路径
        (x, y), path = queue.popleft()
        if (x, y) in ori_list and (x,y) not in occupied_points and (x,y) != (i,j):
            path.pop(0)
            return ori_list[0:ori_list.index((x,y))] + path[::-1]
        # 探索当前位置的所有相邻位置
        for dx, dy in directions:
            nx, ny = x + dx, y + dy            
            # 检查新位置是否在ch内部并且没有被访问过
            if (0 <= nx < len(ch) and 0 <= ny < len(ch[0]) 
                and (ch[nx][ny] == '.' or ch[nx][ny] == 'B' or ch[nx][ny] == 'G' or ch[nx][ny] == 'X')
                and ((nx, ny) not in visited)
                ):
                visited.add((nx, ny))
                # 将新位置和到达新位置的路径加入队列
                queue.append(((nx, ny), path + [(nx, ny)]))
    return []

def test_goodToberth():
    print("test_goodToberth")
    # 港口
    class Berth:
        def __init__(self, x=0, y=0,):
            self._x = x # 港口坐标
            self._y = y # 港口坐标
    berth = [Berth(10,10) for _ in range(1)]
    n = 11
    ch = [['.' for i in range(n)] for j in range(n)]
    i = 0
    j = 0

    N = 1
    ans = goodsToBerth(ch, i, j, berth,N)
    print(ans)

def test_saveReDfs():
    n = 11
    ch = [['.' for i in range(n)] for j in range(n)]
    occupied_points = [(1,1)]
    ori_list = [(1,1)]
    i = 0
    j = 1
    newList = saveReDfs(ch, i, j, ori_list, occupied_points)
    print(ori_list)
    print(newList)

if __name__ == "__main__":
    print("bfs")
    # test_goodToberth()
    test_saveReDfs()