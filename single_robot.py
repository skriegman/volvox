from lxml import etree
import subprocess as sub
import numpy as np
import sys
# from plot import plot_cilia_vectors
from tools import restricted_cilia

"""

Note: when we change the cilia params it can cause the bot to spin too fast and explode (sim will diverge).

Things can be done to make the sim stable again:

Lower the cilia magnitude (base.vxa: line 96).

Lower dtfrac (base.vxa: line 40) but this makes sim slow.

Alter force field, gravity, friction, body size, density/elasticity.

TODO: 
RENAME: activationTimeConstant --> adaptationTime
RENAME: recoveryTimeConstant --> responseTime

"""

SEED = int(sys.argv[1])

RECORD_HISTORY = True  # saves the behavior movie

DRAW_LIGHT_SOURCE = True

LIGHT_SIZE = 3

USE_TWO_LIGHTS = True

WORLD_WIDTH = 21

USE_WALLS = False  # make sure to turn on collisions in base.vxa:line 64 <EnableCollision>1</EnableCollision>

BODY_DIAMETER = 5  # in voxels

LIGHT_X = 100  # fitness is calculated based on how close volvox gets to (80, 10) [line 21 in base.vxa]
LIGHT_Y = 10
LIGHT_Z = BODY_DIAMETER//2+1

np.random.seed(SEED)

# get new voxcraft build
BUILD_DIR = "/home/slk6335/voxcraft-sim/build"
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

# add perpendicular cilia field
# for each voxel, where is the cilia force pointing; 
# first 3 params are voxel location in body (bx,by,bz); the 4th param is x,y,z of cilia vector
# the cilia force vector is relative volvox rotatation; volvox starts upright with world's x,y,z 
# body_cilia = np.zeros((6,6,6,3)) -> 6x6x6 voxels; for each voxel there is a 3D cilia force vector pushing/pulling on the voxel
# body_cilia[0,2,1,:] = np.array([0,-1,1])  x=0,y=2,z=1 voxel has cilia force (0,-1,1)
# (0,0,-1) points down
body_cilia = restricted_cilia(body, DEBUG=True)  # DEBUG means all cilia apply perpendicular force
# debug cilia field:
# body_cilia = 2*np.random.rand(bx,by,bz,3)-1  # random cilia
# body_cilia[:,:,:,2] = 0
# body_cilia = np.ones((bx,by,bz,3))
# body_cilia[:,2:,2:,:] = 0
# body_cilia[:2,:2,:1,:1] = -1

# how sensitive should each voxel be to light? Note: only the surface voxels matter.
# body_activation_time_constant = np.ones((bx,by,bz)) * 6
# body_recovery_time_constant = np.ones((bx,by,bz)) * 0.2
# body_downregulation_constant = np.ones((bx,by,bz)) * 0.4
body_activation_time_constant = 10 * np.random.rand(bx,by,bz)
body_recovery_time_constant = 0.01 * np.random.rand(bx,by,bz)
body_downregulation_constant = 0.1 * np.random.rand(bx,by,bz)

