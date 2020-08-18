from inspect import getsource
import re

# Convert indices to subscripts for printing
SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

# Format the assignment function
def format_g(g_local, n):
	g_local_set = [g_local(i) for i in c]
	g_global_set = [g(i) for i in c]
	if g_local_set == g_global_set:
		return f'g'
	else:
		return f'g({n}/{g_local(n)})'

# Format the lambda functions to a string so we can print them out in a readable way
def format_den_str(f):
	if not isinstance(f, str):
		formatted = getsource(f).rstrip().lstrip().rstrip(',').lstrip("'denotation' : ")
		if formatted.startswith('('):
			formatted = formatted.lstrip('(').rstrip(')')
		formatted = re.sub(r'\n', ' ', formatted)
		formatted = re.sub(r'\t', '', formatted)
		formatted = re.sub(r'lambda (.*?)[:,] ', r'λ\1.', formatted)
		if re.findall(r"\['set'\]", formatted):
			formatted = re.sub(r"\[['\"]set['\"]\]", '', formatted)
			formatted = re.sub(r' if.*$', '', formatted)
		else:
			formatted = re.sub('if', 'iff', formatted)
			formatted = re.sub('==', '=', formatted)
		formatted = re.sub(r'\[(.*?)\]', r'(\g<1>)', formatted)
	else:
		formatted = re.sub(r'_', ' ', f)
	return formatted

# Stringify the output of function application since python lambda functions aren't output as strings
def format_application(*, f, arg):
	formatted = f['den_str']
	if not isinstance(arg['denotation'], str):
		arg = arg['den_str']
		arg = re.sub(r'^λ.*?\.', '', arg)
		arg = re.sub(r'\(.*?\)', '', arg)
	else:
		arg = arg['den_str']
	# Get the label for the argument
	if re.match(r'^λ(.*?)\.', formatted):
		arg_label = re.match(r'^λ(.*?)\.', formatted).groups()[0]
		# Strip off that label
		formatted = re.sub(r'^λ.*?\.', '', formatted)
		# Format assignment functions
		#if re.findall(r'g\(.*?\/.*?\)', formatted):
		#	breakpoint()
		#	g_arg = re.findall(r'g\(.*?\/.*?\)\((.*?)\)', formatted)[0]
		#	g_modification_index = re.findall(r'g\((.*?)\/', formatted)[0]
		#	if g_arg == g_modification_index:
		#		g_modification_label = re.findall(r'g\(.*?\/(.*?)\)', formatted)[0]
		#		formatted = re.sub(fr'g\({g_modification_index}\/{g_modification_label}\)\({g_arg}\)', g_modification_label, formatted)
		# Replace the argument's label with its value
		formatted = re.sub(fr'(^|[^A-Za-z0-9]){arg_label}($|[^A-Za-z0-9])', fr'\g<1>{arg}\g<2>', formatted)
	return formatted

# Stringify the output of predicate modification since python lambda functions aren't output as strings
def format_modification(f1, f2):
	f1 = f1['den_str']
	f2 = f2['den_str']
	# Get the label for the argument from the first function
	arg_label1 = re.match(r'^λ(.*?)\.', f1).groups()[0]
	# Get the label for the argument from the second function
	arg_label2 = re.match(r'^λ(.*?)\.', f2).groups()[0]
	# Strip off that label for the second one
	formatted2 = re.sub(r'^λ.*?\.', '', f2)
	# Replace the argument's label in f2 with the label from f1
	formatted2 = re.sub(fr'(^|[^A-Za-z0-9]+){arg_label2}($|[^A-Za-z0-9]+)', fr'\g<1>{arg_label1}\g<2>', formatted2)
	formatted = f1 + ' & ' + formatted2
	return formatted

# Semantic types
e = 'e'
t = 't'
et = [e,t]

# Define a list of words
# A lexical entry has four parts:
# A PF (string corresponding to what we want to print it as)
# A semantic type, consisting of an order list of e and t
# A denotation, which is a function that takes an argument of the specified type
# A set, which defines the results of applying the function to the argument
# (The set would probably be sufficient here, but it's nice to have a function so it looks more like your traditional lambda semantics)
jumping = {'PF' : 'jumping',
		   'type' : et, 
		   'denotation' : lambda x: jumping['set'][x] if x in jumping['set'].keys() else 0,
		   'set' : {'John' : 1, 'Mary' : 1}}

# Note that the arguments need to be specified in the same order in the function and the set
love = {'PF' : 'love',
		'type' : [e, et],
		'denotation' : lambda x: lambda y: love['set'][x][y] if x in love['set'].keys() and y in love['set'][x].keys() else 0,
		'set' : {'Bill' : {'Mary' : 1}, 
		 		 'John' : {'Susan' : 1}}}

