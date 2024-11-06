import subprocess
import shlex
import os
from prettytable import PrettyTable
import resource
 
SUCCESS = "✔"
FAILURE = "❌"
ERROR = "💀"
TIMEOUT = "Timeout"
JAVA_DIR = "./JavaNative"  # Ensure this path is correct
GO_NATIVE_DIR = "./Go-Native"
GO_WASM_DIR = "./Go-Wasm"
JAVA_DIR = "./JavaNative"
 
def run_program(program, dir): 
    print(f"Running: {program} in {dir}")  # Debugging output
    before_running_time = resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime
    try:
        run_result = subprocess.run(shlex.split(program), cwd=dir, check=False, timeout=120,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = run_result.stdout, run_result.stderr
        if stdout:
            print(f"Output: {stdout.decode(errors='ignore')}")
        if stderr:
            print(f"Error: {stderr.decode(errors='ignore')}")
    except subprocess.TimeoutExpired:
        print(f"{program} timed out.")
        return (-1, None)
    after_running_time = resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime
    time_to_run_program = after_running_time - before_running_time
    return (run_result.returncode, time_to_run_program)

def get_compilation_table(): 
    myTable = PrettyTable(["Program", "Go native", "Go wasm", "java native"])    

    for folder in os.listdir(GO_NATIVE_DIR):        
        folder_path = os.path.join(GO_NATIVE_DIR, folder)
    for folder2 in os.listdir(GO_WASM_DIR):
        folder2_path = os.path.join(GO_WASM_DIR, folder2)
    for folder3 in os.listdir(JAVA_DIR):        
        folder3_path = os.path.join(JAVA_DIR, folder3)

        if not os.path.isdir(folder_path):
            print(f"Skipping non-directory: {folder}")
        if not os.path.isdir(folder2_path):
            print(f"Skipping non-directory: {folder2}")
            continue
        if not os.path.isdir(folder3_path):
            print(f"Skipping non-directory: {folder3}")
            continue


        for go_native_program in os.listdir(folder_path):
            if not go_native_program.endswith(".go"):
                print(f"Skipping non-Go file: {go_native_program}")
                continue
           
            print(f"Compiling {go_native_program}...")

              
        # Go native compilation         
        returncode, time = run_program(f"go build {go_native_program}", folder_path)
        go_native_row_value = f"{time:.2f}" if returncode == 0 else ERROR

        for go_wasm_program in os.listdir(folder2_path):
            if not go_wasm_program.endswith(".wasm"):
                print(f"Skipping non-wasm file: {go_wasm_program}")
                continue
           
            print(f"Compiling {go_wasm_program}...")
               # Go wasm compilation         
            returncode, time = run_program(f"GOOS=js GOARCH=wasm go build -o {go_wasm_program}", folder2_path)
            go_wasm_row_value = f"{time:.2f}" if returncode == 0 else ERROR

        
        for java_program in os.listdir(folder3_path):
            if not java_program.endswith(".java"):
                print(f"Skipping non-javafile: {java_program}")
                continue
           
            print(f"Compiling {java_program}...")
               # Go wasm compilation         
            returncode, time = run_program(f"javac {java_program}", folder3_path)
            java_row_value = f"{time:.2f}" if returncode == 0 else ERROR
  

    myTable.add_row([go_native_program, go_native_row_value, go_wasm_program, go_wasm_row_value, java_program, java_row_value])
    print(myTable)
  get_compilation_table()
