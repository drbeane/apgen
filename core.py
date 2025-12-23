import numpy as np
from apgen.functions import *

class Question:

    def __init__(self, qt=None, file=None):
        '''
        Class representing a single question. 
        
        PARAMETERS
        file : path for file containing question template
        qt   : string containing question template
        '''
        
        # Create some basic attributes
        self.file = file             
        self.qt = qt
        self.type = 'MC'
        self.margin = '0'
        self.error_log={}
        self.attempt_counts = {}  # Used during version generation
        
        # Set default delimiters. This can be changed in the CONFIG section of the template.
        self.var_delim = '[[ ]]'     
        self.eqn_delim = '$ $'
        
        # Create items to store information from template
        self.var_script = ''         # Stores script for variable creation. 
        self.conditions = []         # List of conditions
        self.text_raw = ''           # Stores the raw text from the template. 
        self.text = ''               # Store the processed text (w/o var eval). 
        self.answer_options = []
        self.versions = []
        self.max_versions = float('inf')
        
        # Check if a template has been provided. 
        if qt is None and file is None:
            print('No problem template has been provided.')
            return
        
        # If template file has been provided, load it. 
        if qt is None:
            with open(file) as f:
                self.qt = f.read()
            # Get id from filename if no id has been provided
            if id is None:
                filename = file.split('/')[-1]
                self.id = filename.split('.')[0]
        self.qt = self.qt.strip()

        # Parse the template and text
        self.__parse_template__()
        self.__parse_text__()
        

    def __parse_template__(self):
        
        mode = None
        
        # Split question template
        lines = self.qt.split('\n')
        
        for line in lines:
            
            #line = line.strip()
            
            #-----------------------------------------------------
            # Skip blank lines unless processing the question text
            #-----------------------------------------------------
            if line == '' and mode != '#---TEXT---#':
                pass

            #-----------------------------------------------
            # Determine the mode
            #-----------------------------------------------
            elif line[:4] == '#---':
                mode = line.strip()
            
            #-----------------------------------------------
            # config
            #-----------------------------------------------
            elif mode == '#---CONFIG---#':
                line = line.strip(' ')
                line = line.replace('= ', '=')
                line = line.replace(' =', '=')
                #print(len(line))
                param, value = line.split('=')
                if param == 'type':
                    self.type = value
                elif param == 'margin':
                    self.margin = value
                elif param == 'id':
                    self.id = value
                elif param == 'max_versions':
                    self.max_versions = int(value)
            
            #-----------------------------------------------
            # VARIABLES
            #-----------------------------------------------
            elif mode == '#---VARIABLES---#':
                self.var_script += line + '\n'
            
            #-----------------------------------------------
            # Distractors
            #-----------------------------------------------
            elif mode == '#---DISTRACTORS---#':
                self.var_script += line + '\n'
                
            #-----------------------------------------------
            #  CONDITIONS
            #-----------------------------------------------
            elif mode == '#---CONDITIONS---#':
                self.conditions.append(line)
                
            #-----------------------------------------------
            #  TEXT
            #-----------------------------------------------
            elif mode == '#---TEXT---#':
                self.text_raw += line + '\n'

            #-----------------------------------------------
            # ANSWER_OPTIONS
            #-----------------------------------------------
            elif mode == '#---ANSWER_OPTIONS---#':
                self.answer_options.append(line)
  
        # Line below allows users to use ^ for exponentiation. 
        self.var_script = self.var_script.replace('^', '**')
  

    def __parse_text__(self):
        self.text_raw = self.text_raw.strip()
        
        self.text_sections = []
        
        cur_sec = {'mode':'text', 'prev':None, 'next':None, 'lines':[]}
        
        mode = 'text'
        
        lines = self.text_raw.split('\n')
        for line in lines:
            prev_mode = mode
            
            #---------------------------------------
            # Determine new mode
            # -- blank, table, list, eqn, text
            #---------------------------------------
            stripped = line.strip(' ')
            if stripped == '':
                mode = 'blank'
            elif stripped == 'TABLE' or mode == 'table':    
                mode = 'table'
            elif stripped[0] == '*':
                mode = 'list'
                
            # Check for non-inline equations. Nothing happens with inline equations yet. 
            elif stripped[0] == '$' and stripped[-1] == '$':
                mode = 'eqn' 
            else:
                mode = 'text'
            
            # Append content if mode has not changed
            # Also start a new component for equations. 
            if prev_mode == mode and mode != 'eqn':
                cur_sec['lines'].append(line)
            
            # If mode has changed, start a new component. 
            else:
                cur_sec['next'] = mode
                old_mode = cur_sec['mode']
                self.text_sections.append(cur_sec)
                cur_sec = {'mode':mode, 'prev':old_mode, 'next':None, 'lines':[line]}
            
            if stripped == 'END TABLE':
                mode = None
       
        
        self.text_sections.append(cur_sec)
    
        # This is just for testing. Lets me get some info about the sections. 
        for s in self.text_sections:
            #print(s)
            temp = s.copy()
            temp['lines'] = len(temp['lines'])
            #print(temp)

        text = ''
        for s in self.text_sections:
            text += self.__process_section__(s)
        
        self.text = text
        
        
    def __process_section__(self, s):
        text = ''
        
        if s['mode'] == 'text':
            # Start new paragraph, if needed
            if s['prev'] != 'text':
                text += '<p style="margin: 0px 0px 10px 0px;">'
                
            # Glue lines together. 
            for line in s['lines']:
                text += line.strip(' ') + ' '
            
            # Close paragraph
            text = text.strip()
            text += '</p>\n'
        
        elif s['mode'] == 'blank':
            n = len(s['lines'])
            if n > 1:
                text += f'<div style="height: {10*(n-1)}px;">&nbsp;</div>\n'
            
        elif s['mode'] == 'list':
            text += '<ul>\n'
            
            # Add list items
            for line in s['lines']:
                line = line[1:].strip(' ')
                text += f'    <li style="margin-bottom: 5px">{line}</li>\n'
            
            # End list
            text += '</ul>\n'
        
        # This is just for non-inline equations. 
        # Determines if the equation should be centered, tabbed, or left-aligned. 
        elif s['mode'] == 'eqn':
            
            for line in s['lines']:  # There should always be only one line in an EQN section. 
                if line[:2] == '$$':
                    text += f'<p style="text-align: center; margin: 0px 0px 10px 0px;">{line}</p>\n'
                elif line[:4] == '    ':
                    text += f'<p style="padding-left:40px; margin: 0px 0px 10px 0px;">{line}</p>\n'
                else:
                    text += f'<p margin: 0px 0px 10px 0px;>{line}</p>\n'
        
        elif s['mode'] == 'table':
            
            table_contents = []
            table_config = {}
            
            for line in s['lines'][1:-2]:
                cells = line.split('|')[1:-1]
                cells = [c.strip(' ') for c in cells]
                table_contents.append(cells)
            params = s['lines'][-2].split(';')
            for p_set in params:
                p,v = p_set.split(':')
                p = p.strip(' ')
                v = v.strip(' ')
                if v not in ['C', 'L', 'R']:
                    v = eval(v)
                table_config[p.lower()] = v
            
            text += TABLE(contents=table_contents, config=table_config, inc_margin=False)

        return text
        

    #------------------------------------------------------------
    # generate function creates versions from template
    #------------------------------------------------------------
    def generate(self, n=1, seed=None, time_limit=None, max_attempts=100_000, prevent_duplicates=True, 
                 safe_mode=False, progress_bar=False, updates=None, report_errors=True, compact_output=False):
        
        #-------------------------------------------------------------------------------------------------
        #  Description: Creates versions from template
        #-------------------------------------------------------------------------------------------------
        #  Paramters:
        #  n                  : Number of versions to generate.
        #  max_attempts           : Total number of attempts allowed to generate n questions
        #  time_limt          : Time limit for version generation
        #  prevent_duplicates : If true, question texts are compared and repeats are discarded. 
        #  seed               : Seed for RNG
        #  compact_output     : Compact output primarily used for batch generation. 
        #-------------------------------------------------------------------------------------------------
        
        
        from IPython.core.display import HTML, display
        from tqdm.notebook import tqdm
        import time
        import re
        
        self.versions = []
        
        self.num_attempts = 0
        
        if seed is not None:
            # This sets the "global" seed for the generation process.
            # Each version will also have its own seed. 
            np.random.seed(seed)
        
        
        # Create Progress Bar and Range
        if progress_bar == True:
            my_range = tqdm(range(n))
        else:
            my_range = range(n)
        
        #-------------------------------------------------------------------
        # Dict for counting results
        #-------------------------------------------------------------------
        self.attempt_counts = {'success':0, 'duplicate':0, 'error':0, 'condition':0}
        
        #-------------------------------------------------------------------
        # Time and flag for checking time limit and max versions.
        #-------------------------------------------------------------------
        t0 = time.time()
        limit_reached = False
        
        #-------------------------------------------------------------------
        # Loop for the desired number of versions
        #-------------------------------------------------------------------
        for i in my_range:
            
            #-------------------------------------------------------------------
            # Attempt to generate a problem
            #-------------------------------------------------------------------
            while True:
                
                #-------------------------------------------------------------------
                # Increment counter and check to see if limit has been reached
                #-------------------------------------------------------------------
                if self.num_attempts >= max_attempts:
                    print()
                    display(HTML('<b><font color="DC143C" size=5>--VERSION GENERATION FAILED--</font></b>'))
                    print(f'Failed to generate {n} versions in {max_attempts} attempts.')
                    print(f'{len(self.versions)} versions successfully generated.')
                    print('Consider increasing the max_attempts parameter or adjusting problem template.')
                    limit_reached = True
                    break

                #-------------------------------------------------------------------
                # Check if time limit reached
                #-------------------------------------------------------------------
                dt = time.time() - t0
                if time_limit is not None and dt > time_limit:
                    print()
                    display(HTML('<b><font color="DC143C" size=5>--VERSION GENERATION FAILED--</font></b>'))
                    print(f'Failed to generate {n} versions in {time_limit} seconds.')
                    print(f'{len(self.versions)} versions successfully generated.')
                    print('Consider increasing the time_limit parameter or adjusting problem template.')
                    limit_reached = True
                    break

                # If limit not reached, move on to next version. 
                self.num_attempts += 1

                #-------------------------------------------------------------
                # Generate Seed for current version
                #-------------------------------------------------------------
                temp = np.random.uniform(1,10)
                version_seed = int(100000*temp)
                
                #-------------------------------------------------------------
                # Store state so that "global" seed can be reinstated later. 
                #-------------------------------------------------------------
                np_state = np.random.get_state()
                                
                #-------------------------------------------------------------
                # Attempt to Generate a Version
                #-------------------------------------------------------------
                version = self.generate_one(version_seed, report_errors)
                
                #-------------------------------------------------------------
                # Restore the global random state
                #-------------------------------------------------------------
                np.random.set_state(np_state)
                
                #-------------------------------------------------------------
                #  Check if version was generated sucessfully. 
                #  (no errors + conditions met)
                #  If not, restart loop and try again
                #-------------------------------------------------------------
                if version['status'] != 'Success':
                    continue
                
                #-------------------------------------------------------------
                #  Check if version is a duplicate.
                #  If so, restart loop and try again
                #-------------------------------------------------------------
                if prevent_duplicates:
                    
                    # Names need to be stripped out since they mess up the duplicate checking process
                    text_no_names = re.sub(r'__NAMEa__.*?__NAMEb__', '', version['text'])
                    
                    dup = False
                    for v in self.versions:
                        other_text = re.sub(r'__NAMEa__.*?__NAMEb__', '', v['text'])
                        
                        if text_no_names == other_text:
                        #if version['text'] == v['text']:
                            self.attempt_counts['duplicate'] += 1
                            dup = True 
                            break
                    if dup: 
                        version = None
                        continue
                
                break  # if here, a version was found
            
            
            #-------------------------------------------------------------
            # Check if a limit was reached. If so, exit. 
            #-------------------------------------------------------------
            if limit_reached:
                break
            
            #-------------------------------------------------------------
            # If here, a version was found. Add it to list
            #-------------------------------------------------------------
            self.attempt_counts['success'] += 1
            self.versions.append(version)
            
            # Print update
            if updates is not None and i % updates == 0:
                print(f'{i+1} versions generated.')
        
        
        
        #-------------------------------------------------------------
        # Version generation complete (or terminated, at least)
        #-------------------------------------------------------------
        
        #-------------------------------------------------------------
        # Time to remove name delimiters
        #-------------------------------------------------------------
        for i, v in enumerate(self.versions):
            self.versions[i]['text'] = self.versions[i]['text'].replace('__NAMEa__', '')
            self.versions[i]['text'] = self.versions[i]['text'].replace('__NAMEb__', '')
            self.versions[i]['colab_text'] = self.versions[i]['text'].replace('__NAMEa__', '')
            self.versions[i]['colab_text'] = self.versions[i]['text'].replace('__NAMEb__', '')
        
        #-------------------------------------------------------------
        # Output results 
        # -- Standard is typical. 
        # -- Compact is used for batch processing. 
        #-------------------------------------------------------------
        num_versions = len(self.versions)
        
        if compact_output:
            print(f'{self.id:<24}  -- {self.num_attempts:>5} attempts  -- {num_versions:>3} versions')
        
        else:        
            print()
            
            display(HTML('<b><font size=5>Versions Generated</font></b>'))
            print(f'{self.num_attempts} attempts were required to generate {num_versions} versions.')
            print(f'{self.attempt_counts["duplicate"]} duplicate versions were generated and discarded.')
            print(f'{self.attempt_counts["condition"]} attempts failed to satisfy the conditions.')
            print(f'{self.attempt_counts["error"]} attempts resulted in errors.\n')
            
            if report_errors and len(self.error_log) > 0:
                display(HTML('<b><font size=5>Errors Encountered</font></b>'))
                for e,v in self.error_log.items():
                    display(HTML(f'The following error occurred {v["count"]} times:'))
                    print('   ', e)
                    display(HTML(f'Relevant seed values:'))
                    print(v['seeds'])
        
        return 
        

    def generate_one(self, seed, report_errors=True):
        from IPython.core.display import HTML, display
        import warnings
        warnings.filterwarnings('error', category=RuntimeWarning)
        
        #-------------------------------------------------------------
        # Set the seed provided
        #-------------------------------------------------------------
        np.random.seed(seed)
        
        #-------------------------------------------------------------
        # Prepare the scope. Code will be executed with this scope. 
        # pre_scope is used to determine what to delete from scope 
        # after vars have been added
        #-------------------------------------------------------------
        scope = {}
        exec('from apgen.functions import *', scope)
        pre_scope = scope.copy()   
        
        #-------------------------------------------------------------
        # Create Dictionary for storing information about the version
        #-------------------------------------------------------------
        version_dict = {
            'status': 'Success',
            'version_seed': seed,
            'text' : None,
            'colab_text': None,
            #'jupyter_text': None,
            'qti_text': None,
            'answer_options' : None,
            'var_defns' : scope
        }
        
        #-------------------------------------------------------------
        # Execute Variables
        #-------------------------------------------------------------
        try:
            exec(self.var_script, scope)
        
        except Exception as e:
            # Error encountered
            self.attempt_counts['error'] += 1
            # Log the Error
            e = repr(e)
            if e not in self.error_log.keys(): self.error_log[e] = {'count':0, 'seeds':[]}
            self.error_log[e]['count'] += 1
            self.error_log[e]['seeds'].append(seed)
            version_dict['status'] = 'Error'
            for k in pre_scope.keys(): del scope[k]
            return version_dict
        
        #-------------------------------------------------------------
        # Get rid of precision/rounding issues.
        #-------------------------------------------------------------
        for k, v in scope.items():
            if isinstance(v, float):
                scope[k] = round(v, 12)
        
        #-------------------------------------------------------------
        # Check conditions, return if invalid
        #-------------------------------------------------------------
        for cond in self.conditions:
            try:
                valid = eval(cond, scope)
            except Exception as e:
                self.attempt_counts['error'] += 1
                e = repr(e)
                if e not in self.error_log.keys(): self.error_log[e] = {'count':0, 'seeds':[]}
                self.error_log[e]['count'] += 1
                self.error_log[e]['seeds'].append(seed)
                version_dict['status'] = 'Error'
                for k in pre_scope.keys(): del scope[k]
                return version_dict
                
            if not valid:
                self.attempt_counts['condition'] += 1
                version_dict['status'] = 'Conditions Failed'
                for k in pre_scope.keys(): del scope[k]
                return version_dict
        
        #-------------------------------------------------------------
        # Determine Answer Values
        #-------------------------------------------------------------
        try:
            text_w_vars = insert_vars(self.text, scope)
            ans_w_vars = [insert_vars(ao, scope) for ao in self.answer_options]
        except Exception as e:
            self.attempt_counts['error'] += 1
            e = repr(e)
            if e not in self.error_log.keys(): self.error_log[e] = {'count':0, 'seeds':[]}
            self.error_log[e]['count'] += 1
            self.error_log[e]['seeds'].append(seed)
            version_dict['status'] = 'Error'
            for k in pre_scope.keys(): del scope[k]
            return version_dict
            
        #-------------------------------------------------------------
        # Clean up the scope. 
        # Remove anything not directly relevant to the problem.
        #-------------------------------------------------------------
        for k in pre_scope.keys():
            del scope[k]
        
        #-------------------------------------------------------------
        # Add the text and answer values to the version dict
        #-------------------------------------------------------------
        version_dict['text'] = text_w_vars
        version_dict['answer_options'] = ans_w_vars
        
        return version_dict


    def create_display_html(self, size=3, limit=None, compact_answers=False, show_seeds=False):
        #-------------------------------------------------------------
        # Creates HTML for displaying question version. 
        #-------------------------------------------------------------
        
        from IPython.display import HTML, display, Markdown, Latex, Javascript
        import sys
        
        #-------------------------------------------------------------
        # Check if Colab. If so, we need a few hacks.
        #-------------------------------------------------------------
        COLAB = 'google.colab' in sys.modules
        
        #-------------------------------------------------------------
        # Check if versions have been created. 
        #-------------------------------------------------------------
        if len(self.versions) == 0:
            out = '<b><font size=5>No Versions to Display</font></b>\n'
            out += '<p>No versions have been generated.</p>'
            return out
        
        #-------------------------------------------------------------
        # Determine number of questions to display 
        #-------------------------------------------------------------
        if limit is None: limit = len(self.versions) 
        limit = min(limit, len(self.versions))
        
        #-------------------------------------------------------------
        # Add "Displaying Versions" Header
        #-------------------------------------------------------------
        out = '<b><font size=5>Displaying Versions</font></b>'

        #-------------------------------------------------------------
        # Add Versions to the output
        #-------------------------------------------------------------
        for i in range(limit):
            # Obtain version text. This is used when not in Colab
            question_text = self.versions[i]['text']
                        
            # Mess around with Dollar Signs to be able to use Katex in Colab. 
            colab_text = question_text.replace(r'\$', '__DOLLAR__SIGN__')   # Replace escaped dollar signs. 
            colab_text = colab_text.replace(r'$$', '__DEQN__')           # Replace $$ with __$$__ to be used with Katex
            colab_text = colab_text.replace(r'$', '__EQN__')             # Replace $ with __$__ to be used with Katex
            colab_text = colab_text.replace('__DOLLAR__SIGN__', r'$')    # Put escaped dollar signs back in as $. 
            
            #-------------------------------------------------
            # Display the version text (without answers)
            #-------------------------------------------------
            seed_text = f'  <font size=2>({self.versions[i]["version_seed"]})</font>' if show_seeds else ''
            
            # Add Version Number and Seed
            out += f'<br/><br/><hr><p>'
            out += f'<b><font size=4>Version {i+1}</font></b>{seed_text}<br/>'
            
            # Add Either Colab or Standard text, as needed
            if COLAB:   
                out += f'<font size="{size}">{colab_text}</font></p>'
            else:
                out += f'<font size="{size}">{question_text}</font></p>'
            self.versions[i]['colab_text'] = colab_text
            
            #-----------------------------------------------
            # Display the Answers
            #-----------------------------------------------
            out += f'<p><b><font size={size}>Answer Options</font></b></p>'
            
            answer_options = self.versions[i]['answer_options'].copy()
            if COLAB:
                for i, ao in enumerate(answer_options):
                    ao = str(ao)
                    ao = ao.replace(r'\$', '__DOLLAR__SIGN__')   # Replace escaped dollar signs. 
                    ao = ao.replace(r'$$', '__DEQN__')           # Replace $$ with __$$__ to be used with Katex
                    ao = ao.replace(r'$', '__EQN__')             # Replace $ with __$__ to be used with Katex
                    ao = ao.replace('__DOLLAR__SIGN__', r'$')    # Put escaped dollar signs back in as $. 
                    answer_options[i] = ao
            
            # Multiple Choice
            if self.type == 'MC':
                
                letters = list('abcdefghijklmnopqrstuvwzyz')
                ans_str = ''
                for i, ao in enumerate(answer_options):
                    x = letters[i]
                    ans_str += f'<tt>[{x}]</tt> {ao}' if i==0 else f'<tt>({x})</tt> {ao}'
                    ans_str += '&nbsp'*12 if compact_answers else '<br/>\n'
                ans_str = ans_str.strip('\n')
                out += ans_str
                        
            # Multiple Answer
            elif self.type == 'MA':
                ans_str = ''
                for i, ao in enumerate(answer_options):
                    #print(f'[{x}] {ao}' if i==0 else f'({x}) {ao}')
                    ao_mod = ao
                    if ao_mod[:3] == '[ ]': ao_mod = '<tt>[ ]</tt>' + ao_mod[3:]
                    elif ao_mod[:3] == '[X]': ao_mod = '<tt>[X]</tt>' + ao_mod[3:]
                    
                    ans_str += f'{ao_mod}'
                    ans_str += '&nbsp'*12 if compact_answers else '<br/>\n'
                ans_str = ans_str.strip('\n')
                out += ans_str
                
            # Numerical
            elif self.type == 'NUM':
                out += f'ANSWER: {answer_options[0]}'
            
            # Matching
            elif self.type == 'MT':
                for ao in answer_options:
                    out += f'{ao}'    
        
        #-------------------------------------------------------------
        # Close out the HTML for the current version
        #-------------------------------------------------------------
        out += '<br/><br/><hr>'
        
        return out
    
    def display_versions(self, size=3, limit=None, compact_answers=False, show_seeds=False):    
        from IPython.display import HTML, display, Markdown, Latex, Javascript
        import sys
        
        #-------------------------------------------------------------
        # Check if Colab. If so, we need a hack to render LaTex
        #-------------------------------------------------------------
        COLAB = 'google.colab' in sys.modules
        if COLAB: # Part of hack to make Colab render LaTex
            display(Latex(""))
        
        #-------------------------------------------------------------
        # Generate HTML output
        #-------------------------------------------------------------
        out = self.create_display_html(
            size=size, limit=limit, compact_answers=compact_answers, show_seeds=show_seeds
        )
        display(HTML(out))
        
        #-------------------------------------------------------------
        # More Colab hacking. Uses katex.
        #-------------------------------------------------------------
        if COLAB: 
            from apgen.autorender import katex_autorender_min
            display(Javascript(katex_autorender_min))



    def display_versions_OLD(self, size=3, limit=None, compact_answers=False, show_seeds=False):
        #-------------------------------------------------------------
        # This was deprecated in early 2025. Should be deleted eventually. 
        #-------------------------------------------------------------
        
        from IPython.display import HTML, display, Markdown, Latex, Javascript
        import sys
        COLAB = 'google.colab' in sys.modules
        
        # Check to see if versions have been created. 
        if len(self.versions) == 0:
            print('No versions have been generated. Please call the generate() method.')
            return
        
        # Determine number to display 
        if limit is None: limit = len(self.versions) 
        limit = min(limit, len(self.versions))
        
        
        # Part of hack to make Colab render LaTex
        display(Latex(""))
        
        # Diplaying Versions Header
        display(HTML(f'<b><font size=5>Displaying Versions</font></b>' ))
        
        # Add Versions
        for i in range(limit):
            
            # Just add the version text with no processing if in Jupyter
            question_text = self.versions[i]['text']
                        
            # Mess around with Dollar Signs to be able to use Katex in Colab. 
            colab_text = question_text.replace(r'\$', '__DOLLAR__SIGN__')   # Replace escaped dollar signs. 
            colab_text = colab_text.replace(r'$$', '__DEQN__')           # Replace $$ with __$$__ to be used with Katex
            colab_text = colab_text.replace(r'$', '__EQN__')             # Replace $ with __$__ to be used with Katex
            colab_text = colab_text.replace('__DOLLAR__SIGN__', r'$')    # Put escaped dollar signs back in as $. 
            
            #-------------------------------------------------
            # Display the actual version (without answers)
            #-------------------------------------------------
            seed_text = f'  <font size=2>({self.versions[i]["version_seed"]})</font>' if show_seeds else ''
            display(HTML(f'<hr><p style="margin: 0px 6px 6px 0px;"><b><font size=4>Version {i+1}</font></b>{seed_text}<br/><br/></p>'))
            
            
            if COLAB:   # Display colab_text
                display(HTML(f'<font size="{size}">{colab_text}</font><br/>'))
            else:
                display(HTML(f'<font size="{size}">{question_text}</font><br/>'))
                
                
            self.versions[i]['colab_text'] = colab_text
            #self.versions[i]['jupyter_text'] = question_text
                        
            #-----------------------------------------------
            # Display Answers
            #-----------------------------------------------
            display(HTML(f'<b><font size={size}>Answer Options</font></b>'))
            
            answer_options = self.versions[i]['answer_options'].copy()
            if COLAB:
                for i, ao in enumerate(answer_options):
                    ao = str(ao)
                    ao = ao.replace(r'\$', '__DOLLAR__SIGN__')   # Replace escaped dollar signs. 
                    ao = ao.replace(r'$$', '__DEQN__')           # Replace $$ with __$$__ to be used with Katex
                    ao = ao.replace(r'$', '__EQN__')             # Replace $ with __$__ to be used with Katex
                    ao = ao.replace('__DOLLAR__SIGN__', r'$')    # Put escaped dollar signs back in as $. 
                    answer_options[i] = ao
            
            # Multiple Choice
            if self.type == 'MC':
                
                letters = list('abcdefghijklmnopqrstuvwzyz')
                out = ''
                for i, ao in enumerate(answer_options):
                    x = letters[i]
                    out += f'<tt>[{x}]</tt> {ao}' if i==0 else f'<tt>({x})</tt> {ao}'
                    out += '&nbsp'*12 if compact_answers else '<br/>\n'
                out = out.strip('\n')
                #print(out)
                display(HTML(out))
                        
            # Multiple Answer
            elif self.type == 'MA':
                out = ''
                for i, ao in enumerate(answer_options):
                    #print(f'[{x}] {ao}' if i==0 else f'({x}) {ao}')
                    ao_mod = ao
                    if ao_mod[:3] == '[ ]': ao_mod = '<tt>[ ]</tt>' + ao_mod[3:]
                    elif ao_mod[:3] == '[X]': ao_mod = '<tt>[X]</tt>' + ao_mod[3:]
                    
                    out += f'{ao_mod}'
                    out += '&nbsp'*12 if compact_answers else '<br/>\n'
                out = out.strip('\n')
                #print(out)
                display(HTML(out))
                
            # Numerical
            elif self.type == 'NUM':
                print(f'ANSWER: {answer_options[0]}')
            
            # Matching
            elif self.type == 'MT':
                for ao in answer_options:
                    display(HTML(f'{ao}'))
                    
                
            print()    
        
        display(HTML('<hr>'))
        
        # This is a hack used to fix display in Colab
        if COLAB: 
            from apgen.autorender import katex_autorender_min
            display(Javascript(katex_autorender_min))
    
    def version_details(self, i, show_colab_text=False, show_qti_text=False):
        v = self.versions[i]
        version_details(v, show_colab_text, show_qti_text)
           
    def generate_qti(self, path='', overwrite=True, shuffle=True, save_template=False, seeds='hide', create_files=True, verbose=True):
        from apgen.qti_convert import makeQTI
        import os
        
        # Get the contents of the save directory. 
        if overwrite == False:
            contents = os.listdir(path)
            contents = [x for x in contents if '.zip' in x]
            conflicts = [x for x in contents if self.id in x]
            nums = [0]
            for x in conflicts:
                n = x.replace(self.id, '').replace('_export.zip', '').replace('_v', '') 
                if n != '':
                    nums.append(int(n))
                
            self.id = self.id + f'_v{max(nums)+1:02}'
        
        convertor = makeQTI(self, path=path, shuffle=shuffle)
        convertor.run(create_files=create_files, seeds=seeds)
        
        if save_template and create_files:
            with open(f'{path}/{self.id}.txt', 'w', encoding="utf-8") as f:
                f.write(self.qt)
        
        if create_files and verbose:
            print('QTI file created successfully')
        
      
