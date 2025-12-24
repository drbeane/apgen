import numpy as np
import scipy.stats

#----------------------------------------------------------------------
# Sampling Functions
#----------------------------------------------------------------------

def SAMPLE(start, stop, step, exclude=None, repeat=True, size=None,
           min_diff=None, max_attempts=1000):
    
    
    # Determine the number of values to sample. 
    n = 1 if size is None else np.prod(size)
    
        
    # Loop until an appropriate colleciton is found
    # This loop will restart if we run out of acceptable options or a condition fails.
    for _ in range(max_attempts):
        
        sample_values = []   # List to store sampled values
        
        # Build list of options
        options = np.arange(start, stop+step, step).round(12).tolist()
        
        # Remove exluded values
        if exclude is not None:
            options = [v for v in options if v not in exclude]
        
        
        # Loop to generate required number of values
        failed = False
        for _ in range(n):
            
            # Check to see if we have run out of valid options. 
            if len(options) == 0:
                failed = True
                break  
            
            # Sample a single value. 
            x = np.random.choice(options).item()
            sample_values.append(x)
            
            # Remove value from options if sampling w/o replacement
            if repeat == False:
                options.remove(x)
            
            # Remove values that are too close to x
            if min_diff is not None:
                options = [v for v in options if round(abs(x - v), 10) >= min_diff]

    
        #----------------------------------------------------------------
        # Return values if they were found. Otherwise, restart the loop. 
        #----------------------------------------------------------------                
        if failed == False:
                        
            if size is None:
                return sample_values[0]

            if np.array(size).ndim == 0:
                return sample_values

            if np.array(size).ndim == 1:
                return np.array(sample_values).reshape(size)
        
    print('Unable to find values satifying the given criteria.')           
            

def RANGE(start, stop, step, exclude=None, repeat=True, size=None, 
          min_diff=None, max_attempts=1000):

    return SAMPLE(start=start, stop=stop, step=step, exclude=exclude, repeat=repeat, 
           size=size, min_diff=min_diff, max_attempts=max_attempts)    

def SELECT(values, repeat=True):
    import numpy as np
    return np.random.choice(values, replace=repeat)
    
def COND(max_attempts=1000, conds=[], **kwargs):
    
    for _ in range(max_attempts):
        vars = {}
        for k,v in kwargs.items():
            vars[k] = eval(v)
        
        cond_scope = vars.copy()
        conds_satisfied = True
        for c in conds:
            exec(f'cond_val={c}', cond_scope)
            if cond_scope['cond_val'] == False:
                conds_satisfied = False
                break
        
        if conds_satisfied:
            return vars
    
    raise Exception('Failed to generate values satisfying conditions.')
    
    
#----------------------------------------------------------------------
# Basic Math Functions
#----------------------------------------------------------------------

    
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
        if nearest > 1:
            x = round(x / nearest) * nearest
            x = round(x, 10)
            return x
        else:
            d = x - int(x)
            new_d = round(d / nearest) * nearest
            new_d = round(new_d, 10)
            return int(x) + new_d

def DIFF(x, y):
    return abs(x - y)

def MIN_DIFF(*args):
    
    # This is just used to allow values to be provided as a list. 
    # That should probably be deprecated. 
    if len(args) == 1 and type(args[0]) in [list, tuple, np.ndarray]:
        args = args[0]
        
    n = len(args)
    min_diff = None
    
    
    for i in range(0, n):
        for j in range(i+1, n):
            diff = abs(args[i] - args[j])
            if min_diff is None:
                min_diff = diff
            elif diff < min_diff:
                min_diff = diff
    
    return round(min_diff, 10)

def MAX_DIFF(*args):
    
    # This is just used to allow values to be provided as a list. 
    # That should probably be deprecated. 
    if len(args) == 1 and type(args[0]) in [list, tuple, np.ndarray]:
        args = args[0]
    
    n = len(args)
    max_diff = None
    
    for i in range(0, n):
        for j in range(i+1, n):
            diff = abs(args[i] - args[j])
            if max_diff is None:
                max_diff = diff
            elif diff > max_diff:
                max_diff = diff
    
    return round(max_diff, 10)


def NOT(b):
    return not b


def EXACT_TO(x, digits):
    return ROUND(x, digits=digits) == x


def NOT_EXACT_TO(x, digits):
    return NOT(EXACT_TO(x, digits))

def NEXTO(x, digits):
    return NOT_EXACT_TO(x, digits)

