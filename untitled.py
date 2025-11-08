import math

def find_integer_solutions():
    L_0_values = [1.0, 2.0, 5.0]
    L_max_values = [19.0, 27.5]
    
    solutions = []
    
    for L_0 in L_0_values:
        for L_max in L_max_values:
            upper_bound = math.log10(10 * L_0 / L_max)
            lower_bound = math.log10(2 * L_0 / L_max)
            
            # Find all integers between lower_bound and upper_bound
            min_int = math.ceil(lower_bound)
            max_int = math.floor(upper_bound)
            
            integers_in_range = list(range(min_int, max_int + 1))
            
            possible_l0 = [L_0 * (10 ** -x) for x in integers_in_range]
            
            solutions.append({
                'L_0': L_0,
                'L_max': L_max,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'integer_solutions': integers_in_range,
                'possible_l0': possible_l0
            })
    
    return solutions

# Calculate and display results
results = find_integer_solutions()

print("Integer solutions for x:\n")
for result in results:
    print(f"L_0 = {result['L_0']}, L_max = {result['L_max']}")
    print(f"Range: {result['lower_bound']:.4f} < x < {result['upper_bound']:.4f}")
    print(f"Integer solutions: {result['integer_solutions']}")
    print(f"Possible l0 solutions: {result['possible_l0']}")
    print()

# Summary of all integer solutions
all_integers = set()
for result in results:
    all_integers.update(result['possible_l0'])

print(f"All possible integer solutions for l0: {sorted(all_integers)}")

