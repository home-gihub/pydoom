from collections import namedtuple
import pygame
import pygame.gfxdraw
import math


def dist(x1,y1,x2,y2):
    return math.sqrt((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1))


loadSectors = [
    0, 4, 0, 40, 3, 4,
    4, 8, 0, 40, 5, 6,
    8, 12, 0, 40, 7, 8,
    12, 16, 0, 40, 1, 2,
]

loadWalls = [
    0, 0, 32, 0, 1,
    32, 0, 32, 32, 2,
    32, 32, 0, 32, 1,
    0, 32, 0, 0, 2,

    64, 0, 96, 0, 3,
    96, 0, 96, 32, 4,
    96, 32, 64, 32, 3,
    64, 32, 64, 0, 4,

    64, 64, 96, 63, 5,
    96, 64, 96, 96, 6,
    96, 96, 64, 96, 5,
    64, 96, 64, 96, 6,

    0, 64, 32, 64, 7,
    32, 64, 32, 96, 8,
    32, 96, 0, 96, 7,
    0, 96, 0, 64, 8
]


def initialise():
    i = 0
    for i in range(0, 360):
        M["cos"][i] = math.cos(i/180.0*math.pi)
        M["sin"][i] = math.sin(i / 180.0 * math.pi)

    v1 = 0
    v2 = 0
    for s in range(0,numSect):
        a = S[s]._replace(ws=loadSectors[v1+0])
        a = a._replace(we=loadSectors[v1+1])
        a = a._replace(z1=loadSectors[v1+2])
        a = a._replace(z2=loadSectors[v1+3])
        a = a._replace(c1=loadSectors[v1+4])
        a = a._replace(c2=loadSectors[v1+5])
        S[s] = a
        v1 += 6
        for w in range(S[s].ws, S[s].we):
            b = W[w]._replace(x1=loadWalls[v2+0])
            b = b._replace(y1=loadWalls[v2 + 1])
            b = b._replace(x2=loadWalls[v2 + 2])
            b = b._replace(y2=loadWalls[v2 + 3])
            b = b._replace(c=loadWalls[v2 + 4])
            W[w] = b
            v2+=5

    Player["x"] = 70
    Player["y"] = 110
    Player["z"] = 20
    Player["a"] = 0
    Player["l"] = 0


def drawpixel(s, x, y, c):
    match c:
        case 1:
            rgb = [255, 255, 0]
        case 2:
            rgb = [128.0, 128.0, 0.0]
        case 3:
            rgb = [0.0, 255.0, 0.0]
        case 4:
            rgb = [0.0, 128.0, 0.0]
        case 5:
            rgb = [0.0, 255.0, 255.0]
        case 6:
            rgb = [0.0, 128.0, 128.0]
        case 7:
            rgb = [100.0, 70.0, 50.0]
        case 8:
            rgb = [50.0, 35.0, 25.0]
        case _:
            print(f"error unknown color {c}")
            exit(1)
    try:
        pygame.gfxdraw.pixel(s, int(x), int(y), (rgb[0], rgb[1], rgb[2]))
    finally:
        return


def clipbehindplayer(x1, y1, z1, x_2, y_2, z_2):
    da = y1
    db = y_2
    d = da - db
    if d == 0:
        d = 1
    s = da/(da-db)
    x1 = x1 + s*(x_2-x1)
    y1 = y1 + s*(y_2-y1)
    if y1 == 0:
        y1 = 1
    z1 = z1 + s*(z_2-z1)
    return {
        "x": x1,
        "y": y1,
        "z": z1
    }


