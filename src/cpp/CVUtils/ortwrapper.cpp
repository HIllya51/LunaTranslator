#include "ortwrapper.hpp"
// https://github.com/microsoft/onnxruntime/issues/3172#issuecomment-682193911
#define ORT_API_MANUAL_INIT
#include <onnxruntime_cxx_api.h>
#ifdef WIN10ABOVE
#include <dml_provider_factory.h>
#else
ORT_API_STATUS(OrtSessionOptionsAppendExecutionProvider_DML, _In_ OrtSessionOptions *options, int device_id)
{
    auto pOrtSessionOptionsAppendExecutionProvider_DML = (decltype(&OrtSessionOptionsAppendExecutionProvider_DML))getOrtSessionOptionsAppendExecutionProvider_DML();
    if (!pOrtSessionOptionsAppendExecutionProvider_DML)
        return nullptr;
    return pOrtSessionOptionsAppendExecutionProvider_DML(options, device_id);
}
#endif
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
void *getOrtSessionOptionsAppendExecutionProvider_DML()
{
    auto ort = GetModuleHandle(L"onnxruntime.dll");
    if (!ort)
        return nullptr;
    return GetProcAddress(ort, "OrtSessionOptionsAppendExecutionProvider_DML");
}
static bool __isDMLAvailable()
{
    if (!getOrtSessionOptionsAppendExecutionProvider_DML())
        return false;
    if (GetModuleHandle(L"DirectML.dll"))
        return true;
    WCHAR path[MAX_PATH];
    GetModuleFileNameW(GetModuleHandle(L"onnxruntime.dll"), path, MAX_PATH);
    auto currdir = std::filesystem::path(path).parent_path();
    auto mydml = (currdir / L"DirectML.dll").wstring();
    return LoadLibrary(mydml.c_str()) || LoadLibrary(L"DirectML.dll");
}
bool isDMLAvailable()
{
    static bool __ = __isDMLAvailable();
    return __;
}
class pOnnxSession
{
    std::vector<STRINGT> inputNamesPtr;
    std::vector<STRINGT> outputNamesPtr;
    std::unique_ptr<Ort::Session> session;
    Ort::Env env = Ort::Env(ORT_LOGGING_LEVEL_ERROR);
    Ort::SessionOptions sessionOptions = Ort::SessionOptions();

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
    pOnnxSession(const std::wstring &path, int numOfThread, bool gpu, int device)
    {
        if (gpu && isDMLAvailable())
            Ort::ThrowOnError(OrtSessionOptionsAppendExecutionProvider_DML(sessionOptions, device));
        sessionOptions.SetIntraOpNumThreads(numOfThread);
        sessionOptions.SetInterOpNumThreads(numOfThread); // 需要SetExecutionMode(ExecutionMode::ORT_PARALLEL)(默认即是)。这个好像对当前这个ocr模型没啥卵用
        sessionOptions.SetGraphOptimizationLevel(GraphOptimizationLevel::ORT_ENABLE_ALL);
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
OnnxSession::OnnxSession(const std::wstring &path, int numOfThread, bool gpu, int device)
{
    p_impl = std::make_unique<pOnnxSession>(path, numOfThread, gpu, device);
}
std::pair<std::vector<float>, std::vector<int64_t>> OnnxSession::RunSession(const std::array<int64_t, 4> &inputShape,
                                                                            std::vector<float> &inputTensorValues)
{
    return p_impl->RunSession(inputShape, inputTensorValues);
}

std::vector<std::string> OrtGetAvailableProviders()
{
    try
    {
        return Ort::GetAvailableProviders();
    }
    catch (std::exception &e)
    {
        std::cout << e.what() << std::endl;
        return {};
    }
}
void _InitApi()
{
    Ort::InitApi();
}