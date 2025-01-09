from csp import Constraint, Variable, CSP
from constraints import *
import random

class UnassignedVars:
    '''class for holding the unassigned variables of a CSP. We can extract
       from, re-initialize it, and return variables to it.  Object is
       initialized by passing a select_criteria (to determine the
       order variables are extracted) and the CSP object.

       select_criteria = ['random', 'fixed', 'mrv'] with
       'random' == select a random unassigned variable
       'fixed'  == follow the ordering of the CSP variables (i.e.,
                   csp.variables()[0] before csp.variables()[1]
       'mrv'    == select the variable with minimum values in its current domain
                   break ties by the ordering in the CSP variables.
    '''
    def __init__(self, select_criteria, csp):
        if select_criteria not in ['random', 'fixed', 'mrv']:
            pass #print "Error UnassignedVars given an illegal selection criteria {}. Must be one of 'random', 'stack', 'queue', or 'mrv'".format(select_criteria)
        self.unassigned = list(csp.variables())
        self.csp = csp
        self._select = select_criteria
        if select_criteria == 'fixed':
            #reverse unassigned list so that we can add and extract from the back
            self.unassigned.reverse()

    def extract(self):
        if not self.unassigned:
            pass #print "Warning, extracting from empty unassigned list"
            return None
        if self._select == 'random':
            i = random.randint(0,len(self.unassigned)-1)
            nxtvar = self.unassigned[i]
            self.unassigned[i] = self.unassigned[-1]
            self.unassigned.pop()
            return nxtvar
        if self._select == 'fixed':
            return self.unassigned.pop()
        if self._select == 'mrv':
            nxtvar = min(self.unassigned, key=lambda v: v.curDomainSize())
            self.unassigned.remove(nxtvar)
            return nxtvar

    def empty(self):
        return len(self.unassigned) == 0

    def insert(self, var):
        if not var in self.csp.variables():
            pass #print "Error, trying to insert variable {} in unassigned that is not in the CSP problem".format(var.name())
        else:
            self.unassigned.append(var)



def bt_search(algo, csp, variableHeuristic, allSolutions, trace, piece_constraint, originalB, givens, size):
    '''Main interface routine for calling different forms of backtracking search
       algorithm is one of ['BT', 'FC', 'GAC']
       csp is a CSP object specifying the csp problem to solve
       variableHeuristic is one of ['random', 'fixed', 'mrv']
       allSolutions True or False. True means we want to find all solutions.
       trace True of False. True means turn on tracing of the algorithm

       bt_search returns a list of solutions. Each solution is itself a list
       of pairs (var, value). Where var is a Variable object, and value is
       a value from its domain.
    '''
    varHeuristics = ['random', 'fixed', 'mrv']
    algorithms = ['BT', 'FC', 'GAC']

    #statistics
    bt_search.nodesExplored = 0

    if variableHeuristic not in varHeuristics:
        pass 
    if algo not in algorithms:
        pass

    uv = UnassignedVars(variableHeuristic,csp)
    Variable.clearUndoDict()
    for v in csp.variables():
        v.reset()

    if algo == 'GAC':
        GacEnforce(csp.constraints(), csp, None, None) #GAC at the root
        solutions = GAC(uv, csp, originalB, piece_constraint, givens, size)

    return solutions, bt_search.nodesExplored

def GacEnforce(constraint_csp, csp, assignedvar, assignedval):
    constraint_csp = csp.constraints()
    while len(constraint_csp) != 0:
        cnstr = constraint_csp.pop()
        for var in cnstr.scope():
            for val in var.curDomain():
                if not cnstr.hasSupport(var,val):
                    var.pruneValue(val,assignedvar,assignedval)
                    if var.curDomainSize() == 0:
                        return False #DWO
                    for recheck in csp.constraintsOf(var):
                        if recheck != cnstr and recheck not in constraint_csp:
                            constraint_csp.append(recheck)
    return True

def GAC(unAssignedVars, csp, originalB, p_c, given, size):
    if unAssignedVars.empty():

        sol = []
        for var in csp.variables():
            if int(var._name) > 0:  
                sol.append((var,var.getValue()))
        return [sol]
    bt_search.nodesExplored += 1
    all_sol = []
    nxtvar = unAssignedVars.extract()
    for val in nxtvar.curDomain():
        nxtvar.setValue(val)

        if GacEnforce(csp.constraintsOf(nxtvar), csp, nxtvar, val) and not prune_ship_counts(csp, p_c, size) and not prune(csp, given, size):
            new_sol = GAC(unAssignedVars, csp, originalB, p_c, given, size)
            if new_sol:
                five, four, three, two, one, st = count_ship(new_sol[0], size)
                if one == int(p_c[0]) and two == int(p_c[1]) and three == int(p_c[2]) and four == int(p_c[3]) and five == int(p_c[4]):

                    if (vfy_to_org(originalB, st, size)):
                        all_sol.extend(new_sol)
                        if len(all_sol) > 0:
                            break
        nxtvar.restoreValues(nxtvar,val)
    nxtvar.unAssign()
    unAssignedVars.insert(nxtvar)
    return all_sol


