from dwave.cloud import Client
#client = Client.from_config(token='DEV-cf2dfde4d3bf74d2279b43aa3f26ef6bbb0742ad')
#available_solvers = client.get_solvers()
#print( available_solvers )

# Manual embedding using th ehybrid solver
print(' ')
print( 'Composed sampler' )

from dimod import FixedVariableComposite, ExactSolver
Q = {('x', 'x'): -1, ('x', 'z'): 2, ('z', 'x'): 0, ('z', 'z'): -1}
composed_sampler = FixedVariableComposite(ExactSolver())
sampleset = composed_sampler.sample_qubo(Q, fixed_variables={'x': 1})
print(sampleset)


# QBsolv
print(' ')
print( 'QBsolv' )
from dwave_qbsolv import QBSolv

# Set Q for the minor-embedded problem QUBO
qubit_biases = {(0, 0): 0.3333, (1, 1): -0.333, (4, 4): -0.333, (5, 5): 0.333}
coupler_strengths = {(0, 4): 0.667, (0, 5): -1, (1, 4): 0.667, (1, 5): 0.667}
Q = dict(qubit_biases)
Q.update(coupler_strengths)

response = QBSolv().sample_qubo(Q)
print("samples=" + str(list(response.samples())))
print("energies=" + str(list(response.data_vectors['energy'])))


from dwave_qbsolv import QBSolv
import neal
import itertools
import random

qubo_size = 500
subqubo_size = 30
Q = {t: random.uniform(-1, 1) for t in itertools.product(range(qubo_size), repeat=2)}
sampler = neal.SimulatedAnnealingSampler()
response = QBSolv().sample_qubo(Q, solver=sampler, solver_limit=subqubo_size)
print(response)





# Manual embedding
print(' ')
print( 'Manual embedding' )

from dwave.system.samplers import DWaveSampler

# Set Q for the minor-embedded problem QUBO
qubit_biases = {(0, 0): 0.3333, (1, 1): -0.333, (4, 4): -0.333, (5, 5): 0.333}
coupler_strengths = {(0, 4): 0.667, (0, 5): -1, (1, 4): 0.667, (1, 5): 0.667}
Q = dict(qubit_biases)
Q.update(coupler_strengths)

# Sample once on a D-Wave system and print the returned sample
response = DWaveSampler().sample_qubo(Q, num_reads=100)
print(response)
#for (sample, energy, num_occurrences, chain_break) in response.data():
	#(sample, energy, num_occurrences, chain_break) = item
#	print(sample, "Energy: ", energy, "Occurrences: ", num_occurrences)



# Automated minor embedding
print(' ')
print( 'Automated minor embedding' )
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite

# Set Q for the problem QUBO
linear = {('x0', 'x0'): -1, ('x1', 'x1'): -1, ('x2', 'x2'): -1}
quadratic = {('x0', 'x1'): 2, ('x0', 'x2'): 2, ('x1', 'x2'): 2}
Q = dict(linear)
Q.update(quadratic)

# Minor-embed and sample 1000 times on a default D-Wave system
response = EmbeddingComposite(DWaveSampler()).sample_qubo(Q, num_reads=100)

print(response)
print(response.data())

for (sample, energy, num_occurrences, chain_break) in response.data():
	#(sample, energy, num_occurrences, chain_break) = item
	print(sample, "Energy: ", energy, "Occurrences: ", num_occurrences)

