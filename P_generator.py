import numpy as np
from scipy.stats import unitary_group
from scipy.optimize import minimize
from scipy.linalg import expm 
import time


def real_to_complex(z):      # real vector of length 2n -> complex of length n
    return z[:len(z)//2] + 1j * z[len(z)//2:]


def complex_to_real(z):      # complex vector of length n -> real of length 2n
    return np.concatenate((np.real(z), np.imag(z)))


def find_P_constrained(q, print_result = False):

    R = real_to_complex(np.random.rand(2*(q**8 - 2*q**4 + 1)))
    P_0 = real_to_complex(np.random.rand(2*(q**8 - 2*q**4 + 1))).reshape([q**4 - 1, q**4 - 1])
    P_0 = complex_to_real(((P_0 + P_0.conj().T)/2).flatten())
    I, Z = np.zeros(q**2), np.zeros(q**2)
    I[0], Z[1] = 1, 1
    IZ = np.einsum('a,b->ab',I,Z).flatten()[1:]
    ZI = np.einsum('a,b->ab',Z,I).flatten()[1:]
    #II = np.einsum('a,b->ab',I,I).flatten()

    def Hermiticity(P):
        P = real_to_complex(P)
        P = P.reshape([q**4 - 1,q**4 - 1])
        return np.linalg.norm(P - P.conj().T)
    
    ####def Unitality(P):
        ###P = real_to_complex(P)
        ##P = P.reshape([q**4,q**4])
        #return np.linalg.norm(np.einsum('ab,b->a',P,II))
    
    def Charge_conservation(P):
        P = real_to_complex(P)
        P = P.reshape([q**4 - 1,q**4 - 1])
        Q = IZ + ZI
        return np.linalg.norm(np.einsum('ab,b->a',P,Q))

    def randomise(P, R):
        P = real_to_complex(P)
        return -abs(np.einsum("a,a->", np.conj(P), R))


    cons = [{'type':'eq', 'fun': lambda z:  Hermiticity(z)},
            {'type':'eq', 'fun': lambda z: Charge_conservation(z)}]

        
    result = minimize(
        lambda z: randomise(z, R), x0 = P_0, method='SLSQP', \
        constraints=cons, options={'maxiter': 1000}
                     )

    P = real_to_complex(result.x).reshape([q**4 - 1,q**4 - 1])
    Direct_Sum = np.zeros([np.shape(P)[0]+1, np.shape(P)[1]+1], dtype="complex_")
    Direct_Sum[1:,1:] = P
    
    if print_result == True:
        print(result)
        
    return Direct_Sum


def Exponential_Map(e, P):
    return expm(1j*e*P)


start = time.time()
print("\n")

q=2 #the local Hilbert space dimension
e=0.1 #perturbation parameter
P = find_P_constrained(q)
I, Z = np.zeros(q**2), np.zeros(q**2)
I[0], Z[1] = 1, 1
IZ = np.einsum('a,b->ab',I,Z).flatten()
ZI = np.einsum('a,b->ab',Z,I).flatten()
II = np.einsum('a,b->ab',I,I).flatten()
Q = IZ + ZI
G = Exponential_Map(e, P)

end = time.time()
print(end-start)
print("\n")

print(G)
print("\n\n")

print("Check Hermiticity: ", \
      np.linalg.norm(P - P.conj().T))

print("Check Unitality: ", \
      np.linalg.norm(np.einsum('ab,b->a',P,II)))

print("Check Q-Conservation: ", \
      np.linalg.norm(np.einsum('ab,b->a',P,Q)))

print("Check Unitarity: ", \
      np.linalg.norm(np.einsum('ab,ac->bc', G, np.conj(G)) - np.eye(q**4)))

print("Check Unitality: ", \
      np.linalg.norm(np.einsum('ab,b->a',G,II) - II))

print("Check Q-Conservation: ", \
      np.linalg.norm(np.einsum('ab,b->a',G,Q) - Q))




import matplotlib.pyplot as plt
plt.imshow(np.abs(G),cmap='hot', interpolation='nearest')
plt.show()