def vfy_to_org(originalB, st, size):
    for i in range(1, size-1):
        for j in range(1, size-1):
            sol_value = st[(i*size+j)]
            orig_value = originalB[i][j]
            if orig_value != "0" and sol_value != orig_value:
                return False
    return True


def prune(csp, given, size):
    sol = []
    for var in csp.variables():
        if int(var._name) > 0:
            sol.append((var,var.getValue()))

    t_values = {}
    for (var, val) in sol:
        t_values[int(var.name())] = val

    for (i, j, c) in given:
        if c == "M":
            if j == 1 and t_values[int(i*size+j+1)] == "S":
                return True
            elif i == 1 and t_values[int((i+1)*size+j)] == "S":
                return True
            elif j == size - 2 and t_values[int(i*size+j-1)] == "S":
                return True
            elif i == size - 2 and t_values[int((i-1)*size+j)] == "S":
                return True
        elif c == "<" and t_values[int(i*size+j-1)] == "S":
            return True
        elif c == ">" and t_values[int(i*size+j+1)] == "S":
            return True
        elif c == "^" and t_values[int((i-1)*size+j)] == "S":
            return True
        elif c == "v" and t_values[int((i+1)*size+j)] == "S":
            return True
    return False


def prune_ship_counts(csp, p_c, size):
    n_sol = []
    for var in csp.variables():
        if int(var._name) > 0:
            n_sol.append((var,var.getValue()))
    n5, n4, n3, n2, n1, st = pruning_ship_numbers(n_sol, size)
    if n1 > int(p_c[0]) or n2 > int(p_c[1]) or n3 > int(p_c[2]) or n4 > int(p_c[3]) or n5 > int(p_c[4]):
         return True
    return False

    
