#The file name should be dumped using -fdump-tree-ssa-gimple. It's the 021 tree.

filename = "vecaddPragma.c.021t.ssa"
lines    = []

with open(filename, "r") as file:
    for line in file:
        lines.append(line.strip())



#################################################################################
#Create the list of using variables.

function_name    = 0  #Here I just enumerate
initial_part     = 0
var_dict_temp    = {} #It's local for any function and has the temperory vars
var_dict_static  = {} #It's local for any function and has the args and defined vars
var_all          = {} #Key's are corresponded to the funcation name and values are the var_dict_temp of each function
fun_def          = 0  #check for __GIMPLE to see if we are at the beginning of a function

for line in lines:
    words = line.split()  
    
    if fun_def: #since we know the immidiate line after the __GIMPLE is the argument lines of the function
        fun_def = 0
        args = line.split(sep=',') #first split it based on ','
        for arg in args:
            arg_list = arg.split()
            if '(' not in arg: #check if it is the first arguman and has the function name and other stuff in it
                if ')' not in arg: #check if it is the last arguman and has the last ')'
                    var_dict_static[arg_list[-1]] = arg[1:-(len(arg_list[-1])+1)]
                else:
                    var_dict_static[arg_list[-1][0:-1]] = arg[1:-(len(arg_list[-1])+1)]
            else:
                par_ind = arg.find('(')
                if ')' not in arg:
                    var_dict_static[arg_list[-1]] = arg[par_ind+1:-(len(arg_list[-1])+1)]
                else:
                    if '(' not in arg_list[-1]:
                        var_dict_static[arg_list[-1][0:-1]] = arg[par_ind+1:-(len(arg_list[-1])+1)]

    for word in words:
        if '__GIMPLE' in word: #check for the __GIMPLE that is a distinctive annotation for the beginning of the function
            fun_def                 = 1
         
        if '{' in word: #check to see if we are in the function scope.
            initial_part            = 1 #since in the SSA all the initializations are at the beginning
        if '}' in word: #check to see if we are out of the function scope.
            var_all_local           = {} #to have temp and static vars in dict
            var_all_local['static'] = var_dict_static
            var_all_local['temp']   = var_dict_temp
            var_all[function_name]  = var_all_local #updating var_all for values in the parsed function
            var_dict_temp           = {} #clear the local var_dict_temp
            var_dict_static         = {} #clear the local var_dict_static
            function_name          += 1 #increase the index of function
        if '__BB' in word:
            initial_part            = 0 #check the end of initialization
    
    if initial_part and len(words)>1:
        if words[-1][0] == '_': #having '_' at the beginning indicates it's temperoray and made by the compiler
            var_dict_temp[words[-1][0:-1]]   = line[0:-(len(words[-1])+1)]
        else:
            var_dict_static[words[-1][0:-1]] = line[0:-(len(words[-1])+1)]
        
print(var_all[1]['temp'])       
print("\n\n\n",var_all[1]['static'])




#################################################################################
#Create the adjacent matrix for BBs
fun_def                  = 0 #check for __GIMPLE to see if we are at the beginning of a function
function_scope           = 0 #to check if we are inside a scope
function_name            = 0 #Here I just enumerate
BB_name                  = 0 #to have the name of current BB. It's only valid if BB_scope=1
BB_ind                   = -1#to store a numeric value for BBs.
BB_scope                 = 0 #to check if we are inside a scope
BB_first_line            = 0 #to store the BBs name and info
BB_local_dict            = {}#it has the 0-indexed vertex as key and BBs name in val for each function
BB_global_dict           = {}#it has the 0-indexed vertex as key and BBs name in val for all functoins
BB_rev_local_dict        = {}#it has the 0-indexed vertex as val and BBs name in key for each function
BB_rev_global_dict       = {}#it has the 0-indexed vertex as val and BBs name in key for all functoins
BB_adjacent_mat          = [] #it's for all the BBs inside a function
BB_local_adj             = [] #it's local to each BB in a function
BB_adjacent_mat_global   = {} #it's for all of the funcitons
BB_livness               = [] #it's for all the BBs inside a function
BB_livness_local         = set() #it's local to each BB in a function
BB_livness_gloabal       = {} #it's for all of the funcitons
BB_livness_start         = {} #it's for all the BBs inside a function
BB_livness_gloabal_start = {} #it's for all of the funcitons
BB_all_val               = [] #have all the variable use in a function
BB_all_val_global        = {} #have entire variables
for line in lines:
    words = line.split()

    if fun_def: #since we know the immidiate line after the __GIMPLE is the argument lines of the function
        fun_def = 0

    if '__GIMPLE' in line: #check for the __GIMPLE that is a distinctive annotation for the beginning of the function
        fun_def                                 = 1
        
    if '{' in line: #check to see if we are in the function scope.
        function_scope                          = 1 #check if we are inside of the function scope 
    if '}' in line: #check to see if we are out of the function scope.
        function_scope                          = 0   
        BB_global_dict[function_name]           = BB_local_dict
        BB_local_dict                           = {}
        BB_rev_global_dict[function_name]       = BB_rev_local_dict
        BB_rev_local_dict                       = {}
        BB_adjacent_mat.append(BB_local_adj)
        BB_adjacent_mat_global[function_name]   = BB_adjacent_mat
        BB_local_adj                            = []
        BB_adjacent_mat                         = []
        BB_livness.append(BB_livness_local)
        BB_livness_gloabal[function_name]       = BB_livness
        BB_livness_gloabal_start[function_name] = BB_livness_start
        BB_livness_local                        = set()
        BB_livness                              = []
        BB_livness_start                        = {}
        BB_ind                                  = -1
        function_name                          += 1 #increase the index of function

    if line[0:4] == '__BB':
        BB_scope                        = 1 #check that we are inside a BB
        BB_first_line                   = 1
    
    if BB_first_line: #store BBs data
        if BB_ind>=0: #not for the first one
            BB_adjacent_mat.append(BB_local_adj)
            BB_livness.append(BB_livness_local)
        BB_local_adj                    = [] 
        BB_livness_local                = set()
        BB_livness_local_start          = set()
        BB_first_line                   = 0 #reset the first line flag for BBs
        start                           = line.find('(')+1
        if line.find(',') > 0: #check if there is other info
            end                         = line.find(',')
        else:  
            end                         = line.find(')') 
        BB_name                         = line[start: end]
        BB_ind                         += 1
        BB_local_dict[BB_ind]           = int(BB_name) #update the local dict for BBs' name
        BB_rev_local_dict[int(BB_name)] = BB_ind
    
    if BB_scope:
        if ' =' in line: #Check if there is an assignment. This can be consider as the start of the livenss analysis since the tree is in SSA form
            if '__MEM' not in words[0]:
                BB_livness_local.add(words[0])
                BB_livness_start[words[0]] = BB_ind
             
            for word in words:
                var  = ''
                vars = set()
                if '_' in word and '__' not in word:
                    for char in word:
                        asci = ord(char)
                        if (asci<=90 and asci >=65) or (asci<=57 and asci>=48) or (asci<=122 and asci>=97) or char =='_':
                            var += char                
                        else:
                            if len(var)>0:
                                vars.add(var)
                                var = ''
                    vars.add(var)
                    for var in vars:
                        if '_' in var:
                            BB_livness_local.add(var)



        if 'goto' in line:
            start = line.find('B')+2
            BB_local_adj.append(int(line[start:-1]))
        if 'return' in line:
            BB_local_adj.append(-1)
        


