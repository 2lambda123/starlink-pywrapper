

FFT / BFFT
==========


Purpose
~~~~~~~
Takes the forward FFT of a complex data structure Takes the reverse
FFT of a complex data structure


Description
~~~~~~~~~~~
These Figaro functions take the FFT of the data in a file. FFT
performs a forward transform, BFFT performs an inverse transform. The
input file must contain a complex data structure, i.e. one with
IMAGINARY and DATA components.
The data may be multi-dimensional; if it is, a multi-dimensional FFT
is performed. Note that the Figaro routine R2CMPLX will turn an
existing real data structure into a complex one acceptable to this
routine. FFT does NOT perform any cosine belling or other tapering of
the data, nor does it reduce it to a zero mean.


Usage
~~~~~


::

    
       fft spatial_data frequency_data
       bfft frequency_data spatial_data
       



ADAM parameters
~~~~~~~~~~~~~~~



CDATA = FILE (Read)
```````````````````
CDATA is the name of a complex data structure. Such structures for the
spatial domain are most easily produced using the R2CMPLX command. For
the frequency domain, such data were usually created by R2CMPLX and
transformed by FFT.



OUTPUT = FILE (Write)
`````````````````````
OUTPUT is the name of the resulting Fourier transformed data. If
OUTPUT is the same as CDATA then the transform is performed in situ;
otherwise, a new file is created.



Notes
~~~~~
The fourier transform routines available in the various math libraries
(NAG, IMSL, etc) all have slightly different characteristics, which
show up in the programs that use them. This routine has been written
around the NAG library (mainly the routines C06FAF and C06FJF), so
many of its characteristics may be deduced by reading the relevant
parts of the NAG manuals. In version 5.0 this routine was changed to
use the PDA library, effectively FFTPACK routines. The data is re-
ordered by FFT after the transform so that the zero frequency
component is in the center of the resulting array, and this re-
ordering is reversed by BFFT before the transform. This means that
after FFT has been run, the various axes all go from -N to +N where N
is the Nyquist frequency. New axis data structures that reflect this
are created by FFT and will be deleted by BFFT.