# This assumes recipient theme order (when using a right-branch structure)
give = {'PF' : 'give',
		'type' : [e, [e, et]],
		'denotation' : (lambda x: lambda y: lambda z: give['set'][x][y][z] if
														   x in give['set'].keys() and 
														   y in give['set'][x].keys() and 
														   z in give['set'][x][y].keys() else 0),
		'set' : {'the_hat' : {'Bill' : {'Mary' : 1,
									    'Susan' : 1},
							  'John' : {'Bill' : 1}},
				 'the_dress' : {'Susan' : {'Mary' : 1}}}}

blue = {'PF' : 'blue',
		'type' : et,
		'denotation' : lambda x: blue['set'][x] if x in blue['set'].keys() else 0,
		'set' : {'the_hat' : 1, 'the_dress' : 1}} 

hat = {'PF' : 'hat',
		'type' : et,
	   'denotation' : lambda x: hat['set'][x] if x in hat['set'].keys() else 0,
	   'set' : {'the_hat' : 1}}

dress = {'PF' : 'dress',
		 'type' : et,
		 'denotation' : lambda x: dress['set'][x] if x in dress['set'].keys() else 0,
		 'set' : {'the_dress' : 1}}

the_hat = {'PF' : 'the hat',
		   'type' : e,
		   'denotation' : 'the_hat'}

the_dress = {'PF' : 'the dress',
			 'type' : e,
			 'denotation' : 'the_dress'}

John = {'PF' : 'John',
		'type': e,
		'denotation' : 'John'}

Bill = {'PF' : 'Bill',
		'type' : e,
		'denotation' : 'Bill'}

Susan = {'PF' : 'Susan',
		 'type' : e,
		 'denotation' : 'Susan'}

Mary = {'PF' : 'Mary',
		'type' : e,
		'denotation' : 'Mary'}

word_list = [jumping, love, blue, hat, dress, the_hat, Bill, Susan, Mary, John, the_dress]

IS_PRED = {'PF' : 'is',
		   'type' : [et, et],
	  	   'denotation' : lambda P: lambda x: P(x),
	       'set' : {word['denotation'] : word['set'] for word in word_list if word['type'] == et}}

IS_IDENT = {'PF' : 'is',
			'type' : [e, et],
		    'denotation' : lambda x: lambda y: 1 if x == y else 0,
		    'set' : {word['denotation'] : {word['denotation'] : 1} for word in word_list if word['type'] == e}}
word_list.extend([IS_PRED, IS_IDENT])

# Shifts IS_IDENT to IS_PRED
SHIFT = {'PF' : '(SHIFT)',
		 'type' : [[e, et], [et, et]],
		 'denotation' : lambda P: lambda Q: lambda x: Q(x),
		 'set' : {word1['denotation'] : word2['set'] 
		 							    for word2 in word_list if word2['type'] == [et, et] 
		 		  for word1 in word_list if word1['type'] == [e, et]}}
word_list.extend([SHIFT])

# Context for pronoun resolution
c = {1 : John['denotation'], 2: Mary['denotation'], 3: Bill['denotation']}

# Return a modified version of g
def g_mod(mod):
	return lambda n: g(n, mod = mod)

# Assignment function that maps an index to an entity in the context
def g(n, *, mod = ''):
	# Create a local copy of the context so we don't modify it globally
	c_local = c.copy()
	# If we have modified the assignment function because of an index
	if mod:
		# Get the index from the string
		index = int(re.findall('^[0-9]*', mod)[0])
		# Get the new output for that index
		modified_output = re.findall('/(.*)$', mod)[0]
		c_local.update({index : modified_output})
	try:
		if n in c_local.keys():
			return c_local[n]
		else:
			raise Exception
	except:
		print(f'{n} not in domain of assignment function g.')

pronouns = []

# Pronouns and traces are functions that return lexical entries given an index
def he(i):
	he_i = {'PF' : f'he{i}'.translate(SUB),
		  'index' : i,
		  'type' : e,
		  'denotation' : f'g({i})'}
	if not he_i in word_list:
		word_list.extend([he_i])
	if not he_i in pronouns:
		pronouns.extend([he_i])
	return he_i

def t(i):
	t_i = {'PF' : f't{i}'.translate(SUB),
		 'index' : i,
		 'type' : e,
		 'denotation' : f'g({i})'}
	if not t_i in word_list:
		word_list.extend([t_i])
	if not t_i in pronouns:
		pronouns.extend([t_i])
	return t_i

# One final thing each word has: a version of its denotation function formatted as a string
# This is just so we can print out the results of each semantic composition step in a readable way, since Python lambda functions are not output as strings
for word in word_list:
	word.update({'den_str' : format_den_str(word['denotation'])})

