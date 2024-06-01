from PIL import ImageGrab
import pyautogui as gui
import numpy as np
import time


hold_x = 400
hold_y = 290
hold_w = 1
hold_h = 10

x = 500
y = 230
w = 300
h = 600

b = 30
hb = 15

board = np.zeros((10,20))
bottom = []
block_shapes = [
    #T
    [
            np.flipud(np.rot90(np.array([
            [0, 1, 0],
            [1, 1, 1]
        ]))),
            np.flipud(np.rot90(np.array([
            [1, 0],
            [1, 1],
            [1, 0]
        ]))),
            np.flipud(np.rot90(np.array([
            [1, 1, 1],
            [0, 1, 0]
        ]))),
            np.flipud(np.rot90(np.array([
            [0, 1],
            [1, 1],
            [0, 1]
        ])))
    ],
    #Z
    [
        np.flipud(np.rot90(np.array([
            [1, 1, 0],
            [0, 1, 1]
        ]))),
        np.flipud(np.rot90(np.array([
            [0, 1],
            [1, 1],
            [1, 0]
        ])))
    ],
    #L
    [
        np.flipud(np.rot90(np.array([
            [0, 0, 1],
            [1, 1, 1]
        ]))),
        np.flipud(np.rot90(np.array([
            [1, 0],
            [1, 0],
            [1, 1]
        ]))),
        np.flipud(np.rot90(np.array([
            [1, 1, 1],
            [1, 0, 0]
        ]))),
        np.flipud(np.rot90(np.array([
            [1, 1],
            [0, 1],
            [0, 1]
        ])))
    ], 
    #::
    [
        np.flipud(np.rot90(np.array([
            [1, 1],
            [1, 1]
        ]))),
    ],
    #S
    [
        np.flipud(np.rot90(np.array([
            [0, 1, 1],
            [1, 1, 0]
        ]))),
        np.flipud(np.rot90(np.array([
            [1, 0],
            [1, 1],
            [0, 1]
        ])))
    ],
    #|
    [
        np.flipud(np.rot90(np.array([
            [1, 1, 1, 1]
        ]))),
        np.flipud(np.rot90(np.array([
            [1],
            [1],
            [1],
            [1]            
        ])))
    ],
    #Γ
    [
        np.flipud(np.rot90(np.array([
            [1, 0, 0],
            [1, 1, 1]
        ]))),
        np.flipud(np.rot90(np.array([
            [1, 1],
            [1, 0],
            [1, 0]
        ]))),
        np.flipud(np.rot90(np.array([
            [1, 1, 1],
            [0, 0, 1]
        ]))),
        np.flipud(np.rot90(np.array([
            [0, 1],
            [0, 1],
            [1, 1]
        ])))
    ]    
]
block_colours = [
    (0xaf,0x29,0x8a), 
    (0xd7,0x0f,0x37),
    (0xe3,0x5b,0x02),
    (0xe3,0x9f,0x02),
    (0x59,0xb1,0x01),
    (0x0f,0x9b,0xd7),
    (0x21,0x41,0xc6),
    (0x99,0x99,0x99),
    (0x6a,0x6a,0x6a)
]



def getAllPermutations(board, block_colours):
    board_height, board_width = board.shape
    block_height, block_width = block_colours.shape
    lowest_positions = []
    for y in range(board_height - block_height + 1):
        lowest_x = None
        for x in range(board_width - block_width + 1):
            submatrix = board[y:y+block_height, x:x+block_width]
            if np.all(submatrix + block_colours <= 1):
                lowest_x = x
            else:
                break
        if lowest_x is not None:
            lowest_positions.append((y, lowest_x))
    return lowest_positions

def printBoard(array):
    print('-'*16)
    for y in range(len(array[0])):
        for x in range(len(array)):
            if array[x,y] != 0:
                print('::', end="")
            else:
                print('  ', end="")
        print()

def scoreBoard(tetris_board,x_end,y):
    #Punish Holes
    holes = 0
    #Punish bumpiness and promote flatness
    bump = 0
    #Punish deep crevaces (3+ height) 
    deep3 = 0
    #Punish higher move (change value)
    height = ((h/b)-y)
    #Punish end placement as they are for THICK TETRIS
    end = int((w/b)==x_end)

    tops = []
    prev_height = h/b

    for column in tetris_board:
        found_block = False
        i_c = h/b
        for item in column:
            if item == 0:
                if found_block:
                    holes += 1
            else:
                if not found_block:
                    tops.append(prev_height-i_c)
                    prev_height = i_c
                found_block = True
            i_c-=1

        if not found_block:
            tops.append(prev_height-i_c)
            prev_height = i_c


    for i in range(0,len(tops)-1):
        bump += abs(tops[i])
        if tops[i]>=3 and tops[i+1]<=-3:
            deep3+=1
    
    bump += abs(tops[-1])

    #Forget hitting tets when holes re there
    if holes != 0:
        end = 0
    return (holes*1200) + (2000*deep3) + (100*height) + (10*bump) + (end*300)

def executeMove(block_index):
    d__score = 4294967296
    d__X = -1
    d__rot = -1
    
    rot_i = 0
    for block_rot in block_shapes[block_index]:
        positions = getAllPermutations(board,block_rot)
        for dx, dy in positions:
            new_board = board.copy()
            new_board[dx:dx+block_rot.shape[0], dy:dy+block_rot.shape[1]] += block_rot
            score = scoreBoard(new_board,dx+block_rot.shape[0],dy)
            if d__score > score:
                d__score = score
                d__X = dx
                d__rot = rot_i
        rot_i += 1

    return (d__score,d__rot,d__X)    

def clickTetris():
    hold_index = -1
    block_index = -1

    snapshot = ImageGrab.grab(bbox=(hold_x,hold_y,hold_w+hold_x,hold_h+hold_y))
    snapshot.save("C:\\Users\\agnee\\OneDrive\\Desktop\\img.png")
    for hx in range(hold_w):    
        for hy in range(hold_h):
            colour = snapshot.getpixel((hx,hy))
            if colour in block_colours:
                hold_index = block_colours.index(colour)


    snapshot = ImageGrab.grab(bbox=(x,y,w+x,h+y))
    snapshot.save("C:\\Users\\agnee\\OneDrive\\Desktop\\img1.png")
    cleaned = False
    for iy in range(hb,h,b):
        iY = int((iy-hb)/b)
        clean = 0
        for ix in range(hb,w,b):
            iX = int((ix-hb)/b)
            colour = snapshot.getpixel((ix,h-iy))
            if colour in block_colours:
                if not cleaned:
                    board[iX][~iY] = 1
                else:
                    block_index = block_colours.index(colour) 
            else:
                clean= clean+1
                board[iX][~iY] = 0
        if clean == w/b:
            cleaned = True
    
    holdmove = None
    if hold_index != -1:
        holdmove = executeMove(hold_index)
    else:
        gui.press('c') 

    if block_index != len(block_colours)-2 and block_index != len(block_colours)-1:    
        move = executeMove(block_index)

        if holdmove != None and holdmove[0] < move[0]:
            move = holdmove
            gui.press('c')

        gui.press('up', presses=move[1])
        gui.press('left',presses=5)
        gui.press('right',presses=move[2])
        gui.press('space')



if __name__ == "__main__":
    gui.hotkey('alt','tab')
    # gui.press('f4') 
    time.sleep(3)
    gui.press('c') 
    while True:
        clickTetris()
        # time.sleep(0.1)
