import pygame, random, math

pygame.init()

size = (320, 320)
bottomBar = 50
scale = 2
fireSpread = 0.125    # fireSpread = fireSpread/dist
fireSpreadDist = 3
firePutOut = 0.005
fireChance = 0.000001
treeRepop = 1
chunkSize = fireSpreadDist

weather = {
    'wind':
        {'direction': 0, 'speed': 0},
    'precipitation':
        {'amount': 0.0},
    'temperature':
        {'current offset': 0, 'minimum offset': -10, 'maximum offset': 10},
    'season':
        {'current': 0, 'wind': 1.75, 'precipitation': 1.5, 'temperature': -30.0, 'yearly temperature range': [-30, 30]}}

screen = pygame.display.set_mode((size[0] * scale, size[1] * scale + bottomBar))

def Sigmoid(n):
    return 1/(1+(math.e**(-n)))

def tick():
    weather['season']['current'] += 1
    if weather['season']['current'] > 365:
        weather['season']['current'] = 1
    weather['season']['wind'] = math.cos(math.pi * (weather['season']['current'] * 2 / 365 + 1)) + 1
    weather['season']['wind'] *= 7/8
    weather['season']['precipitation'] = math.cos(math.pi * (weather['season']['current'] * 2 / 365 + 1)) + 1
    weather['season']['precipitation'] *= 3/4
    weather['season']['temperature'] = math.cos(math.pi * (weather['season']['current'] * 2 / 365 + 1)) * (math.fabs(weather['season']['yearly temperature range'][0]) + math.fabs(weather['season']['yearly temperature range'][1])) / 2 + weather['season']['yearly temperature range'][0] + weather['season']['yearly temperature range'][1]
    weather['wind']['direction'] += random.uniform(-10, 10)
    if (weather['wind']['direction'] >= 360):
        weather['wind']['direction'] -= 360
    elif (weather['wind']['direction'] <= 0):
        weather['wind']['direction'] += 360
    weather['wind']['speed'] += random.uniform(-0.2, 0.2)
    weather['wind']['speed'] = max(0, min(1, weather['wind']['speed']))
    weather['precipitation']['amount'] += random.uniform(-0.2, 0.2)
    weather['precipitation']['amount'] = max(0, min(1, weather['precipitation']['amount']))
    weather['temperature']['current offset'] += Sigmoid(random.uniform(-5, 5)) - 0.5
    if weather['temperature']['current offset'] > weather['temperature']['maximum offset']:
        weather['temperature']['current offset'] = weather['temperature']['maximum offset']
    elif weather['temperature']['current offset'] < weather['temperature']['minimum offset']:
        weather['temperature']['current offset'] = weather['temperature']['minimum offset']

class Tree:
    trees = []
    chunks = {}
    def chunkToStr(this, offset):
        return str(chunkSize * math.floor(this.position[0] / (fireSpreadDist + 1)) + offset[0] * chunkSize) + ',' + str(chunkSize * math.floor(this.position[1] / (fireSpreadDist + 1)) + offset[1] * chunkSize)
    def __init__(this):
        this.position = (random.uniform(0, 1)*size[0], random.uniform(0, 1)*size[1])
        this.trees.append(this)
        this.onFire = False
        this.strucInteg = 1
        this.chunk = this.chunkToStr((0, 0))
        this.neighboringChunks = []
        for x in range(-1, 2):
            for y in range(-1, 2):
                this.neighboringChunks.append(this.chunkToStr((x, y)))
        if this.chunk in this.chunks:
            this.chunks[this.chunk].append(this)
        else:
            this.chunks[this.chunk] = [this]
    def setFire(this):
        this.onFire = True
    def putOutFire(this):
        this.onFire = False
    def die(this):
        this.trees.remove(this)
    def findProxyTrees(this):
        found = []
        chunks = []
        dir = weather['wind']['direction'] / 180 * math.pi
        spd = weather['wind']['speed']
        for i in this.neighboringChunks:
            try:
                for j in this.chunks[i]:
                    chunks.append(j)
            except KeyError:
                pass
        for index, tree in enumerate(chunks):
            dX = this.position[0] - tree.position[0]
            dY = this.position[1] - tree.position[1]
            dist = ((dX + math.cos(dir) * spd) ** 2 + (dY + math.sin(dir) * spd) ** 2) ** 0.5
            if dist <= fireSpreadDist and tree != this:
                found.append([tree, dist])
        return found
    def fireTick(this):
        this.strucInteg -= random.uniform(0, 0.1)
        for tree in this.findProxyTrees():
            temp = weather['season']['temperature'] + weather['temperature']['current offset']
            if fireSpread/tree[1] + (temp - 15) / 1320 - (weather['precipitation']['amount'] * weather['season']['precipitation'])/30 >= random.uniform(0, 1):
                tree[0].setFire()
        temp = weather['season']['temperature'] + weather['temperature']['current offset']
        if random.uniform(0, 1) <= firePutOut - (temp - 15) / 1320 + (weather['precipitation']['amount'] * weather['season']['precipitation'])/3:
            this.putOutFire()
        if this.strucInteg <= 0:
            this.die()
    def tick(this):
        if not this.onFire:
            this.strucInteg += random.uniform(0, 0.025)
            if this.strucInteg > 1:
                this.strucInteg = 1
        else:
            this.fireTick()

