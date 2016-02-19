from os import popen2

def Int(msg, default=1):
    din, dout = popen2('zenity --entry --text="%s"  --entry-text="%s"' % (msg, default))
    return int(dout.read())

def Str(msg, default=1):
    din, dout = popen2( 'zenity --entry --text="%s"  --entry-text="%s"'% (msg, default))
    return str(dout.read()).strip()
