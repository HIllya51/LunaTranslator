#include "ortwrapper.hpp"
#include <onnxruntime_cxx_api.h>
#if ORT_API_VERSION <= 10
#define STRINGT const char *
#define FGetInputName GetInputName
#define FGetOutputName GetOutputName
#define GetVector(X) X
#else
#define STRINGT Ort::AllocatedStringPtr
#define FGetInputName GetInputNameAllocated
#define FGetOutputName GetOutputNameAllocated
#define GetVector(X) {X.data()->get()}
#endif

BOOL APIENTRY DllMain(HMODULE hModule,
                      DWORD ul_reason_for_call,
                      LPVOID lpReserved)
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
    {
        for (auto &&s : Ort::GetAvailableProviders())
        {
            std::cout << s << "\n";
        }
    }
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}

class pOnnxSession
{
    std::vector<STRINGT> inputNamesPtr;
    std::vector<STRINGT> outputNamesPtr;
    std::unique_ptr<Ort::Session> session;
    Ort::Env env = Ort::Env(ORT_LOGGING_LEVEL_ERROR);
    Ort::SessionOptions sessionOptions = Ort::SessionOptions();

    void setNumThread(int numOfThread)
    {
        sessionOptions.SetInterOpNumThreads(numOfThread);
        sessionOptions.SetGraphOptimizationLevel(GraphOptimizationLevel::ORT_ENABLE_EXTENDED);
    }

    template <typename T, typename Func, typename Func2>
    void getinputoutputNames(T &vec, Func func, Func2 func2)
    {
        Ort::AllocatorWithDefaultOptions allocator;
        const size_t numInputNodes = ((*session.get()).*func)();
        vec.reserve(numInputNodes);
        std::vector<int64_t> input_node_dims;

        for (size_t i = 0; i < numInputNodes; i++)
        {
            auto inputName = ((*session.get()).*func2)(i, allocator);
            vec.push_back(std::move(inputName));
        }
    }

public:
    pOnnxSession(const std::wstring &path, int numOfThread)
    {
        setNumThread(numOfThread);
        session = std::make_unique<Ort::Session>(env, path.c_str(), sessionOptions);
        getinputoutputNames(inputNamesPtr, &Ort::Session::GetInputCount, &Ort::Session::FGetInputName);
        getinputoutputNames(outputNamesPtr, &Ort::Session::GetOutputCount, &Ort::Session::FGetOutputName);
    }

    std::pair<std::vector<float>, std::vector<int64_t>> RunSession(const std::array<int64_t, 4> &inputShape,
                                                                   std::vector<float> &inputTensorValues)
    {
        auto memoryInfo = Ort::MemoryInfo::CreateCpu(OrtDeviceAllocator, OrtMemTypeCPU);
        Ort::Value inputTensor = Ort::Value::CreateTensor<float>(memoryInfo, inputTensorValues.data(),
                                                                 inputTensorValues.size(), inputShape.data(),
                                                                 inputShape.size());
        assert(inputTensor.IsTensor());
        std::vector<const char *> inputNames = GetVector(inputNamesPtr);
        std::vector<const char *> outputNames = GetVector(outputNamesPtr);
        auto outputTensor = session->Run(Ort::RunOptions{nullptr}, inputNames.data(), &inputTensor,
                                         inputNames.size(), outputNames.data(), outputNames.size());
        assert(outputTensor.size() == 1 && outputTensor.front().IsTensor());
        std::vector<int64_t> outputShape = outputTensor[0].GetTensorTypeAndShapeInfo().GetShape();
        auto outputCount = outputTensor.front().GetTensorTypeAndShapeInfo().GetElementCount();
        float *floatArray = outputTensor.front().GetTensorMutableData<float>();
        std::vector<float> outputData(floatArray, floatArray + outputCount);
        return {outputData, outputShape};
    }
};
OnnxSession::OnnxSession(OnnxSession &&rhs) = default;
OnnxSession &OnnxSession::operator=(OnnxSession &&rhs) = default;
OnnxSession::~OnnxSession() = default;
OnnxSession::OnnxSession(const std::wstring &path, int numOfThread)
{
    p_impl = std::make_unique<pOnnxSession>(path, numOfThread);
}
std::pair<std::vector<float>, std::vector<int64_t>> OnnxSession::RunSession(const std::array<int64_t, 4> &inputShape,
                                                                            std::vector<float> &inputTensorValues)
{
    return p_impl->RunSession(inputShape, inputTensorValues);
}