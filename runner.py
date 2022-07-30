import subprocess as sub

for g in [3, 2]:
    for s in range(15):
        print("seed {0}, gridsize: {1}".format(g*100+s, g))
        sub.call("python single_robot.py {0} {1}".format(s, g), shell=True)
    
exit()