def function_application(*, f, arg):
	# Return the result of function application
	# PF is just concatenation of the strings
	# Den_str is handled by the formatting function above
	# The type is the result of getting rid of the first type in f
	# The denotation is the result of applying the function's denotation to the argument's denotation
	# The set is whatever the characteristic set of f maps the argument to (0 if arg is not in f's characteristic set)
	if f['set'] == 0:
		s = 0
	else:
		s = f['set'][arg['denotation']] if arg['denotation'] in f['set'].keys() else 0
	return {'PF' : f'{f["PF"]} {arg["PF"]}'.rstrip(),
			'den_str': format_application(f = f, arg = arg),
			'type' : f['type'][1:][0],
			'denotation' : f['denotation'](arg['denotation']),
			'set' : s}
			#'set' : {t[1:][0] for t in Y['set'] if X['denotation'] == t[0] and len(t) > 0}}
			#'set' : {t[1:] for t in Y['set'] if X['denotation'] == t[0] and len(t) > 0}}

def predicate_modification(*, f1, f2):
	# Return the result of predicate modification
	# PF is contactenation of the strings
	# Den_str is handled by the formatting function above
	# Since this is only called when f1 and f2 have the same type, the type is equal to their type (either f1['type'] or f2['type'] would work, since the types are identical)
	# The denotation is True iff f1(x) and f2(x)
	# The set is the set of all items in both f1 and f2 (e.g., every item in f1 that is also in f2)
	return {'PF' : f'{f1["PF"]} {f2["PF"]}',
			'den_str' : format_modification(f1, f2),
			'type' : f1['type'],
			'denotation' : lambda x: 1 if f1['denotation'](x) and f2['denotation'](x) else 0,
			'set' : [item for item in f1['set'] if item in f2['set']]}

def predicate_abstraction(*, index, pred, g_local, verbose = False):
	# Predicate abstraction
	# PF-ified semantics is the index + the PF of the predicate
	# Den_str is the abstracted version of the predicate, with the value given by the usual assignment function replaced by the modified assignment function applied to the argument
	# Type is [e, pred['type']]
	# The denotation is the recursive interpretation of the structure where index is mapped to x
	# The set is the mapping of a word's denotation to true if it's type e and if it's in the set of the interpretation of the predicate wrt the modified assignment function
	# We do this so that we only print out the results of interpreting things once
	if verbose:
		interpret_sentence_r(pred, g_local = g_mod(f'{index}/x'), verbose = verbose)
	return {'PF' : f'{index} ' + re.sub(f'^{index} ', '', interpret_sentence_r(pred, g_local = g_local)['PF']),
			'den_str' : 'λx.' + re.sub(g(index), f'g({index}/x)({index})', interpret_sentence_r(pred, g_local = g_local)['den_str']),
			'type' : [e, interpret_sentence_r(pred, g_local = g_local)['type']],
			'denotation' : lambda x: interpret_sentence_r(pred, g_local = g_mod(f'{index}/{x}'))['denotation'],
			'set' : {word['denotation'] : 1 for word in word_list if word['type'] == e and (interpret_sentence_r(pred, g_local = g_mod(f'{index}/{word["denotation"]}')))['set'] == 1}}

