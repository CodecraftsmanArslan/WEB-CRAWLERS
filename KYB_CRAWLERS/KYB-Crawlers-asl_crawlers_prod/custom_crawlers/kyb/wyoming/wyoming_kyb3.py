import os
from nodejs import node, npm
import sys 

def run_crawler():
    if os.path.isdir('wyoming/input/node_modules'):
        if len(sys.argv) > 1:
            code = node.call([f'wyoming/input/index3.js',sys.argv[1]])
        else:
            code = node.call([f'wyoming/input/index3.js'])
    else:
        os.chdir('wyoming/input')
        print('node_modules not found')
        npm.call(['install'])
        os.chdir('../../')
        print(os.curdir)
        if len(sys.argv) > 1:
            code = node.call([f'wyoming/input/index3.js',sys.argv[1]])
        else:
            code = node.call(['wyoming/input/index3.js'])

run_crawler()
print('FINISHED')