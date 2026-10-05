#THIS IS THE PROJECT IDEA : BEST
"""
INPUT : K
GENERATE : 2^K ROWS WITH K VARIABLES WITH DIFFERENT COMBINATIONS.

"""


"""
Things to focus on : 
--->  Slicing of strings , format func , 


Key concepts used : 
--> x**y is basically x^y.
--> format(i , 'b') - formats the number to its binary representation
--> bin(n) - gives the binary representation of the number.
--> " ".join(string name) - funcntion helps to join the letters of the string with some spacing.
"""

#Taking input of the output of each rows:
def get_table(k):
    op = [] #To store the output of each rows 
    min_terms = [] #To store the pos/rows of min terms (high-1)
    dont_cares = [] #To store the pos/rows of dont care condtions (x)
    for i in range(2**k):
    #since the list has 0 based indexing so the ith term of the list will correspond to the output of the ith row of the TT
        y = input(f"Enter the output(0/1/X) for {i}th term: ").strip().upper()
        while(y!="0" and y!="1" and y!="X"):
            print("ERROR")
            y = input("Enter valid input(0/1/X) : ")
        op.append(y)
        if(y=="1"):
            min_terms.append(i)
        if(y=="X"):
            dont_cares.append(i)
    return op,min_terms,dont_cares


#Taking input from user - the no. of variables: 
k = int(input("Enter the value of K : "))
for i in range(2**k):
    binary = format(i, f"0{k}b") #dynamic padding with k variables f is for formatting the strings.
    print(" ".join(binary))

op,min_terms,dont_cares = get_table(k)
print(op)
print(min_terms)
print(dont_cares)
