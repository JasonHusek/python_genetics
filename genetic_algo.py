import random

GENE_MAP = {
	'0000' : 0,
	'0001' : 1,
	'0010' : 2,
	'0011' : 3,
	'0100' : 4,
	'0101' : 5,
	'0110' : 6,
	'0111' : 7,
	'1000' : 8,
	'1001' : 9,
	'1010' : '+',
	'1011' : '-',
	'1100' : '*',
	'1101' : '/'
}
OPERATOR_GENES = ['+','-','*','/']
NUMERIC_GENES = list(range(10))
GENE_PER_CHROMOSOME_RANGE = range(4, 20)
GENE_SIZE = 4
POPULATION = [] #the current list of our genes and their fitness (if calculated)
CROSSOVER_RATE = 0.6 #60%
MUTATION_RATE = 0.001 # 1 tenth of a percent

GENERATION = 1 #what generation it is

TARGET_RESULT = 42

"""
	Turn a chromosome (string of 1's and 0's) into a list of numbers or operators
"""
def decode_chromosome(chromosome):
	chromosome_len = len(chromosome)
	if(chromosome_len % GENE_SIZE != 0):
		raise Exception('Incorrect chromosome length, must be multiple of %s, got %s -- %s' %(GENE_SIZE, chromosome_len, chromosome))
	chunks = chromosome_len // GENE_SIZE
	results = []
	prev_chunk = 0
	for x in range(1,chunks + 1):
		this_gene = chromosome[prev_chunk:(x * GENE_SIZE)]
		prev_chunk = x * GENE_SIZE
		#filter out invalid genes
		if this_gene == '1111' or this_gene == '1110': 
			continue
		decoded_gene = GENE_MAP[this_gene]
		# we can only have one operator or number in a row
		if len(results) > 0 and decoded_gene in NUMERIC_GENES and results[len(results)-1] in NUMERIC_GENES:
			continue
		if len(results) > 0 and decoded_gene in OPERATOR_GENES and results[len(results)-1] in OPERATOR_GENES:
			continue
		results.append(decoded_gene)

	return results


"""
	Turn a list of genes into a number (i.e. calculate the results of a given chromosome)
"""
def calculate_gene(gene_list):
	if gene_list[0] in OPERATOR_GENES: #no viable candidate will start with an operator
		return None
	result = gene_list[0]
	for x in range(0, len(gene_list)):
		current_gene = gene_list[x]
		if current_gene in NUMERIC_GENES :
			#we know that the previous number was an operator
			operation = gene_list[x-1]
			if operation == OPERATOR_GENES[0]:
				result = current_gene + result
			elif operation == OPERATOR_GENES[1]:
				result = current_gene - result
			elif operation == OPERATOR_GENES[2]:
				result = current_gene * result
			elif operation == OPERATOR_GENES[3]: #no viable candidate will div by 0
				try:
					result = current_gene // result
				except:
					return None
	return result

"""
	Assign a numeric value for the fitness of a given candidate
"""
def judge_fitness(chromosome):
	result = calculate_gene(decode_chromosome(chromosome))
	if result == None: #candidate would of caused an exception
		return 0
	if (TARGET_RESULT - result) == 0: #found a viable solution
		print('SOLUTION FOUND FOR %s :: %s = %s' 
				%(
					TARGET_RESULT,
				 	calculate_gene(decode_chromosome(chromosome)), 
				 	decode_chromosome(chromosome)
				 )
			)
		exit()
		return 100
	fitness = 1/(TARGET_RESULT - result)
	if fitness < 0:
		fitness = 0
	return fitness

"""
	Create the initial population
"""
def seed_population(size):
	for x in range(size):
		chromosome_size = random.choice(GENE_PER_CHROMOSOME_RANGE) * GENE_SIZE #how large will this candidate be
		chromosome = ''.join(random.choice('10') for _ in range(chromosome_size))
		
		POPULATION.append(
			{'dna' : chromosome,
			 'fitness' : None
			 })

"""
	create a list of touples, each with 2 chromosomes.
	these are the parents of the next generation
"""
def select_parents():
	
	parents = []
	chosen = None

	p_len = len(parents)
	pop_len = len(POPULATION) / 2

	while(p_len < pop_len):
		parent = select_parent()
		if chosen == None:
			chosen = parent
		else:
			parents.append( (chosen, parent) )
			chosen = None
		p_len = len(parents)

	return parents

"""
	Roulette wheel selection
"""
def select_parent():
	total_fitness = sum(x['fitness'] for x in POPULATION)
	fitness_to_target = random.uniform(0,total_fitness)
	for x in POPULATION:
		fitness_to_target -= x['fitness']
		if fitness_to_target <= 0:
			POPULATION.remove(x)
			return  x

"""
	Create a new generation from the list of couples ( touple(parent,parent) )
"""			

def create_generation(parents):
	global POPULATION
	for couple in parents:
		p1 = couple[0]['dna']
		p2 = couple[1]['dna'] 
		#determine if crossover happens for child1
		if random.random() <= CROSSOVER_RATE:
			c1 = crossover(p1,p2)
		else:
			c1 = p1
		if random.random() <= CROSSOVER_RATE:
			c2 = crossover(p2,p1)
		else:
			c2 = p2

		#check for mutations
		c1 = mutate(c1)
		c2 = mutate(c2)
		#add these children to the new population pool
		POPULATION.append({'dna' : c1, 'fitness' : None})
		POPULATION.append({'dna' : c2, 'fitness' : None})

def crossover(source1, source2):
	crossover_point = random.choice(range(0,len(source1)))
	result = source1[:crossover_point] + source2[crossover_point:] #the beginning of parent1 and end of parent 2
	#trim the crossover section to conform to acceptable chunk sizes
	trimsize = len(result) % GENE_SIZE
	result = result[trimsize:]
	return result

def mutate(dna):
	result = ''
	for x in dna:
		if random.random() < MUTATION_RATE:
			if x == '1':
				result += '0'
			else:
				result += '1'
		else:
			result += x
	return result

def judge_generation():
	for x in range(len(POPULATION)):
		POPULATION[x]['fitness'] = judge_fitness(POPULATION[x]['dna'])


def main():
	global TARGET_RESULT
	
	TARGET_RESULT = 300
	seed_population(100)
	judge_generation()

	gen = 0
	while True:
		print("GEN %s -- %s"%(gen, sum(x['fitness'] for x in POPULATION)))
		parents = select_parents()
		create_generation(parents)
		judge_generation()
		gen += 1


main()




