all: gcwin.so

clean:
	rm gcwin.c gcwin.o gcwin.so

gcwin.c: gcwin.pyx render.h
	pyrexc gcwin.pyx
gcwin.o: gcwin.c
	gcc -O2 -ffast-math -funroll-all-loops -c -fPIC -I/usr/include/python2.5 -I/home/student/n/nwilming/local/EyeLinkDisplaySoftwareLinux/addon/include/SDL gcwin.c
gcwin.so: gcwin.o
	gcc -shared gcwin.o -lcv -lhighgui -lSDL -o gcwin.so 
