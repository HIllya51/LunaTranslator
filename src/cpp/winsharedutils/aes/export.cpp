#include "aes.hpp"
DECLARE_API void AES_decrypt(uint8_t *key, uint8_t *iv, uint8_t *ptr, size_t size)
{
    AES_ctx ctx;
    AES_init_ctx_iv(&ctx, key, iv);
    AES_CBC_decrypt_buffer(&ctx, ptr, size);
}