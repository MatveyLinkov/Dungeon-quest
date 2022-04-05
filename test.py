import timeit

print(timeit.timeit("[sqrt(x) for x in range(1000000)]",
                    "from math import sqrt", number=1))

print(timeit.timeit("[sqrt(x) for x in range(1000000)]",
                    "from math import sqrt", number=1))

print(timeit.timeit("for i in range(1000000): a.append(sqrt(i))",
                    "from math import sqrt; a=[]", number=1))

print(timeit.timeit("list(map(sqrt, range(1000000)))",
                    "from math import sqrt; a=[]", number=1))