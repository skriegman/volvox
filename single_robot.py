from lxml import etree
import subprocess as sub
import numpy as np
import sys
# from plot import plot_cilia_vectors
from tools import restricted_cilia


SEED = int(sys.argv[1])

RECORD_HISTORY = True  # saves the behavior movie

DRAW_LIGHT_SOURCE = True

BODY_DIAMETER = 5  # in voxels

LIGHT_X = 35  # np.random.randint(0, 200)
LIGHT_Y = 35  # np.random.randint(0, 200)
LIGHT_Z = 5

np.random.seed(SEED)

# clear workspace (don't do this if other jobs are running in folder)
sub.call("rm -r workspace", shell=True)

# get new voxcraft build
BUILD_DIR = "/users/s/k/skriegma/phototaxis/voxcraft-sim/build"
sub.call("cp {}/voxcraft-sim .".format(BUILD_DIR), shell=True)
sub.call("cp {}/vx3_node_worker .".format(BUILD_DIR), shell=True)

# create data folder if it doesn't already exist
sub.call("mkdir data{}".format(SEED), shell=True)
sub.call("cp base.vxa data{}/base.vxa".format(SEED), shell=True)

# clear old .vxd robot files from the data directory
sub.call("rm data{}/*.vxd".format(SEED), shell=True)

# delete old hist file
sub.call("rm a{}.hist".format(SEED), shell=True)

# remove old sim output.xml to save new stats
sub.call("rm output{}.xml".format(SEED), shell=True)

# body
bx, by, bz = (BODY_DIAMETER, BODY_DIAMETER, BODY_DIAMETER)
body = np.ones((bx, by, bz), dtype=np.int8)

# make sphere
sphere = np.zeros((BODY_DIAMETER+2,)*3, dtype=np.int8) 
radius = BODY_DIAMETER//2+1
r2 = np.arange(-radius, radius+1)**2
dist2 = r2[:, None, None] + r2[:, None] + r2
sphere[dist2 <= radius**2] = 1
# remove shell
for layer in range(bz):
    body[:, :, layer] *= sphere[1:bx+1, 1:by+1, layer+1]


# get random cilia field
# cilia_forces = restricted_cilia(body, DEBUG=True)
cilia_forces = 2*np.random.rand(bx,by,bz,3)-1
cilia_forces = cilia_forces.reshape(bz, 3*bx*by)

# ##### Debug cilia #######

# for z in range(bz):
#     for c in range(2):
#         cilia_forces[:,:,z,c][np.where(body[:,:,0] == 0)] = 0
# cilia_forces[:,:,:,2] = 0

# # normalize vectors
# cilia_forces[:,:,:,:2] /= np.sqrt((cilia_forces[:,:,:,:2] ** 2).sum(-1))[..., np.newaxis]

# print(body.shape())
# # cilias = [restricted_cilia(body, DEBUG=False) for _ in range(1)]
# cilias = [cilia_forces]
# plot_cilia_vectors(body, cilias, plot_multiple=True, save_dir="cilia.pdf", l=1, scale=16, width=0.005)
# exit()  
# #########################

# world
wx,wy,wz = LIGHT_X+bx, LIGHT_Y+by, LIGHT_Z+bz
world = body

if DRAW_LIGHT_SOURCE > 0:
    print("drawing light bulb in env")
    world = np.zeros((wx,wy,wz), np.int8)
    world[:bx, :by, :bz] = body

    # get random cilia field
    cilia_forces = restricted_cilia(world, DEBUG=True)  # different cilia
    cilia_forces = cilia_forces.reshape(wz, 3*wx*wy)

    # Lightbulb:
    l_size = 2
    lx = LIGHT_X-l_size//2 # light source min x
    ly = LIGHT_Y-l_size//2 # min y
    lz = LIGHT_Z-l_size//2 # min z
    LIGHT_BULB = np.ones((l_size,)*3, dtype=np.int8)*2  # light bulb is material 2
    print("light pos: " + str(lx+l_size/2-0.5) + ", " + str(ly+l_size/2-0.5) + ", " + str(lz+l_size/2-0.5) )
    world[lx:lx+l_size, ly:ly+l_size, lz:lz+l_size] = LIGHT_BULB 

# reformat data for voxcraft
world = np.swapaxes(world, 0,2)
world = world.reshape(wz, wx*wy)

# start vxd file
root = etree.Element("VXD")

vxa_light_pos_x = etree.SubElement(root, "LightPosX")
vxa_light_pos_x.set('replace', 'VXA.Simulator.LightPosX')
if DRAW_LIGHT_SOURCE:
    vxa_light_pos_x.text = str(lx+l_size/2-0.5)  # for drawing
else:
    vxa_light_pos_x.text = str(lx)

vxa_light_pos_y = etree.SubElement(root, "LightPosY")
vxa_light_pos_y.set('replace', 'VXA.Simulator.LightPosY')
if DRAW_LIGHT_SOURCE:
    vxa_light_pos_y.text = str(ly+l_size/2-0.5)
else:
    vxa_light_pos_y.text = str(ly)

vxa_light_pos_z = etree.SubElement(root, "LightPosZ")
vxa_light_pos_z.set('replace', 'VXA.Simulator.LightPosZ')
if DRAW_LIGHT_SOURCE:
    vxa_light_pos_z.text = str(lz+l_size/2-0.5)
else:
    vxa_light_pos_z.text = str(lz)

if RECORD_HISTORY:
    # sub.call("rm a{0}_gen{1}.hist".format(seed, pop.gen), shell=True)
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
etree.SubElement(structure, "X_Voxels").text = str(wx)
etree.SubElement(structure, "Y_Voxels").text = str(wy)
etree.SubElement(structure, "Z_Voxels").text = str(wz)

data = etree.SubElement(structure, "Data")
for i in range(world.shape[0]):
    layer = etree.SubElement(data, "Layer")
    str_layer = "".join([str(c) for c in world[i]])  # the body doesn't have commas between the voxels
    layer.text = etree.CDATA(str_layer)

data = etree.SubElement(structure, "BaseCiliaForce")
for i in range(cilia_forces.shape[0]):
    layer = etree.SubElement(data, "Layer")
    str_layer = "".join([str(c) + ", " for c in cilia_forces[i]]) # other variables can be floats so they need commas
    layer.text = etree.CDATA(str_layer)

# save the vxd to data folder
with open('data'+str(SEED)+'/bot_0.vxd', 'wb') as vxd:
    vxd.write(etree.tostring(root))

# ok let's finally evaluate all the robots in the data directory

if RECORD_HISTORY:
    sub.call("./voxcraft-sim -i data{0} -o output{0}.xml -f > a{0}.hist".format(SEED), shell=True)
else:
    sub.call("./voxcraft-sim -i data{0} -o output{0}.xml".format(SEED), shell=True)