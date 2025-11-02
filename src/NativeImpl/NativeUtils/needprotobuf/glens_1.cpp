#include <lens_overlay_server.pb.h>
#include <lens_overlay_platform.pb.h>
#include <lens_overlay_filters.pb.h>
#include <lens_overlay_service_deps.pb.h>
using namespace lens;

void _glens_create_request(uint64_t uuid, const char *analytics_id, size_t size1, const char *bytes, size_t size, int32_t width, int32_t height, void (*cb)(const char *, size_t))
{
    LensOverlayServerRequest request;
    request.mutable_objects_request()->mutable_request_context()->mutable_request_id()->set_uuid(uuid);
    request.mutable_objects_request()->mutable_request_context()->mutable_request_id()->set_sequence_id(0);
    request.mutable_objects_request()->mutable_request_context()->mutable_request_id()->set_image_sequence_id(0);
    request.mutable_objects_request()->mutable_request_context()->mutable_request_id()->set_analytics_id(analytics_id, size1);

    request.mutable_objects_request()->mutable_request_context()->mutable_client_context()->set_platform(Platform::PLATFORM_WEB);
    request.mutable_objects_request()->mutable_request_context()->mutable_client_context()->set_surface(Surface::SURFACE_CHROMIUM);
    request.mutable_objects_request()->mutable_request_context()->mutable_client_context()->mutable_locale_context()->set_time_zone("");
    request.mutable_objects_request()->mutable_request_context()->mutable_client_context()->set_app_id("");
    request.mutable_objects_request()->mutable_request_context()->mutable_client_context()->mutable_client_filters()->add_filter()->set_filter_type(LensOverlayFilterType::AUTO_FILTER);

    request.mutable_objects_request()->mutable_image_data()->mutable_payload()->set_image_bytes(bytes, size);
    request.mutable_objects_request()->mutable_image_data()->mutable_image_metadata()->set_width(width);
    request.mutable_objects_request()->mutable_image_data()->mutable_image_metadata()->set_height(width);

    auto result = request.SerializeAsString();
    cb(result.c_str(), result.size());
}

void _glens_parse_response(const char *data, size_t size, void (*cb)(const char *, float, float, float, float))
{
    LensOverlayServerResponse response;
    if (!response.ParseFromArray(data, size))
        return;
    if (!response.has_objects_response())
        return;
    auto objects_response = response.objects_response();
    if (!objects_response.has_text())
        return;
    auto text = objects_response.text();
    if (!text.has_text_layout())
        return;
    auto text_layout = text.text_layout();
    auto paragraphs = text_layout.paragraphs();
    for (auto &&paragraph : paragraphs)
    {
        std::string lines;
        for (auto &&line : paragraph.lines())
        {
            for (auto &&word : line.words())
            {
                lines += word.plain_text();
                if (word.has_text_separator())
                    lines += word.text_separator();
            }
        }
        if (lines.empty())
            continue;
        if (!paragraph.has_geometry())
            continue;
        auto geometry = paragraph.geometry();
        if (!geometry.has_bounding_box())
            continue;
        auto bounding_box = geometry.bounding_box();
        cb(lines.c_str(), bounding_box.center_x(), bounding_box.center_y(), bounding_box.width(), bounding_box.height());
    }
}