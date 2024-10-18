# Auto-run all experiments 
# Metrics: Compiled successfully, Expected output, Time for compilation, Time for execution 
# Key: 1(success), 0(unsuccessful). -1(failure/error)

# -compile and run Java natively
# compile- javac {file name}
# run - java {file}.java

import subprocess
import shlex
import os
from prettytable import PrettyTable
import resource

SUCCESS = "✔"
FAILURE = "❌" 
ERROR = "💀"
TIMEOUT = "Timeout"
JAVA_DIR = "./JavaNative"
#GO_DIR = "./JavaNative"

def run_program(program, dir):  
    before_running_time = resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime
    try: 
        run_result = subprocess.run(shlex.split(program), cwd=dir, check=False, timeout=20, 
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL) 
    except  subprocess.TimeoutExpired: 
        return (-1, None) 
    after_running_time = resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime
    time_to_run_program = after_running_time - before_running_time
    return (run_result.returncode, time_to_run_program)

def get_file_with_extension(dir, ext):
    for file in os.listdir(dir):
        if file.endswith(ext):
            return file
        
def get_compilation_table(): 
    myTable = PrettyTable(["Program", "Java native", "Wasm from Java", "Go Native", "Wasm from Go"])    

    for (java_native_program) in zip(
        os.listdir(JAVA_DIR), 
    ): 
        #Java Native ccompilation
        returncode, time = run_program(f"javac {java_native_program}", f"{JAVA_DIR}/{java_native_program}")
        java_row_value = f"{time:.2f}" if returncode == 0 else ERROR      

        myTable.add_row([java_native_program, java_row_value])

        print(myTable)

def get_execution_table(): 
    myTable = PrettyTable(["Program", "Java native", "Wasm from Java", "Go Native", "Wasm from Go"])    

    for (java_native_program) in zip(
        os.listdir(JAVA_DIR), 
    ): 
        
         #java native excution
        returncode, _ = run_program(f"javac {java_native_program}", f"{JAVA_DIR}/{java_native_program}")
        if returncode != 0: java_row_value = ""
        else:
            java_run = (f"java {java_native_program}")
            assert(os.path.isfile(java_run))
            print(f"Testing native Java {java_native_program}...")
            returncode, time = run_program(java_run, ".")
            if returncode == 0: java_row_value = f"{time:.2f}" 
            elif returncode == -1: java_row_value = TIMEOUT
            else: java_row_value = ERROR

        myTable.add_row([java_native_program, java_row_value])


    myTable.title
    print(myTable)

#get_compilation_table()
get_execution_table()