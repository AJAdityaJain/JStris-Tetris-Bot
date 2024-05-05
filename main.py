from PIL import ImageGrab
import pyautogui as gui
import numpy as np
import time


hold_x = 400
hold_y = 340
hold_w = 1
hold_h = 10

x = 500
y = 280
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
    (0x21,0x41,0xc6)
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
def get(tetris_board, x,y):
    if x == -1 or y == -1 :return 1
    if x >= len(tetris_board) or y >= len(tetris_board[0]): return 1
    return tetris_board[x][y]

def scoreBoard(tetris_board,y):
    score = 0
    #Punish higher move (change value)
    score += ((h/b)-y)*100
    Xiter = 0
    for column in tetris_board:
        found_block = False
        Yiter = 0
        for item in column:
            if item == 0:
                if found_block:
                    #Punish Holes
                    score+=1200
            else:
                if (not found_block)  and get(tetris_board, Xiter-1,Yiter-3) and get(tetris_board, Xiter+1,Yiter-3):
                    score+=2000
                found_block = True
            Yiter+=1
        if (not found_block):
            if get(tetris_board, Xiter-1,Yiter-3) and get(tetris_board, Xiter+1,Yiter-3):
                score+=2000
        Xiter+=1
    return score

def executeMove(block_index):
    d__score = 4294967296
    d__X = -1
    d__rot = -1
    print("Index:" ,block_index)
    
    rot_i = 0
    for block_rot in block_shapes[block_index]:
        positions = getAllPermutations(board,block_rot)
        for dx, dy in positions:
            new_board = board.copy()
            new_board[dx:dx+block_rot.shape[0], dy:dy+block_rot.shape[1]] += block_rot
            score = scoreBoard(new_board,dy)
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
    for hx in range(hold_w):    
        for hy in range(hold_h):
            colour = snapshot.getpixel((hx,hy))
            if colour in block_colours:
                hold_index = block_colours.index(colour)


    snapshot = ImageGrab.grab(bbox=(x,y,w+x,h+y))
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
    move = executeMove(block_index)

    if holdmove != None and holdmove[0] < move[0]:
        print('switch PLZZZZ')
        move = holdmove
        gui.press('c')

    for i in range(move[1]):
        gui.press('up')

    gui.keyDown('left')
    time.sleep(0.2)
    gui.keyUp('left')    
        
    # for i in range(d__X):
    gui.press('right',presses=move[2])

    gui.press('space')
    print(move[0], 'X: ', move[2], ' Rot:', move[1])








if __name__ == "__main__":
    gui.hotkey('alt','tab')
    gui.press('f4') 
    time.sleep(3)
    gui.press('c') 
    while True:
        clickTetris()
        time.sleep(0.3)
