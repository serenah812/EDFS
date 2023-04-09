import sys
import os
import requests
import base64

def check_if_file(path):
    # check if the path is a path to file
    if '.' in path[path.rfind('/') + 1:]:
        return 'file'
    else:
        return 'not file'

def encoding(s):
    # return the encoded string
    return base64.b64encode(s.encode()).decode()

def decoding_if_file(s):
    try:
        # decoding if the string is encoded
        return base64.b64decode(s).decode()
    except:
        # if error incurred, means that the string is not encoded, return the original string
        return s

def check_exist(url, path):
    # check if the path is a path to file
    # if it is, the file name need to be encoded to match the file name in the system
    if check_if_file(path) == 'file':
        path = path[:path.rfind('/')] + '/' + encoding(path[path.rfind('/') + 1:])
    r = requests.get(url+path+'.json').json()
    if r is None:
        # the path does not exist
        return False
    else:
        # the path exists
        return True

def ls(url, path):
    # lists the files in the specified directory on EDFS
    r = requests.get(url+path+'.json').json()
    dir_list = []
    # check if the path is a path to file
    if check_if_file(path) == 'file':
        return 'Error: \'ls\' only list content under directory, ' + path + ' is a path to file.'
    # check if the directory exists
    elif check_exist(url, path):
        # check if the directory has content
        if type(r) is dict:
            for key in r.keys():
                dir_list.append(decoding_if_file(key))
            return dir_list
        else:
            return dir_list
    else:
        return 'Error: no such directory.'

def mkdir(url, path):
    # creates a directory on EDFS
    if check_if_file(path) == 'not file':
        if check_exist(url, path):
            return 'Error: directory already exists'
        elif path.count('/') == 1:
            r = requests.patch(url+'/.json', json={path[path.rfind('/')+1:]:''})
            return ''
        else:
            r = requests.patch(url+path[:path.rfind('/')]+'.json', json={path[path.rfind('/')+1:]:''})
            return ''
    else:
        return 'Error: cannot create file using \'-mkdir\', please use \'-create\'.'

def rmdir(url, path):
    # removes a directory on EDFS
    if check_if_file(path) == 'not file':
        if check_exist(url, path):
            if len(ls(url, path)) == 0:
                r = requests.delete(url+path+'.json')
                # add the parent directory back
                if path.count('/') > 1:
                    parent_path = path[:path.rfind('/')]
                    mkdir(url, parent_path)
            else:
                print('Error: directory not empty.')
        else:
            print('Error: no such directory.')
    else:
        print('Error: cannot remove file using \'-rmdir\', please use \'-rm\'.')

def rm(url, path):
    # removes the specified file or directory on EDFS
    if check_if_file(path) == 'file':
        if check_exist(url, path):
            path = path[:path.rfind('/')] + '/' + encoding(path[path.rfind('/') + 1:])
            r = requests.delete(url + path + '.json')
            if path.count('/') > 1:
                    parent_path = path[:path.rfind('/')]
                    mkdir(url, parent_path)
        else:
            print('Error: no such file.')
    else:
        rmdir(url, path)

def cat(url, path):
    # displays the contents of a file on EDFS
    if check_if_file(path) == 'file':
        if check_exist(url, path):
            path = path[:path.rfind('/')] + '/' + encoding(path[path.rfind('/') + 1:])
            r = requests.get(url + path + '.json').json()
            print(r)
        else:
            print('Error: no such file.')
    else:
        print('Error: ' + path + ' is a directory.')

def put(url, local_path, edfs_path):
    # uploads a file from the local file system to EDFS
    if check_exist(url, edfs_path):
        local_file_name = local_path[local_path.rfind('/')+1:]
        file_name_encoded = encoding(local_file_name)
        if edfs_path.endswith('/'):
            if check_exist(url, edfs_path+local_file_name):
                print('Error: file already exists.')
            else:
                with open(local_path) as f:
                    file_content = f.read()
                r = requests.patch(url+edfs_path+'.json', json={file_name_encoded:file_content})
        else:
            if check_exist(url, edfs_path+'/'+local_file_name):
                print('Error: file already exists.')
            else:
                with open(local_path) as f:
                    file_content = f.read()
                r = requests.patch(url+edfs_path+'.json', json={file_name_encoded:file_content})
    else:
        print('Error: the parent directory does not exist in EDFS.')

def get(url, edfs_path, local_path):
    # downloads a file from EDFS to the local file system
    if check_if_file(edfs_path) == 'file':
        if check_exist(url, edfs_path):
            file_name = decoding_if_file(edfs_path[edfs_path.rfind('/') + 1:])
            file_path = os.path.join(local_path, file_name)
            if os.path.exists(file_path):
                print('Error: file with the same name already exists.')
            else:
                edfs_path = edfs_path[:edfs_path.rfind('/')] + '/' + encoding(edfs_path[edfs_path.rfind('/') + 1:])
                with open(file_path, 'w+') as f:
                    file_content = requests.get(url + edfs_path + '.json').json()
                    f.write(file_content)
        else:
            print('Error: no such file in EDFS.')
    else:
        print('Error: ' + edfs_path + ' is a directory.')

def main():
    url = 'https://hw2-ee3e3-default-rtdb.firebaseio.com'
    # url = 'https://dsci551-default-a0090-default-rtdb.firebaseio.com'
    # check if the command start with -
    command = sys.argv[1]
    if not command.startswith('-'):
        print('Error: command is required to be starts with \'-\'.')
        exit(0)
    elif command in ['-ls', '-rm', '-mkdir', '-rmdir', '-cat']:
        if len(sys.argv) != 3:
            print('Error: command is not following the execution format.')
            exit(0)
        else:
            edfs_path = sys.argv[2]
            # check if the path is absolute path
            if not edfs_path.startswith('/'):
                print('Error: path is required to be start with \'/\'.')
                exit(0)
            elif command == '-ls':
                print(ls(url, edfs_path))
            elif command == '-rm':
                rm(url, edfs_path)
            elif command == '-mkdir':
                result = mkdir(url, edfs_path)
                if result != '':
                    print(result)
            elif command == '-rmdir':
                rmdir(url, edfs_path)
            elif command == '-cat':
                cat(url, edfs_path)
    elif command in ['-put', '-get']:
        if len(sys.argv) != 4:
            print('Error: command is not following the execution format.')
            exit(0)
        elif command == '-put':
            local_path = sys.argv[2]
            edfs_path = sys.argv[3]
            if not edfs_path.startswith('/'):
                print('Error: path is required to be start with \'/\'.')
                exit(0)
            else:
                if os.path.exists(local_path) and os.path.isfile(local_path):
                    put(url, local_path, edfs_path)
                else:
                    print('Error: no such local file.')
                    exit(0)
        elif command == '-get':
            local_path = sys.argv[3]
            edfs_path = sys.argv[2]
            if not edfs_path.startswith('/'):
                print('Error: path is required to be start with \'/\'.')
                exit(0)
            else:
                if os.path.exists(local_path) and os.path.isdir(local_path):
                    get(url, edfs_path, local_path)
                else:
                    print('Error: no such local directory.')
                    exit(0)
    else:
        print('Error: no such command.')


if __name__ == '__main__':
    main()