def pruning_ship_numbers(sol, size):

    # A helper function to check if cells are already part of another ship
    def istoverlap(i, j, length, direction, st):
        if direction == "vertical":
            for k in range(length):
                if st.get(((i + k) * size + j)) not in ("S", None):
                    return True
        elif direction == "horizontal":
            for k in range(length):
                if st.get((i * size + j + k)) not in ("S", None):
                    return True
        return False
    
    st = {}
    for (var, val) in sol:
        st[int(var.name())] = val


    one = 0
    two = 0
    three = 0
    four = 0
    five = 0 
    for i in range(1, size-1):
        for j in range(1, size-1):
            # vertical
            below = None
            above = None
            right = None
            left = None
            # for ships of size five
            if (i < (size - 5) and st[(i*size+j)] == "S" and st[((i+1)*size+j)] == "S" and st[((i+2)*size+j)] == "S" and st[((i+3)*size+j)] == "S" and st[((i+4)*size+j)] == "S" and not istoverlap(i, j, 5, "vertical", st)):
                 
                five += 1
                st[((i)*size+j)] = "^"
                st[((i+1)*size+j)] = "M"
                st[((i+2)*size+j)] = "M"
                st[((i+3)*size+j)] = "M"
                st[((i+4)*size+j)] = "v"
            # for ships of size four
            elif (i < (size - 4) and st[(i*size+j)] == "S" and st[((i+1)*size+j)] == "S" and st[((i+2)*size+j)] == "S" and st[((i+3)*size+j)] == "S" and not istoverlap(i, j, 4, "vertical", st)):
                four += 1
                st[((i)*size+j)] = "^"
                st[((i+1)*size+j)] = "M"
                st[((i+2)*size+j)] = "M"
                st[((i+3)*size+j)] = "v"
            elif (i < (size - 3) and st[(i*size+j)] == "S" and st[((i+1)*size+j)] == "S" and st[((i+2)*size+j)] == "S" and not istoverlap(i, j, 3, "vertical", st)):
                if i != size - 4:
                    below = st[((i+3)*size+j)]
                if i != 1:
                    above = st[((i-1)*size+j)]
                if below == "." and above == ".":
                    three += 1
                    st[((i)*size+j)] = "^"
                    st[((i+1)*size+j)]= "M"
                    st[((i+2)*size+j)] = "v"
            elif (i < (size - 2) and st[(i*size+j)] == "S" and st[((i+1)*size+j)] == "S" and not istoverlap(i, j, 2, "vertical", st)):
                if i != size - 3:
                    below = st[((i+2)*size+j)]
                if i != 1:
                    above = st[((i-1)*size+j)]
                if below == "." and above == ".":
                    two += 1
                    st[((i)*size+j)] = "^"
                    st[((i+1)*size+j)] = "v"


            # horizontal 
            if (j < (size - 5) and st[(i*size+j)] == "S" and st[(i*size+j+1)] == "S" and st[(i*size+j+2)] == "S" and st[(i*size+j+3)] == "S" and st[(i*size+j+4)] == "S" and not istoverlap(i, j, 5, "horizontal", st)):
                five += 1
                st[(i*size+j)] = "<"
                st[(i*size+j+1 )] ="M"
                st[(i*size+j+2 )] ="M"
                st[(i*size+j+3 )] ="M"
                st[(i*size+j+4 )] =">"
            elif (j < (size - 4) and st[(i*size+j)] == "S" and st[(i*size+j+1)] == "S" and st[(i*size+j+2)] == "S" and st[(i*size+j+3)] == "S" and not istoverlap(i, j, 4, "horizontal", st)):
                four += 1
                st[(i*size+j)] = "<"
                st[(i*size+j+1 )] ="M"
                st[(i*size+j+2 )] ="M"
                st[(i*size+j+3 )] =">"
            elif (j < (size - 3) and st[(i*size+j)] == "S" and st[(i*size+j+1)] == "S" and st[(i*size+j+2)] == "S" and not istoverlap(i, j, 3, "horizontal", st)):
                if j != size - 4:
                    right = st[(i*size+j+3)] 
                if j != 1:
                    left = st[(i*size+j-1)]
                if right == "." and left == ".":
                    three += 1
                    st[(i*size+j)] = "<"
                    st[(i*size+j+1)] = "M"
                    st[(i*size+j+2)] = ">"
            elif (j < (size - 2) and st[(i*size+j)] == "S" and st[(i*size+j+1)] == "S" and not istoverlap(i, j, 2, "horizontal", st)):
                if j != size - 3:
                    right = st[(i*size+j+2)] 
                if j != 1:
                    left = st[(i*size+j-1)]
                if right == "." and left == ".":
                    two += 1
                    st[(i*size+j)] = "<"
                    st[(i*size+j+1)] = ">"
            
       # Check for lone ship parts (size 1)
    for i in range(1, size - 1):
        for j in range(1, size - 1):
            if (
                st[(i * size + j)] == "S"
                and all(
                    st.get((i + di) * size + j + dj, ".") == "."
                    for di, dj in [
                        (-1, 0), (1, 0), (0, -1), (0, 1),  # Adjacent directions
                        (-1, -1), (-1, 1), (1, -1), (1, 1)  # Diagonal directions
                    ]
                )
            ):
                one += 1
    
    return five, four, three, two, one, st



def print_sol(sol, size):
    st = {}
    for (var, val) in sol:
        st[int(var.name())] = val

    for i in range(1, size-1):
        for j in range(1, size-1):
            # For ships of size 5 SSSSS
            if j < (size - 4) and st[(i*size+j)] == "S" and st[(i*size+j+1)] == "S" and st[(i*size+j+2)] == "S" and st[(i*size+j+3)] == "S" and st[(i*size+j+4)] == "S":
               st[(i*size+j)] = "<"
               st[(i*size+j+1 )] ="M"
               st[(i*size+j+2 )] ="M"
               st[(i*size+j+3 )] = "M"
               st[(i*size+j+4 )] =">"
            # SSSS
            elif j < (size - 3) and st[(i*size+j)] == "S" and st[(i*size+j+1)] == "S" and st[(i*size+j+2)] == "S" and st[(i*size+j+3)] == "S":
                st[(i*size+j)] = "<"
                st[(i*size+j+1 )] ="M"
                st[(i*size+j+2 )] ="M"
                st[(i*size+j+3 )] =">"
            elif j < (size - 2) and st[(i*size+j)] == "S" and st[(i*size+j+1)] == "S" and st[(i*size+j+2)] == "S":
                st[(i*size+j)] = "<"
                st[(i*size+j+1)] = "M"
                st[(i*size+j+2)] = ">"
            elif j < (size - 1) and st[(i*size+j)] == "S" and st[(i*size+j+1)] == "S":
                st[(i*size+j)] = "<"
                st[(i*size+j+1)] = ">"

            # vertical 5 size
            if i < (size - 4) and st[(i*size+j)] == "S" and st[((i+1)*size+j)] == "S" and st[((i+2)*size+j)] == "S" and st[((i+3)*size+j)] == "S" and st[((i+4)*size+j)] == "S":
                st[(i*size+j)] = "^"
                st[(i*size+j+1 )] ="M"
                st[(i*size+j+2 )] ="M"
                st[(i*size+j+3 )] = "M"
                st[(i*size+j+4 )] = "v"
            elif i < (size - 3) and st[(i*size+j)] == "S" and st[((i+1)*size+j)] == "S" and st[((i+2)*size+j)] == "S" and st[((i+3)*size+j)] == "S":
                st[((i)*size+j)] = "^"
                st[((i+1)*size+j)] = "M"
                st[((i+2)*size+j)] = "M"
                st[((i+3)*size+j)] = "v"
            elif i < (size - 2) and st[(i*size+j)] == "S" and st[((i+1)*size+j)] == "S" and st[((i+2)*size+j)] == "S":
                st[((i)*size+j)] = "^"
                st[((i+1)*size+j)]= "M"
                st[((i+2)*size+j)] = "v"
            elif i < (size - 1) and st[(i*size+j)] == "S" and st[((i+1)*size+j)] == "S":
                st[((i)*size+j)] = "^"
                st[((i+1)*size+j)] = "v"
        
    for i in range(1, size-1):
        for j in range(1, size-1):
            if st[(i*size+j)] == None:
                print("0",end="")
            else:
                print(st[(i*size+j)],end="")
        print('')

