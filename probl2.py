import math
import random

def gcd(a, b):
    if a==0 or b==0:
        return a+b
    else:
        return gcd(a%b, b) if a>b else gcd(a, b%a)

#return a prime number between 2 and 1000
def gen_prime(): 
    
    #Eratosthene sieve
    N=1000
    sieve = [True] * N
    for i in range(2, round(math.sqrt(N)) + 1):
        if sieve[i] == True:           
            for j in range(i+i, N, i):
                sieve[j] = False
    
    #Get randomly one prime nr from list
    return random.choice([i for i in range(2, N) if sieve[i] == True])


p, q = gen_prime(), gen_prime()
n = p*q
phi_n = (p-1)*(q-1) #Euler totient function

while 1:
    x = random.choice([3, 5, 17, 257, 65537]) #Fermat's numbers
    if gcd(x, phi_n) == 1:
        e = x
        break

#Find multiplicative inverse of e (mod phi_n)
d = pow(e, -1, phi_n)

print("Enter message:")
message = input()

#Convert each symbol in ASCII dec format
m1 = [ord(symbol) for symbol in message]

print(f"Public key: \n (e, n) = ({e}, {n})")
print(f"Private key: \n (d, n) = ({d}, {n})")

#Codify each symbol
c = [(symbol**e)%n for symbol in m1]

print(f"Encrypted message:")
print(*c, sep='')

#Decodify each symbol
m2 = [chr((cypher**d)%n) for cypher in c]

print(f"Decrypted message:")
print(*m2, sep='')




