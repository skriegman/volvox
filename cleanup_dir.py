import subprocess as sub

# clear workspace (don't do this if other jobs are running in folder)
sub.call("rm -r workspace", shell=True)

# clear old .vxd robot files from the data directory
sub.call("rm -r data*", shell=True)

# delete old hist file
sub.call("rm a*.hist", shell=True)

# remove old sim output.xml to save new stats
sub.call("rm output*.xml", shell=True)

# remove compiled python artifacts
sub.call("rm *.pyc", shell=True)
sub.call("rm -r __pycache__", shell=True)
