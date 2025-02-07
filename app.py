from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import os
import subprocess
import threading
import stat
import zipfile
import tarfile
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='threading')

UPLOAD_FOLDER = '/app/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

running_process = None

def get_file_list(directory):
    """获取指定目录下所有文件的列表，只返回文件名"""
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            files.append(os.path.relpath(os.path.join(root, filename), directory))  # 使用相对路径
    return files

def install_dependencies(extract_dir):
    """安装项目依赖"""
    try:
        # 更新 pip
        subprocess.check_call(['pip', 'install', '--upgrade', 'pip'], cwd=extract_dir, text=True)
        print("Successfully updated pip")
    except subprocess.CalledProcessError as e:
        print(f"Failed to update pip: {e}")

    # 检查是否存在 requirements.txt 文件 (Python)
    requirements_file = os.path.join(extract_dir, 'requirements.txt')
    if os.path.exists(requirements_file):
        try:
            result = subprocess.run(['pip', 'install', '-r', requirements_file, '-i https://pypi.tuna.tsinghua.edu.cn/simple'], cwd=extract_dir, capture_output=True, text=True, check=True)
            print(f"Successfully installed Python dependencies from {requirements_file}")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Failed to install Python dependencies: {e}")
            print(e.stderr)

    # 检查是否存在 package.json 文件 (Node.js)
    package_json_file = os.path.join(extract_dir, 'package.json')
    if os.path.exists(package_json_file):
        try:
            subprocess.check_call(['npm', 'install'], cwd=extract_dir)
            print(f"Successfully installed Node.js dependencies from {package_json_file}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install Node.js dependencies: {e}")

@app.route('/', methods=['GET'])
def index():
    # 获取 /app/uploads 目录下所有子目录的文件列表
    all_files = []
    for item in os.listdir(UPLOAD_FOLDER):
        item_path = os.path.join(UPLOAD_FOLDER, item)
        if os.path.isdir(item_path):
            # 假设解压后，文件都在这个子目录中
            extracted_dir = item_path
            all_files.extend([os.path.join(item, f) for f in get_file_list(extracted_dir)])

    return render_template('index.html', files=all_files)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    filename = file.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # 创建解压目录
    extract_dir_name = filename.rsplit('.', 1)[0]
    extract_dir = os.path.join(app.config['UPLOAD_FOLDER'], extract_dir_name)
    os.makedirs(extract_dir, exist_ok=True)

    # 解压文件到子目录
    try:
        if filename.endswith('.zip'):
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        elif filename.endswith(('.tar', '.tar.gz', '.tgz')):
            with tarfile.open(filepath, 'r') as tar_ref:
                tar_ref.extractall(extract_dir)
        else:
            os.remove(filepath)
            return jsonify({'error': 'Unsupported file type. Only .zip, .tar.gz, and .tgz are allowed.'})

        os.remove(filepath)
    except Exception as e:
        os.remove(filepath)
        return jsonify({'error': f'Extraction failed: {str(e)}'})

    # 安装项目依赖
    install_dependencies(extract_dir)

    # 获取 /app/uploads 目录下所有子目录的文件列表
    all_files = []
    for item in os.listdir(UPLOAD_FOLDER):
        item_path = os.path.join(UPLOAD_FOLDER, item)
        if os.path.isdir(item_path):
            # 假设解压后，文件都在这个子目录中
            extracted_dir = item_path
            all_files.extend([os.path.join(item, f) for f in get_file_list(extracted_dir)])

    # 返回包含文件列表的 JSON 响应
    return jsonify({'message': 'File uploaded and extracted successfully', 'files': all_files})

@app.route('/run', methods=['POST'])
def run():
    global running_process
    if running_process and running_process.poll() is None:
        return jsonify({'error': 'A process is already running'})

    filename = request.form.get('filename')
    arguments = request.form.get('arguments', '')
    if not filename:
        return jsonify({'error': 'No filename provided'})

    # 修改文件查找逻辑，从解压目录中查找文件
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'})

    def run_process(filepath, arguments):
        global running_process
        try:
            args = ['python3', filepath] + arguments.split()
            running_process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            while True:
                output = running_process.stdout.readline()
                if output:
                    socketio.emit('output', {'data': output.strip()})
                if running_process.poll() is not None:
                    break

            return_code = running_process.returncode
            socketio.emit('output', {'data': f'Process finished with return code: {return_code}'})
        except Exception as e:
            socketio.emit('output', {'data': f'Error: {str(e)}'})
        finally:
            running_process = None

    threading.Thread(target=run_process, args=(filepath, arguments)).start()
    return jsonify({'message': 'Process started'})

@socketio.on('connect')
def test_connect():
    print('Client connected')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=8000)