def drawwall(x1, x_2, b1, b_2, t1, t_2, c, s):
    dyb = b_2 - b1
    dyt = t_2 - t1
    dx = x_2-x1
    if dx == 0:
        dx = 1
    xs = x1

    if x1 < 1:
        x1 = 1
    if x_2 < 1:
        x_2 = 1
    if x1 > screenwidth - 1:
        x1 = screenwidth - 1
    if x_2 > screenwidth - 1:
        x_2 = screenwidth - 1

    for x in range(int(x1),int(x_2)):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        y1 = dyb*(x-xs+0.5)/dx+b1
        y2 = dyt*(x-xs+0.5)/dx+t1

        if y1 < 1:
            y1 = 1
        if y2 < 1:
            y2 = 1
        if y1 > screenheight - 1:
            y1 = screenheight - 1
        if y2 > screenheight - 1:
            y2 = screenheight - 1

        if S[s].surface == 1:
            a = S[s].surf
            a[x] = y1
            S[s] = S[s]._replace(surf=a)
            continue
        if S[s].surface == 2:
            a = S[s].surf
            a[x] = y2
            S[s] = S[s]._replace(surf=a)
        if S[s].surface == -1:
            for y in range(S[s].surf[x], y1):
                drawpixel(displayplane, x, y, S[s].c1)
        if S[s].surface == -2:
            for y in range(y2, S[s].surf[x]):
                drawpixel(displayplane, x, y, S[s].c2)


        for y in range(int(y1 - 1),int(y2)):
            drawpixel(displayplane, x, y, c)


def draw3d():
    s = 0
    w = 0

    for s in range(0,numSect):
        for w in range(0, numSect-s-1):
            if S[w].d < S[w+1].d:
                st = S[w]
                S[w]=S[w+1]
                S[w+1]=st

    for s in range(0,numSect):
        S[s] = S[s]._replace(d=0)

        if Player["z"]<S[s].z1:
            S[s] = S[s]._replace(surface=1)
        elif Player["z"]>S[s].z2:
            S[s] = S[s]._replace(surface=2)
        else:
            S[s] = S[s]._replace(surface=0)

        for loop in range(0,2):
            for w in range(S[s].ws, S[s].we):
                wx = [None] * 4
                wy = [None] * 4
                wz = [None] * 4
                cs = M["cos"][Player["a"]]
                sn = M["sin"][Player["a"]]

                x1 = W[w].x1 - Player["x"]
                y1 = W[w].y1 - Player["y"]
                x2 = W[w].x2 - Player["x"]
                y2 = W[w].y2 - Player["y"]

                if loop == 0:
                    swp = x1
                    x1 = x2
                    z2 = swp
                    swp = y1
                    y1 = y2
                    y2 = swp

                wx[0] = x1 * cs - y1 * sn
                wx[1] = x2 * cs - y2 * sn
                wx[2] = wx[0]
                wx[3] = wx[1]

                wy[0] = y1 * cs + x1 * sn
                wy[1] = y2 * cs + x2 * sn
                wy[2] = wy[0]
                wy[3] = wy[1]

                # div by 0 checks lol
                if wy[0] == 0:
                    wy[0] = 1
                if wy[1] == 0:
                    wy[1] = 1
                if wy[2] == 0:
                    wy[2] = 1
                if wy[3] == 0:
                    wy[3] = 1

                wz[0] = 0 - Player["z"] + Player["l"] * wy[0] / 32.0
                wz[1] = 0 - Player["z"] + Player["l"] * wy[1] / 32.0
                wz[2] = wz[0] + S[s].z2
                wz[3] = wz[1] + S[s].z2
                S[s] = S[s]._replace(d=S[s].d + dist(0, 0, (wx[0] + wx[1]) / 2, (wy[0] + wy[1]) / 2))

                if wy[0] < 1 and wy[1] < 1:
                    continue

                if wy[0] < 1:
                    clip = clipbehindplayer(wx[0], wy[0], wz[0], wx[1], wy[1], wz[1])
                    wx[0] = clip["x"]
                    wy[0] = clip["y"]
                    wz[0] = clip["z"]
                    clip = clipbehindplayer(wx[2], wy[2], wz[2], wx[3], wy[3], wz[3])
                    wx[2] = clip["x"]
                    wy[2] = clip["y"]
                    wz[2] = clip["z"]

                if wy[1] < 1:
                    clip = clipbehindplayer(wx[1], wy[1], wz[1], wx[0], wy[0], wz[0])
                    wx[1] = clip["x"]
                    wy[1] = clip["y"]
                    wz[1] = clip["z"]
                    clip = clipbehindplayer(wx[3], wy[3], wz[3], wx[2], wy[2], wz[2])
                    wx[3] = clip["x"]
                    wy[3] = clip["y"]
                    wz[3] = clip["z"]

                wx[0] = wx[0] * 200 / wy[0] + screenwidth2
                wx[1] = wx[1] * 200 / wy[1] + screenwidth2
                wx[2] = wx[2] * 200 / wy[2] + screenwidth2
                wx[3] = wx[3] * 200 / wy[3] + screenwidth2

                wy[0] = wz[0] * 200 / wy[0] + screenheight2
                wy[1] = wz[1] * 200 / wy[1] + screenheight2
                wy[2] = wz[2] * 200 / wy[2] + screenheight2
                wy[3] = wz[3] * 200 / wy[3] + screenheight2

                # if wx[0] > 0 and wx[0] < screenwidth and wy[0] > 0 and wy[0] < screenheight:
                #     drawpixel(displayplane,int(wx[0]),int(wy[0]),1)
                # if wx[1] > 0 and wx[1] < screenwidth and wy[1] > 0 and wy[1] < screenheight:
                # s    drawpixel(displayplane, int(wx[1]), int(wy[1]), 1)

                drawwall(wx[0], wx[1], wy[0], wy[1], wy[2], wy[3], W[w].c, s)
        S[s] = S[s]._replace(d=S[s].d / (S[s].we - S[s].ws))
        S[s] = S[s]._replace(surface=S[s].surface * -1)


