import numpy as np
import scipy.stats

def RANGE(start, stop, step, exclude=None, repeat=True, shape=None, 
          length=None, min_diff=None, max_attempts=1000):
    
    if length is not None:
        n = length
    elif shape is not None:
        n = np.prod(shape)
    else:
        n = 1
    
    
    # Loop until an appropriate colleciton is found
    # This loop will restart ONLY if we have run out of acceptable options. 
    for _ in range(max_attempts):
        
        values = []
        # Build list of options
        options = np.arange(start, stop+step, step).round(10).tolist()
        options = [ROUND(o,nearest=step) for o in options]
        
        if exclude is not None:
            options = [v for v in options if v not in exclude]
        
        failed = False
        # Loop to generate required number of values
        for i in range(n):
            
            if len(options) == 0:
                failed = True
                break  # We have failed and need to start over. 
            
            x = np.random.choice(options)     # Select a value
            values.append(x)
            
            # Remove from list if repeats not allowed
            if repeat == False:
                options.remove(x)
            
            # Remove values that are too close to x
            if min_diff is not None:
                options = [v for v in options if round(abs(x - v), 10) >= min_diff]

        # Return values if they were found. Otherwise, restart the loop.         
        if failed == False:
            
            if shape is None and length is None:
                return values[0]

            if length is not None:
                return values

            if shape is not None:
                return np.array(values).reshape(shape)
        
    print('Unable to find values satifying the given criteria.')           
            

def EXP(x):
    return float(np.exp(x))

def LN(x):
    import math
    return math.log(x)

def LOG(x, b=10):
    import math
    return math.log(x, b)
    

def ROUND(x, digits=None, nearest=None):
    
    if nearest is None and digits is None:
        return round(x)
    
    if nearest is None:
        return round(x, digits)
    
    if nearest is not None:
        x = round(x / nearest) * nearest
        x = round(x, 10)
        return x

def DIFF(x, y):
    return abs(x - y)

def MIN_DIFF(values):
    n = len(values)
    min_diff = None
    for i in range(0, n):
        for j in range(i+1, n):
            diff = abs(values[i] - values[j])
            if min_diff is None:
                min_diff = diff
            elif diff < min_diff:
                min_diff = diff
    return min_diff

def MAX_DIFF(values):
    n = len(values)
    max_diff = None
    for i in range(0, n):
        for j in range(i+1, n):
            diff = abs(values[i] - values[j])
            if max_diff is None:
                max_diff = diff
            elif diff > max_diff:
                max_diff = diff
    return max_diff


def NOT(b):
    return not b


def EXACT_TO(x, digits):
    return ROUND(x, digits=digits) == x


def UNIQUE(values):
    n1 = len(values)
    n2 = len(np.unique(values))
    if n1 != n2: 
        return False
    return True

def FLOOR(x):
    import math
    return math.floor(x)


def CEIL(x):
    import math
    return math.ceil(x)


def DISTRACTORS_A(ans, n=4, step=1, seed=None):
    if seed is not None:
        np.random.seed(seed)

    k = np.random.choice(range(n+1))
    
    distractors = []
    for i in range(-k, n-k+1):
        if i == 0: continue
        d = ans + i
        distractors.append(d)

    return distractors


def DISTRACTORS(ans, n=4, p_rng=None, step=None, digits=None, nearest=None, seed=None):
    if seed is not None:
        np.random.seed(seed)

    # if no step is provided, determine step using p_range
    if step is None: 
        if p_rng is None: p_rng = [0.03, 0.06]
        p = np.random.uniform(p_rng[0], p_rng[1])
        step = ans*p
    
    # Determine position for correct answer
    k = np.random.choice(range(n+1))
    
    distractors = []
    for i in range(-k, n-k+1):
        if i == 0: continue
        d = ans + i * step
        d = ROUND(d, digits=digits, nearest=nearest)
        #if digits is not None:
        #    d = round(d, digits)
        distractors.append(d)

    return distractors
        
def FACT(n):
    import math
    assert(n == int(n))
    return math.factorial(int(n))

def COMBIN(n, r):
    assert(n == int(n))
    assert(r == int(r))
    return FACT(n) / FACT(r) / FACT(n - r)

def PERM(n, r):
    assert(n == int(n))
    assert(r == int(r))
    return FACT(n) / FACT(n - r) 

def MIN(values):
    return min(values)

def MAX(values):
    return max(values)

def ARGMIN(values, axis=None):
    return np.argmin(values, axis=axis)

def ARGMAX(values, axis=None):
    return np.argmax(values, axis=axis)

def WHERE(cond, a, b):
    return np.where(cond, a, b)

def INT(x):
    return int(x)

