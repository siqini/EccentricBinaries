import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

#Zs is 2d array
def SaveContourPlot (Xs, Ys, Zs, my_cmap, xlabel, ylabel, save_filename, colorbar):
    fig = plt.figure()
    if (len(Xs)!= len(Ys)) or (Zs.shape != (len(Xs), len(Ys))):
        print ("Shapes of the input arrays do not match!")
        return
    plt.contourf(Xs, Ys, Zs, cmap=my_cmap)
    if (colorbar == True):
        plt.colorbar()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    fig.savefig(save_filename)
    return

#Zs is 1d array
def SaveScatterPlot (Xs, Ys, Zs, my_cmap, xlabel, ylabel, marker_size, save_filename, colorbar):
    fig = plt.figure()
    if (len(Xs)!= len(Ys)) or (len(Xs) != len(Zs)):
        print ("Shapes of the input arrays do not match!")
        return
    plt.scatter(Xs, Ys, c=Zs, s=marker_size, cmap=my_cmap)
    if (colorbar == True):
        plt.colorbar()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    fig.savefig(save_filename)
    return

def save_a_plot (WhichPlot, Xs, Ys, Zs, my_cmap="plasma", xlabel, ylabel, marker_size=50, save_filename, colorbar=True):
    fig = plt.figure()
    if (WhichPlot == 0):
        print ("No plot type selected")
        return
    if (WhichPlot == 1):
        SaveContourPlot(Xs = Xs, Ys = Ys, Zs = Zs, xlabel = xlabel, ylabel = ylabel, save_filename = save_filename, colorbar = colorbar)
    if (WhichPlot == 2):
        SaveScatterPlot(Xs = Xs, Ys = Ys, Zs = Zs, xlabel = xlabel, ylabel = ylabel, save_filename = save_filename, colorbar = colorbar)
    else:
        print ("Illegal plot code!")
        return
