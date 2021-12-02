from matplotlib import pyplot as plt

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
        self.fig.savefig(filename)

    def show(self) -> None:
        plt.show()

