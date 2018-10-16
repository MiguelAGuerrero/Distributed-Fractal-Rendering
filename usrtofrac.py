'''
    Takes an string from user that is passed in
    and creates a lambda function based on the
    string. create_function will fail if the
    the equation does not reference z and c.
    It will also fail if the equation
    references more variables than z and c
    (i.e. z**2 + c * x/y/or any other var)
'''
def create_function(eqn):
    lamb_str = 'lambda z, c : '
    return eval(lamb_str + eqn)


'''
    Using gen_with_escape_cond we wrap the fractal function that will use
    the generated lambda expression to populate the data numpy array and
    we also provide the escape condition for the custom equation
'''
def gen_with_escape_cond(f, i):
    def with_escape_cond(z, maxiter):
        c = z
        for n in range(maxiter):
            if abs(z) > i:
                return n
            z = f(z, c)
        return maxiter
    return with_escape_cond

'''
    Using gen we wrap the fractal function that will use
    the generated lambda expression to populate the data
    numpy array
'''
def gen(f):
    def fu(r1, r2, maxitr, n3):
        height  = len(r1)
        width = len(r2)
        for i in range(width):
            for j in range(height):
                n3[j, i] = f(r1[j] + 1j * r2[i], maxiter)