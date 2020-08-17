from dill.source import getsource
import re

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
		formatted = re.sub(r'\[(.*?)\]', r'(\g<1>)', formatted)
	else:
		formatted = re.sub(r'_', ' ', f)
	return formatted

# Stringify the output of function application since python lambda functions aren't output as strings
def format_application(*, f, arg):
	f = f['den_str']
	if not isinstance(arg['denotation'], str):
		arg = arg['den_str']
		arg = re.sub(r'^λ.*?\.', '', arg)
		arg = re.sub(r'\(.*?\)', '', arg)
	else:
		arg = arg['den_str']
	# Get the label for the argument
	arg_label = re.match(r'^λ(.*?)\.', f).groups()[0]
	# Strip off that label
	formatted = re.sub(r'^λ.*?\.', '', f)
	# Replace the argument's label with its value
	formatted = re.sub(fr'(^|[^A-Za-z0-9]+){arg_label}($|[^A-Za-z0-9]+)', fr'\g<1>{arg}\g<2>', formatted)
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
# A lexical entry has three parts:
# A semantic type, consisting of an order list of e and t
# A denotation, which is a function that takes an argument of the specified type
# A set, which defines the results of applying the function to the argument
# (We probably don't really need the function, but it's nice so it looks more like your traditional lambda semantics)
jumping = {'PF' : 'jumping',
		   'type' : et, 
		   'denotation' : lambda x: jumping['set'][x] if x in jumping['set'].keys() else 0,
		   'set' : {'John' : 1, 'Mary' : 1}}

# Note that the arguments need to be specified in the same order in the function and the set
love = {'PF' : 'love',
		'type' : [e, et], 
		'denotation' : lambda x: lambda y: love['set'][x][y] if x in love['set'].keys() and y in love['set'][x].keys() else 0,
		'set' : {'John' : {'Mary' : 1}, 
		 		 'Bill' : {'Susan' : 1}}}

# The weirdness allows this to go in either recipient theme or theme recipient order
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

word_list = [jumping, love, blue, hat, dress, the_hat, Bill, Susan, Mary, the_dress]

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

# Assignment function
def g(n):
	try:
		if n in c.keys():
			return c[n]
		else:
			raise Exception
	except:
		print(f'{n} not in domain of assignment function g.')

# Pronoun (get the right labels for these)
he1 = {'PF' : 'he',
	   'type' : e,
	   'denotation' : g(1)}

word_list.extend([he1])

for word in word_list:
	word.update({'den_str' : format_den_str(word['denotation'])})

def function_application(*, f, arg):
	# The way we get the set to return here is a bit tricky, since python doesn't allow us to define sets of sets easily
	# It's really a hack to make 'IS' work
	return {'PF' : f'{f["PF"]} {arg["PF"]}'.rstrip(),
			'den_str': format_application(f = f, arg = arg),
			'type' : f['type'][1:][0],
			'denotation' : f['denotation'](arg['denotation']),
			'set' : (s := f['set'][arg['denotation']] if arg['denotation'] in f['set'].keys() else 0)}
			#'set' : {t[1:][0] for t in Y['set'] if X['denotation'] == t[0] and len(t) > 0}}
			#'set' : {t[1:] for t in Y['set'] if X['denotation'] == t[0] and len(t) > 0}}

def predicate_modification(*, f1, f2):
	return {'PF' : f'{f1["PF"]} {f2["PF"]}',
			'den_str' : format_modification(f1, f2),
			'type' : f1['type'],
			'denotation' : lambda P: 1 if f1['denotation'](P) and f2['denotation'](P) else 0,
			'set' : [item for item in f1['set'] if item in f2['set']]}

# Interpretation function
def i(X, Y = '', /, *, verbose = False):
	if Y:
		# Function application when either X or Y is in the domain of the other
		if Y['type'] == X['type'][0]:
			if verbose:
				print(f"[{X['den_str']}]({Y['den_str']}) = {function_application(f = X, arg = Y)['den_str']} by FA([[{X['PF']}]], [[{Y['PF']}]])")
			return function_application(f = X, arg = Y) 
		elif X['type'] == Y['type'][0]:
			if verbose:
				print(f"[{Y['den_str']}]({X['den_str']}) = {function_application(f = Y, arg = X)['den_str']} by FA([[{Y['PF']}]], [[{X['PF']}]])")
			return function_application(f = Y, arg = X)
		# Predicate modification when X and Y have the same domain of application
		elif X['type'] == Y['type']:
			if verbose:
				print(f"PM({X['den_str']}, {Y['den_str']} = {predicate_modification(f1 = X, f2 = Y)['den_str']} by PM([[{X['PF']}]], [[{Y['PF']}]])")
			return predicate_modification(f1 = X, f2 = Y)
		else:
			print(f'Type mismatch: type {X["type"]} cannot compose with type {Y["type"]}.')
	else:
		return X

# Some test sentences
sentence1 = {'PF' : "The hat is blue", 'LF' : [the_hat, [[IS_IDENT, SHIFT], blue]]}
sentence2 = {'PF' : 'The hat is the dress', 'LF' : [the_hat, [IS_IDENT, the_dress]]}
sentence3 = {'PF' : 'He is jumping', 'LF' : [he1, [IS_PRED, jumping]]}

# Interpret a sentence helper (binary branching only!)
def interpret_sentence_r(sentence, /, verbose = False):
	try:
		if len(sentence) > 2:
			raise Exception
		branch1 = sentence[0]
		branch2 = sentence[1]
		if not isinstance(branch1, dict):
			branch1 = interpret_sentence_r(branch1, verbose = verbose)
		if not isinstance(branch2, dict):
			branch2 = interpret_sentence_r(branch2, verbose = verbose)
		return i(branch1, branch2, verbose = verbose)
	except:
		print(f'Error: only binary branching! {sentence} has too many branches!')

# Interpret a sentence (allows for printing the full sentence only once)
def interpret_sentence(sentence, /, verbose = False):
	#if verbose:
	print(f'Interpretation of sentence "{sentence["PF"]}":')
	interpretation = interpret_sentence_r(sentence['LF'], verbose = verbose)
	#if verbose:
	print(interpretation['denotation'])

# TODO: pronominal binding, quantifiers, read in and format dict from CSV(?)