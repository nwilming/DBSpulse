
long render(int count, SDL_Surface * surf, IplImage * result, IplImage * images[], IplImage * masks[], int x, int y)
{
        CvPoint center;
        CvRect cent;
        SDL_Surface * res_sdl;
        IplImage * current;
        CvMat mask;
		int i;
        current = images[count-1];
        cent.x = x;
        cent.y = y;
        cent.width = current->width;
        cent.height = current->height;
        cvCopy(current, result, NULL);
        for (i=count-2; i >= 0; i--)
		{
            current = images[i];
            cvGetSubRect(masks[i], &mask, cent);
            cvCopy(current, result, &mask);
		}
        res_sdl  = SDL_CreateRGBSurfaceFrom(result->imageData, result->width, result->height, 24, result->width*3, surf->format->Rmask,  surf->format->Gmask, surf->format->Bmask, surf->format->Amask);
        SDL_BlitSurface(res_sdl, NULL, surf, NULL);
        SDL_Flip(surf);
}
