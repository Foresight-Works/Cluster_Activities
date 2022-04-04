import matplotlib.pyplot as plt
import numpy as np
from utils import *
print('plots imported')

def save_fig(fig_name, results_dir, tight_layout=True,\
             fig_extension="png", resolution=300):

    '''
    Save plot to the stated path

    :params:
    fig_name: The plot file name
    results_dir: The directory to story the plot
    fig_extension: The file extension/type
    resolution: The desired plot resolution
    '''

    path = os.path.join(results_dir, fig_name + "." + fig_extension)
    print("Saving figure", fig_name)
    if tight_layout:
        plt.tight_layout()
    plt.savefig(path, format=fig_extension, dpi=resolution)



def histogram_stats(x, title, xtitle, fig_path):

    '''
    Plot histogram marking the mean, median and 3rd percentile values
    and limit the x values range by outliers

    :params:
    x: A list or array of numeric values
    title: The histogram title
    xtitle: The counted values (x axis title)
    fig_path: The path (directory and file name) to where the plot will be saved
    :return: A saved histogram plot at the specified path
    '''

    result = plt.hist(x, bins=100, color='c', edgecolor='k', alpha=0.65)
    min_ylim, max_ylim = plt.ylim()

    # Add median line and value
    plt.axvline(x.median(), color='k', linestyle='dashed', linewidth=1)
    plt.text(x.median() * 1.1, max_ylim * 0.9, 'Median: {:.2f}'.format(x.median()))

    # Add 3rd quartile
    plt.axvline(np.quantile(x, .75), color='k', linestyle='dashed', linewidth=1)
    plt.text(x.median() * 1.1, max_ylim * 0.7, '3rd Quartile: {:.2f}'.format(np.quantile(x, .75)))

    #Add mean line and value
    plt.axvline(x.mean(), color='k', linestyle='dashed', linewidth=1)
    plt.text(x.mean() * 1.1, max_ylim * 0.5, 'Mean: {:.2f}'.format(x.mean()))

    x = list(x)
    max_xlim = x_outliers(x)
    plt.xlim(0, max_xlim)
    plt.xlabel(xtitle)
    plt.title(title)
    plt.savefig(fig_path)
    plt.close()


def masked_heatmap(corr_matrix):

    '''
    Plot the heatmap for features correlation
    :param:
    corr_matrix: Correlation matrix
    '''
    plt.figure(figsize=(12, 7))

    # Generate a mask for the upper triangle
    mask = np.zeros_like(corr_matrix, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True

    # Generate a custom diverging colormap
    #cmap = sns.diverging_palette(220, 10, as_cmap=True)

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(corr_matrix, mask=mask, cmap='YlOrBr', vmax=1.0, annot=True,
                square=True, linewidths=.5, cbar_kws={"shrink": .5})

    # save_fig("features_correlation", './results')
    plt.show()
