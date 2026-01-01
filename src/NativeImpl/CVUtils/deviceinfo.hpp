
struct DeviceInfo
{
    struct normal
    {
    };
    struct dml
    {
        int device;
    };
    struct openvino
    {
        std::string device_type;
    };
    std::variant<normal, dml, openvino> info = DeviceInfo::normal{};
};