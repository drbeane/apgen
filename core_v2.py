import numpy as np
from amps.functions import *


class Question:

    def __init__(self, qt=None, file=None, id=None):
        '''
        Parameters 
            file - path for file containing problem template
            qt - question template (string)
            id - identifier for problem
        '''
        
        self.file = file
        self.qt = qt
        self.id = id
        #self.qti_text = None
        
        #self.versions = []
        
        if qt is None and file is None:
            print('No problem template has been provided.')
            return
        
        if qt is None:
            with open(file) as f:
                self.qt = f.read()


    #------------------------------------------------------------
    # generate function creates versions from template
    #------------------------------------------------------------
    def generate(self, n=1, seed=None, attempts=1000, prevent_duplicates=True):
        '''
        Description: Creates versions from template
        
        Paramters:
        n                  : Number of versions to generate.
        attempts           : Total number of attempts allowed to generate each question
        prevent_duplicates : ??????????????????
        seed               : Seed for RNG
        '''
        
        from IPython.core.display import HTML, display
        
        self.versions = []
        
        generation_attempts = 0
        duplicates_encountered = 0
        
        if seed is not None:
            np.random.seed(seed)
        
        
        # Loop for the desired number of questions
        for i in range(n):
            
            # Attempt to generated a problem
            for k in range(attempts):
                
                generation_attempts += 1
                version = self.generate_one()
                
                # Check to see if conditions were met.
                # If not, restart loop and try again. 
                if version is None:
                    continue
                
                
                # Check to see if the question is a duplicate
                # If so, restart loop and try again. 
                if prevent_duplicates:
                    dup = False
                    for v in self.versions:
                        if version['text'] == v['text']:
                            duplicates_encountered += 1
                            dup = True 
                            break
                    if dup: continue
                
                break  # if here, a version was found
            
            # Add version to list
            self.versions.append(version)
                
        
        display(HTML('<h3>Generating Versions</h3>'))
        print(f'{generation_attempts} attempts were required to generate {n} versions. {duplicates_encountered} duplicate versions were generated and discarded.\n')
        

    def generate_one(self, testing_level=0):
        from IPython.core.display import HTML, display
        
        variables = {}
        distractors = []
        answer_options = []


        scope = {}
        exec('from amps.functions import *', scope)

        mode = None
        text = ''
        need_new_par = True
        need_end_par = False
        table_mode = False
        table_contents = []
        table_config = {}
        
        lines = self.qt.split('\n')
        
        for line in lines:
            if testing_level > 4: print(line)
            line = line.strip()
            
            # Skip blank lines unless processing the question text
            if line == '' and mode != '#---TEXT---#':
                pass

            #-----------------------------------------------
            # Determine the mode
            #-----------------------------------------------
            elif line[:4] == '#---':
                mode = line
                if testing_level > 2: print(f'\nSetting mode to {mode}')

            #-----------------------------------------------
            #   VARIABLES
            #-----------------------------------------------
            elif mode == '#---VARIABLES---#':
                # After running the line below, the variable will be created
                # But must be accessed using eval(var_name)
                exec(line, scope)  
                if testing_level >=3: 
                    var_string = line.replace(' ', '').split('=')[0]   # split on equal sign
                    var_list = var_string.split(',')
                    for v in var_list:
                        print(f'  VARIABLE: {v} = {scope[v]}')

            #-----------------------------------------------
            #  DISTRACTORS 
            #-----------------------------------------------
            elif mode == '#---DISTRACTORS---#':
                exec(line, scope)  
                if testing_level >=3: 
                    var_string = line.replace(' ', '').split('=')[0]   # split on equal sign
                    var_list = var_string.split(',')
                    for v in var_list:
                        print(f'  VARIABLE: {v} = {scope[v]}')


            #-----------------------------------------------
            #  CONDITIONS
            #-----------------------------------------------
            elif mode == '#---CONDITIONS---#':
                valid = eval(line, scope)
                if not valid:
                    if testing_level >=3: 
                        print(f'  Unsatisfied Condition: "{line}"')
                    return None


            #-----------------------------------------------
            #  CONFIG
            #-----------------------------------------------
            elif mode == '#---CONFIG---#':
                exec(line, scope)
                #var_name, expr = line.replace(' ', '').split('=')
                #config[var_name] = eval(var_name)
                
            
            #-----------------------------------------------
            #  TEXT
            #-----------------------------------------------
            elif mode == '#---TEXT---#':
                
                line = line.strip(' ')
                
                # Process Tables
                if line == 'TABLE':
                    table_mode = True
                    
                elif line == 'END TABLE':
                    text += TABLE(table_contents, table_config)
                    
                    table_mode = False
                    table_contents = []
                    table_config = {}
                    
                
                elif table_mode == True:
                    if line[0] == '|':
                        cells = line.split('|')[1:-1]
                        cells = [c.strip(' ') for c in cells]
                        table_contents.append(cells)
                    else:
                        params = line.split(',')
                        for p_set in params:
                            p,v = p_set.split(':')
                            p = p.strip(' ')
                            v = v.strip(' ')
                            if np.char.isnumeric(v) or v == 'True' or v == 'False':
                                v = eval(v)
                            table_config[p.lower()] = v
                    
                        
                
                # A blank line indicates the start of a new paragraph. 
                # Consecutive blank lines are treated as a single blank line (at least for now)
                # The <p> tag will be added at a later line. 
                elif line == '':
                    need_new_par = True
                    if need_end_par == True:
                        text += '</p>'
                        need_end_par = False
                
                # Check to see if current line is a continuation of previous lines. 
                # If so, append a space and the new line of text.
                elif line[:3] == '...':
                    line = line[3:].strip(' ')
                    text += ' ' + line
                
                # Standard line of text. This will either start a new par or a new line.
                else:
                    if need_new_par == True:
                        text += '<p>' + line
                        need_new_par = False
                        need_end_par = True
                    else:
                        text += '<br />' + line
                
                if testing_level >= 3:
                    print(f'  PROCESSING {line:50} {need_new_par = }, {need_end_par = }')        
                
                    
            elif mode == '#---ANSWER_OPTIONS---#':
                line = f"f'{line}'"
                ao = eval(line, scope)
                answer_options.append(ao)
        
        # Close final paragraph in text.
        if need_end_par == True: 
            text += '</p>'
        
        if testing_level >=5: 
            print(f'\nQUESTION TEXT:\n{text}')
        
        # Delete builtins. Just for tidiness. 
        del scope['__builtins__']
        
        for k, v in scope.items():
            if isinstance(v, float):
                scope[k] = round(v, 12)
            
        
        
        # Insert variables into text and answer options. 
        text = insert_vars(text, scope)
        answer_options = [insert_vars(ao, scope) for ao in answer_options]
        
        if testing_level >=3: 
            print(f'\nQUESTION TEXT:\n{text}')
            
            display(HTML('<h3>HTML Output</h3>'))
            display(HTML(text))
            
        if testing_level >= 3:
            display(HTML('<h3>Answer Options</h3>'))
            for ao in answer_options:
                print(ao)
        
        return {'text':text, 'answer_options':answer_options}


    def display_versions(self, size=3, limit=None, compact_answers=False):
        from IPython.display import HTML, display, Markdown
        
        if len(self.versions) == 0:
            print('No versions have been generated. Please call the generate() method.')
            return
        
        if limit is None: limit = len(self.versions) 
        limit = min(limit, len(self.versions))
        
        display(HTML('<b>Displaying Versions</b><br /><br />'))
        for i in range(limit):
            text = self.versions[i]['text']
            answer_options = self.versions[i]['answer_options']
            
            display(HTML(f'<b>Version {i+1}</b>'))
            display(Markdown(f'<font size="{size}">{text}</font>'))
            print()
            if compact_answers:
                print(answer_options)
            else:
                letters = list('abcdefghijklmnopqrstuvwzyz')
                for i, ao in enumerate(answer_options):
                    x = letters[i]
                    print(f'[{x}] {ao}' if i==0 else f'({x}) {ao}')
            print()    
            

