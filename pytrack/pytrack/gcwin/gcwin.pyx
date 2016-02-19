from math import sqrt
from time import time

cdef extern from "opencv/cxcore.h":
    ctypedef struct IplImage:
        int width
        int height
        int depth
        int nChannels
        void * imageData
    ctypedef struct CvSize:
        pass
    ctypedef struct CvScalar:
        pass
    ctypedef struct CvPoint:
        int x
        int y
    ctypedef struct CvMat:
        pass
    ctypedef struct CvArr:
        pass
    ctypedef struct CvRect:
        int x
        int y
        int width
        int height
    cdef void cvGetSubRect(IplImage * arr, CvMat * submat, CvRect rect)
    cdef CvSize cvSize(int width, int height)
    cdef IplImage * cvCloneImage(IplImage * im)
    cdef void cvZero(IplImage * im)
    cdef CvScalar cvScalarAll(double v)
    cdef void cvReleaseImage(IplImage ** im)
    cdef void cvGetModuleInfo(int foo, char * cv, char * ad)

cdef extern from "opencv/highgui.h":
    IplImage *cvLoadImage(char * file, int mode)

cdef extern from "opencv/cv.h":
    IplImage *cvCreateImage(CvSize s, int d, int c)
    cdef void cvSmooth(IplImage * out_im, IplImage * in_im, int t, int w, int h, double v, double sigma)
    cdef void cvCircle(IplImage * im, CvPoint c, int size, CvScalar color, int a, int b, int c)
    cdef void cvCopy(IplImage * src, IplImage * dst, CvMat * msk)

cdef extern from "SDL.h":
    ctypedef struct SDL_PixelFormat:
        unsigned int Rmask
        unsigned int Gmask
        unsigned int Bmask
        unsigned int Amask
    ctypedef struct SDL_Surface:
        SDL_PixelFormat * format
    cdef SDL_Surface * SDL_CreateRGBSurfaceFrom(void *pixels, int width, int height, int depth, int pitch, unsigned int Rmask, unsigned int Gmask, unsigned int Bmask, unsigned int Tmask)
    ctypedef struct SDL_Rect:
        pass
    cdef int SDL_BlitSurface(SDL_Surface *src, SDL_Rect *srcrect, SDL_Surface *dst, SDL_Rect *dstrect)
    cdef int SDL_Flip(SDL_Surface * screen)
    cdef SDL_Surface * SDL_GetVideoSurface()

cdef extern from "pygame/pygame.h":
    ctypedef struct PySurfaceObject:
        SDL_Surface * surf

cdef extern from "render.h":
    long render(int count, SDL_Surface * surf, IplImage * result, IplImage * images[], IplImage * masks[], int x, int y)

CV_GAUSSIAN = 2

cdef class GC:
    cdef SDL_Surface * surf
    cdef IplImage * images[20]
    cdef IplImage * masks[20]
    cdef IplImage * result
    cdef int count
    cdef int step
    cdef lx
    cdef ly

    def __cinit__(self, step, filename):
        self.step = step
        self.surf = SDL_GetVideoSurface()
        if type(filename) == tuple:
            fn, count = filename
            self.count = count
            self.load_image(fn)
        else:
            self.count = len(filename)
            self.load_images(filename)
        self.mk_masks()
        self.result = cvCloneImage(self.images[self.count-1])
        self.lx = -1
        self.ly = -1

    def __del__(self):
        cvReleaseImage(&self.result)
        for i in range(self.count):
            cvReleaseImage(&self.images[i])
            cvReleaseImage(&self.masks[i])

    def load_images(self, filenames):
        for i, f in enumerate(filenames):
            self.images[i] = cvLoadImage(f, 1)

    cdef load_image(self, char * filename):
        cdef IplImage * start
        start = cvLoadImage(filename, 1)
        self.images[0] = start
        for 1 <= i < self.count:
            self.images[i] = cvCreateImage(cvSize(start.width, start.height), start.depth, start.nChannels)
            cvSmooth(start, self.images[i], CV_GAUSSIAN, 21, 21, 0.1+i*0.2,0)

    cdef mk_masks(self):
        cdef CvPoint center
        center.x, center.y = self.images[0].width, self.images[0].height
        for 0 <=i < self.count:
            self.masks[i] = cvCreateImage(cvSize(center.x*2, center.y*2), 8, 1)
            cvZero(self.masks[i])
            cvCircle(self.masks[i], center, (i+1)*self.step, cvScalarAll(255), -1, 8, 0)

    def render(self, x, y):
        a = time()
        w, h = self.images[0].width, self.images[0].height
        if (sqrt((self.lx-x)**2+(self.ly-y)**2)>self.step/2.0):
            x = max(min(w - x, w-1), 0)
            y = max(min(h - y, h-1), 0)
            res = render(self.count, self.surf, self.result, self.images, self.masks, x, y)
            #res = self._render(x, y)
            self.lx, self.ly = x, y
        return (time()-a)*1000

    cdef SDL_Surface * _ipl_to_sdl(self, IplImage * im):
        cdef SDL_Surface * r
        r = SDL_CreateRGBSurfaceFrom(im.imageData, im.width, im.height, 24, im.width*3, self.surf.format.Rmask,  self.surf.format.Gmask, self.surf.format.Bmask, self.surf.format.Amask)
        return r

    cdef long _render(self, int x, int y):
        cdef CvPoint center
        cdef CvRect cent
        cdef SDL_Surface * res_sdl
        cdef IplImage * current
        cdef CvMat mask
        current = self.images[self.count-1]
        cent.x = x/2
        cent.y = y/2
        cent.width = current.width
        cent.height = current.height
        start = time()
        cvCopy(current, self.result, NULL)
        for self.count-1 > i >= 0:
            current = self.images[i]
            cvGetSubRect(self.masks[i], &mask, cent)
            cvCopy(current, self.result, &mask)
        start = (time()-start)*1000
        res_sdl = self._ipl_to_sdl(self.result)
        SDL_BlitSurface(res_sdl, NULL, self.surf, NULL)
        SDL_Flip(self.surf)
        return start

