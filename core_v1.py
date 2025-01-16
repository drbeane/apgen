import numpy as np
from apgen.functions import *

MIN_DIFF = 0.02
MAX_DIFF = 0.10
NUM_DIST = 4
ANS_PREC = 0.0001
PRES_SIGN = False

config = dict(
    MIN_DIFF = 0.02,
    MAX_DIFF = 0.10,
    NUM_DIST = 4,
    ANS_PREC = 0.0001,
    PRES_SIGN = False
)
    


def generate_distractor(min_diff, max_diff, ans, distractors, max_attempts=1000):
    min_abs_diff = min_diff * ans
    for i in range(max_attempts):    
        d = np.random.uniform(low=ans*(1-max_diff), high=ans*(1+max_diff))
        
        valid = True
        for option in [ans] + distractors:
            if abs(option - d) < min_abs_diff:
                valid = False
                break
        if valid:
            return d
    
    print('No distractor found. ')
    0/0
        

def process_lines(lines):
    variables = {}
    distractors = []
    answer_options = []

    mode = None
    text = ''
    for line in lines:
        line = line.strip()
        
        # Skip blank lines unless processing the question text
        if line == '' and mode != 'TEXT':
            pass

        # Determine the mode
        elif line[:4] == '#---':
            mode = line

        elif mode == '#---VARIABLES---#':
            # After running the line below, the variable will be created
            # But must be accessed using eval(var_name)
            exec(line)  
            if '=' in line:
                #var_name, expr = line.replace(' ', '').split('=')
                var_name = line.replace(' ', '').split('=')[0]
                variables[var_name] = eval(var_name)

        elif mode == '#---CONDITIONS---#':
            valid = eval(line)
            if not valid:
                #print('invalid')
                return None, None, None, None, None
            
        elif mode == '#---DISTRACTORS---#':
            exec(line)
            if '=' in line:
                var_name, expr = line.replace(' ', '').split('=')
                value = eval(var_name)
                variables[var_name] = value
            
            #dist = eval(line)
            distractors.append(value)
        
        elif mode == '#---CONFIG---#':
            exec(line)
            var_name, expr = line.replace(' ', '').split('=')
            config[var_name] = eval(var_name)
            
            
        elif mode == '#---TEXT---#':
            line = line.strip(' ')
            if line == '':
                #text += '<!--newline--!>'
                #text += '<p>&nbsp;</p>'            # This might be what should be here. Dunno.
                text += '</br>'
            else:
                text += line + ' ' + '</br>'
                
        elif mode == '#---ANSWER_OPTIONS---#':
            line = f"f'{line}'"
            ao = eval(line)
            answer_options.append(ao)
    
    #print(answer_options)
    
    while text[-5:] == '</br>':
        text = text[:-5]
    
    answer = variables['ANS']
    
    # Pad Distractors
    
    #-----------------------------------------
    # I need to revisit this
    #-----------------------------------------
    n = NUM_DIST - len(distractors)
    for i in range(n):
        d = generate_distractor(MIN_DIFF, MAX_DIFF, answer, distractors)
        distractors.append(d)
        
    # Round Answer and Distractors
    ANS_PREC = float(config['ANS_PREC'])
    _, dec_portion = str(ANS_PREC).split('.')
    dec_digits = len(dec_portion)
    
    variables['ANS'] = ROUND(answer, ANS_PREC)
    
    distractors = [ROUND(d, ANS_PREC) for d in distractors]
                
    return text, variables, distractors, answer_options, dec_digits

