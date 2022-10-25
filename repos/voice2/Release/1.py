import subprocess
p=subprocess.Popen("voice2.exe",stdin=subprocess.PIPE,stdout=subprocess.PIPE)
p.stdin.write("おはよう\r\n".encode("utf-16-le"))
while True:
    x=p.stdout.readline()
    if x!=b'':
       print(x)
import winsound
winsound.PlaySound(open('1.wav','rb'))