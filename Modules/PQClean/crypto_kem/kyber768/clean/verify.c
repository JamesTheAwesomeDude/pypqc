#include "verify.h"
#include <stddef.h>
#include <stdint.h>

/*************************************************
* Name:        PQCLEAN_KYBER768_CLEAN_verify
*
* Description: Compare two arrays for equality in constant time.
*
* Arguments:   const uint8_t *a: pointer to first byte array
*              const uint8_t *b: pointer to second byte array
*              size_t len:       length of the byte arrays
*
* Returns 0 if the byte arrays are equal, 1 otherwise
**************************************************/
int PQCLEAN_KYBER768_CLEAN_verify(const uint8_t *a, const uint8_t *b, size_t len) {
    size_t i;
    uint8_t r = 0;

    for (i = 0; i < len; i++) {
        r |= a[i] ^ b[i];
    }

    return (-(uint64_t)r) >> 63;
}

/*************************************************
* Name:        PQCLEAN_KYBER768_CLEAN_cmov
*
* Description: Copy len bytes from x to r if b is 1;
*              don't modify x if b is 0. Requires b to be in {0,1};
*              assumes two's complement representation of negative integers.
*              Runs in constant time.
*
* Arguments:   uint8_t *r:       pointer to output byte array
*              const uint8_t *x: pointer to input byte array
*              size_t len:       Amount of bytes to be copied
*              uint8_t b:        Condition bit; has to be in {0,1}
**************************************************/
void PQCLEAN_KYBER768_CLEAN_cmov(uint8_t *r, const uint8_t *x, size_t len, uint8_t b) {
    size_t i;

    b = -b;
    for (i = 0; i < len; i++) {
        r[i] ^= b & (r[i] ^ x[i]);
    }
}

/*************************************************
* Name:        PQCLEAN_KYBER768_CLEAN_cmov_int16
*
* Description: Copy 16 bits from v to r if b is 1;
*              don't modify v if b is 0. Requires b to be in {0,1};
*              assumes two's complement representation of negative integers.
*              Runs in constant time.
*
* Arguments:   uint16_t *r:      pointer to output byte array
*              uint16_t v:       pointer to input byte array
*              uint16_t b:       Condition bit; has to be in {0,1}
**************************************************/
void PQCLEAN_KYBER768_CLEAN_cmov_int16(int16_t *r, int16_t v, uint16_t b) {
  b = -b;
  *r ^= b & ((*r) ^ v);
}
