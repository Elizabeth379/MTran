import subprocess

def execute_cpp_file(file_path):
    try:
        compile_process = subprocess.Popen(['g++', file_path, '-o', 'executable'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        compile_output, compile_error = compile_process.communicate()

        if compile_error:
            print("Ошибка компиляции:")
            print(compile_error.decode("utf-8"))
            return

        execution_process = subprocess.Popen(['./executable'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        execution_output, execution_error = execution_process.communicate()

        if execution_error:
            print("Ошибка выполнения:")
            print(execution_error.decode("utf-8"))
            return

        print("Результат выполнения программы:")
        print(execution_output.decode("utf-8"))

    except Exception as e:
        print("Произошла ошибка:")
        print(str(e))

if __name__ == "__main__":
    cpp_file_path = "file.cpp"
    execute_cpp_file(cpp_file_path)