def insert_vars(text, scope):
    a = 0
    b = 0
    temp = text
    new_text = ''
    
    while len(temp) > 0:
        if len(temp) < 3:
            new_text += temp
            break        
        
        a = temp.find('[[')
        while temp[a+2] == '[':
            a += 1
        
        # count [ before next ]
        k = temp.find(']')
        n = 0
        for i in range(a+2, k):
            if temp[i] == '[': 
                n += 1
                
        # Skip 'interior' closing brackets
        x = a
        for i in range(n):
            x = temp.find(']', x+1)
        
        b = temp.find(']]', x+1)
                
        if a == -1 or b == -1:
            new_text += temp 
            break
        
        var_string = temp[a+2:b]      
        new_text += temp[:a]
        new_text += evaluate_and_format_var(var_string, scope)            
        
        temp = temp[b+2:]

    return new_text


def evaluate_and_format_var(x, scope):
    import re
    
    # Variable string on ":"
    tokens = x.split(':')
    
    # Determine value of variable or expression.
    # Need to re-round values if evaluating an expression
    var_name = tokens[0]
    value = eval(var_name, scope)  
    
    if type(value) == np.str_: value = str(value)
    elif type(value) == np.float64: value = float(value)
    elif type(value) == np.int32: value = int(value)
    
    if type(value) == float:
        value = round(value, 10)
        if value == int(value):
            value = int(value)
    
    
    # Return if there is no format string
    if len(tokens) == 1:
        return str(value)
    
    
    #--------------------------------
    # Apply Formatting 
    #--------------------------------
    formatting = tokens[1]

    # Get the number of digits to round to. 
    digits = re.sub('[^0-9]', '', formatting)
    rounding = f'.{digits}f' if digits != '' else ''
    
    # Detemrine if commas need to be added. 
    b1 = (',' in formatting) and (',,' not in formatting)
    b2 = (',,' in formatting) and (int(value) >= 10_000)
    comma = ',' if b1 or b2 else ''
    
    raw_f_string = 'f"{'   +   f'{value}:{comma}{rounding}'  +   '}"'
    formatted_value = eval(raw_f_string)
    
    # Check to see if number is a leading coefficient
    if 'a' in formatting.lower():
        if value == 1: return ''                          #  1 --> ''
        if value == -1: return '-'                        # -1 -->  -
        if value >= 0: return formatted_value             #  x -->  x    
        if value < 0: return  formatted_value             # -x --> -x
    
    # Check to see if number is a non-leading coefficient
    if 'b' in formatting.lower():
        if value == 1: return '+ '                        #  1 -->  +
        if value == -1: return '- '                       # -1 -->  -
        if value >= 0: return '+ ' + formatted_value      #  x --> +x    
        if value < 0: return  '- ' + formatted_value[1:]  # -x --> -x
        
    # Check to see if number is a additive constant
    if 'c' in formatting.lower():
        if value >= 0: return '+ ' + formatted_value      #  x --> +x    
        if value < 0: return  '- ' + formatted_value[1:]  # -x --> -x

    return formatted_value


