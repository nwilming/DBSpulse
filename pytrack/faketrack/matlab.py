# The newer scipy version have loadmat in io, not io.mio
# Assume that we are using the scipy >= 0.7.0
try:
    from scipy.io import loadmat
except ImportError:
    from scipy.io.mio import loadmat

from numpy import ndarray

class pdict(dict):
	def __getattr__(self, attr):
		if attr in self:
			return self[attr]
		raise AttributeError, attr


def Matlab(filename):
	r = loadmat(filename)
	r.pop('__header__')
	r.pop('__version__')
	d = r.values()[0]
	def castval(val):
		if type(val) == ndarray:
			return val.item()
		else:
			return val
	return [[pdict((f, castval(getattr(t,f))) for f in dir(t) if f[:1]!='_') for t in sub] for sub in d]
