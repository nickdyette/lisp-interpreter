#!/usr/bin/env python3
"""6.009 Lab 7: carlae Interpreter"""

import doctest
import sys
#from cturtle import turtle 
# NO ADDITIONAL IMPORTS!


class EvaluationError(Exception):
    """
    Exception to be raised if there is an error during evaluation other than a
    NameError.
    """
    pass

class Enviro:
    
    #Initializes an environment containing a dictionary that holds the variable
    #assignments and a map to the parent environment
    def __init__(self, parent):
        self.parent = parent
        self.variables = {}
    
    #Assigns a variable with the name key to the given value
    def __setitem__(self, key, value):
        self.variables[key] = value
    
    #Returns the variable with a give name
    def __getitem__(self, key):
        #Checks if the variable is in the current environment and returns it if it is
        if key in self.variables:
            return self.variables[key]
        #Otherwise, checks the parent environment, returning None if no parent environment
        #exists
        else:
            if self.parent == None:
                return 'not found'
            else:
                return self.parent[key]
    

class Function:
    
    #Initializes a function object storing the parameters of the function, the body
    #of the function and the environment that the function is defined in 
    def __init__(self, parameters, body, environment):
        self.parameters = parameters
        self.body = body
        self.environment = environment


class Pair:
    
    #Intializes a Pair object containing a car and a cdr variable
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr
        
    #Appends a value to the pair object
    def append(self, value):
        current = self
        #If the pair is an empty list, only changes the car value
        if (current.car == 'blank') and (current.cdr is None):
            current.car = value
        else:
            #Finds the end pair of the linked list and changes the car value
            while current.cdr is not None:
                current = current.cdr
            current.cdr = Pair(value, None)
    
    #String representation of Pairs
    def __str__(self):
        return '(' + str(self.car) + ' , ' + str(self.cdr) + ')'
    
    #Loops through the car values of the linked list, yielding from the
    #remainder of the list if it is not None
    def __iter__(self):
        yield self.car
        if self.cdr is not None:
            yield from self.cdr
    
    #Returns car and cdr in a tuple to allow for equality check between Pairs 
    def values(self):
        return(self.car, self.cdr)
        