# Interpretation function
def i(X, Y = '', /, *, g_local, verbose = False):
	# Set up local copies of the variables so we don't override the global ones.
	# We define these names first in case they are ints, in which case copying wouldn't work
	X_local = X
	Y_local = Y
	# If X is a pronoun, update its denotation and den_str relative to any modified assignment function
	if X in pronouns:
		# Make local copies so we don't mess with the global ones
		X_local = X.copy()
		X_local.update({'denotation' : re.sub('g', 'g_local', X_local['denotation'])})
		if verbose:
			print(f"{X_local['PF']} = {re.sub('_local', '', X_local['denotation'])} = {eval(X_local['denotation'])}")
		X_local['denotation'] = eval(X_local['denotation'])
		X_local.update({'den_str' : format_den_str(X_local['denotation'])})
	# If there are two arguments, figure out what semantic composition rule to apply
	if Y:
		# If Y is a pronoun, update its denotation and den_str relative to any modified assignment function
		if Y in pronouns:
			Y_local = Y.copy()
			Y_local.update({'denotation' : re.sub('g', 'g_local', Y_local['denotation'])})
			if verbose:
				print(f"{Y_local['PF']} = {format_g(g_local, Y_local['index'])}({Y_local['index']}) = {eval(Y_local['denotation'])}")
			Y_local['denotation'] = eval(Y_local['denotation'])
			Y_local.update({'den_str' : format_den_str(Y_local['denotation'])})
		# Predicate abstraction when X or Y is an index
		if isinstance(X_local, int):
			if verbose:
				print(f"[[{X_local} {interpret_sentence_r(Y_local, g_local = g_local)['PF']}]] = {predicate_abstraction(index = X_local, pred = Y_local, g_local = g_local)['den_str']} by PA\nSubproof:")
			return predicate_abstraction(index = X_local, pred = Y_local, g_local = g_local, verbose = verbose)
		elif isinstance(Y_local, int):
			if verbose:
				print(f"[[{Y_local} {interpret_sentence_r(X_local, g_local = g_local)['PF']}]] = {predicate_abstraction(index = Y_local, pred = X_local, g_local = g_local)['den_str']} by PA\nSubproof:")
			return predicate_abstraction(index = Y_local, pred = X_local, g_local = g_local, verbose = verbose)
		# Function application when either X_local or Y_local is in the domain of the other
		elif Y_local['type'] == X_local['type'][0]:
			if verbose:
				print(f"[{X_local['den_str']}]({Y_local['den_str']}) = {function_application(f = X_local, arg = Y_local)['den_str']} by FA([[{X_local['PF']}]], [[{Y_local['PF']}]])")
			return function_application(f = X_local, arg = Y_local) 
		elif X_local['type'] == Y_local['type'][0]:
			if verbose:
				print(f"[{Y_local['den_str']}]({X_local['den_str']}) = {function_application(f = Y_local, arg = X_local)['den_str']} by FA([[{Y_local['PF']}]], [[{X_local['PF']}]])")
			return function_application(f = Y_local, arg = X_local)
		# Predicate modification when X_local and Y_local have the same domain of application
		elif X_local['type'] == Y_local['type']:
			if verbose:
				print(f"PM({X_local['den_str']}, {Y_local['den_str']} = {predicate_modification(f1 = X_local, f2 = Y_local)['den_str']} by PM([[{X_local['PF']}]], [[{Y_local['PF']}]])")
			return predicate_modification(f1 = X_local, f2 = Y_local)
		else:
			print(f'Type mismatch: type {X_local["type"]} cannot compose with type {Y_local["type"]}.')
	# Otherwise, return the single argument
	else:
		# If X is a pronoun, update its denotation and den_str relative to any modified assignment function
		if X in pronouns:
		# Make local copies so we don't mess with the global ones
			X_local = X.copy()
			X_local.update({'denotation' : re.sub('g', 'g_local', X_local['denotation'])})
			if verbose:
				print(f"{X_local['PF']} = {re.sub('_local', '', X_local['denotation'])} = {eval(X_local['denotation'])}")
			X_local['denotation'] = eval(X_local['denotation'])
			X_local.update({'den_str' : format_den_str(X_local['denotation'])})
		return X_local

# Interpret a sentence helper (binary branching only!)
def interpret_sentence_r(sentence, /, *, g_local, verbose = False):
	try:
		if len(sentence) > 2:
			raise Exception
		if len(sentence) == 2 and not isinstance(sentence, dict):
			branch1 = sentence[0]
			branch2 = sentence[1]
			if not isinstance(branch1, dict):
				if isinstance(branch1, int):
					return i(branch1, branch2, g_local = g_local, verbose = verbose)
				else:
					branch1 = interpret_sentence_r(branch1, g_local = g_local, verbose = verbose)
			if not isinstance(branch2, dict):
				if isinstance(branch2, int):
					return i(branch1, branch2, verbose = verbose)
				else:
					branch2 = interpret_sentence_r(branch2, g_local = g_local, verbose = verbose)
			return i(branch1, branch2, g_local = g_local, verbose = verbose)
		elif isinstance(sentence, dict):
			return i(sentence, g_local = g_local, verbose = verbose)
	except:
		print(f'Error: only binary branching! {sentence} has too many branches!')

# Interpret a sentence (allows for printing the full sentence only once)
def interpret_sentence(sentence, /, *, g_local = g, verbose = False):
	if verbose:
		print(f'\nInterpretation of sentence "{sentence["PF"]}":')
	interpretation = interpret_sentence_r(sentence['LF'], g_local = g_local, verbose = verbose)
	if verbose:
		print(f'{interpretation["denotation"]}\n')
	return interpretation

# Some test sentences
sentence1 = {'PF' : "The hat is blue", 'LF' : [the_hat, [[IS_IDENT, SHIFT], blue]]}
sentence2 = {'PF' : 'The hat is the dress', 'LF' : [the_hat, [IS_IDENT, the_dress]]}
sentence3 = {'PF' : 'He1 is jumping'.translate(SUB), 'LF' : [he(1), [IS_PRED, jumping]]}
sentence4 = {'PF' : 'Bill, Mary loves', 'LF' : [Bill, [1, [Mary, [love, t(1)]]]]}
sentence5 = {'PF' : 'John, Mary loves', 'LF' : [John, [1, [Mary, [love, t(1)]]]]}

# Note that sentences involving multiple predicate abstractions don't currently work because we use the same label for all when abstracting---this is not a simple thing to fix since it involves generating a unique new label that isn't being used. It will be implemented later