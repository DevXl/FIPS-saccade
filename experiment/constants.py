# MAIN
DUMMYMODE = False  # False for gaze contingent display, True for dummy mode (using mouse or joystick)
LOGFILENAME = 'testing'  # logfilename, without path
LOGFILE = LOGFILENAME[:]  # .txt; adding path before logfilename is optional; logs responses (NOT eye movements, these are stored in an EDF file!)
TRIALS = 10

# DISPLAY
# used in libscreen, for the *_display functions. The values may be adjusted,
# but not the constant's names
SCREENNR = 0  # number of the screen used for displaying experiment
DISPTYPE = 'psychopy'  # either 'psychopy' or 'pygame'
DISPSIZE = (1920, 1080)  # canvas size
# DISPSIZE = [1707, 960]
# DISPSIZE = (2560, 1440)
SCREENSIZE = (73, 33)  # physical display size in cm
# SCREENSIZE = (38, 20)
SCREENDIST = 60
MOUSEVISIBLE = True  # mouse visibility
FULLSCREEN = True
BGC = (125, 125, 125)  # backgroundcolour
FGC = (0, 0, 0)  # foregroundcolour

# INPUT
# used in libinput. The values may be adjusted, but not the constant names.
MOUSEBUTTONLIST = None # None for all mouse buttons; list of numbers for buttons of choice (e.g. [1,3] for buttons 1 and 3)
MOUSETIMEOUT = None # None for no timeout, or a value in milliseconds
KEYLIST = None # None for all keys; list of keynames for keys of choice (e.g. ['space','9',':'] for space, 9 and ; keys)
KEYTIMEOUT = 1 # None for no timeout, or a value in milliseconds
JOYBUTTONLIST = None # None for all joystick buttons; list of button numbers (start counting at 0) for buttons of choice (e.g. [0,3] for buttons 0 and 3 - may be reffered to as 1 and 4 in other programs)
JOYTIMEOUT = None # None for no timeout, or a value in milliseconds

# EYETRACKER
# general
TRACKERTYPE = 'eyelink' # either 'smi', 'eyelink' or 'dummy' (NB: if DUMMYMODE is True, trackertype will be set to dummy automatically)
SACCVELTHRESH = 100 # degrees per second, saccade velocity threshold
SACCACCTHRESH = 100 # degrees per second, saccade acceleration threshold

# FRL
# Used in libgazecon.FRL. The values may be adjusted, but not the constant names.
FRLSIZE = 200 # pixles, FRL-size
FRLDIST = 125 # distance between fixation point and FRL
FRLTYPE = 'gauss' # 'circle', 'gauss', 'ramp' or 'raisedCosine'
FRLPOS = 'center' # 'center', 'top', 'topright', 'right', 'bottomright', 'bottom', 'bottomleft', 'left', or 'topleft'
