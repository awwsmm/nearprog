import utils

test_mode = False

def tests(arr):
    if (test_mode):
        print('')
        for elem in arr:
            print(elem,'=',eval(elem))

# used to test that "Styx" == "styx", etc.
def match(a, b):
    a_lower = a.lower()
    b_lower = b.lower()
    return (a_lower in b_lower or b_lower in a_lower)

tests([
    'match("dog", "dog")',
    'match("dog", "Dog!")',
    'match("Dog", "? dog ")',
    'match("Dog", "I have a DOG")',
    'match("cat", "dog")',
    'match("cat", "I love cats and dogs")',
    ])

def contains(array, elem):
    return utils.any(array, lambda x: match(x, elem))

arr = ["dog", "hello i am a CAT", "dogs and cats"]
tests([
    'contains('+ str(arr) +', "DOG")',
    'contains('+ str(arr) +', "cat")',
    'contains('+ str(arr) +', "frog")'
    ])
