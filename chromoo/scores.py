from numpy import log10

def sse(y0, y):
    """
        calculate the SSE given 2 vectors
    """
    assert(len(y0) == len(y))
    return sum([(n1 - n2)**2 for n1, n2 in zip(y, y0)])

def logsse(y0, y):
    """
        Calculate the log of SSE of given 2 vectors
    """

    assert(len(y0) == len(y))
    return log10(sum([(n1 - n2)**2 for n1, n2 in zip(y, y0)]))

scores_dict = {
    'sse': sse,
    'logsse': logsse
}