def UNIQUE(*args):
    # This is just used to allow values to be provided as a list. 
    # That should probably be deprecated. 
    if len(args) == 1 and type(args[0]) == list:
        args = args[0]
        
    n1 = len(args)
    n2 = len(np.unique(args))
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
        d = ans + i*(step)
        distractors.append(d)

    return distractors


def DISTRACTORS(ans, n=4, prop=None, p_rng=None, step=None, digits=None, nearest=None, seed=None):
    if seed is not None:
        np.random.seed(seed)

    # if no step is provided, determine step using p_range
    if step is not None: 
        pass
    elif prop is not None:
        step = ans*prop
    elif p_rng is not None:
        p = np.random.uniform(p_rng[0], p_rng[1])
        step = ans*p
    else:
        p = np.random.uniform(0.03, 0.06)
        step = ans*p
        
    
    #if step is None: 
    #    if p_rng is None: p_rng = [0.03, 0.06]
    #    p = np.random.uniform(p_rng[0], p_rng[1])
    #    step = ans*p
    
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

def MIN(*args):
    
    # This is just used to allow values to be provided as a list. 
    # That should probably be deprecated. 
    if len(args) == 1 and type(args[0]) == list:
        args = args[0]
    
    return min(args)

def MAX(*args):
    # This is just used to allow values to be provided as a list. 
    # That should probably be deprecated. 
    if len(args) == 1 and type(args[0]) == list:
        args = args[0]
        
    return max(args)

def ARGMIN(*args):
    # This is just used to allow values to be provided as a list. 
    # That should probably be deprecated. 
    if len(args) == 1 and type(args[0]) == list:
        args = args[0]
        
    return np.argmin(args)

def ARGMAX(*args):
    # This is just used to allow values to be provided as a list. 
    # That should probably be deprecated. 
    if len(args) == 1 and type(args[0]) == list:
        args = args[0]
        
    return np.argmax(args)

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
    name = np.random.choice(names)
    return '__NAMEa__' + name + '__NAMEb__'

def FNAME():
    names = [
        'Abby', 'Allison', 'Beth', 'Bridgett', 'Cindy', 'Clair', 'Dana', 'Darcy', 'Ellen', 'Emma', 'Flora', 
        'Faye', 'Gail', 'Gloria', 'Hailey', 'Heidi', 'Isabell', 'Ivy', 'Joan', 'Jackie', 'Kate', 'Kayla', 
        'Lori', 'Leah', 'Marie', 'Megan', 'Nikki', 'Norah', 'Olivia', 'Ophelia', 'Paige', 'Paula', 'Rachel', 
        'Rose', 'Sadie', 'Selena', 'Tina', 'Tess', 'Vera', 'Vicky', 'Wendy', 'Willa', 'Yolanda', 'Yvonne', 'Zora', 'Zena'
    ]
    name = np.random.choice(names)
    return '__NAMEa__' + name + '__NAMEb__'


def NORMAL_CDF(x, mean=0, sd=1):
    from scipy.stats import norm
    return norm.cdf(x=x, loc=mean, scale=sd)
    
def INV_NORMAL_CDF(p, mean=0, sd=1):
    from scipy.stats import norm
    return norm.ppf(q=p, loc=mean, scale=sd)

def PNORM(x, mean=0, sd=1):
    NORMAL_CDF(x, mean=mean, sd=sd)

def QNORM(p, mean=0, sd=1):
    INV_NORMAL_CDF(p, mean=mean, sd=sd)


def SUM(*args):
    
    # This is just used to allow values to be provided as a list. 
    # That should probably be deprecated. 
    if len(args) == 1 and type(args[0]) == list:
        args = args[0]
    
    return sum(args)

def ABS(x):
    return abs(x)

def SUMMATION(start, end, fn):
    return sum([fn(x) for x in range(start, end+1)])




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


def TABLE_OLD(contents, config=None):

    default_config = {'cw':50, 'ch':30, 'sr1':True, 'sc1':True, 'align':'C'}
    if config == None: config = {}
    for k,v in default_config.items():
        if k not in config.keys():
            config[k] = v
        
    
    t = '<table style="border:1px solid black;  border-spacing:0px; border-collapse: collapse; '
    t += 'background-color:#FFFFFF; margin: 0px 0px 15px 0px;">\n'
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



