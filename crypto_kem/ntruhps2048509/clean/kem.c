#include <stdint.h>

#include "api.h"
#include "fips202.h"
#include "owcpa.h"
#include "params.h"
#include "randombytes.h"
#include "verify.h"

// API FUNCTIONS
int PQCLEAN_NTRUHPS2048509_CLEAN_crypto_kem_keypair(uint8_t *pk, uint8_t *sk) {
    uint8_t seed[NTRU_SAMPLE_FG_BYTES];

    randombytes(seed, NTRU_SAMPLE_FG_BYTES);
    PQCLEAN_NTRUHPS2048509_CLEAN_owcpa_keypair(pk, sk, seed);

    randombytes(sk + NTRU_OWCPA_SECRETKEYBYTES, NTRU_PRFKEYBYTES);

    return 0;
}

int PQCLEAN_NTRUHPS2048509_CLEAN_crypto_kem_enc(uint8_t *c, uint8_t *k, const uint8_t *pk) {
    uint8_t rm[NTRU_OWCPA_MSGBYTES];
    uint8_t rm_seed[NTRU_SAMPLE_RM_BYTES];

    randombytes(rm_seed, NTRU_SAMPLE_RM_BYTES);
    PQCLEAN_NTRUHPS2048509_CLEAN_owcpa_samplemsg(rm, rm_seed);

    sha3_256(k, rm, NTRU_OWCPA_MSGBYTES);

    PQCLEAN_NTRUHPS2048509_CLEAN_owcpa_enc(c, rm, pk);

    return 0;
}

int PQCLEAN_NTRUHPS2048509_CLEAN_crypto_kem_dec(uint8_t *k, const uint8_t *c, const uint8_t *sk) {
    int i, fail;
    uint8_t rm[NTRU_OWCPA_MSGBYTES];
    uint8_t buf[NTRU_PRFKEYBYTES + NTRU_CIPHERTEXTBYTES];
    uint8_t *cmp = buf + NTRU_PRFKEYBYTES;

    fail = PQCLEAN_NTRUHPS2048509_CLEAN_owcpa_dec(rm, c, sk);
    /* If fail = 0 then c = Enc(h, rm), there is no need to re-encapsulate. */
    /* See comment in PQCLEAN_NTRUHPS2048509_CLEAN_owcpa_dec for details.                                */

    sha3_256(k, rm, NTRU_OWCPA_MSGBYTES);

    /* shake(secret PRF key || input ciphertext) */
    for (i = 0; i < NTRU_PRFKEYBYTES; i++) {
        buf[i] = sk[i + NTRU_OWCPA_SECRETKEYBYTES];
    }
    for (i = 0; i < NTRU_CIPHERTEXTBYTES; i++) {
        cmp[i] = c[i];
    }
    sha3_256(rm, cmp, NTRU_CIPHERTEXTBYTES);

    PQCLEAN_NTRUHPS2048509_CLEAN_cmov(k, rm, NTRU_SHAREDKEYBYTES, (unsigned char) fail);

    return 0;
}
