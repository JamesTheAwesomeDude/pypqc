from ._sign_cffi_maker import make_sign_ffi
from textwrap import dedent

def make_dilithium_ffi(build_root):
	common_sources = ['fips202.c', 'randombytes.c']

	extra_cdefs = [dedent("""\
	// Exposed internal interface
	#define CRHBYTES ...
	#define RNDBYTES ...
	#define N ...
	#define Q ...
	#define D ...
	#define ROOT_OF_UNITY ...
	#define K ...
	#define L ...
	#define ETA ...
	#define TAU ...
	#define BETA ...
	#define GAMMA1 ...
	#define GAMMA2 ...
	#define OMEGA ...
	#define CTILDEBYTES ...
	""")]

	extra_c_header_sources = [dedent("""\
	// Exposed internal interface
	#include "params.h"
	""")]

	return make_sign_ffi(build_root=build_root, extra_c_header_sources=extra_c_header_sources, extra_cdefs=extra_cdefs, common_sources=common_sources)