def moveplayer():
    keys = pygame.key.get_pressed()
    # move up, down, left, right
    if keys[pygame.K_a] and not keys[pygame.K_m]:
        Player["a"] -= 4
        if Player["a"] < 0:
            Player["a"] += 360
    if keys[pygame.K_d] and not keys[pygame.K_m]:
        Player["a"] += 4
        if Player["a"] > 359:
            Player["a"] -= 360
    dx = M["sin"][Player["a"]] * 10.0
    dy = M["cos"][Player["a"]] * 10.0
    if keys[pygame.K_w] and not keys[pygame.K_m]:
        Player["x"] += dx
        Player["y"] += dy
    if keys[pygame.K_s] and not keys[pygame.K_m]:
        Player["x"] -= dx
        Player["y"] -= dy
    # strafe
    if keys[pygame.K_COMMA]:
        Player["x"] += dy
        Player["y"] += dx
    if keys[pygame.K_PERIOD]:
        Player["x"] -= dy
        Player["y"] -= dx
    # move up, down, look up, look down
    if keys[pygame.K_w] and keys[pygame.K_m]:
        Player["z"] -= 4
    if keys[pygame.K_s] and keys[pygame.K_m]:
        Player["z"] += 4
    if keys[pygame.K_a] and keys[pygame.K_m]:
        Player["l"] -= 1
    if keys[pygame.K_d] and keys[pygame.K_m]:
        Player["l"] += 1


############################################################
res = 1
screenwidth = 160*res
screenheight = 120*res
screenwidth2 = screenwidth / 2
screenheight2 = screenheight / 2
pixelscale = 4/res
renderscreenwidth = screenwidth * pixelscale
renderscreenheight = screenheight * pixelscale
numSect = 4
numWall = 16

M = {
    "sin": [None] * 360,
    "cos": [None] * 360
}

Player = {
    "x": 0,
    "y": 0,
    "z": 0,
    "a": 0,
    "l": 0
}

Walls = namedtuple('Walls', ['x1','y1','x2','y2','c'])
W = [Walls(0,0,0,0,0)] * 30
Sectors = namedtuple('Sectors', ['ws', 'we', 'z1', 'z2', 'd', 'c1', 'c2', 'surf', "surface"])
S = [Sectors(0,0,0,0,0,0,0,[0]*screenwidth,0)] * 30
############################################################

if __name__ == "__main__":
    initialise()

    pygame.init()
    screen = pygame.display.set_mode((renderscreenwidth, renderscreenheight))
    displayplane = pygame.Surface((screenwidth, screenheight))
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        ##########################
        screen.fill("black")
        displayplane.fill("black")
        ##########################
        moveplayer()
        draw3d()
        ############################################################################################################
        screen.blit(pygame.transform.scale(displayplane, (renderscreenwidth, renderscreenheight)), (0, 0))
        pygame.display.flip()
        print("draw")
        clock.tick(60)
        #############################################################################################################

    pygame.quit()