def MNAME():
    names = [
        'Aaron', 'Alex', 'Barry', 'Bryce', 'Carlos', 'Craig', 'Darren', 'Doug', 'Edward', 'Eric', 'Felix', 
        'Frank', 'Gary', 'Greg', 'Hector', 'Hugo', 'Ian', 'Ivan', 'Jake', 'Juan', 'Kent', 'Kevin', 'Leon', 
        'Lucas', 'Matt', 'Milo', 'Nathan', 'Nick', 'Oliver', 'Owen', 'Paul', 'Phillip', 'Quentin', 'Quinn', 
        'Rick', 'Rodney', 'Shawn', 'Scott', 'Toby', 'Tyler', 'Vince', 'Vernon', 'Wade', 'William', 'Zack'
    ]
    return np.random.choice(names)

def FNAME():
    names = [
        'Abby', 'Allison', 'Beth', 'Bridgett', 'Cindy', 'Clair', 'Dana', 'Darcy', 'Ellen', 'Emma', 'Flora', 
        'Faye', 'Gail', 'Gloria', 'Hailey', 'Heidi', 'Isabell', 'Ivy', 'Joan', 'Jackie', 'Kate', 'Kayla', 
        'Lori', 'Leah', 'Marie', 'Megan', 'Nikki', 'Norah', 'Olivia', 'Ophelia', 'Paige', 'Paula', 'Rachel', 
        'Rose', 'Sadie', 'Selena', 'Tina', 'Tess', 'Vera', 'Vicky', 'Wendy', 'Willa', 'Yolanda', 'Yvonne', 'Zora', 'Zena'
    ]
    return np.random.choice(names)


def NORMAL_CDF(x, mean=0, sd=1):
    from scipy.stats import norm
    return norm.cdf(x=x, loc=mean, scale=sd)
    
def INV_NORMAL_CDF(q, mean=0, sd=1):
    from scipy.stats import norm
    return norm.ppf(q=q, loc=mean, scale=sd)


def SUM(values):
    return sum(values)

def ABS(x):
    return abs(x)

def SUMMATION(start, end, fn):
    return sum([fn(x) for x in range(start, end+1)])

def SELECT(values):
    import numpy as np
    return np.random.choice(values)


def GCD(a, b):
    import math 
    return math.gcd(a,b)

def LCM(a, b):
    import math 
    return math.lcm(a,b)


def REDUCE(a, b, part=None):
    n = int(a / GCD(a,b))
    d = int(b / GCD(a,b))
    if part == 1:
        return n
    if part == 2:
        return d
    
    return n, d


def SQRT(x):
    return x**0.5

def QUAD(a, b, c):
    x1 = (-b - SQRT(b**2 - 4*a*c)) / (2*a)
    x2 = (-b + SQRT(b**2 - 4*a*c)) / (2*a)
    return x1, x2


def TABLE(contents, config=None):

    default_config = {'cw':50, 'ch':20, 'sr1':True, 'sc1':True, 'align':'C'}
    if config == None: config = {}
    for k,v in default_config.items():
        if k not in config.keys():
            config[k] = v
        
    
    t = '<table style="border:1px solid black;  border-spacing:0px; border-collapse: collapse; '
    t += 'background-color:#FFFFFF; ; margin: 0px 0px 20px 0px;"">\n'
    t += '<tbody>\n'
    for i, row in enumerate(contents):
        # Determine height
        temp = config['ch']
        ch = temp[i] if type(temp) == list else temp

        # Start row
        t += f'    <tr style="height:{ch}px">\n'
        
        for j, x in enumerate(row):

            # Determine Cell Color
            col = '#FFFFFF'
            if (config['sr1'] and i == 0) or (config['sc1'] and j == 0):
                col = '#E0E0E0'
                x = f'<b>{x}</b>'

            # Determine width
            temp = config['cw']
            cw = temp[j] if type(temp) == list else temp
            
            # Alignment
            temp = config['align']
            align = temp[j] if type(temp) == list else temp
            a = {'C':'center', 'L':'left', 'R':'right'}[align]
                
            t += f'        <td  style="border:1px solid black; background-color:{col}; '
            t += f'width:{cw}px; text-align:{a}">'
            t += f'{x}</td>\n'

        t += '    </tr>\n'
    t += '</tbody>\n</table>\n'
    
    return t



