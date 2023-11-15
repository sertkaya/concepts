__all__ = ['dg_basis', 'dg_basis_optimized']

import ast
import time
import copy

arrow = " -> "

def double_derivation(A, context):   # Used to check if input set is a closed set
    return context.intension(context.extension(A))


# Algorithm to find the next preclosure in lectical order:
def next_preclosure(A, M):
    M_reversed = list(reversed(list(M)))
    
    for m in M_reversed:
        
        if m in A:
            A.remove(m)
        else:
            A.extend([m])
            return A
    return M


# Algorithm to find the closure of a premise 'X' of an implication
# and determine based on the result if the implication is redundant:
def implication_closure(X, implications):
    XCopy = copy.copy(X)
    copyImplications = copy.copy(implications)   # Creating a copy of implications to not change the original list
    stable = False
        
    while not stable:
        stable = True
        remove = []
        
        for implication in copyImplications:
            currentImplication = implication.split(arrow)
            currentPremise = list(ast.literal_eval(currentImplication[0]))
            currentConclusion = list(ast.literal_eval(currentImplication[1]))
            
            if set(currentPremise).issubset(set(XCopy)):  # Check if the premise of an implication is a subset of XCopy
                for element in currentConclusion:
                    if element not in XCopy:
                        XCopy.extend(currentConclusion)
                stable = False
                remove.append(implication)
                
        for implication in remove:
            copyImplications.remove(implication)
    return XCopy
        

# Construct canonical basis:
def canonical_basis(attributes, context):
    implications = []
    subset = []
    
    while(subset != attributes):
        derived_closure = double_derivation(subset, context)
        
        if tuple(sorted(subset)) != sorted(derived_closure):
            conclusion = set(derived_closure) - set(subset)
            closureSet = implication_closure(subset, implications)
            
            if conclusion and sorted(closureSet) == sorted(subset):
                implications.append(str(tuple(sorted(subset))) + arrow + str(tuple(sorted(conclusion))))
                
        subset = next_preclosure(subset, attributes)
    return implications


# Check if subset A has any element less than 'a' over given set M:
def has_less_than(A, a, M):
    j = M[len(M) - 1]
    num = 1

    while j != a:
        if j in A:
            return True
        elif j == M[0]:
            return False
        else:
            num +=  1
            j = M[len(M) - num]
    return False


# More efficient version of implication_closure() in linear time:
def lin_implication_closure(X, implications):
    XCopy = copy.copy(X)
    copyImplications = copy.copy(implications)   # Creating a copy of implications to not change the original list
    countDict = {}
    implDict = {}

    for implication in copyImplications:
        currentImplication = implication.split(arrow)
        currentPremise = list(ast.literal_eval(currentImplication[0]))
        currentConclusion = list(ast.literal_eval(currentImplication[1]))
        
        countDict[str(currentImplication)] = len(currentPremise)
        
        if len(currentPremise) == 0:
            XCopy = list(set(XCopy).union(currentConclusion))
        
        for a in currentPremise:
            if a in implDict:
                implDict[str(a)].append(currentImplication)
            else:
                implDict[str(a)] = [currentImplication]
            
    update = copy.copy(XCopy)

    while update:
        remove = update.pop(0)
        
        implList = implDict.get(str(remove), [])
        
        for implication in implList:
            countDict[str(implication)] -= 1
            
            if countDict[str(implication)] == 0:
                add = [x for x in list(ast.literal_eval(implication[1])) if x not in XCopy]
                XCopy = list(set(XCopy).union(add))
                update = list(set(update).union(add))
                
    return XCopy


# Construct canonical basis in linear time:
def canonical_basis_optimized(attributes, context):
    implications = []
    subset = list(double_derivation([], context))
    if len(subset):
        implications.append("('',)" + arrow + str(tuple(sorted(subset))))
    i = attributes[len(attributes) - 1]   # largest element of attributes
    
    while sorted(subset) != sorted(attributes):
        
        copyAttributes = copy.copy(attributes)
        copyElement = copyAttributes[len(copyAttributes) - 1]
        while copyElement != i:
            copyAttributes.remove(copyElement)
            copyElement = copyAttributes[len(copyAttributes) - 1]
        
        for element in list(reversed(copyAttributes)):
            if element in subset:
                subset.remove(element)
            else:
                B = subset.copy()
                B.extend([element])
                BnoA = [x for x in B if x not in subset]
                if not has_less_than(BnoA, element, attributes):
                    subset = B.copy()
                    i = element
                    break
                
        derived_closure = double_derivation(subset, context)
        
        if tuple(subset) != derived_closure:
            conclusion = set(derived_closure) - set(subset)
            closureSet = lin_implication_closure(subset, implications)
            
            if conclusion and sorted(closureSet) == sorted(subset):
                implications.append(str(tuple(sorted(subset))) + arrow + str(tuple(sorted(conclusion))))
                
        ACLnoA = [x for x in list(derived_closure) if x not in subset]

        if not has_less_than(ACLnoA, i, attributes):
            
            if sorted(list(derived_closure)) != sorted(attributes):
                
                if subset != list(derived_closure):
                    
                    for m in list(reversed(attributes)):
                        
                        if m not in subset and m != i:
                            subset.append(m)
                        elif m == i:
                            break
                        
            i = attributes[len(attributes) - 1]
            
        else:
            for m in list(reversed(attributes)):
                if m in subset and m != i:
                    subset.remove(m)
                elif m == i:
                    break
                
            if attributes[0] in subset:
                i = attributes[len(attributes) - 1]
    return implications


# Check which implications are trivial and label as trivial if so:
def trivial_implications(implications, attributes):
    newImplications = []
    
    for implication in implications:
        
        if all(attr in implication for attr in attributes):
            implication = implication + " [trivial]"
            
        newImplications.append(implication)
    return newImplications


# Method to calculate the canonical basis:
def dg_basis(context):
    Properties = list(context.properties)
    start_time = time.time()
    
    canonBase = canonical_basis(Properties, context)
    
    elapsed_time = time.time() - start_time
    elapsed_time_seconds = round(elapsed_time, 3)
    print("Time elapsed during algorithm: %s seconds" % elapsed_time_seconds)
    return trivial_implications(canonBase, Properties)


# Optimized version of dg_basis():
def dg_basis_optimized(context):
    Properties = list(context.properties)
    start_time_optimized = time.time()
    
    canonBaseOptimized = canonical_basis_optimized(Properties, context)
    
    elapsed_time_optimized = time.time() - start_time_optimized
    elapsed_time_optimized_seconds = round(elapsed_time_optimized, 3)
    print("Time elapsed during algorithm: %s seconds" % elapsed_time_optimized_seconds)
    return trivial_implications(canonBaseOptimized, Properties)