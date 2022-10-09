from lxml import etree
import subprocess as sub
import numpy as np
import sys
from tools import restricted_cilia

SEED = int(sys.argv[1])

BODY_DIAMETER = 5  # in voxels

np.random.seed(SEED)

# get new voxcraft build
BUILD_DIR = "/home/slk6335/voxcraft-sim/build"
sub.call("cp {}/voxcraft-sim .".format(BUILD_DIR), shell=True)
sub.call("cp {}/vx3_node_worker .".format(BUILD_DIR), shell=True)

# create data folder if it doesn't already exist
sub.call("mkdir data{}".format(SEED), shell=True)
sub.call("cp base_test.vxa data{}/base.vxa".format(SEED), shell=True)  # Note we are using base_test.vxa

# clear old .vxd robot files from the data directory
sub.call("rm data{}/*.vxd".format(SEED), shell=True)

# delete old hist file
sub.call("rm a{}.hist".format(SEED), shell=True)

# remove old sim output.xml to save new stats
sub.call("rm output{}.xml".format(SEED), shell=True)

# body
bx, by, bz = (BODY_DIAMETER, BODY_DIAMETER, BODY_DIAMETER)
body = np.ones((bx, by, bz), dtype=np.int8)
body[0,0,0] = 0
body[0,0,4] = 0
body[0,4,0] = 0
body[0,4,4] = 0
body[4,0,0] = 0
body[4,4,0] = 0
body[4,4,4] = 0
body[4,0,4] = 0
# print(np.sum(body))

# reformat data for voxcraft
body = np.swapaxes(body, 0,2)
body = body.reshape(bz, bx*by)

# add cilia
body_cilia = np.zeros((bx,by,bz,3))
body_cilia[0,2,2,0] = 1  # (1, 0, 0)
body_cilia = np.swapaxes(body_cilia, 0,2)
body_cilia = body_cilia.reshape(bz, 3*bx*by)

# start vxd file
root = etree.Element("VXD")

# save the behavior "history" movie
history = etree.SubElement(root, "RecordHistory")
history.set('replace', 'VXA.Simulator.RecordHistory')
etree.SubElement(history, "RecordStepSize").text = '50'
etree.SubElement(history, "RecordVoxel").text = '1'
etree.SubElement(history, "RecordLink").text = '0'
etree.SubElement(history, "RecordFixedVoxels").text = '1'
etree.SubElement(history, "RecordCoMTraceOfEachVoxelGroupfOfThisMaterial").text = '0'  # draw CoM trace
    
structure = etree.SubElement(root, "Structure")
structure.set('replace', 'VXA.VXC.Structure')
structure.set('Compression', 'ASCII_READABLE')
etree.SubElement(structure, "X_Voxels").text = str(bx)
etree.SubElement(structure, "Y_Voxels").text = str(by)
etree.SubElement(structure, "Z_Voxels").text = str(bz)

data = etree.SubElement(structure, "Data")
for i in range(body.shape[0]):
    layer = etree.SubElement(data, "Layer")
    str_layer = "".join([str(c) for c in body[i]])  # the body doesn't have commas between the voxels
    layer.text = etree.CDATA(str_layer)

data = etree.SubElement(structure, "BaseCiliaForce")
for i in range(body_cilia.shape[0]):
    layer = etree.SubElement(data, "Layer")
    str_layer = "".join([str(c) + ", " for c in body_cilia[i]]) # other variables can be floats so they need commas
    layer.text = etree.CDATA(str_layer)

# save the vxd to data folder
with open('data'+str(SEED)+'/bot_0.vxd', 'wb') as vxd:
    vxd.write(etree.tostring(root))

# ok let's finally evaluate all the robots in the data directory

sub.call("./voxcraft-sim -i data{0} -o output{0}.xml -f > a{0}.hist".format(SEED), shell=True)
