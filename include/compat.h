#ifndef COMPAT_H
#define COMPAT_H

#if !__MWERKS__
#define __option(x) x
typedef unsigned int wchar_t;
#endif

#endif