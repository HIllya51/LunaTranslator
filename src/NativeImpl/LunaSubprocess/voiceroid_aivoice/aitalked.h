#ifndef EBYROID_H
#define EBYROID_H

#include "api_settings.h"
#include "abstract.hpp"
#include "aitalked_func.h"
using ebyroid::ApiAdapter;

struct aitalked : public Abstracttts
{
  aitalked(const Settings &settings);
  virtual std::vector<int16_t> Speech(float _rate, float _pitch, const std::string &text) override;
  virtual ~aitalked() override;
  virtual void setvoice(Settings &settings) override;

private:
  ApiAdapter *api_adapter_;
  std::string lastlang_;
  bool hasloadvoice = false;
  void Setparam(float volume, float speed, float pitch);
  int Hiragana(const char *inbytes, std::vector<char> &);
  int Speech(const char *inbytes, std::vector<int16_t> &, uint32_t mode = 0u);
};

#endif // EBYROID_H
