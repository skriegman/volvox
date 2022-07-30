import numpy as np 
import math

import seaborn as sns
import matplotlib
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import LightSource
# import matplotlib.patches as mpatches
# matplotlib.use('agg')
import matplotlib.pyplot as plt

# plt.switch_backend('agg')
# matplotlib.rcParams['pdf.fonttype'] = 42
# matplotlib.rcParams['ps.fonttype'] = 42
# matplotlib.rcParams['legend.frameon'] = 'True'
# matplotlib.rcParams["legend.framealpha"] = 0.75
# matplotlib.rcParams["legend.fancybox"] = True

sns.set(color_codes=True, context="poster")
sns.set_style("white")

# colors = ["dark pink", "ocean green", "sea blue", "grey", "tan"]
# sns.set_palette(sns.xkcd_palette(colors), desat=.9)


def plot_body(body, dpi=1200):

    cmap = cm.get_cmap('Set2')

    fig = plt.figure(figsize=(8, 8))

    ls = LightSource(0, 90)

    n = 0
    print("printing bot {}".format(n))
    n += 1
    ax = fig.add_subplot(8,8, n, projection='3d')
    ax.set_xlim([0, max(body.shape)])
    ax.set_ylim([0, max(body.shape)])
    ax.set_zlim([0, max(body.shape)])

    # ax.set_aspect('equal')
    ax.view_init(elev=65, azim=-10)
    ax.set_axis_off()

    # colors = (np.rot90(body,2)-1) / (np.max(body)-1)
    # colors = cmap(colors)
    colors = cmap(np.rot90(body,2)-1)
    print(cmap(0))
    print(cmap(1))
    print(cmap(2))
    print(cmap(3))
    # x, y, z = np.indices((7, 7, 5))
    ax.voxels(np.rot90(body,2), facecolors=colors, edgecolor='k', linewidth=0.1, shade=True, lightsource=ls, alpha=0.6)
    # ax.text(0.5 * body.shape[0], 1.0*body.shape[1], -6*body.shape[2], "R: {}".format(round(fits[n-1]-1, 2)), fontsize=10, ha='center')

    fig.subplots_adjust(wspace=-0.8, hspace=-0.8)
    bbox = fig.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    plt.savefig("body.png", bbox_inches='tight', dpi=dpi, transparent=True)


def plot_cilia_vectors(body, cilia, save_dir, scale, width, l=None, plot_multiple=False):
    
    if not plot_multiple:
        # Plot cilia vectors 
        for l in range(body.shape[2]):

            layer = body[:,:,l]
            layer_cilia = cilia[:,:,l,:]
            
            if np.sum(layer==2) != 0:

                fig,ax = plt.subplots()
                ax.matshow(layer, origin='lower')

                # iterate through cells to draw on cilia vectors
                for r in range(layer_cilia.shape[0]):
                    for c in range(layer_cilia.shape[1]):
                        vector = layer_cilia[r,c,:]
                        if np.sum(vector)!=0:
                            x = vector[0]
                            y = vector[1]
                            assert vector[2]==0

                            # print(r,c)
                            # print(x,y)

                            # Draw vector onto image at r,c
                            # ax.quiver(c,r,c+x,r+y,angles='xy')
                            ax.quiver(c,r,x,y,angles=math.degrees(math.atan2(y,x)), scale=scale, width=width, pivot='tip')
                            # ax.annotate(r'({:.2f},{:.2f})'.format(x,y), (c,r))

                plt.title(f'layer {l}')
                plt.savefig(f'{save_dir}cilia_vectors_layer{l}')
                plt.close()
                # plt.show()
                # exit()
    else:
        assert type(cilia)==list
        layer = body[:,:,l]
        
        fig,ax = plt.subplots()
        ax.matshow(layer, origin='lower')

        for c in cilia:

            layer_cilia = c[:,:,l,:]
            
            # iterate through cells to draw on cilia vectors
            for r in range(layer_cilia.shape[0]):
                for c in range(layer_cilia.shape[1]):
                    vector = layer_cilia[r,c,:]
                    if np.sum(vector)!=0:
                        x = vector[0]
                        y = vector[1]
                        assert vector[2]==0

                        # print(r,c)
                        # print(x,y)

                        # Draw vector onto image at r,c
                        # ax.quiver(c,r,c+x,r+y,angles='xy')
                        ax.quiver(c,r,x,y,angles=math.degrees(math.atan2(y,x)), scale=scale, width=width, pivot='tip')
                        # ax.annotate(r'({:.2f},{:.2f})'.format(x,y), (c,r))

        plt.title(f'layer {l}')
        plt.savefig(save_dir)
        # plt.show()
        # exit()