# world
world = body
l_size = LIGHT_SIZE
wx,wy,wz = LIGHT_X+bx, LIGHT_Y+by, max(LIGHT_Z+l_size//2+1, bz)

if USE_TWO_LIGHTS:
    wy = WORLD_WIDTH
    LIGHT_X += bx-2  # light embedded in the wall
    LIGHT_Y = WORLD_WIDTH//2

if DRAW_LIGHT_SOURCE > 0:
    print("drawing light bulb in env")
    world = np.zeros((wx,wy,wz), np.int8)
    world[wx//2-bx//2:wx//2+bx//2+1, wy//2-by//2:wy//2+by//2+1, :bz] = body

    # Lightbulb:
    lx = LIGHT_X-l_size//2 # light source min x
    ly = LIGHT_Y-l_size//2 # min y
    lz = LIGHT_Z-l_size//2 # min z
    print("lightA pos: " + str(l_size/2-0.5) + ", " + str(ly+l_size/2-0.5) + ", " + str(lz+l_size/2-0.5) )
    world[:l_size, ly:ly+l_size, lz:lz+l_size] = np.ones((l_size,)*3, dtype=np.int8) * 2  # light bulb A is mat 2
    print("lightB pos: " + str(lx+l_size/2-0.5) + ", " + str(ly+l_size/2-0.5) + ", " + str(lz+l_size/2-0.5) )
    world[lx:lx+l_size, ly:ly+l_size, lz:lz+l_size] = np.ones((l_size,)*3, dtype=np.int8) * 3  # light bulb B is mat 3

if USE_WALLS:
    # add walls to world
    world[:2, :, :bz+2] = 4  # wall
    world[:, :2, :bz+2] = 4
    world[-2:, :, :bz+2] = 4
    world[:, -2:, :bz+2] = 4    
    # world[3*wx//4:3*wx//4+2, :, :bz+2] = 4  ## debug collisions

# reshape body data for world
world_cilia = np.zeros((wx,wy,wz, 3))
world_cilia[wx//2-bx//2:wx//2+bx//2+1, wy//2-by//2:wy//2+by//2+1, :bz, :] = body_cilia
world_cilia = np.swapaxes(world_cilia, 0,2)  # looks good; todo: test
world_cilia = world_cilia.reshape(wz, 3*wx*wy)

world_activation_time_constant = np.zeros((wx,wy,wz))
world_activation_time_constant[wx//2-bx//2:wx//2+bx//2+1, wy//2-by//2:wy//2+by//2+1, :bz] = body_activation_time_constant
world_activation_time_constant = np.swapaxes(world_activation_time_constant, 0,2) 
world_activation_time_constant = world_activation_time_constant.reshape(wz, wx*wy)

world_recovery_time_constant = np.zeros((wx,wy,wz))
world_recovery_time_constant[wx//2-bx//2:wx//2+bx//2+1, wy//2-by//2:wy//2+by//2+1, :bz] = body_recovery_time_constant
world_recovery_time_constant = np.swapaxes(world_recovery_time_constant, 0,2)  
world_recovery_time_constant = world_recovery_time_constant.reshape(wz, wx*wy)

world_downregulation_constant = np.zeros((wx,wy,wz))
world_downregulation_constant[wx//2-bx//2:wx//2+bx//2+1, wy//2-by//2:wy//2+by//2+1, :bz] = body_downregulation_constant
world_downregulation_constant = np.swapaxes(world_downregulation_constant, 0,2) 
world_downregulation_constant = world_downregulation_constant.reshape(wz, wx*wy)


# reformat data for voxcraft
world = np.swapaxes(world, 0,2)
world = world.reshape(wz, wx*wy)

# start vxd file
root = etree.Element("VXD")

# Light A
vxa_lightA_pos_x = etree.SubElement(root, "LightAPosX")
vxa_lightA_pos_x.set('replace', 'VXA.Simulator.LightAPosX')
if DRAW_LIGHT_SOURCE:
    vxa_lightA_pos_x.text = str(l_size/2-0.5)  # for drawing
else:
    vxa_lightA_pos_x.text = str(0)

vxa_lightA_pos_y = etree.SubElement(root, "LightAPosY")
vxa_lightA_pos_y.set('replace', 'VXA.Simulator.LightAPosY')
if DRAW_LIGHT_SOURCE:
    vxa_lightA_pos_y.text = str(ly+l_size/2-0.5)
else:
    vxa_lightA_pos_y.text = str(ly)

vxa_lightA_pos_z = etree.SubElement(root, "LightAPosZ")
vxa_lightA_pos_z.set('replace', 'VXA.Simulator.LightAPosZ')
if DRAW_LIGHT_SOURCE:
    vxa_lightA_pos_z.text = str(lz+l_size/2-0.5)
else:
    vxa_lightA_pos_z.text = str(lz)

# Light B
vxa_lightB_pos_x = etree.SubElement(root, "LightBPosX")
vxa_lightB_pos_x.set('replace', 'VXA.Simulator.LightBPosX')
if DRAW_LIGHT_SOURCE:
    vxa_lightB_pos_x.text = str(lx+l_size/2-0.5)  # for drawing
else:
    vxa_lightB_pos_x.text = str(lx)

vxa_lightB_pos_y = etree.SubElement(root, "LightBPosY")
vxa_lightB_pos_y.set('replace', 'VXA.Simulator.LightBPosY')
if DRAW_LIGHT_SOURCE:
    vxa_lightB_pos_y.text = str(ly+l_size/2-0.5)
else:
    vxa_lightB_pos_y.text = str(ly)

vxa_lightB_pos_z = etree.SubElement(root, "lightBPosZ")
vxa_lightB_pos_z.set('replace', 'VXA.Simulator.LightBPosZ')
if DRAW_LIGHT_SOURCE:
    vxa_lightB_pos_z.text = str(lz+l_size/2-0.5)
else:
    vxa_lightB_pos_z.text = str(lz)

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
for i in range(world_cilia.shape[0]):
    layer = etree.SubElement(data, "Layer")
    str_layer = "".join([str(c) + ", " for c in world_cilia[i]]) # other variables can be floats so they need commas
    layer.text = etree.CDATA(str_layer)

data = etree.SubElement(structure, "ActivationTimeConstant")
for i in range(world_activation_time_constant.shape[0]):
    layer = etree.SubElement(data, "Layer")
    str_layer = "".join([str(c) + ", " for c in world_activation_time_constant[i]])
    layer.text = etree.CDATA(str_layer)

data = etree.SubElement(structure, "RecoveryTimeConstant")
for i in range(world_recovery_time_constant.shape[0]):
    layer = etree.SubElement(data, "Layer")
    str_layer = "".join([str(c) + ", " for c in world_recovery_time_constant[i]])
    layer.text = etree.CDATA(str_layer)

data = etree.SubElement(structure, "DownregulationConstant")
for i in range(world_downregulation_constant.shape[0]):
    layer = etree.SubElement(data, "Layer")
    str_layer = "".join([str(c) + ", " for c in world_downregulation_constant[i]])
    layer.text = etree.CDATA(str_layer)

# save the vxd to data folder
with open('data'+str(SEED)+'/bot_0.vxd', 'wb') as vxd:
    vxd.write(etree.tostring(root))

# ok let's finally evaluate all the robots in the data directory

if RECORD_HISTORY:
    sub.call("./voxcraft-sim -i data{0} -o output{0}.xml -f > a{0}.hist".format(SEED), shell=True)
else:
    sub.call("./voxcraft-sim -i data{0} -o output{0}.xml".format(SEED), shell=True)
