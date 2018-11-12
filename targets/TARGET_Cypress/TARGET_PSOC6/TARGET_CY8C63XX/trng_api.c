#include "trng_api.h"

#if DEVICE_TRNG

/** TRNG HAL structure. trng_s is declared in the target's HAL
 */
#ifdef __cplusplus
extern "C" {
#endif

/**
 * \defgroup hal_trng TRNG hal functions
 * @{
 */

/** Initialize the TRNG peripheral
 *
 * @param obj The TRNG object
 */
void trng_init(trng_t *obj)
{
    (void)(obj);
}

/** Deinitialize the TRNG peripheral
 *
 * @param obj The TRNG object
 */
void trng_free(trng_t *obj)
{
    (void)(obj);
}

/** Get random data from TRNG peripheral
 *
 * @param obj The TRNG object
 * @param output The pointer to an output array
 * @param length The size of output data, to avoid buffer overwrite
 * @param output_length The length of generated data
 * @return 0 success, -1 fail
 */
int trng_get_bytes(trng_t *obj, uint8_t *output, size_t length, size_t *output_length)
{
    uint8_t s = 0;
    for (size_t i = 0; i < length; i++) {
        output[i] = s++;
    }

    *output_length = length;
    return 0;
}

/**@}*/

#ifdef __cplusplus
}
#endif

#endif
