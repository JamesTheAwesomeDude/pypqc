from cffi import FFI

from distutils.sysconfig import parse_makefile
from pathlib import Path
import platform
import re
from textwrap import dedent

from pqc._util import partition_list, map_immed, fix_compile_args

_NAMESPACE_RE = re.compile(r'(?ms)^#define\s+(CRYPTO_NAMESPACE)\s*\(\s*(\w+)\s*\)\s+(\w+)\s+##\s*\2\s*$')

def make_ffi(build_root, *, parent_module='pqc._lib'):
	build_root = Path(build_root)
	makefile_parsed = parse_makefile(build_root / 'Makefile')
	common_dir = build_root / '..' / '..' / '..' / 'common'

	lib_name = Path(makefile_parsed['LIB']).stem
	assert lib_name.startswith('libmceliece')
	module_name = f'{parent_module}.{lib_name}'
	namespace = _NAMESPACE_RE.search((build_root / 'namespace.h').read_text()).group(3)

	included_ffis = []
	extra_compile_args = []
	libraries = []
	c_header_sources = []
	cdefs = []


	source_names = makefile_parsed['SOURCES'].split()
	source_names.remove('aes256ctr.c')  # Upstream test infrastructure
	sources, extra_objects = partition_list(
	    lambda p: p.suffix == '.c',
	    ((build_root / fn) for fn in source_names)
	)

	include = [(common_dir), (build_root / 'api.h'), (build_root / 'params.h')]
	include_h = [p.name for p in include if not p.is_dir()]
	include_dirs = list({(p.parent if not p.is_dir() else p) for p in include})

	cdefs.append(dedent(f"""\
	static const char {namespace}CRYPTO_ALGNAME[...];
	int {namespace}crypto_kem_keypair(unsigned char *pk, unsigned char *sk);
	int {namespace}crypto_kem_enc(unsigned char *c, unsigned char *key, const unsigned char *pk);
	int {namespace}crypto_kem_dec(unsigned char *key, const unsigned char *c, const unsigned char *sk);
	"""))

	c_header_sources.extend(f'#include "{h}"' for h in include_h)

	cdefs.append(dedent(f"""\
	// Site interface
	static const char _NAMESPACE[...];
	typedef uint8_t {namespace}crypto_secretkey[...];
	typedef uint8_t {namespace}crypto_publickey[...];
	typedef uint8_t {namespace}crypto_kem_plaintext[...];
	typedef uint8_t {namespace}crypto_kem_ciphertext[...];
	#define GFBITS ...
	#define SYS_N ...
	#define SYS_T ...
	"""))

	c_header_sources.append(dedent(f"""\
	// Site interface
	static const char _NAMESPACE[] = "{namespace}";
	typedef uint8_t {namespace}crypto_secretkey[{namespace}CRYPTO_SECRETKEYBYTES];
	typedef uint8_t {namespace}crypto_publickey[{namespace}CRYPTO_PUBLICKEYBYTES];
	typedef uint8_t {namespace}crypto_kem_plaintext[{namespace}CRYPTO_BYTES];
	typedef uint8_t {namespace}crypto_kem_ciphertext[{namespace}CRYPTO_CIPHERTEXTBYTES];
	"""))


	sources.append((common_dir / 'fips202.c'))
	sources.append((common_dir / 'randombytes.c'))


	ffibuilder = FFI()
	map_immed(ffibuilder.include, included_ffis)
	map_immed(ffibuilder.cdef, cdefs)
	fix_compile_args(extra_compile_args)
	ffibuilder.set_source(
		module_name,
		'\n'.join(c_header_sources),
		sources=[p.as_posix() for p in sources],
		include_dirs=[p.as_posix() for p in include_dirs],
		extra_objects=extra_objects,
		extra_compile_args=extra_compile_args,
		libraries=libraries,
	)
	return ffibuilder
