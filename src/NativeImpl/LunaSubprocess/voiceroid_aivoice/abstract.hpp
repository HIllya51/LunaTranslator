#pragma once

struct Abstracttts
{
    virtual std::vector<int16_t> Speech(float _rate, float _pitch, const std::string &text) = 0;
    virtual ~Abstracttts() = default;
    virtual void setvoice(Settings& settings) = 0;
};