def TABLE_NEW(contents, row_labels=None, col_labels=None, config=None):

    default_config = {'cw':50, 'ch':20, 'sr1':True, 'sc1':True, 'align':'C'}
    if config == None: config = {}
    for k,v in default_config.items():
        if k not in config.keys():
            config[k] = v
        
    
    t = '<table style="border:1px solid black;  border-spacing:0px; border-collapse: collapse; '
    t += 'background-color:#FFFFFF; ; margin: 0px 0px 20px 0px;"">\n'
    t += '<tbody>\n'
    
    
    # Fold labels into contents:
    # Current assumes that upper right cell belows to row labels
    new_contents = contents.copy()
    if col_labels is not None:
        new_contents.insert(0, col_labels)
    if row_labels is not None:
        for i, rl in enumerate(row_labels):
            new_contents[i].insert(0,rl)
        
    
    for i, row in enumerate(new_contents):
        # Determine height
        temp = config['ch']
        ch = temp[i] if type(temp) == list else temp

        # Start row
        t += f'    <tr style="height:{ch}px">\n'
        
        for j, x in enumerate(row):

            # Determine Cell Color
            col = '#FFFFFF'
            if (config['sr1'] and i == 0) or (config['sc1'] and j == 0):
                col = '#E0E0E0'
                x = f'<b>{x}</b>'

            # Determine width
            temp = config['cw']
            cw = temp[j] if type(temp) == list else temp
            
            # Alignment
            temp = config['align']
            align = temp[j] if type(temp) == list else temp
            a = {'C':'center', 'L':'left', 'R':'right'}[align]
                
            t += f'        <td  style="border:1px solid black; background-color:{col}; '
            t += f'width:{cw}px; text-align:{a}">'
            t += f'{x}</td>\n'

        t += '    </tr>\n'
    t += '</tbody>\n</table>'
    
    return t




def ANNUITY_PV(n, i, due=False):
    v = 1/(1+i)
    pv = (1 - v**n) / i
    if due: pv *= (1+i)*pv
    return pv

def ANNUITY_FV(n, i, due=False):
    a = 1+i
    fv = (a**n - 1) / i
    if due: fv *= (1+i)*fv
    return fv

def INC_ANNUITY_PV(n, i, P=None, Q=None, due=False):
    if P is None: P = 1
    if Q is None: Q = 1
    v = 1/(1+i)
    an = ANNUITY_PV(n, i, due=False)
    pv = P*an + Q * (an - n*v**n) / i
    if due: pv *= (1+i)*pv
    return pv

def INC_ANNUITY_FV(n, i, P=None, Q=None, due=False):
    if P is None: P = 1
    if Q is None: Q = 1
    a = 1+i
    sn = ANNUITY_FV(n, i, due=False)
    fv = P*sn + Q*(sn - n) / i
    if due: fv *= (1+i)*fv
    return fv

def DEC_ANNUITY_PV(n, i, due=False):
    return INC_ANNUITY_PV(n, i, P=n, Q=-1, due=due)

def DEC_ANNUITY_FV(n, i, due=False):
    return INC_ANNUITY_FV(n, i, P=n, Q=-1, due=due)

def GEOM_ANNUITY_PV(n, i, g, P, due=False):
    r = (i - g) / (1 + g)
    pv = P * ANNUITY_PV(n, r, due=False) / (1 + g)
    if due: pv *= (1+i)*pv
    return pv

def GEOM_ANNUITY_FV(n, i, g, P, due=False):
    pv = GEOM_ANNUITY_PV(n, i, g, P, due)
    fv = pv * (1+i)**n
    return fv
    
def TVM_SOLVER(N=None, I=None, PV=None, PMT=None, FV=None):
    none_count = 0
    if N is None: none_count += 1
    if I is None: none_count += 1
    if PV is None: none_count += 1
    if PMT is None: none_count += 1
    if FV is None: none_count += 1
    if none_count != 1:
        print('Exactly one parameter must be missing from the function call.')
    
    if I is None:
        
        x = 0.05
        
        def new_x(x):
            v = 1 / (1 + x)
            top = x*PMT - x*PMT*v**N + x**2*FV*v**N + PV*x**2
            bot = -PMT + N*x*PMT*v**(N+1) + PMT*v**N - N*FV*x**2*v**(N+1)
            return x - top/bot
        
        while True:
            old_x = x
            x = new_x(x)
            if abs(x - old_x) < 0.000000000001:
                break
        return x
    
    v = 1 / (1 + I)    
    
    if N is None:
        x1 = -PV - PMT / I
        x2 = FV - PMT / I
        n = np.log(x1/x2) / np.log(v)
        return round(n, 10)
    
    an = ANNUITY_PV(N, I)
    
    if PV is None:
        pv = PMT * an + FV*v**N
        return -pv
    
    if FV is None:
        fv = (-PV - PMT * an) * (1+I)**N
        return fv
    
    if PMT is None:
        pmt = (-PV - FV * v**N) / an
        return pmt
        
    
    
    pass


if __name__ == '__main__':
    #print(RANGE(10, 150, 5))
    #print(ROUND(36.5, 5))
    #print(EXACT_TO(3.47, 0.1))
    #print(not EXACT_TO(3.47, 0.1))
    
    #print(UNIQUE([2, 3, 4]))
    #print(UNIQUE([2, 3, 4.01, 4 + 1/100]))
    
    #print(MIN([5, 7, 10]))
    
    #f = lambda x : x**2
    
    #print(SUMMATION(1, 5, f))
    
    #print(QUAD(1, -5, 6))
    
    #print(DISTRACTORS(ans=37, step=1))
    
    print(TVM_SOLVER(N=20, I=None, PV=-1000, PMT=50, FV=20000))