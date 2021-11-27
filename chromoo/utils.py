from cadet import Cadet

def loadh5(filename):

    sim = Cadet()
    sim.filename = filename
    sim.load()

    return sim