#-----------------------------------------
# This REALLY needs a new name
#-----------------------------------------
def colab_process_template(qt, num_versions, num_to_display, compact_answers, generate_qti, 
                     save_template, shuffle_answers, max_attempts=1000, seed=None):
    from google.colab import files # type: ignore
    import os, sys
    from IPython.display import display, Javascript
    
    if 'google.colab' in sys.modules:
        display(Javascript('''google.colab.output.setIframeHeight(0, true, {maxHeight: 10000})'''))
    
    q = Question(qt=qt)
    q.generate(n=num_versions, max_attempts=max_attempts, seed=seed)
    q.display_versions(limit=num_to_display, compact_answers=compact_answers)
    
    

    
    if not os.path.exists('output/'):
        os.mkdir('output/')

    if generate_qti:
        q.generate_qti(path='output/', shuffle=shuffle_answers)
        files.download(f'output/{q.id}_export.zip')

    if save_template:
        fname = f'output/{q.id}.txt'
        with open(fname, 'w') as f:
            f.write(q.qt)
        files.download(fname)

    return q

def version_details(v, show_colab_text=False, show_qti_text=False):
        from IPython.display import display, HTML
        
        display(HTML(f'<text size=5><b>Seed</b></text>'))
        print(v["version_seed"])
        display(HTML(f'<text size=5><b>Status</b></text>'))
        print(v["status"])
        print()
        
        display(HTML('<text size=5><b>Text Objects</b></text>'))
        if 'text' in v: 
            display(HTML('<text size=4><code>text</code></text>'))
            print(v['text'])
        
        if 'colab_text' in v and show_colab_text:
            display(HTML('<text size=5><code>colab_text</code></text>'))
            print(v['colab_text'])
        
        if 'qti_text' in v and show_qti_text:
            display(HTML('<text size=5><code>qti_text</code></text>'))
            print(v['qti_text'])
            print()
        
        display(HTML('<text size=5><b>Variables</b></text>'))
        for k,val in v['var_defns'].items():
            display(HTML(f'<code>{k} - {val}</code>'))
            
        print()
        display(HTML('<text size=5><b>Answer Options</b></text>'))
        print(v['answer_options'])
        

def DISPLAY_DELETE(x, scope):
    print(x)
       
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


def blank_lines(n):
    if n <= 0: return ''
    if n == 1: return '<p>&nbsp;</p>' + '\n'
    return '<p>&nbsp;' + '<br />'*n + '</p>' + '\n'


blank_template = '''
#---CONFIG---#
id = 
type = 

#---VARIABLES---#


#---CONDITIONS---#


#---TEXT---#


#---ANSWER_OPTIONS---#

'''

if __name__ == '__MAIN__':
    import os 
    print('-'*54)
    text = 'x:2'
    scope = {'x':3.1415926535}
    evaluate_and_format_var(text, scope)
