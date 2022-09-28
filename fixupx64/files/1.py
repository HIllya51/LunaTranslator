import subprocess
x=subprocess.run('hookcodecheck.exe /HQN1',stdout=subprocess.PIPE)
print(x.stdout[0])