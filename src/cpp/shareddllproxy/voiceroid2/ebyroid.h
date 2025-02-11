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

    static Ebyroid *Create(const std::string &base_dir, const std::string &dllpath, const std::string &voice, const std::string &Lang);
    int Hiragana(const char *inbytes, std::vector<char> &);
    int Speech(const char *inbytes, std::vector<int16_t> &, uint32_t mode = 0u);

  private:
    Ebyroid(ApiAdapter *api_adapter) : api_adapter_(api_adapter) {}
    ApiAdapter *api_adapter_;

  public:
    void Setparam(float volume, float speed, float pitch);
  };

  template <typename T>
  class Response
  {
  public:
    Response(ApiAdapter *adapter) : api_adapter_(adapter)
    {
      event.Create(NULL, FALSE, FALSE, NULL);
    }
    void Write(T *bytes, size_t size)
    {
      buffer_.insert(std::end(buffer_), bytes, bytes + size);
    }
    std::vector<T> End()
    {
      return std::move(buffer_);
    }
    ApiAdapter *api_adapter() { return api_adapter_; };
    CEvent event;

  private:
    ApiAdapter *api_adapter_;
    std::vector<T> buffer_;
  };

} // namespace ebyroid

#endif // EBYROID_H