def TABLE(contents, config=None, rlab=None, clab=None, inc_margin=True):

    if type(config) == str:
        new_config = {}
        tokens = config.split(';')
        for t in tokens:
            k,v = t.strip().split(':')
            k = k.strip()
            v = v.strip()
            if v == 'False': v = False
            if v == 'True': v = True
            new_config[k] = v
        config = new_config

    default_config = {'cw':50, 'ch':30, 'sr1':True, 'sc1':True, 'align':'C'}
    if config == None: config = {}
    for k,v in default_config.items():
        if k not in config.keys():
            config[k] = v
        
    tm = 20 if inc_margin else 0
    t = '<table style="border:1px solid black;  border-spacing:0px; border-collapse: collapse; '
    t += f'background-color:#FFFFFF; ; margin: 20px 0px 20px 0px;"">\n'
    t += '<tbody>\n'
    
    
    if rlab is None: rlab = []
    if clab is None: clab = []
    rlab = np.array(rlab).reshape((-1,1))
    clab = np.array(clab).reshape((1,-1))
    #row_labels = np.array([]) if row_labels is None else np.array(row_labels).reshape((-1,1))
    #col_labels = np.array([]) if col_labels is None else np.array(col_labels).reshape((1,-1))
    contents = np.array(contents)
    if contents.ndim == 1:
        contents = contents.reshape([1,-1])
    
    # Assert something about the dimensions
    n_row = contents.shape[0]
    n_col = contents.shape[1]
    b1 = (rlab.size == 0) and (clab.size == 0)
    b2 = (rlab.size == 0) and (clab.size == n_col)
    b3 = (rlab.size == n_row) and (clab.size == 0)
    b4 = (rlab.size == n_row) and (clab.size == n_col)
    b5 = (rlab.size == n_row) and (clab.size == n_col+1)
    b6 = (rlab.size == n_row+1) and (clab.size == n_col)
    msg = f'Size mismatch: contents={contents.shape}, rlab={rlab.size}, clab={clab.size}'
    assert (b1 or b2 or b3 or b4 or b5 or b6), msg
    
    # Step 1  (b3, b4, b5)
    row_labels_added = False
    if rlab.shape[0] == contents.shape[0]:
        contents = np.hstack([rlab, contents])
        row_labels_added = True
    
    # Step 2 (b4)
    if clab.shape[1] == contents.shape[1] - 1:
        clab = np.hstack([[['']], clab])
     
    # Step 3 (b2, b4, b5, b6)
    if clab.shape[1] == contents.shape[1]:
        contents = np.vstack([clab, contents])
        
    # Step 4 (b6)
    if len(rlab) == contents.shape[0] and row_labels_added == False:
        contents = np.hstack([rlab, contents])
    
    
    
    # Fold labels into contents:
    # Current assumes that upper right cell belows to row labels
    #new_contents = contents.copy()
    #if col_labels is not None:
    #    new_contents.insert(0, col_labels)
    #if row_labels is not None:
    #   for i, rl in enumerate(row_labels):
    #        new_contents[i].insert(0,rl)

    
    
    
    
    
    
    # -----------------------------------------
    # Add contents
    # -----------------------------------------
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
    
def TVM_SOLVER(N=None, I=None, PV=None, PMT=None, FV=None, max_iter=10000):
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
        
        for i in range(max_iter):
            old_x = x
            x = new_x(x)
            if abs(x - old_x) < 0.000000000001:
                break
        
        if i == max_iter-1:
            print('TVM_SOLVER failed to converge!')
            return None
            
        return x
    
    v = 1 / (1 + I)    
    
    if N is None:
        x1 = -PV - PMT / I
        x2 = FV - PMT / I
        n = np.log(x1/x2).item() / np.log(v).item()
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
    
    #x = 5.000003
    
    #print(NOT_EXACT_TO(x, 4))
    #print(NOT_EXACT_TO(x, 5))
    #print(NOT_EXACT_TO(x, 6))
    #print(NOT_EXACT_TO(x, 7))
    
    
    i = TVM_SOLVER(N=10, I=None, PV=-100, PMT=10, FV=50)
    
    print(i)
    
    
    '''
    x = COND(
        x='SAMPLE(1,10,1)',
        y='SAMPLE(1,10,1)',
        z='SAMPLE(1,10,1)',
        conds=[
            'x < y', 
            'x < z', 
            'y < z'
        ]
    )
    
    b = UNIQUE([6, 7, 8])
    print(b)
    '''