def insert_vars(text, scope):
    a = 0
    b = 0
    temp = text
    new_text = ''
    while len(temp) > 0:
        
        a = temp.find('[[')
        b = temp.find(']]', a)
        
        if a == -1 or b == -1:
            new_text += temp 
            break
        
        var_string = temp[a+2:b]      
        new_text += temp[:a]
        new_text += DISPLAY(var_string, scope)            
        
        temp = temp[b+2:]

    return new_text

        
def DISPLAY(x, scope):
       
    tokens = x.split(':')
    
    var_name = tokens[0]
    value = eval(var_name, scope)
    
    
    # If only a value is supplied, find it and move on
    if len(tokens) == 1:
        return str(value)
    
    # Get params (they exist, if we get to this point)
    param_string = tokens[1]
    params = param_string.split(',')
    
    prec = params[0].strip()
    fmt = 'U' if len(params) == 1 else params[1].strip()

    if prec != '':
        # If var_name contains operations (x*10) then format method will break.
        # We will create a temp variable to handle this situation. 
        if var_name not in scope.keys():
            scope['__TEMP_VAR__'] = value
            var_name = '__TEMP_VAR__'
        
        f_string = '{' + f'{var_name}:.{prec}f' + '}'
        val_string = f_string.format(**scope)
        value = round(value, int(prec))
    
    
    # Check to see if number is a leading coefficient
    if fmt in ['Ca', 'C0']:
        if value == 1: return ''                        #  1 --> ''
        if value == -1: return '- '                     # -1 -->  -
        if value >= 0: return str(value)                #  x -->  x    
        if value < 0: return  ' - ' + str(abs(value))   # -x --> -x
    
    # Check to see if number is a leading coefficient
    if fmt in ['Cb', 'C1']:
        if value == 1: return '+ '                      #  1 -->  +
        if value == -1: return '- '                     # -1 -->  -
        if value >= 0: return '+ ' + str(value)         #  x --> +x    
        if value < 0: return  '- ' + str(abs(value))    # -x --> -x
        
    # Check to see if number is a leading coefficient
    if fmt in ['Cc', 'C2']:
        if value >= 0: return '+ ' + str(value)         #  x --> +x    
        if value < 0: return  '- ' + str(abs(value))    # -x --> -x
    
    
    return val_string
        