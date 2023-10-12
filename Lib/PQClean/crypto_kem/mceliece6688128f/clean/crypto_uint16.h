#ifndef PQCLEAN_MCELIECE6688128F_CLEAN_crypto_uint16_h
#define PQCLEAN_MCELIECE6688128F_CLEAN_crypto_uint16_h

#include <inttypes.h>
typedef uint16_t crypto_uint16;

typedef int16_t crypto_uint16_signed;

#include "namespace.h"

#define crypto_uint16_signed_negative_mask CRYPTO_NAMESPACE(crypto_uint16_signed_negative_mask)
crypto_uint16_signed crypto_uint16_signed_negative_mask(crypto_uint16_signed crypto_uint16_signed_x);
#define crypto_uint16_nonzero_mask CRYPTO_NAMESPACE(crypto_uint16_nonzero_mask)
crypto_uint16 crypto_uint16_nonzero_mask(crypto_uint16 crypto_uint16_x);
#define crypto_uint16_zero_mask CRYPTO_NAMESPACE(crypto_uint16_zero_mask)
crypto_uint16 crypto_uint16_zero_mask(crypto_uint16 crypto_uint16_x);
#define crypto_uint16_unequal_mask CRYPTO_NAMESPACE(crypto_uint16_unequal_mask)
crypto_uint16 crypto_uint16_unequal_mask(crypto_uint16 crypto_uint16_x, crypto_uint16 crypto_uint16_y);
#define crypto_uint16_equal_mask CRYPTO_NAMESPACE(crypto_uint16_equal_mask)
crypto_uint16 crypto_uint16_equal_mask(crypto_uint16 crypto_uint16_x, crypto_uint16 crypto_uint16_y);
#define crypto_uint16_smaller_mask CRYPTO_NAMESPACE(crypto_uint16_smaller_mask)
crypto_uint16 crypto_uint16_smaller_mask(crypto_uint16 crypto_uint16_x, crypto_uint16 crypto_uint16_y);
#define crypto_uint16_min CRYPTO_NAMESPACE(crypto_uint16_min)
crypto_uint16 crypto_uint16_min(crypto_uint16 crypto_uint16_x, crypto_uint16 crypto_uint16_y);
#define crypto_uint16_max CRYPTO_NAMESPACE(crypto_uint16_max)
crypto_uint16 crypto_uint16_max(crypto_uint16 crypto_uint16_x, crypto_uint16 crypto_uint16_y);
#define crypto_uint16_minmax CRYPTO_NAMESPACE(crypto_uint16_minmax)
void crypto_uint16_minmax(crypto_uint16 *crypto_uint16_a, crypto_uint16 *crypto_uint16_b);

#endif
