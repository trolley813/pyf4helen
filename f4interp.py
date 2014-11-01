import copy
from f4error import error

__author__ = 'hyst329'

varmap = {}

defvals = {
    'INT': 0,
    'REAL': 0.0
}

functions = {}
current_function = None
return_value = None


def interpret(ast):
    for stat in ast:
        process(stat)


def call_function(name, args):
    global current_function, return_value
    # return_value = None
    i = 0
    # print(args)
    argsc = copy.deepcopy(args)
    while i < len(args):
        argsc[i] = evaluate(args[i])
        i += 1
    f = functions[name]
    i = 0
    for a in f[0]:
        f[3][a[1]] = (a[0], argsc[i])
        i += 1
    current_function = name
    for s in f[1]:
        process(s)
    current_function = None
    return return_value


def evaluate(expr):
    global return_value
    op = expr[0]
    if op == 'ADD':
        return evaluate(expr[1]) + evaluate(expr[2])
    elif op == 'SUB':
        return evaluate(expr[1]) - evaluate(expr[2])
    elif op == 'MUL':
        return evaluate(expr[1]) * evaluate(expr[2])
    elif op == 'DIV':
        return evaluate(expr[1]) / evaluate(expr[2])
    elif op == 'EQL':
        return evaluate(expr[1]) == evaluate(expr[2])
    elif op == 'LEQ':
        return evaluate(expr[1]) <= evaluate(expr[2])
    elif op == 'GEQ':
        return evaluate(expr[1]) >= evaluate(expr[2])
    elif op == 'LES':
        return evaluate(expr[1]) < evaluate(expr[2])
    elif op == 'GTR':
        return evaluate(expr[1]) > evaluate(expr[2])
    elif op == 'IND':
        return varmap[expr[1]][1][evaluate(expr[2]) - 1]
    elif op == 'INT':
        return int(expr[1])
    elif op == 'REAL':
        return float(expr[1])
    elif op == 'ID':
        try:
            if current_function and expr[1] in functions[current_function][3]:
                return functions[current_function][3][expr[1]][1]
            else:
                return varmap[expr[1]][1]
        except KeyError:
            error('NOVAR')
    elif op == 'CALL':
        r = call_function(expr[1], expr[2])
        # print(r)
        return r


def process(stat):
    global return_value, current_function
    # print(stat)
    instr = stat[0]
    if instr == 'BLANK':
        return
    elif instr == 'DEBUGVAR':
        for k in varmap.keys():
            print("%s  \t%s = %s" % (varmap[k][0], k, varmap[k][1]))
    elif instr == 'NEW':
        typename, ident, value = stat[1], stat[2], stat[3]
        if current_function:
            functions[current_function][3][ident] = [typename, evaluate(value)]
        else:
            varmap[ident] = [typename, evaluate(value)]
    elif instr == 'NEWARR':
        typename, ident, size = stat[1], stat[3], evaluate(stat[2])
        if current_function:
            functions[current_function][3][ident] = [typename + '.' + str(size), [defvals[typename]] * int(size)]
        else:
            varmap[ident] = [typename + '.' + str(size), [defvals[typename]] * int(size)]
    elif instr == 'IN':
        ident = stat[1]
        if len(ident) == 2:
            varmap[ident[1]][1] = input('Enter value for %s:' % ident[1])
        else:
            varmap[ident[1]][1][evaluate(ident[2]) - 1] = input(
                'Enter value for %s.%s:' % (ident[1], evaluate(ident[2])))
    elif instr == 'OUT':
        expr = stat[1]
        print(evaluate(expr))
    elif instr == 'MOV':
        ident, expr = stat[1], stat[2]
        if len(ident) == 1:
            if current_function:
                functions[current_function][3][ident[0]][1] = evaluate(expr)
            else:
                varmap[ident[0]][1] = evaluate(expr)
        else:
            if current_function:
                functions[current_function][3][ident[1]][1][evaluate(ident[2]) - 1] = evaluate(expr)
            else:
                varmap[ident[1]][1][evaluate(ident[2]) - 1] = evaluate(expr)
    elif instr == 'IF':
        cond, iftrue, iffalse = stat[1], stat[2], stat[3]
        if evaluate(cond):
            for s in iftrue:
                process(s)
        else:
            for s in iffalse:
                process(s)
    elif instr == 'LOOP':
        init, cond, oniter, body = stat[1], stat[2], stat[3], stat[4]
        process(init)
        while evaluate(cond):
            for s in body:
                process(s)
            process(oniter)
    elif instr == 'FUN':
        name, args, retn, body = stat[1], stat[2], stat[3], stat[4]
        functions[name] = (args, body, retn, {})
    elif instr == 'RET':
        return_value = evaluate(stat[1])
        # print("Returned %s" % return_value)