font = pygame.font.Font('DroidSansMono.ttf', 15)

def draw(fire):
    bottom = size[1] * scale
    pygame.draw.rect(screen, (0, 0, 0), (0, 0, size[0] * scale, size[1] * scale))
    pygame.draw.rect(screen, (255, 255, 255), (0, bottom, size[0] * scale, bottomBar))
    soFarWidth = 5
    textSurfaceDay = font.render(f'Day: {weather['season']['current']}', True, (0, 0, 0))
    textRect = textSurfaceDay.get_rect()
    textRect.topleft = (soFarWidth, bottom + 5)
    soFarWidth += 100
    screen.blit(textSurfaceDay, textRect)
    textSurfaceRain = font.render(f'Precipitation:', True, (0, 0, 0))
    textRect = textSurfaceRain.get_rect()
    pygame.draw.rect(screen, (51, 153, 255), [soFarWidth + textRect.size[0] + 10, bottom + 5 + 15 - math.ceil(weather['precipitation']['amount'] * 15), 10, math.ceil(weather['precipitation']['amount'] * 15)])
    textRect.topleft = (soFarWidth, bottom + 5)
    soFarWidth += 175
    screen.blit(textSurfaceRain, textRect)
    textSurfaceRain = font.render(f'Temperature:', True, (0, 0, 0))
    textRect = textSurfaceRain.get_rect()
    temp = weather['season']['temperature'] + weather['temperature']['current offset']
    pygame.draw.rect(screen, (round((temp/80 + 0.5) * 255), 0, round(255 - (temp/80 + 0.5) * 255)), [soFarWidth + textRect.size[0] + 10, bottom + 5 + 15 - math.ceil((temp / 80 + 0.5) * 15), 10, math.ceil((temp / 80 + 0.5) * 15)])
    textRect.topleft = (soFarWidth, bottom + 5)
    soFarWidth += 150
    screen.blit(textSurfaceRain, textRect)
    textSurfaceRain = font.render(f'Wind:', True, (0, 0, 0))
    textRect = textSurfaceRain.get_rect()
    dir = weather['wind']['direction'] / 180 * math.pi
    spd = weather['wind']['speed']
    pygame.draw.circle(screen, (0, 0, 0), (soFarWidth + 75, bottom + 25), 15, 2)
    pygame.draw.line(screen, (0, 0, 0), (soFarWidth + 75, bottom + 25), (soFarWidth + 75 + math.cos(dir) * spd * 15, bottom + 25 + math.sin(dir) * spd * 15))
    textRect.topleft = (soFarWidth, bottom + 5)
    screen.blit(textSurfaceRain, textRect)
    for tree in Tree.trees:
        temp = weather['season']['temperature'] + weather['temperature']['current offset']
        if random.uniform(0, 1) <= fireChance + (temp - 15) / 990000:
            tree.setFire()
        tree.tick()
    # if fire:
    #     for i in range(20):
    #         for tree in Tree.trees:
    #             pygame.draw.circle(screen, (255 - round(255 * tree.strucInteg), round(255 * tree.strucInteg), 0),
    #                                (tree.position[0] * scale, tree.position[1] * scale), scale / 2, 0)
    #         pygame.display.update()
    #         for tree in Tree.trees:
    #             tree.tick()
    for tree in Tree.trees:
        pygame.draw.circle(screen, (255-round(255*tree.strucInteg), round(255*tree.strucInteg), 0), (tree.position[0] * scale, tree.position[1] * scale), scale/2, 0)
    pygame.display.update()

running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
    fire = any(tree.onFire for tree in Tree.trees)
    for i in range(int(16/scale)**2):
        if random.uniform(0, 1) <= treeRepop:  # and not fire:
            Tree()
    tick()
    draw(fire)

pygame.quit()
