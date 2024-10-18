#ifndef EBYROID_H
#define EBYROID_H


namespace ebyroid
{

  // forward-declaration to avoid including api_adapter.h
  class ApiAdapter;

  struct ConvertParams
  {
    bool needs_reload;
    char *base_dir;
    char *voice;
    float volume;
  };

  class Ebyroid
  {
  public:
    Ebyroid(const Ebyroid &) = delete;
    Ebyroid(Ebyroid &&) = delete;
    ~Ebyroid();

    static Ebyroid *Create(const std::string &base_dir, const std::string &dllpath, const std::string &voice, float volume, float speed);
    int Hiragana(const unsigned char *inbytes, unsigned char **outbytes, size_t *outsize);
    int Speech(const unsigned char *inbytes, int16_t **outbytes, size_t *outsize, uint32_t mode = 0u);
    int Convert(const ConvertParams &params,
                const unsigned char *inbytes,
                int16_t **outbytes,
                size_t *outsize);

  private:
    Ebyroid(ApiAdapter *api_adapter) : api_adapter_(api_adapter) {}
    ApiAdapter *api_adapter_;
  };

  class Response
  {
  public:
    Response(ApiAdapter *adapter) : api_adapter_(adapter) {}
    void Write(char *bytes, uint32_t size);
    void Write16(int16_t *shorts, uint32_t size);
    std::vector<unsigned char> End();
    std::vector<int16_t> End16();
    ApiAdapter *api_adapter() { return api_adapter_; };

  private:
    ApiAdapter *api_adapter_;
    std::vector<unsigned char> buffer_;
    std::vector<int16_t> buffer_16_;
  };

} // namespace ebyroid

#endif // EBYROID_H
