
def create_function(eqn):
    lamb_str = 'lambda z, c : '
    return eval(lamb_str + eqn)

def gen_with_escape_cond(f, i):
    def with_escape_cond(z, maxiter):
        c = z
        for n in range(maxiter):
            if abs(z) > i:
                return n
            z = f(z, c)
        return maxiter
    return with_escape_cond

def gen(f):
    def fu(r1, r2, maxitr, n3):
        height  = len(r1)
        width = len(r2)
        for i in range(width):
            for j in range(height):
                n3[j, i] = f(r1[j] + 1j * r2[i], maxiter)