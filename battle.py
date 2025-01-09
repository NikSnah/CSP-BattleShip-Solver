import sys
import argparse
from csp import Constraint, Variable, CSP
from constraints import *
from backtracking import * 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="The input file that contains the puzzle."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The output file that contains the solution."
    )
    
    args = parser.parse_args()
    
    file = open(args.inputfile, 'r')
    b = file.read()
    b2 = b.split()
    piece_constraint = b2[2]
    size = len(b2[0])
    size = size + 2
    b3 = []
    b3 += ['0' + b2[0] + '0']
    b3 += ['0' + b2[1] + '0']
    b3 += [b2[2] + ('0' if len(b2[2]) == 3 else '')]
    b3 += ['0' * size]
    for i in range(3, len(b2)):
        b3 += ['0' + b2[i] + '0']
    b3 += ['0' * size]
    board = "\n".join(b3)

    varlist = []
    varn = {}
    conslist = []

    given = []

    originalB = board.split()[3:]

    row_constraint = []
    for i in board.split()[0]:
        row_constraint += [int(i)]

    col_constraint = []
    for i in board.split()[1]:
        col_constraint += [int(i)]

    # Convert originalB rows to lists for mutability
    originalB = [list(row) for row in originalB]

    # Preprocessing rows/columns with zero constraints
    for i in range(size):
        if row_constraint[i] == 0:  # Row with 0 ships
            for j in range(1, size - 1):
                originalB[i][j - 1] = "."  # Mark entire row as water

        if col_constraint[i] == 0:  # Column with 0 ships
            for j in range(1, size - 1):
                originalB[j - 1][i] = "."  # Mark entire column as water

    # Directions for neighbors based on ship parts
    directions = {
        "<": [(-1, 0), (1, 0), (0, -1), (-1, -1), (1, -1)],  # Left, Top, Bottom, Diagonals
        ">": [(-1, 0), (1, 0), (0, 1), (-1, 1), (1, 1)],    # Right, Top, Bottom, Diagonals
        "^": [(0, -1), (0, 1), (-1, 0), (-1, -1), (-1, 1)],  # Top, Left, Right, Diagonals
        "v": [(0, -1), (0, 1), (1, 0), (1, -1), (1, 1)],    # Bottom, Left, Right, Diagonals
        "S": [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)],  # All directions
    }

    # Preprocessing known ship parts
    for i in range(1, size - 1):
        for j in range(1, size - 1):
            cell = originalB[i - 1][j - 1]  # Adjust for padding
            if cell in directions:
                for di, dj in directions[cell]:
                    ni, nj = i + di, j + dj
                    if 1 <= ni < size - 1 and 1 <= nj < size - 1:  # Stay within bounds
                        if originalB[ni - 1][nj - 1] == "0":  # Only mark empty cells
                            originalB[ni - 1][nj - 1] = "."  # Mark as water

    # Convert rows back to strings if needed
    originalB = ["".join(row) for row in originalB]

    for i in range(0,size):
        for j in range(0, size):
            v = None
            if i == 0 or i == size-1 or j == 0 or j == size-1:
                v = Variable(str(-1-(i*size+j)), [0])
            else:
                ch = originalB[i][j]
                v = Variable(str(-1-(i*size+j)), [0,1])
                if ch != "0":
                    given.append((i,j,ch))

            varlist.append(v)
            varn[str(-1-(i*size+j))] = v

    ii = 0
    for i in board.split()[3:]:
        jj = 0
        for j in i:
            if j != '0' and j != '.': # must be ship parts
                conslist.append(TableConstraint('boolean_match', [varn[str(-1-(ii*size+jj))]], [[1]]))
            elif j == '.':
                conslist.append(TableConstraint('boolean_match', [varn[str(-1-(ii*size+jj))]], [[0]]))
            jj += 1
        ii += 1


    for row in range(0,size):
        conslist.append(NValuesConstraint('row', [varn[str(-1-(row*size+col))] for col in range(0,size)], [1], row_constraint[row], row_constraint[row]))

    # print(col_constraint)
    for col in range(0,size):
        conslist.append(NValuesConstraint('col', [varn[str(-1-(col+row*size))] for row in range(0,size)], [1], col_constraint[col], col_constraint[col]))

    #diagonal constraints on 1/0 variables
    for i in range(1, size-1):
        for j in range(1, size-1):
            for k in range(9):
                conslist.append(NValuesConstraint('diag', [varn[str(-1-(i*size+j))], varn[str(-1-((i-1)*size+(j-1)))]], [1], 0, 1))
                conslist.append(NValuesConstraint('diag', [varn[str(-1-(i*size+j))], varn[str(-1-((i-1)*size+(j+1)))]], [1], 0, 1))


    for i in range(0, size):
        for j in range(0, size):
            v = Variable(str(i*size+j), ['.', 'S'])
            varlist.append(v)
            varn[str(i*size+j)] = v
            conslist.append(TableConstraint('connect', [varn[str(-1-(i*size+j))], varn[str(i*size+j)]], [[0,'.'],[1,'S']]))
        
    csp = CSP('battleship', varlist, conslist)
    # t_start = time.time()
    sols, num_nodes = bt_search('GAC', csp, 'mrv', False, False, piece_constraint, originalB, given, size)

    for i in range(len(sols)):
        # print to file the solution
        sys.stdout = open(args.outputfile, 'w')
        print_sol(sols[i], size)
        
        # bring sys.stdout back to normal
        sys.stdout = sys.__stdout__



#   python3 battle.py --inputfile input_medium2.txt --outputfile output_medium2.txt  
#   python3 battle.py --inputfile input_medium1.txt --outputfile output_medium1.txt  
#   python3 battle.py --inputfile input_hard2.txt --outputfile output_hard2.txt  