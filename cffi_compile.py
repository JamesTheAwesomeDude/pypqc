from cffi import FFI

from distutils.sysconfig import parse_makefile
import hashlib
import os
from pathlib import Path, PurePosixPath
import platform
import re


_IS_WINDOWS = (platform.system() == 'Windows')
_IS_x86_64 = (platform.machine() == 'AMD64')
_IS_x86 = (platform.machine() in {'i386', 'i686', 'x86'})
_IN_x86_64_VSCMD = ('x64' == os.environ.get('VSCMD_ARG_TGT_ARCH'))
_IN_x86_VSCMD = ('x32' == os.environ.get('VSCMD_ARG_TGT_ARCH'))
if (_IS_WINDOWS) and (((_IS_x86_64) and (not _IN_x86_64_VSCMD)) or ((_IS_x86) and (not _IN_x86_VSCMD))):
	# Painful-to-debug problems for the caller arise if this is neglected
	raise AssertionError("Call this script from *within* \"Developer Command Prompt for VS 2022\"\nhttps://visualstudio.microsoft.com/visual-cpp-build-tools/")


_CDEF_EXTRA = """
extern "Python+C" {
	void shake256(
		uint8_t *output,
		size_t outlen,
		const uint8_t *input,
		size_t inlen
	);

	int PQCLEAN_randombytes(
		uint8_t *output,
		size_t n
	);

	void sha512(
		uint8_t *out,
		const uint8_t *in,
		size_t inlen
	);
}"""

_CDEF_RE = re.compile(r'(?ms)^\s*(#define\s+\w+ \d+|\w[\w ]*\s(\w+)\s*\(.*?\);)$')
_NAMESPACE_RE = re.compile(r'(?ms)^#define\s+(CRYPTO_NAMESPACE)\s*\(\s*(\w+)\s*\)\s+(\w+)\s+##\s*\2\s*$')
_NAMESPACED_RE = re.compile(r'(?ms)^#define\s+(\w+)\s+CRYPTO_NAMESPACE\s*\(\s*\1\s*\)\s*$')


