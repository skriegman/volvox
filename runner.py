import subprocess as sub

for s in range(10):
    print("seed {0}".format(s))
    sub.call("python single_robot.py {0}".format(s), shell=True)
    
exit()
