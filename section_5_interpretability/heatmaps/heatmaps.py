from collections import defaultdict
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.ticker import FixedLocator, FixedFormatter
import matplotlib.ticker as tkr
from pathlib import Path
import click
import datetime
import os

num_layers = 6
def get_files(path, dfname):
    files = []
    print("path:",path)
    print("dfname:",dfname)
    if not dfname:
        print("No file name provided")
    else:
        if len(dfname) > 1:
            files = list(dfname)
        else:
            dfname = dfname[0]
            print("No file name provided")
            tpath = os.path.join(path, dfname)
            if Path(tpath).is_file():
                files = [tpath]
            else:
                files = []
                for root, dirs, _files in os.walk(path):
                    for _file in _files:
                        root_file = os.path.join(root, _file)
                        if all(s in root_file for s in dfname.split("|")):
                            files.append(root_file)
    return files


def load(filename):
    result = []
    labels = []
    smallest = float('inf')
    largest = 0
    with open(filename) as file:
        for line in file:
            line = line.strip().split('\t')
            name_of_matrix = line[0]
            if "cossim" not in filename:
                amount_bigger = 2
                if "11b" in filename:
                    amount_bigger = 64
                if "large" in filename:
                    amount_bigger = 4
                if "small" in filename:
                    amount_bigger = 2
                if name_of_matrix == "wi" or name_of_matrix == "wo":
                    change = amount_bigger * 1.048 * 1000000
                else:
                    change = 1.048 * 1000000
                #change = 1 
            else:
                change = 1
            values = [float(x) / change for x in line[1:]]
            # if 'cossim' in filename:
            #     values = [1 - x for x in values]
            result.append(values)
            labels.append(name_of_matrix)
            for i in values:
                largest = max(i, largest)
                smallest = min(i, smallest)
    return np.asarray(result), labels
  
def get_s_l(filename):
    other_filename = filename.replace('encoder', 'decoder')
    if 'l1_decoder' in filename:
        other_filename = filename.replace('l1_decoder', 'l1_encoder')
    if 'cossim_decoder' in filename:
        other_filename = filename.replace('cossim_decoder', 'cossim_encoder')
    result = []
    labels = []
    smallest = float('inf')
    largest = 0
    with open(filename) as file:
        for line in file:
            line = line.strip().split('\t')
            name_of_matrix = line[0]
            if "cossim" not in filename:
                amount_bigger = 2
                if "11b" in filename:
                    amount_bigger = 64
                if "large" in filename:
                    amount_bigger = 4
                if "small" in filename:
                    amount_bigger = 2
                if name_of_matrix == "wi" or name_of_matrix == "wo":
                    change = amount_bigger * 1.048 * 1000000
                else:
                    change = 1.048 * 1000000
                #change = 1
            else:
                change = 1
            values = [float(x) / change for x in line[1:]]
            # if 'cossim' in filename:
            #     values = [1 - x for x in values]
            result.append(values)
            labels.append(name_of_matrix)
            if name_of_matrix != "wo":
                for i in values:
                    largest = max(i, largest)
                    smallest = min(i, smallest)
    with open(other_filename) as file:
        for line in file:
            line = line.strip().split('\t')
            name_of_matrix = line[0]
            if "cossim" not in filename:
                if "11b" in filename:
                    amount_bigger = 64
                if "large" in filename:
                    amount_bigger = 4
                if "small" in filename:
                    amount_bigger = 2
                if name_of_matrix == "wi" or name_of_matrix == "wo" and 'cossim' not in filename:
                    change = amount_bigger * 1.048 * 1000000
                else:
                    change = 1.048 * 1000000
                #change = 1
            else:
                change = 1
            values = [float(x) / change for x in line[1:]]
            result.append(values)
            labels.append(name_of_matrix)
            if name_of_matrix != "wo":
                for i in values:
                    largest = max(i, largest)
                    smallest = min(i, smallest)
    return smallest, largest

def gen_pic(names,fid):
    for j, name in enumerate(names):
        matrix, labels = load(name)
        s, l = get_s_l(name)
        j = j // 2
        color = "Blues" if "l1_encoder" in name or "l1_decoder" in name else "Greens"
        new_labels = []
        for item in labels:
            if item == "wo":
                item = "w_o"
            if item == "wi":
                item = "w_i"
            if "x" in item:
                item = item[-1] + "_x"
            item = "$" + item + "$"
            new_labels.append(item)
        cbar_val = True
        formatter = tkr.ScalarFormatter()
        formatter.set_powerlimits((0, 0))
        ax = sns.heatmap(matrix, cmap=color, vmax=l, vmin=s, yticklabels=new_labels, xticklabels=range(num_layers), square=True, cbar=cbar_val, cbar_kws={"shrink": .35, "format": formatter})
        cbar_axes = ax.figure.axes[-1]
        cbar_axes.yaxis.label.set_size(2)
        plt.yticks(rotation=0)
        plt.xticks(rotation=0)
        fig = ax.get_figure()
        for i in range(matrix.shape[0] + 1):
            ax.axhline(i, color='white', lw=2)
        for i in range(matrix.shape[1] + 1):
            ax.axvline(i, color='white', lw=2)
        fig.tight_layout()
        path = "/home/ahmad/heatmaps/{fid}"
        Path(path).mkdir(parents=True, exist_ok=True)
        fig.savefig(f"{name.split('.')[0]}.png", dpi=300, bbox_inches='tight', pad_inches = 0)
        fig.clf()


@click.command()
@click.argument("fname", nargs=-1, type=str)
@click.option(
    "--path",
    envvar="PWD",
    #    multiple=True,
    type=click.Path(),
    help="The current path (it is set by system)"
)
@click.option(
    "--fid",
    "-fid",
    default="",
    type=str,
    help=""
)
def main(fname, path, fid):
    files = get_files(path, fname)
    print(files)
    if not fid:
        fid = datetime.datetime.now().strftime('%m-%d-%H-%M')
    gen_pic(files,fid)


main()