class Question:

    def __init__(self, q=None, src=None, id=None):
        self.src = src
        self.q = q
        self.id = id
        self.qti_text = None
        
        self.versions = []
        
        if q is not None:
            self.q_string = q
        elif src is not None:
            with open(src) as f:
                self.q_string = f.read()

    def try_generate(self):  # Could be invalid
        lines = self.q_string.split('\n')

        
        text, variables, distractors, answer_options, self.dec_digits = process_lines(lines)
        
        if text is None:
            return None, None, None, None

        text = text.replace('{', '_OB_')
        text = text.replace('}', '_CB_')
        text = text.replace('[[', '{')
        text = text.replace(']]', '}')
        
        var_string = ', '.join([f'{k}={v}' for k,v in variables.items()])
        
        format_message = 'text.format({var_string})'.format(var_string=var_string)
        
        
        final_text = eval(format_message)
        final_text = final_text.replace('_OB_', '{')
        final_text = final_text.replace('_CB_', '}')
        final_text = final_text.rstrip('\n')
        
        return final_text, variables['ANS'], distractors, answer_options
        

    def generate(self, n=1, seed=None, attempts=1000, prevent_duplicates=True):
        from IPython.core.display import HTML, display
        
        self.versions = []
        
        generation_attempts = 0
        duplicates_encountered = 0
        
        if seed is not None:
            np.random.seed(seed)
        
        # Loop over the number of questions
        for i in range(n):
            # Attempt to generated a problem
            for k in range(attempts):
                generation_attempts += 1
                text, answer, distractors, answer_options = self.try_generate()
                
                
                success = True
                
                if text is None: success = False   # Check to see if conditions were met
                
                # Check to see if the question is a duplicate
                if prevent_duplicates:
                    for v in self.versions:
                        if text == v['text']:
                            duplicates_encountered += 1
                            success = False
                            break
                
                # Log question if it is a success
                if success: 
                    q = {
                        'text':text,
                        'answer':answer,
                        'distractors':distractors,
                        'answer_options': answer_options
                    }
                    self.versions.append(q)
                    break
        
        display(HTML('<h3>Generating Versions</h3>'))
        print(f'{generation_attempts} attempts were required to generate {n} versions. {duplicates_encountered} duplicate versions were generated and discarded.\n')
        


    def display_versions(self, size=3, limit=None, compact_answers=False):
        from IPython.display import HTML, display, Markdown
        
        if len(self.versions) == 0:
            print('No versions have been generated. Please call the generate() method.')
            return
        
        if limit is None: limit = len(self.versions) 
        limit = min(limit, len(self.versions))
        
        display(HTML('<h3>Displaying Versions</h3>'))
        for i in range(limit):
            text = self.versions[i]['text']
            answer = self.versions[i]['answer']
            distractors = self.versions[i]['distractors']
            answer_options = self.versions[i]['answer_options']
            
            #text = text.replace('<!--newline--!>', '\n\n')
            
            display(HTML(f'<h4>Version {i+1}</h4>'))
            display(Markdown(f'<font size="{size}">{text}</font>'))
            print()
            if compact_answers:
                print(answer_options)
                #distractor_str = ", ".join([str(d) for d in distractors])
                #print(f'Answer: {answer} \nDistractors: {distractor_str}')
            else:
                letters = list('abcdefghijklmnopqrstuvwzyz')
                for i, ao in enumerate(answer_options):
                    x = letters[i]
                    print(f'[{x}] {ao}' if i==0 else f'({x}) {ao}')
                
                #print(f'[a] {answer:.{self.dec_digits}f}')
                #letters = list('bcdefghijklmnopqrstuvwzyz')[:len(distractors)]
                #for x,d in zip(letters, distractors):
                #    print(f'({x}) {d:.{self.dec_digits}f}')
                
            print()    
        
        

    def generate_qti_text(self, shuffle=True):
        qti_text = f'Quiz title: {self.id}\n\n'
        qti_text += 'shuffle answers: true\n\n'
        
        for i, v in enumerate(self.versions):
            text = v['text']
            text = text.replace('\n', '\n      ')
            answer = v['answer']
            distractors = v['distractors']
            letters = list('abcdefghijklmnopqrstuvwxyz')
            
            correct_idx = 0
            option_array = np.array([answer] + distractors)
            
            qti_text += f'{i+1}.  {text}\n'
            
            # Shuffle Answers
            if shuffle:
                indices = np.arange(len(option_array))
                np.random.shuffle(indices)
                correct_idx = np.where(indices == 0)[0][0]
                option_array = option_array[indices]
                
            
            
            #qti_text += f'*a)  {answer:.{self.dec_digits}f}\n'
                    
            for i, opt in enumerate(option_array):
                star = '*' if indices[i] == 0 else ''
                qti_text += f'{star}{letters[i]})  {opt:.{self.dec_digits}f}\n'
                
            #qti_text += f'=   {answer} +- 0.0001\n'
            qti_text += '\n\n'
        
        self.qti_text = qti_text
        
        
    def generate_qti(self):
        import subprocess 
        
        fname = f'output/{self.id}.txt'
        #fname = f'{self.id}.txt'
        
        self.generate_qti_text()
        f = open(fname, 'w')
        f.write(self.qti_text)
        f.close()        
        
        result = subprocess.run(f'text2qti {fname}', capture_output=True, text=True)
        
        if result.returncode != 0:
            print(result.returncode)
            print()
            print(result.stdout)
            print()
            print(result.stderr)
        else:
            print('QTI Generated Successfully!')


if __name__ == '__main__':

    #q = Question(src = '../problems/03d_01.txt')
    q = Question(src = '../problems/04a_01.txt')
    #print(q.q_string)
    
    q.generate_one()
    #print(RANGE(10, 150, 5))