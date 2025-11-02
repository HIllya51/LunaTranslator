void _glens_create_request(uint64_t uuid, const char *analytics_id, size_t size1, const char *bytes, size_t size, int32_t width, int32_t height, void (*cb)(const char *, size_t));
void _glens_parse_response(const char *data, size_t size, void (*cb)(const char *, float, float, float, float));

DECLARE_API void glens_create_request(uint64_t uuid, const char *analytics_id, size_t size1, const char *bytes, size_t size, int32_t width, int32_t height, void (*cb)(const char *, size_t))
{
    _glens_create_request(uuid, analytics_id, size1, bytes, size, width, height, cb);
}
DECLARE_API void glens_parse_response(const char *data, size_t size, void (*cb)(const char *, float, float, float, float))
{
    _glens_parse_response(data, size, cb);
}