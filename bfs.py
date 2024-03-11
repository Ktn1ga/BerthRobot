# bfs
from collections import deque

# 机器人路径规划
def bfsToBerth(ch, i, j, berth,robot):
    # 初始化队列，用于存储待探索的位置及其路径
    queue = deque([((i, j), [(i, j)])]) # (最后位置，历史路径)
    # 记录已访问的位置
    visited = set([(i, j)])
    # 定义移动方向（上，下，左，右）
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    path_list_berch = []
    path_list_robot = []
    while queue:
        # 从队列中取出当前位置和到达当前位置的路径
        (x, y), path = queue.popleft()
        # 找港口
        for i in range(len(berth)):
            targetx, targety = berth[i].x, berth[i].y
            # 如果当前位置是目标位置，返回路径
            if (x, y) == (targetx, targety):
                path_list_berch.append([i,path])
        # 找机器人
        for i in range(len(robot)):
            targetx, targety = robot[i].x, robot[i].y
            # 如果当前位置是目标位置，返回路径
            if (x, y) == (targetx, targety):
                path_list_robot.append([i,path])
        # 如果找到了目标位置，返回路径
        if (len(path_list_berch)>=5 and len(path_list_robot)>=5):
            return [path_list_berch,path_list_robot]
        # 探索当前位置的所有相邻位置
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            # 检查新位置是否在ch内部并且没有被访问过
            if 0 <= nx < len(ch) and 0 <= ny < len(ch[0]) and ch[nx][ny] == '.' and (nx, ny) not in visited:
                visited.add((nx, ny))
                # 将新位置和到达新位置的路径加入队列
                queue.append(((nx, ny), path + [(nx, ny)]))
    # 如果无法到达目标，返回空列表
    return []
