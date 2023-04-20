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
BB_local_dict            = {}
BB_global_dict           = {}
BB_adjacent_mat          = [] #it's for all the BBs inside a function
BB_local_adj             = [] #it's local to each BB in a function
BB_adjacent_mat_global   = {} #it's for all of the funcitons
BB_livness               = [] #it's for all the BBs inside a function
BB_livness_local         = [] #it's local to each BB in a function
BB_livness_gloabal       = {} #it's for all of the funcitons
BB_livness_start         = [] #it's for all the BBs inside a function
BB_livness_local_start   = [] #it's local to each BB in a function
BB_livness_gloabal_start = {} #it's for all of the funcitons
for line in lines:
    words = line.split()

    if fun_def: #since we know the immidiate line after the __GIMPLE is the argument lines of the function
        fun_def = 0
    
    for word in words:

        if '__GIMPLE' in word: #check for the __GIMPLE that is a distinctive annotation for the beginning of the function
            fun_def                               = 1
        
        if '{' in word: #check to see if we are in the function scope.
            function_scope                        = 1 #check if we are inside of the function scope 
        if '}' in word: #check to see if we are out of the function scope.
            function_scope                        = 0   
            BB_global_dict[function_name]         = BB_local_dict
            BB_local_dict                         = {}
            BB_adjacent_mat.append(BB_local_adj)
            BB_adjacent_mat_global[function_name] = BB_adjacent_mat
            BB_local_adj                          = []
            BB_adjacent_mat                       = []
            BB_ind                                = -1
            function_name                        += 1 #increase the index of function

    if line[0:4] == '__BB':
        BB_scope                      = 1 #check that we are inside a BB
        BB_first_line                 = 1
    
    if BB_first_line: #store BBs data
        if BB_ind>=0: #not for the first one
            BB_adjacent_mat.append(BB_local_adj)
        BB_local_adj           = [] 
        BB_first_line          = 0 #reset the first line flag for BBs
        start                  = line.find('(')+1
        if line.find(',') > 0: #check if there is other info
            end                = line.find(',')
        else:
            end                = line.find(')') 
        BB_name                = line[start: end]
        BB_ind                += 1
        BB_local_dict[BB_ind]  = int(BB_name) #update the local dict for BBs' name
    
    if BB_scope:
        
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


#################################################################################
#Traversing the tree to check the liveness

livness_global = {} #To store liveness for each BBs of all function 
livness_local  = {} #To store liveness for each BBs of each function 
visited_global = {} #To store visited edge of all functions
function_name  = 0

for BB_adjacent_mat_global_key in BB_adjacent_mat_global: #create an empty lists for colored edges
    BB_adjacent_mat = BB_adjacent_mat_global[BB_adjacent_mat_global_key]
    visited_local   = []
    for BB_local_adj in BB_adjacent_mat: 
        BB_edge     = []
        for edge in BB_local_adj:
            BB_edge.append(0)
        visited_local.append(BB_edge)
    visited_global[function_name] = visited_local
    function_name                += 1



##################################################################################


        


