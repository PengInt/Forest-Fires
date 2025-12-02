import random

import pygame, math

fireSpreadDist = 3
size = (400, 400)    # 25x25
gridSize = 16
screen = pygame.display.set_mode(size, vsync=1)

class gridsquare:
    def __init__(self) -> None:
        self.stats = []
    def avg(self) -> float:
        t = 0
        for i in self.stats:
            t += i
        if len(self.stats):
            t /= len(self.stats)
        return t

def sim(dir, f) -> list:
    grid = []
    for x in range(0, size[0]):
        grid.append([])
        for y in range(0, size[1]):
            grid[x].append(gridsquare())
    for i in range(360):
        t = 0
        p = [13, 13]
        d = i * math.pi / 180
        v = [math.cos(d)/10, math.sin(d)/10]
        w = [math.cos(dir)*f/160, math.sin(dir)*f/160]
        pP = [0, 0]
        while t <= 3:
            t += 0.1
            v[0] += w[0]
            v[1] += w[1]
            p[0] += v[0]
            p[1] += v[1]
            if math.floor(p[0]+0.5) != pP[0] or math.floor(p[1]+0.5) != pP[1]:
                pP[0] = math.floor(p[0]+0.5)
                pP[1] = math.floor(p[1]+0.5)
                grid[math.floor(p[0]+0.5)][math.floor(p[1]+0.5)].stats.append((3-t)/3)
    stats = []
    for i in grid:
        stats.append([])
        for j in i:
            stats[grid.index(i)].append(j.avg())
    return stats

def draw() -> None:
    stats = sim(random.uniform(0, 1)*2*math.pi, random.uniform(0, 1))
    for x in range(0, size[0], gridSize):
        for y in range(0, size[1], gridSize):
            pygame.draw.rect(screen, (stats[int(x/gridSize)][int(y/gridSize)]*255, 0, 255-stats[int(x/gridSize)][int(y/gridSize)]*255), (x, y, gridSize, gridSize))
    pygame.display.update()

frame = 0
running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
    if frame == 10:
        draw()
        frame = 0
    frame += 1

pygame.quit()