def _main(src='Lib/PQClean'):
	src = Path(src)
	COMMON_INCLUDE = src / 'common'
	for kem_alg_src in (src / 'crypto_kem').iterdir():
		alg_name = kem_alg_src.name
		if alg_name.startswith('hqc-rmrs'):
			continue  # TODO
		if alg_name.startswith('kyber'):
			continue  # TODO needs miscellaneous shake256_* suite functions

		for BUILD_ROOT in (p for p in kem_alg_src.iterdir() if p.is_dir()):
			variant = BUILD_ROOT.name
			if variant == 'clean':
				variant = None

			if variant == 'avx2':
				continue  # TODO this raises "too few actual parameters for intrinsic function"

			if variant == 'aarch64':
				continue  # TODO figure out cross-compiling

			if alg_name.startswith('mceliece'):
				if alg_name.endswith('f'):
					# "fast" key generation
					alg_name = alg_name[:-1]
				else:
					# "simple" key generation
					# (unclear if this has any
					# use beyond the existence
					# of the source code itself)
					variant = f'{f"{variant}_" if variant else ""}ref'

			module_name = f'pqc.kem._{alg_name}{f"_{variant}" if variant else ""}'

			extra_compile_args = []
			if _IS_WINDOWS:
				# https://foss.heptapod.net/pypy/cffi/-/issues/516
				# https://www.reddit.com/r/learnpython/comments/175js2u/def_extern_says_im_not_using_it_in_api_mode/
				# https://learn.microsoft.com/en-us/cpp/build/reference/tc-tp-tc-tp-specify-source-file-type?view=msvc-170
				extra_compile_args.append('/TC')

			ffibuilder = FFI()

			namespace = _NAMESPACE_RE.search((BUILD_ROOT / 'namespace.h').read_text()).group(3)

			# PQClean-provided interface
			ffibuilder.cdef(fr"""
				const char {namespace}CRYPTO_ALGNAME[...];
				int {namespace}pk_gen(unsigned char *pk, unsigned char *sk, const uint32_t *perm, int16_t *pi, uint64_t *pivots);
				void {namespace}encrypt(unsigned char *s, const unsigned char *pk, unsigned char *e);
				int {namespace}decrypt(unsigned char *e, const unsigned char *sk, const unsigned char *c);
				int {namespace}crypto_kem_keypair(unsigned char *pk, unsigned char *sk);
				int {namespace}crypto_kem_enc(unsigned char *c, unsigned char *key, const unsigned char *pk);
				int {namespace}crypto_kem_dec(unsigned char *key, const unsigned char *c, const unsigned char *sk);
			""")

			# Our internal interface
			ffibuilder.cdef(fr"""
				const char _NAMESPACE[...];
				typedef uint8_t _{namespace}CRYPTO_SECRETKEY[...];
				typedef uint8_t _{namespace}CRYPTO_PUBLICKEY[...];
				typedef uint8_t _{namespace}CRYPTO_KEM_PLAINTEXT[...];
				typedef uint8_t _{namespace}CRYPTO_KEM_CIPHERTEXT[...];
			""")
			bonus_csource = fr"""
				typedef uint8_t _{namespace}CRYPTO_SECRETKEY[{namespace}CRYPTO_SECRETKEYBYTES];
				typedef uint8_t _{namespace}CRYPTO_PUBLICKEY[{namespace}CRYPTO_PUBLICKEYBYTES];
				typedef uint8_t _{namespace}CRYPTO_KEM_PLAINTEXT[{namespace}CRYPTO_BYTES];
				typedef uint8_t _{namespace}CRYPTO_KEM_CIPHERTEXT[{namespace}CRYPTO_CIPHERTEXTBYTES];
			"""

			# Our injected dependencies
			ffibuilder.cdef(_CDEF_EXTRA)

			# PQClean McEliece-specific
			ffibuilder.cdef(fr"""
				const int GFBITS;
				const int SYS_N;
				const int SYS_T;
			""")

			# Actual source
			object_names = parse_makefile(BUILD_ROOT / 'Makefile')['OBJECTS'].split()
			object_names = [fn for fn in object_names if not fn.startswith('aes')]  # Not sure why this is necessary
			objects = [(BUILD_ROOT / fn) for fn in object_names]
			sources = [str(p.with_suffix('.c')) for p in objects]

			include = [COMMON_INCLUDE, (BUILD_ROOT / 'api.h'), (BUILD_ROOT / 'params.h')]
			include_h = '\n'.join(f'#include "{p.name}"' for p in include if not p.is_dir())
			include_dirs = list({PurePosixPath(p.parent if not p.is_dir() else p) for p in include})

			ffibuilder.set_source(module_name, fr"""
				{include_h}
				// low-priority semantics quibble: escaping
				// https://stackoverflow.com/posts/comments/136533801
				static const char _NAMESPACE[] = "{namespace}";
				{bonus_csource}
				""",
				include_dirs=include_dirs,
				sources=sources,
				extra_compile_args=extra_compile_args
			)

			yield ffibuilder

	for sign_alg_src in (src / 'crypto_sign').iterdir():
		continue  # TODO


def main():
	for ffibuilder in _main():
		# TODO https://github.com/python-cffi/cffi/pull/30.diff
		ffibuilder.compile(verbose=True)


def _setuptools_thing():
	# HOW THE HECK IS THIS SUPPOSED TO WORK
	# I DON'T GET THIS INTERFACE AT ALL
	# WHY CAN'T I RETURN A LIST??? :(
	for ffibuilder in _main():
		if ffibuilder._assigned_source[0] == 'pqc.kem._mceliece6960119':
			print("RETURNING", ffibuilder)
			return ffibuilder
	else:
		raise RuntimeError()



if __name__ == "__main__":
	main()
