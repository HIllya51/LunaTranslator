
// https://zhuanlan.zhihu.com/p/321947743
struct pOnnxSession;
class OnnxSession
{
public:
    ~OnnxSession();
    OnnxSession(OnnxSession &&rhs);
    OnnxSession &operator=(OnnxSession &&rhs);
    OnnxSession() = delete;
    OnnxSession(const std::wstring &path, int numOfThread = 4, bool gpu = false, int device = 0);
    std::pair<std::vector<float>, std::vector<int64_t>> RunSession(const std::array<int64_t, 4> &inputShape,
                                                                   std::vector<float> &inputTensorValues);

private:
    std::unique_ptr<pOnnxSession> p_impl;
};
std::vector<std::string> OrtGetAvailableProviders();
bool isDMLAvailable();
void *getOrtSessionOptionsAppendExecutionProvider_DML();
void _InitApi();