def count_ship(sol, size):

    st = {}
    for (var, val) in sol:
        st[int(var.name())] = val

    one = 0
    two = 0
    three = 0
    four = 0
    five = 0 
    for i in range(1, size-1):
        for j in range(1, size-1):
            # For Ship size of 5 SSSSS vertical 
            if (i < (size - 4) and st[(i*size+j)] == "S" and st[((i+1)*size+j)] == "S" and st[((i+2)*size+j)] == "S" and st[((i+3)*size+j)] == "S" and st[((i+4)*size+j)] == "S"):
                five += 1
                st[(i*size+j)] = "^"
                st[(i*size+j+1 )] ="M"
                st[(i*size+j+2 )] ="M"
                st[(i*size+j+3 )] = "M"
                st[(i*size+j+4 )] ="v"
            elif (i < (size - 4) and st[(i*size+j)] == "S" and st[((i+1)*size+j)] == "S" and st[((i+2)*size+j)] == "S" and st[((i+3)*size+j)] == "S"):
                four += 1
                st[((i)*size+j)] = "^"
                st[((i+1)*size+j)] = "M"
                st[((i+2)*size+j)] = "M"
                st[((i+3)*size+j)] = "v"
            elif (i < (size - 3) and st[(i*size+j)] == "S" and st[((i+1)*size+j)] == "S" and st[((i+2)*size+j)] == "S"):
                three += 1
                st[((i)*size+j)] = "^"
                st[((i+1)*size+j)]= "M"
                st[((i+2)*size+j)] = "v"
            elif (i < (size - 2) and st[(i*size+j)] == "S" and st[((i+1)*size+j)] == "S"):
                two += 1
                st[((i)*size+j)] = "^"
                st[((i+1)*size+j)] = "v"
            
            if (j < (size - 4) and st[(i*size+j)] == "S" and st[(i*size+j+1)] == "S" and st[(i*size+j+2)] == "S" and st[(i*size+j+3)] == "S" and st[(i*size+j+4)] == "S"):
                five += 1
                st[(i*size+j)] = "<"
                st[(i*size+j+1 )] ="M"
                st[(i*size+j+2 )] ="M"
                st[(i*size+j+3 )] = "M"
                st[(i*size+j+4 )] =">"
            elif (j < (size - 4) and st[(i*size+j)] == "S" and st[(i*size+j+1)] == "S" and st[(i*size+j+2)] == "S" and st[(i*size+j+3)] == "S"):
                four += 1
                st[(i*size+j)] = "<"
                st[(i*size+j+1 )] ="M"
                st[(i*size+j+2 )] ="M"
                st[(i*size+j+3 )] =">"
            elif (j < (size - 3) and st[(i*size+j)] == "S" and st[(i*size+j+1)] == "S" and st[(i*size+j+2)] == "S"):
                three += 1
                st[(i*size+j)] = "<"
                st[(i*size+j+1)] = "M"
                st[(i*size+j+2)] = ">"
            elif (j < (size - 2) and st[(i*size+j)] == "S" and st[(i*size+j+1)] == "S"):
                two += 1
                st[(i*size+j)] = "<"
                st[(i*size+j+1)] = ">"
            
    for i in range(1, size-1):
        for j in range(1, size-1):
            if st[(i*size+j)] == "S":
                one += 1
    return five, four, three, two, one, st


