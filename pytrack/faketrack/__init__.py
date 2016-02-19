from tracker import Tracker, PsychoTracker
from display import Display
from matlab import Matlab
import Dialog
import Trial

randcb = None

def randomint(max):
	assert callable(randcb)
	f = sys._getframe(1)
	return randcb(f.f_code.co_name, f.f_lineno)
