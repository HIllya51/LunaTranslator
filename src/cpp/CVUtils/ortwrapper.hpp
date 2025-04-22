
// https://zhuanlan.zhihu.com/p/321947743
struct pOnnxSession;
class __declspec(dllexport) OnnxSession
{
public:
    ~OnnxSession();
    OnnxSession(OnnxSession &&rhs);
    OnnxSession &operator=(OnnxSession &&rhs);
    OnnxSession() = delete;
    OnnxSession(const std::wstring &path, int numOfThread = 4);
    std::pair<std::vector<float>, std::vector<int64_t>> RunSession(const std::array<int64_t, 4> &inputShape,
                                                                   std::vector<float> &inputTensorValues);

private:
    std::shared_ptr<pOnnxSession> p_impl;
};
