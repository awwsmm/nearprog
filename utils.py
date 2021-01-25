test_mode = False

def tests(arr):
    if (test_mode):
        print('')
        for elem in arr:
            print(elem,'=',eval(elem))

# returns a new array where the function f() has been applied to each element of the array
def foreach(array, f):
    return [f(elem) for elem in array]

tests([
    'foreach(["hi", "hey", "ho"], lambda x: x.upper())',
    'foreach([1, 2, 3, 4, 5], lambda x: x * x)'
    ])

# returns True if any element of the array satisfies the predicate, p
def any(array, p):
    for elem in array:
        if p(elem):
            return True
    return False

tests([
    'any([1, 2, 3, 4], lambda x: x > 3)',
    'any([1, 2, 3, 4], lambda x: x > 5)'
    ])
