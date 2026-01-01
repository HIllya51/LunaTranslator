#include "ortwrapper.hpp"
// https://github.com/microsoft/onnxruntime/issues/3172#issuecomment-682193911
#define ORT_API_MANUAL_INIT
#include <onnxruntime_cxx_api.h>

#define get_provider_ptr(T)                                                                 \
    []() -> void *                                                                          \
    {                                                                                       \
        auto ort = GetModuleHandle(L"onnxruntime.dll");                                     \
        if (!ort)                                                                           \
            return nullptr;                                                                 \
        return (void *)GetProcAddress(ort, "OrtSessionOptionsAppendExecutionProvider_" #T); \
    }()

#ifdef WIN10ABOVE
#include <dml_provider_factory.h>
#else
ORT_API_STATUS(OrtSessionOptionsAppendExecutionProvider_DML, _In_ OrtSessionOptions *options, int device_id)
{
    auto pOrtSessionOptionsAppendExecutionProvider_DML = (decltype(&OrtSessionOptionsAppendExecutionProvider_DML))get_provider_ptr(DML);
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

ORT_API_STATUS(OrtSessionOptionsAppendExecutionProvider_OpenVINO, _In_ OrtSessionOptions *options, _In_ const char *device_type)
{
    auto p = (decltype(&OrtSessionOptionsAppendExecutionProvider_OpenVINO))get_provider_ptr(OpenVINO);
    if (!p)
        return nullptr;
    return p(options, device_type);
}

static bool __isDMLAvailable()
{
    if (!get_provider_ptr(DML))
        return false;
    if (GetModuleHandle(L"DirectML.dll"))
        return true;
    WCHAR path[MAX_PATH];
    GetModuleFileNameW(GetModuleHandle(L"onnxruntime.dll"), path, MAX_PATH);
    auto currdir = std::filesystem::path(path).parent_path();
    return LoadLibrary((currdir / L"DirectML.dll").wstring().c_str()) ||
           LoadLibrary(L"DirectML.dll");
}
static bool __isOpenVINOAvailableLAvailable()
{
    if (!get_provider_ptr(OpenVINO))
        return false;
    if (GetModuleHandle(L"openvino.dll"))
        return true;
    WCHAR path[MAX_PATH];
    GetModuleFileNameW(GetModuleHandle(L"onnxruntime.dll"), path, MAX_PATH);
    auto currdir = std::filesystem::path(path).parent_path();
    return LoadLibrary((currdir / L"tbb12.dll").wstring().c_str()) &&
           LoadLibrary((currdir / L"openvino.dll").wstring().c_str());
}
bool isDMLAvailable()
{
    static bool __ = __isDMLAvailable();
    return __;
}
bool isOpenVINOAvailable()
{
    static bool __ = __isOpenVINOAvailableLAvailable();
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
    bool is_using_gpu = false;
    std::mutex gpu_run_lock;

public:
    pOnnxSession(const std::wstring &path, int numOfThread, const DeviceInfo &info)
    {
        auto visitf = [&](auto &&info)
        {
            using T = std::decay_t<decltype(info)>;
            if constexpr (std::is_same_v<T, DeviceInfo::dml>)
            {
                try
                {
                    Ort::ThrowOnError(OrtSessionOptionsAppendExecutionProvider_DML(sessionOptions, info.device));
                    // 失败返回err=66，但没有errmsg，会回退到cpu，不要报错。
                    is_using_gpu = true;
                }
                catch (std::exception &e)
                {
                    std::cout << e.what() << std::endl;
                }
            }
            else if constexpr (std::is_same_v<T, DeviceInfo::openvino>)
            {
                // https://docs.openvino.ai/2024/openvino-workflow/running-inference/inference-devices-and-modes/cpu-device.html
                try
                {
                    Ort::ThrowOnError(OrtSessionOptionsAppendExecutionProvider_OpenVINO(sessionOptions, info.device_type.c_str()));
                }
                catch (std::exception &e)
                {
                    std::cout << e.what() << std::endl;
                }
            }
            else if constexpr (std::is_same_v<T, DeviceInfo::normal>)
            {
            }
        };
        std::visit(visitf, info.info);

        sessionOptions.SetIntraOpNumThreads(numOfThread);
        sessionOptions.SetInterOpNumThreads(numOfThread);
        if (is_using_gpu)
        {
            // https://onnxruntime.ai/docs/execution-providers/DirectML-ExecutionProvider.html
            // If creating the onnxruntime InferenceSession object directly, you must set the appropriate fields on the onnxruntime::SessionOptions struct. Specifically, execution_mode must be set to ExecutionMode::ORT_SEQUENTIAL, and enable_mem_pattern must be false.
            sessionOptions.SetExecutionMode(ExecutionMode::ORT_PARALLEL);
            sessionOptions.DisableMemPattern();
        }
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
        std::vector<Ort::Value> outputTensor;
        {
            // https://onnxruntime.ai/docs/execution-providers/DirectML-ExecutionProvider.html
            // Additionally, as the DirectML execution provider does not support parallel execution, it does not support multi-threaded calls to Run on the same inference session. That is, if an inference session using the DirectML execution provider, only one thread may call Run at a time. Multiple threads are permitted to call Run simultaneously if they operate on different inference session objects.
            std::unique_lock lock(gpu_run_lock, std::defer_lock);
            if (is_using_gpu)
                lock.lock();
            outputTensor = session->Run(Ort::RunOptions{nullptr}, inputNames.data(), &inputTensor,
                                        inputNames.size(), outputNames.data(), outputNames.size());
        }
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
OnnxSession::OnnxSession(const std::wstring &path, int numOfThread, const DeviceInfo &info)
{
    p_impl = std::make_unique<pOnnxSession>(path, numOfThread, info);
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