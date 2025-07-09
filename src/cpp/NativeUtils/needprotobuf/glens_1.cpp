#include <lens_overlay_server.pb.h>
#include <lens_overlay_platform.pb.h>
#include <lens_overlay_filters.pb.h>
#include <lens_overlay_service_deps.pb.h>
using namespace lens;

void _glens_create_request(uint64_t uuid, const char *analytics_id, size_t size1, const char *bytes, size_t size, int32_t width, int32_t height, void (*cb)(const char *, size_t))
{
    LensOverlayServerRequest request;
    auto objects_request = new LensOverlayObjectsRequest;
    auto request_context = new LensOverlayRequestContext;
    auto request_id = new LensOverlayRequestId;
    auto routing_info = new LensOverlayRoutingInfo;
    auto client_context = new LensOverlayClientContext;
    auto locale_context = new LocaleContext;
    auto client_filters = new AppliedFilters;
    request_id->set_uuid(uuid);
    request_id->set_sequence_id(0);
    request_id->set_image_sequence_id(0);
    request_id->set_analytics_id(analytics_id, size1);
    request_id->set_allocated_routing_info(routing_info);
    request_context->set_allocated_request_id(request_id);

    client_context->set_platform(Platform::PLATFORM_WEB);
    client_context->set_surface(Surface::SURFACE_CHROMIUM);
    locale_context->set_time_zone("");
    client_context->set_allocated_locale_context(locale_context);
    client_context->set_app_id("");

    auto filter = client_filters->add_filter();
    filter->set_filter_type(LensOverlayFilterType::AUTO_FILTER);
    client_context->set_allocated_client_filters(client_filters);

    request_context->set_allocated_client_context(client_context);
    objects_request->set_allocated_request_context(request_context);

    auto image_data = new ImageData;
    auto payload = new ImagePayload;
    payload->set_image_bytes(bytes, size);
    image_data->set_allocated_payload(payload);
    auto image_metadata = new ImageMetadata;
    image_metadata->set_width(width);
    image_metadata->set_height(width);
    image_data->set_allocated_image_metadata(image_metadata);
    objects_request->set_allocated_image_data(image_data);

    request.set_allocated_objects_request(objects_request);

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