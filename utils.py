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

# returns True if all elements of the array satisfy the predicate, p
def all(array, p):
    for elem in array:
        if not p(elem):
            return False
    return True

tests([
    'all([1, 2, 3, 4], lambda x: x > 3)',
    'all([1, 2, 3, 4], lambda x: x > 0)'
    ])

# filters out (removes) elements which do not satisfy the predicate, p
def filter(array, p):
    return [elem for elem in array if p(elem)]

tests([
    'filter(["a", "ab", "abc", "abcd"], lambda x: len(x) > 2)',
    'filter([False, True, True, False], lambda x: x)',
    'filter([-1, 1, -2, 3], lambda x: x * x > 1)',
    ])
