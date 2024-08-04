from matplotlib import pyplot as plt
from matplotlib import gridspec 
import matplotlib
from cycler import cycler

matplotlib.use('Agg')

class Plotter():
    def __init__(
    self, 
    title=None,
    xlabel=None,
    ylabel=None,
    xscale='linear', 
    yscale='linear',
    cmap='tab10',
    n_total_curves=1
    ) -> None:

        # try: 
        #     import scienceplots
        #     plt.style.use('science')
        # except ImportError:
        #     pass

        # plt.style.use('science')
        self.fig, self.ax = plt.subplots()
        self.ax.set(xscale=xscale)
        self.ax.set(yscale=yscale)
        self.ax.set(xlabel=xlabel)
        self.ax.set(ylabel=ylabel)
        self.ax.set(title=title)

        _cmap = plt.cm.get_cmap(cmap)
        if 'colors' in _cmap.__dict__: 
            COLORS = _cmap.colors
        elif n_total_curves == 1: 
            COLORS = [_cmap(1.0)]
        else: 
            COLORS = [_cmap(1.*i/(n_total_curves-1)) for i in range(n_total_curves)]

        self.colors = COLORS
        self.cycler = cycler('color', COLORS)
        self.ax.set_prop_cycle(self.cycler)

    def __enter__(self): 
        return self

    def __exit__(self, type, value, traceback): 
        plt.close(self.fig)

    def plot(self, x, y, label=None, ls='solid', lw=1, marker=None, zorder=None) -> None:
        self.ax.plot(x, y, label=label, linestyle=ls, linewidth=lw, marker=marker, zorder=zorder)

    def scatter(self, x, y, **kwargs) -> None:
        self.ax.scatter(x, y, **kwargs)

    def hist(self, x, bins=10):
        self.ax.hist(x, bins=bins)

    def save(self, filename, dpi=300) -> None:
        self.fig.savefig(filename, dpi=dpi)

    def legend(self, location='upper center', anchor=(0.5,-0.2), ncol=1, frame=False):
        self.ax.legend(loc=location, bbox_to_anchor=anchor, ncol=ncol)
        if frame:
            plt.rcParams.update({
                "legend.shadow": True,
                "legend.frameon": True })

    def show(self) -> None:
        plt.show()

    def close(self):
        plt.close(self.fig)


class Subplotter():
    def __init__(
    self, 
    nrows = 1,
    ncols = 1,
    title = None,
    xscale='linear', 
    yscale='linear',
    figsize=None,
    ) -> None:

        if not figsize: 
            self.figsize = (ncols * 4, nrows * 3)

        self.xscale = xscale
        self.yscale = yscale

        self.nrows = nrows
        self.ncols = ncols
        self.fig, self.axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=self.figsize, constrained_layout=True, sharex=True, sharey=True, squeeze=False)
        self.fig.suptitle(title)

    def __enter__(self): 
        return self

    def __exit__(self, type, value, traceback): 
        plt.close(self.fig)

    def plot(self, x, y, irow, icol, xlabel=None, ylabel=None, ls='solid', lw=1, marker=None) -> None:
        ax = self.axes[irow, icol]
        ax.plot(x, y, ls=ls, lw=lw, marker=marker)
        ax.set(xscale=self.xscale)
        ax.set(yscale=self.yscale)
        ax.set(xlabel=xlabel)
        ax.set(ylabel=ylabel)

    def scatter(self, x, y, irow, icol, title=None, xlabel=None, ylabel=None, fontsize=None, **kwargs) -> None:
        ax = self.axes[irow, icol]
        ax.scatter(x, y, **kwargs)
        ax.set(xscale=self.xscale)
        ax.set(yscale=self.yscale)
        ax.set_title(title, fontsize=fontsize)
        ax.set(xlabel=xlabel)
        ax.set(ylabel=ylabel)
        # plt.gca().axes.get_xaxis().set_visible(False)
        # plt.gca().axes.get_yaxis().set_visible(False)
        # ax.grid('off')
        # ax.axis('off')

    def hist(self, x, irow, icol, bins=10):
        ax = self.fig.add_subplot(self.gs[irow * self.ncols + icol])
        ax.hist(x, bins=bins)

    def legend(self, irow, icol, location='upper center', anchor=(0.5,-0.2), ncol=1, frame=False):
        ax = self.fig.add_subplot(self.gs[irow * self.ncols + icol])
        ax.legend(loc=location, bbox_to_anchor=anchor, ncol=ncol)
        if frame:
            plt.rcParams.update({
                "legend.shadow": True,
                "legend.frameon": True })

    def save(self, filename, dpi=300) -> None:
        self.fig.savefig(filename, dpi=dpi)

    def show(self) -> None:
        plt.show()

    def close(self):
        plt.close(self.fig)