def FunctionCall(function, args):
    '''
    Passes arguments into a function object, evaluates it, and returns the 
    result
    
    Arguments:
        function(Function): A function object
        args(list): Arguments being passed into the function
    '''
    #Raises error if the number of parameters passed in does not match the 
    #number of parameters that the function accepts
    if len(args) != len(function.parameters):
        raise EvaluationError('Error: Number of parameters does not match.')
    
    #Raises error if the variable being passed in does not map to a function
    #object
    checker = Function(None, None, None)
    if type(function) != type(checker):
        raise EvaluationError('Error: Attempted to call a non-function.')
    
    #Evaluates all the arguments passed in and stores them
    evaluated = []
    for val in args:
        evaluated.append(evaluate(val, function.environment))
    
    #Creates a new environment that maps to the environment the function is defined in
    new = Enviro(function.environment)
    
    #Maps the function's parameters to the evaluated arguments
    for i in range(len(args)):
        new.variables[function.parameters[i]] = evaluated[i]
    
    #Evaluates the function body within the new environment
    return evaluate(function.body, new)


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a carlae
                      expression
    """
    #Divides the source into lines to be considered individually
    new = []
    line_split = source.splitlines()
    
    #Places spaces on either end of the parentheses so they're isolated when
    #split is called, then splits the source into words
    for line in line_split:
        replace = line.replace('(', ' ( ')
        replace2 = replace.replace(')', ' ) ')
        new.append(replace2.split())
    
    #Goes through each line adding every value, and ignoring the rest of the 
    #line if a semicolon is found
    final = []
    for line in new:
        for char in line:
            if char == ';':
                break
            else:
                final.append(char)
    
    return final
            

def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    #Checks the lists of length 1 so that the SyntaxError checks don't
    #raise value errors
    if len(tokens) == 1:
        token = tokens[0]
        #Tries casting the token as an int and then a float, and if neither
        #of them work, returns the token as is
        try:
            token = int(token)
        except:
            try:
                token = float(token)
            except:
                pass
        return token
    
    #Checks for if an s-expression does not contain parenthesis
    if len(tokens) > 1 and tokens.count('(') == 0:
        raise SyntaxError('Error: S-expression does not contain parenthesis')
    
    #Checks for unmatched parenthesis
    if tokens.count('(') != tokens.count(')'):
        raise SyntaxError('Error: Unmatched parenthesis')

    #Checks for closing parenthesis before opening parenthesis
    if tokens.index(')') < tokens.index('('):
        raise SyntaxError('Error: Closing parenthesis before opening parenthesis')
        
    def parse_expression(tokens):
        #Takes the first token from the list and removes it
        token = tokens.pop(0)
        
        #If the token is an open parenthesis, recursively calls parse_expression
        #on the values inside the parenthesis until it reaches a close parenthesis
        if token == '(':
            new = []
            while tokens[0] != ')':
                new.append(parse_expression(tokens))
            tokens.pop(0)
            return new
        #Otherwise, tries the same casting system as before to see what type
        #the token is
        else:
            try:
                token = int(token)
            except:
                try:
                    token = float(token)
                except:
                    pass
            return token
        
    return parse_expression(tokens)
            
            
#Definition of subtraction for carlae_builtins
def subtraction(args):
    if len(args) == 1:
        return -args[0]
    else:
        return args[0] - sum(args[1:])
    
#Definition of multiplication for carlae_builtins
def multiplication(args):
    if len(args) == 1:
        return 0
    else:
        first = args[0]
        for val in args[1:]:
            first *= val
        return first
    
#Definition of division for carlae_builtins   
def division(args):
    if len(args) == 1:
        return 0
    else:
        first = args[0]
        for val in args[1:]:
            first /= val
        return first

#Definition of equality function
def equality(args):
    if len(args) == 1:
        return '#t'
    else:
        first = args[0]
        for val in args[1:]:
            if val != first:
                return '#f'
        return '#t'

#Definition of decreasing function
def decreasing(args):
    if len(args) == 1:
        return '#t'
    else:
        current = args[0]
        for val in args[1:]:
            if val >= current:
                return '#f'
            else:
                current = val
        return '#t'

#Definition of nonincreasing function
def nonincreasing(args):
    if len(args) == 1:
        return '#t'
    else:
        current = args[0]
        for val in args[1:]:
            if val > current:
                return '#f'
            else:
                current = val
        return '#t'

#Definition of increasing function
def increasing(args):
    if len(args) == 1:
        return '#t'
    else:
        current = args[0]
        for val in args[1:]:
            if val <= current:
                return '#f'
            else:
                current = val
        return '#t'

#Definition of nondecreasing function
def nondecreasing(args):
    if len(args) == 1:
        return '#t'
    else:
        current = args[0]
        for val in args[1:]:
            if val < current:
                return '#f'
            else:
                current = val
        return '#t'

#Definition of 'not' keyword function
def notfunc(args):
    if len(args) != 1:
        raise EvaluationError('Error: Incorrect number of args.')
    else:
        current = evaluate(args[0])
        if current == '#t':
            return '#f'
        elif current == '#f':
            return '#t'

#Definition of cons function        
def cons(args):
    if len(args) != 2:
        raise EvaluationError('Error: Incorrect number of args.')
    #Creates new Pair object with passed in car and cdr
    else:
        newcar = args[0]
        newcdr = args[1]
        newpair = Pair(newcar , newcdr)
        return newpair

#Definition of car function
def car(args):
    if len(args) != 1:
        raise EvaluationError('Error: Incorrect number of args.')
    checker = Pair(None, None)
    if type(args[0]) != type(checker):
        raise EvaluationError('Error: Input of car must be of type Pair.')
    return args[0].car

#Definition of cdr function
def cdr(args):
    if len(args) != 1:
        raise EvaluationError('Error: Incorrect number of args.')
    checker = Pair(None, None)
    if type(args[0]) != type(checker):
        raise EvaluationError('Error: Input of cdr must be of type Pair.')
    return args[0].cdr

#Definitino of list function
def listfunc(args):
    #If no arguments passed in, returns an empty list
    if len(args) == 0:
        return None
    #If only one arg is passed in, creates the end of the linked list
    elif len(args) == 1:
        return cons([args[0], None])
    #Otherwise, creates a pair object storing the current arg, and recursively
    #calls the function on the remaining args
    else:
        return cons([args[0], listfunc(args[1:])])


#Definition for length function
def length(args):
    #Checks for incorrect number of arguments
    if len(args) != 1:
        raise EvaluationError('Incorrect number of args')
    checker = Pair(None, None)
    
    #Defines the current variable to the list and checks for an empty list
    current = args[0]
    if current == None:
        return 0
    
    #Checks for if the argument is not of type Pair
    if type(args[0]) != type(checker):
        raise EvaluationError('Input of length must be a linked list')
    
    #Checks for if the argument is of type Pair but is not a linked list
    if (args[0].cdr is not None) and (type(args[0].cdr) != type(checker)):
        raise EvaluationError('Input of length must be a linked list')
    
    #Goes through the list increasing length by 1 each time a new value is found
    length = 1
    while current.cdr != None:
        current = current.cdr
        length += 1
    return length


#Returns the Pair structure at a given index
def structure_at_index(args):
    #Checks for incorrect number of arguments 
    if len(args) != 2:
        raise EvaluationError('Incorrect number of args') 
        
    #Returns the argument at index 0 if 0 is passed in
    if args[1] == 0:
        return args[0]
    
    #Checks for out of index inputs
    if (args[1] < 0) or (args[1] >= length([args[0]])):
        raise EvaluationError('Error: Index out of range')
        
    #Recursively goes deeper into the linked list and lowers the index
    #returning 0 when the index is 0
    if args[1] == 0:
        return args[0]
    else:
        return structure_at_index([args[0].cdr, (args[1] - 1)])


#Returns element at given index
def elt_at_index(args):
    #If an empty list is returned, no index can be accessed
    if args[0] == None:
        raise EvaluationError('Error: Index out of range')
    #Returns the car of the returned structure
    else:
        return structure_at_index(args).car
       
#Concatenate function
def concat(args):
    #Returns empty list if no arguments are passed in
    if len(args) == 0:
        return None
    
    checker = Pair('blank', None)
    
    #Creates blank modifiable list to return
    newlist = Pair('blank', None)
    
    #Loops through every list in the arguments
    for lis in args:
        
        #Does nothing if the list is empty
        if lis == None:
            continue
        
        #Checks if the list is of type Pair
        if type(lis) != type(checker):
            raise EvaluationError('Input of concat must be a linked list')
            
        #Checks if the list is a linked list
        if (lis.cdr is not None) and (type(lis.cdr) != type(checker)):
            raise EvaluationError('Input of concat must be a linked list')
            
        #Loops through every value in the list and appends it to the list that
        #will eventually be returned
        for val in lis:
            newlist.append(val)
            
    if newlist.values() == checker.values():
        return None
    else:
        return newlist
        

#Map function
def map_func(args):
    #Checks for incorrect number of args
    if len(args) != 2:
        raise EvaluationError('Incorrect number of args')
    
    #Returns an empty list if an empty list is passed in 
    if length([args[1]]) == 0:
        return None
    
    #Creates an empty list to modify and return
    newlist = Pair('blank', None)
    checker = Pair('blank', None)
    
    #Checks if the function is in the builtins
    if evaluate(args[0]) in carlae_builtins.values():
        #Loops through every value in the list, applies the function to it and
        #appends it to the new list
        for val in args[1]:
            newlist.append(args[0]([val]))
            
    #Otherwise the function must be user defined
    else:
        for val in args[1]:
            newlist.append(FunctionCall(args[0], [val]))
            
    if newlist.values() == checker.values():
        return None
    else:
        return newlist


#Definition of filter function    
def filter_func(args):
    
    #Creates new list object to be returned
    newlist = Pair('blank', None)
    checker = Pair('blank', None)
    
    #Checks for incorrect number of args
    if len(args) != 2:
        raise EvaluationError('Incorrect number of args')
    
    #Returns empty list if an empty list is passed in 
    if length([args[1]]) == 0:
        return None
    
    #Calls the function on all of the arguments passed in, and appends the argument
    #to the list if the function returns true
    if evaluate(args[0]) in carlae_builtins.values():
        for val in args[1]:
            if args[0]([val]) == '#t':
                newlist.append(val)
    else:
        for val in args[1]:
            if FunctionCall(args[0], [val]) == '#t':
                newlist.append(val)
            
    if newlist.values() == checker.values():
        return None
    else:
        return newlist


#Definition of reduce function
def reduce(args):
    #Checks for incorrect number of args
    if len(args) != 3:
        raise EvaluationError('Incorrect number of args')
        
    #Returns the initial value if the list is empty
    if length([args[1]]) == 0:
        return args[2]
    
    #Stores the initial value in a variable
    current = args[2]
    
    #For every value in the list, passes it into a function with the current value
    #and updates the current value to the result of that function
    if evaluate(args[0]) in carlae_builtins.values():
        for val in args[1]:
            inputs = [current,val]
            current = args[0](inputs)
    else:
        for val in args[1]:
            inputs = [current, val]
            current = FunctionCall(args[0], inputs)
    
    return current


#Definition of begin function
def begin(args):
    #Returns last argument in series of args
    return (args[len(args) - 1])


#Definition of evaluate file function
def evaluate_file(file, e = None):
    #Stores the text of the file into a string
    text = open(file)
    store = text.read()
    text.close()
    
    #Tokenizes and parses the string, then returns the result of evaluating the 
    #parsed version
    tokenized = tokenize(store)
    parsed = parse(tokenized)
    return result_and_env(parsed, e)[0]
        
            
carlae_builtins = {
    '+': sum,
    '-': subtraction,
    '*': multiplication,
    '/': division,
    '=?': equality,
    '>': decreasing,
    '>=': nonincreasing,
    '<': increasing,
    '<=': nondecreasing,
    'not': notfunc,
    'cons': cons,
    'car': car,
    'cdr': cdr,
    'list': listfunc,
    'length': length,
    'elt-at-index': elt_at_index,
    'concat': concat,
    'map': map_func,
    'filter': filter_func,
    'reduce': reduce,
    'begin': begin
}


#Defines the builtin environment that has no parent environment
builtins = Enviro(None)
builtins.variables = carlae_builtins


def evaluate(tree, environment = None):
    
    #If no environment is passed in, creates a new environment to evaluate in
    #otherwise assigns the passed in environment to a variable
    if environment == None:
        e = Enviro(builtins)
    else:
        e = environment
    #Checks for individual values being passed in
    if type(tree) is not list:
        if type(tree) is str:
            #If a variable is passed in, returns the value assigned to it, raises
            #NameError if no value is defined
            if e[tree] != 'not found':
                return e[tree]
            elif (tree == '#t') or (tree == '#f'):
                  return tree
            elif tree == 'nil':
                return None
            else:
                raise NameError('Error: Variable is not defined.')
        #Returns the same value if an int or float is passed in
        else:
            return tree
    #Checks for define keyword 
    elif len(tree) == 0: 
        raise EvaluationError('Error: Empty S-Expression.')
    elif tree[0] == 'define':
        #Raises error if define statement doesn't have exactly 3 arguments
        if len(tree) != 3:
            raise EvaluationError('Error: Define must contain 3 arguments.')
        #Checks for simple function assignment
        if type(tree[1]) is list:
            #Creates new function object, assigns the parameters and body, then
            #returns the object.
            f = Function([], None, e)
            for val in tree[1][1:]:
                f.parameters.append(val)
            f.body = tree[2]
            e[tree[1][0]] = f
            return f
        else:
            #Variable assignment: Evaluates the expression passed in and assigns it
            #to the name key in the environment's variables dictionary
            e[tree[1]] = evaluate(tree[2], e)
            return evaluate(tree[2], e)
    #Checks for lambda keyword
    elif tree[0] == 'lambda':
        #Creates new function object, assigns the parameters and body, then returns
        #the object.
        f = Function([], None, e)
        for val in tree[1]:
            f.parameters.append(val)
        f.body = tree[2]
        return f
    #Checks for and keyword
    elif tree[0] == 'and':
        #Loops through all values in tree and returns false at first occurence of 
        #a false value, returns true if all values evaluate to true
        for val in tree[1:]:
            if val == '#f':
                return '#f'
            elif val == '#t':
                continue
            else:
                current = evaluate(val, e)
                if current == '#f':
                    return '#f'
                elif current == '#t':
                    continue
        return '#t'
    #Checks for or keyword
    elif tree[0] == 'or':
        #Loops through all values in tree and returns true at first occurence of
        #a true value, returns false if all values evaluate to false 
        for val in tree[1:]:
            if val == '#t':
                return '#t'
            elif val == '#f':
                continue
            else:
                current = evaluate(val, e)
                if current == '#t':
                    return '#t'
                elif current == '#f':
                    continue
        return '#f'
    #Checks for if keyword
    elif tree[0] == 'if':
        #Evaluates first expression and picks which other expression to evaluate
        #based on whether initial expression is true or false
        cond = evaluate(tree[1], e)
        if cond == '#t':
            return(evaluate(tree[2], e))
        elif cond == '#f':
            return(evaluate(tree[3], e))
    #Checks for let keyword
    elif tree[0] == 'let':
        #Creates dictionary to store variables
        vardict = {}
        #Checks for incorrect number of args
        if len(tree) != 3:
            raise EvaluationError('Incorrect number of args')
        #Evaluates each argument and stores it in the dictionary mapping it to the
        #variable name
        for val in tree[1]:
            vardict[val[0]] = evaluate(val[1], e)
        #Creates new environment, stores the variables in that environment,
        #then evaluates final expression within that environment
        new = Enviro(e)
        for key,value in vardict.items():
            new.variables[key] = value
        return evaluate(tree[2], new)
    #Checks for set! keyword
    elif tree[0] == 'set!':
        if len(tree) != 3:
            raise EvaluationError('Incorrect number of args')
        #Evaluates expression within current environment
        evald = evaluate(tree[2], e)
        current = e
        #Starts from current environment and goes into parent environmments looking
        #for variable name and updates its value when found
        if tree[1] in current.variables:
            current.variables[tree[1]] = evald
            return evald
        else:
            current = current.parent
            while current is not None:
                if tree[1] in current.variables:
                    current.variables[tree[1]] = evald
                    return evald
                else:
                    current = current.parent
            #Raises NameError if all environments are checked and variable is not found
            raise NameError('Variable not found')
    #Function calling 
    else:
        #Evaluates the first subexpression and assigns it to a variable
        first_sub = evaluate(tree[0], e)
        checker = Function(None, None, None)
        #If the first_sub function is in the builtin functions, evaluates
        #that function with the given args
        if first_sub in carlae_builtins.values():
            function = first_sub
            args = []
            for value in tree[1:]:
                args.append(evaluate(value, e))
            return function(args)
        #If the first_sub function is a user-defined function, evalutes that
        #function with the given args
        elif first_sub in e.variables.values():
            function = first_sub
            args = []
            for value in tree[1:]:
                args.append(evaluate(value, e))
            return FunctionCall(first_sub, args)
        #Checks for in-line lambda definitions by comparing the type to a generic
        #function object, and evaluates it with the given args
        elif type(first_sub) == type(checker):
            args = []
            for value in tree[1:]:
                args.append(evaluate(value, e))
            return FunctionCall(first_sub, args)
        #Raises an Evaluation error if the function passed in is not defined
        else:
            raise EvaluationError('Error: Function is not defined.')


#Same as the evaluate function but also returns the environment in which the 
#evaluation was done. 
def result_and_env(tree, environment = None):
    if environment == None:
        e = Enviro(builtins)
    else:
        e = environment
    if type(tree) is not list:
        if type(tree) is str:
            if e[tree] != 'not found':
                return (e[tree], e)
            elif (tree == '#t') or (tree == '#f'):
                  return (tree, e)
            elif tree == 'nil':
                return (None, e)
            else:
                raise NameError('Error: Variable is not defined.')
        else:
            return (tree, e)
    elif len(tree) == 0: 
        raise EvaluationError('Error: Empty S-Expression.')
    elif tree[0] == 'define':
        if len(tree) != 3:
            raise EvaluationError('Error: Define must contain 3 arguments.')
        if type(tree[1]) is list:
            f = Function([], None, e)
            for val in tree[1][1:]:
                f.parameters.append(val)
            f.body = tree[2]
            e[tree[1][0]] = f
            return(f, e)
        else:
            e[tree[1]] = evaluate(tree[2], e)
            return (evaluate(tree[2], e), e)
    elif tree[0] == 'lambda':
        f = Function([], None, e)
        for val in tree[1]:
            f.parameters.append(val)
        f.body = tree[2]
        return (f, e)
    elif tree[0] == 'and':
        for val in tree[1:]:
            if val == '#f':
                return ('#f', e)
            elif val == '#t':
                continue
            else:
                current = evaluate(val, e)
                if current == '#f':
                    return ('#f', e)
                elif current == '#t':
                    continue
        return ('#t', e)
    elif tree[0] == 'or':
        for val in tree[1:]:
            if val == '#t':
                return ('#t', e)
            elif val == '#f':
                continue
            else:
                current = evaluate(val, e)
                if current == '#t':
                    return ('#t', e)
                elif current == '#f':
                    continue
        return ('#f', e)
    elif tree[0] == 'if':
        cond = evaluate(tree[1], e)
        if cond == '#t':
            return(evaluate(tree[2], e), e)
        elif cond == '#f':
            return(evaluate(tree[3], e), e)
    elif tree[0] == 'let':
        vardict = {}
        if len(tree) != 3:
            raise EvaluationError('Incorrect number of args')
        for val in tree[1]:
            vardict[val[0]] = evaluate(val[1], e)
        new = Enviro(e)
        for key,value in vardict.items():
            new.variables[key] = value
        return (evaluate(tree[2], new), e)
    elif tree[0] == 'set!':
        if len(tree) != 3:
            raise EvaluationError('Incorrect number of args')
        evald = evaluate(tree[2], e)
        current = e
        if tree[1] in current.variables:
            current.variables[tree[1]] = evald
            return (evald,e)
        else:
            current = current.parent
            while current is not None:
                if tree[1] in current.variables:
                    current.variables[tree[1]] = evald
                    return (evald,e)
                else:
                    current = current.parent
            raise NameError('Variable not found')
    else:
        first_sub = evaluate(tree[0], e)
        checker = Function(None, None, None)
        if first_sub in carlae_builtins.values():
            function = first_sub
            args = []
            for value in tree[1:]:
                args.append(evaluate(value, e))
            return (function(args), e)
        elif first_sub in e.variables.values():
            args = []
            for value in tree[1:]:
                args.append(evaluate(value, e))
            return (FunctionCall(first_sub, args), e)
        elif type(first_sub) == type(checker):
            args = []
            for value in tree[1:]:
                args.append(evaluate(value, e))
            return (FunctionCall(first_sub, args), e)
        else:
            raise EvaluationError('Error: Function is not defined.')
            

#Definition of REPL
def REPL(enviro):
    args = None
    #Runs until 'QUIT' is passed in
    while args != 'QUIT':
        #Receives input fron the user
        args = input()
        #Breaks out if QUIT is the initial input 
        if args == 'QUIT':
            break
        try:
            #Tokenizes, parses, evaluates, and prints the input in the current environment
            tokenized = tokenize(args)
            parsed = parse(tokenized)
            evald = result_and_env(parsed, enviro)[0]
            print(evald)
        #If an exception is received, prints the exception message and continues the loop
        except Exception as e:
            print(e)
            continue

            
if __name__ == '__main__':
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
#    doctest.testmod()

    e = Enviro(builtins)
    for val in sys.argv[1:]:
        evaluate_file(val, e)
    REPL(e)


    
    
    
    
