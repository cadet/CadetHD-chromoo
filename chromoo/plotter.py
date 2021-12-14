from matplotlib import pyplot as plt
from matplotlib import gridspec 

class Plotter():
    def __init__(
    self, 
    title=None,
    xlabel=None,
    ylabel=None,
    xscale='linear', 
    yscale='linear'
    ) -> None:

        # plt.style.use('science')
        self.fig, self.ax = plt.subplots()
        self.ax.set(xscale=xscale)
        self.ax.set(yscale=yscale)
        self.ax.set(xlabel=xlabel)
        self.ax.set(ylabel=ylabel)
        self.ax.set(title=title)

    def plot(self, x, y, label=None, ls='solid', lw=1, marker=None) -> None:
        self.ax.plot(x, y, label=label, linestyle=ls, linewidth=lw, marker=marker)

    def scatter(self, x, y, label=None, ls='solid', lw=1, marker=None) -> None:
        self.ax.scatter(x, y, label=label, linestyle=ls, linewidth=lw, marker=marker)

    def save(self, filename) -> None:
        self.fig.savefig(filename, dpi=300)

    def show(self) -> None:
        plt.show()


class Subplotter():
    def __init__(
    self, 
    nrows = 1,
    ncols = 1,
    xscale='linear', 
    yscale='linear'
    ) -> None:

        self.xscale = xscale
        self.yscale = yscale

        self.nrows = nrows
        self.ncols = ncols
        self.fig = plt.figure(figsize=(16,9), constrained_layout=True)
        self.gs = gridspec.GridSpec(nrows, ncols, figure=self.fig)

    def plot(self, x, y, irow, icol, xlabel=None, ylabel=None, ls='solid', lw=1, marker=None) -> None:
        ax = self.fig.add_subplot(self.gs[irow * self.nrows + icol])
        ax.plot(x, y, ls=ls, lw=lw, marker=marker)
        ax.set(xscale=self.xscale)
        ax.set(yscale=self.yscale)
        ax.set(xlabel=xlabel)
        ax.set(ylabel=ylabel)

    def scatter(self, x, y, irow, icol, xlabel=None, ylabel=None, ls='solid', lw=0.1, marker=None) -> None:
        ax = self.fig.add_subplot(self.gs[irow * self.ncols + icol])
        ax.scatter(x, y, ls=ls, lw=lw, marker=marker)
        ax.set(xscale=self.xscale)
        ax.set(yscale=self.yscale)
        ax.set(xlabel=xlabel)
        ax.set(ylabel=ylabel)

    def save(self, filename) -> None:
        self.fig.savefig(filename, dpi=300)

    def show(self) -> None:
        plt.show()

    def close(self):
        plt.close(self.fig)