print("\n\n---------------\n\nThe adjacent mat\n\n------------------\n\n")
print(BB_adjacent_mat_global[1])
BB_ind = 0
for BB_local_adj in BB_adjacent_mat_global[1]:
    print(BB_global_dict[1][BB_ind], "-> ", end='')
    print(BB_local_adj)
    BB_ind += 1

print("\n\n---------------\n\nDef of livness\n\n------------------\n\n")
for var in BB_livness_gloabal_start[1]:
    print(var, " := ", BB_global_dict[1][BB_livness_gloabal_start[1][var]], sep='')

print("\n\n---------------\n\nUse of livness\n\n------------------\n\n")
BB_ind = 0
for BB_livness in BB_livness_gloabal[0]:
    print(BB_global_dict[0][BB_ind], ": ", end='', sep='')
    if len(BB_livness)>0:
        print(BB_livness)
    BB_ind += 1
print("\n")





#################################################################################
#Traversing the tree to check the liveness
def check_finish_teavers(visted_vertex, BB_adjacent_mat):
    for vertex in visted_vertex:
        if visted_vertex[vertex] < len(BB_adjacent_mat[vertex]):
            return 1
    return 0

live_global    = BB_livness_gloabal #To store liveness for each BBs of all function 
live_local     = set() #To store liveness for each BBs of each function 
live           = [] #to store liveness for each function
visited        = [] #To store visited edge of all functions
visited_times  = [] #To store number of visited edge of all functions
function_name  = -1

for BB_adjacent_mat_key in BB_adjacent_mat_global:
    BB_adjacent_mat = BB_adjacent_mat_global[BB_adjacent_mat_key]
    function_name += 1
    visited_times  = []
    for vertex in BB_adjacent_mat: #set all vertex zero visited
        visited_times.append(0)    
    while check_finish_teavers(visited_times, BB_adjacent_mat): #Continue until all paths have been visited
        next = 2
        visited = []

        while next!=-1:#Continue until the last BB
            visited.append(next)
            BB_ind   = BB_rev_global_dict[function_name][next]
            len_next = len(BB_adjacent_mat[BB_ind])
            if visited_times[BB_ind] < len_next:
                next = BB_adjacent_mat[BB_ind][visited_times[BB_ind]]
                visited_times[BB_ind] += 1
            else:
                next = BB_adjacent_mat[BB_ind][visited_times[BB_ind]-1]

        for var in BB_livness_gloabal_start[function_name]:#Update the liveness of the BB in the path
            BB_ind = BB_livness_gloabal_start[function_name][var]
            BB     = BB_global_dict[function_name][BB_ind]
            start  = visited.index(BB)
            last   = start
            for i in range(start+1,len(visited)):
                BB_ind_visited = BB_rev_global_dict[function_name][visited[i]]
                if var in BB_livness_gloabal[function_name][BB_ind_visited]:
                    last = i
            for i in range(start+1, last+1):
                BB_ind_visited = BB_rev_global_dict[function_name][visited[i]]
                live_global[function_name][BB_ind_visited].add(var)
                    
print("\n\n---------------\n\nlivness\n\n---------------\n\n")
BB_ind = 0
for BB_livness in live_global[1]:
    print(BB_global_dict[1][BB_ind], ": ", end='', sep='')
    if len(BB_livness) >0:
        print(BB_livness)
    BB_ind += 1    
print("\n")


##################################################################################


        


