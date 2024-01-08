//#include <node_api.h>
//
//#include <stdint.h>
//
//#include "ebyroid.h"
//#include "ebyutil.h"
//
//using ebyroid::Ebyroid, ebyroid::ConvertParams;
//
//typedef struct {
//  Ebyroid* ebyroid;
//} module_context;
//
//typedef enum { WORK_HIRAGANA, WORK_SPEECH, WORK_CONVERT } work_type;
//
//typedef struct {
//  work_type worktype;
//  unsigned char* input;
//  size_t input_size;
//  void* output;
//  size_t output_size;
//  napi_async_work self;
//  napi_ref javascript_callback_ref;
//  char* error_message;
//  size_t error_size;
//  ConvertParams* convert_params;
//} work_data;
//
//static module_context* module;
//
//static void async_work_on_execute(napi_env env, void* data) {
//  int result;
//  napi_status status;
//  work_data* work = (work_data*) data;
//
//  switch (work->worktype) {
//    case WORK_HIRAGANA:
//      try {
//        unsigned char* out;
//        result = module->ebyroid->Hiragana(work->input, &out, &work->output_size);
//        work->output = out;
//      } catch (std::exception& e) {
//        Eprintf("(Ebyroid::Hiragana) %s", e.what());
//        size_t size = strlen(e.what());
//        char* what = (char*) malloc(size + 1);
//        strcpy(what, e.what());
//        work->error_message = what;
//        work->error_size = size;
//      }
//      break;
//    case WORK_SPEECH:
//      try {
//        int16_t* out;
//        result = module->ebyroid->Speech(work->input, &out, &work->output_size);
//        work->output = out;
//      } catch (std::exception& e) {
//        Eprintf("(Ebyroid::Speech) %s", e.what());
//        size_t size = strlen(e.what());
//        char* what = (char*) malloc(size + 1);
//        strcpy(what, e.what());
//        work->error_message = what;
//        work->error_size = size;
//      }
//      break;
//    case WORK_CONVERT:
//      try {
//        int16_t* out;
//        result =
//            module->ebyroid->Convert(*work->convert_params, work->input, &out, &work->output_size);
//        work->output = out;
//      } catch (std::exception& e) {
//        Eprintf("(Ebyroid::Convert) %s", e.what());
//        size_t size = strlen(e.what());
//        char* what = (char*) malloc(size + 1);
//        strcpy(what, e.what());
//        work->error_message = what;
//        work->error_size = size;
//      }
//      break;
//  }
//}
//
//static void async_work_on_complete(napi_env env, napi_status work_status, void* data) {
//  static const size_t RETVAL_SIZE = 2;
//  napi_status status;
//  napi_value retval[RETVAL_SIZE];
//  napi_value callback, undefined, null_value;
//  work_data* work = (work_data*) data;
//
//  // prepare JS 'undefined' value
//  status = napi_get_undefined(env, &undefined);
//  e_assert(status == napi_ok);
//
//  // prepare JS 'null' value
//  status = napi_get_null(env, &null_value);
//  e_assert(status == napi_ok);
//
//  if (work_status == napi_cancelled) {
//    static const char* what = "N-API async work has been cancelled";
//    napi_value message, error_object;
//    status = napi_create_string_utf8(env, what, strlen(what), &message);
//    e_assert(status == napi_ok);
//    status = napi_create_error(env, NULL, message, &error_object);
//    e_assert(status == napi_ok);
//
//    retval[0] = error_object;
//    retval[1] = null_value;
//    goto DO_FINALLY;
//  }
//
//  if (work->error_message) {
//    napi_value message, error_object;
//    status = napi_create_string_utf8(env, work->error_message, work->error_size, &message);
//    e_assert(status == napi_ok);
//    status = napi_create_error(env, NULL, message, &error_object);
//    e_assert(status == napi_ok);
//
//    retval[0] = error_object;
//    retval[1] = null_value;
//    goto DO_FINALLY;
//  }
//
//  napi_value return_value;
//  switch (work->worktype) {
//    case WORK_HIRAGANA:
//      // convert output bytes to node buffer
//      status = napi_create_buffer_copy(env, work->output_size, work->output, NULL, &return_value);
//      e_assert(status == napi_ok);
//      break;
//    case WORK_SPEECH:
//    case WORK_CONVERT:
//      // convert output bytes to int16array
//      // create underlying arraybuffer
//      void* node_memory;
//      napi_value array_buffer;
//      status = napi_create_arraybuffer(env, work->output_size, &node_memory, &array_buffer);
//      e_assert(status == napi_ok);
//      // copy data to arraybuffer and create int16array
//      memcpy(node_memory, work->output, work->output_size);
//      e_assert(work->output_size % 2 == 0);
//      status = napi_create_typedarray(
//          env, napi_int16_array, work->output_size / 2, array_buffer, 0, &return_value);
//      e_assert(status == napi_ok);
//      break;
//  }
//  retval[0] = null_value;
//  retval[1] = return_value;
//
//DO_FINALLY:
//  // acquire the javascript callback function
//  status = napi_get_reference_value(env, work->javascript_callback_ref, &callback);
//  e_assert(status == napi_ok);
//
//  // actually call the javascript callback function
//  status = napi_call_function(env, undefined, callback, RETVAL_SIZE, retval, NULL);
//  e_assert(status == napi_ok || status == napi_pending_exception);
//
//  // decrement the reference count of the function
//  // ... means it will be GC'd
//  uint32_t refs;
//  status = napi_reference_unref(env, work->javascript_callback_ref, &refs);
//  e_assert(status == napi_ok && refs == 0);
//
//  // now neko work is done so we delete the work object
//  status = napi_delete_async_work(env, work->self);
//  e_assert(status == napi_ok);
//
//  // and manually allocated recources
//  free(work->input);
//  free(work->output);
//  free(work->error_message);
//  if (work->convert_params) {
//    free(work->convert_params->base_dir);
//    free(work->convert_params->voice);
//    free(work->convert_params);
//  }
//  free(work);
//}
//
//static napi_value do_async_work(napi_env env, napi_callback_info info, work_type worktype) {
//  napi_status status;
//  napi_valuetype valuetype;
//
//  size_t argc = 3;
//  napi_value argv[3];
//  status = napi_get_cb_info(env, info, &argc, argv, NULL, NULL);
//  en_assert(status == napi_ok);
//
//  // first arg must be buffer
//  bool is_buffer;
//  status = napi_is_buffer(env, argv[0], &is_buffer);
//  en_assert(status == napi_ok && is_buffer == true);
//
//  // second arg must be object
//  status = napi_typeof(env, argv[1], &valuetype);
//  en_assert(status == napi_ok && valuetype == napi_object);
//
//  // third arg must be function
//  status = napi_typeof(env, argv[2], &valuetype);
//  en_assert(status == napi_ok && valuetype == napi_function);
//
//  // fetch buffer data
//  unsigned char* node_buffer_data;
//  size_t node_buffer_size;
//  status = napi_get_buffer_info(env, argv[0], (void**) &node_buffer_data, &node_buffer_size);
//
//  // allocate
//  unsigned char* buffer = (unsigned char*) malloc(node_buffer_size + 1);
//  memcpy(buffer, node_buffer_data, node_buffer_size);
//  *(buffer + node_buffer_size) = '\0';
//
//  // check if the object arg is for params
//  bool is_param;
//  status = napi_has_named_property(env, argv[1], "needs_reload", &is_param);
//  en_assert(status == napi_ok);
//
//  // build ConvertParam if it's for param
//  ConvertParams* params = NULL;
//  if (is_param) {
//    napi_value value;
//    params = (ConvertParams*) malloc(sizeof(*params));
//
//    // fetch .needs_reload boolean
//    status = napi_get_named_property(env, argv[1], "needs_reload", &value);
//    en_assert(status == napi_ok);
//    status = napi_get_value_bool(env, value, &params->needs_reload);
//    en_assert(status == napi_ok);
//
//    if (params->needs_reload) {
//      size_t bufsize;
//
//      // fetch .base_dir string
//      char* base_dir;
//      status = napi_get_named_property(env, argv[1], "base_dir", &value);
//      en_assert(status == napi_ok);
//      status = napi_get_value_string_utf8(env, value, NULL, NULL, &bufsize);
//      en_assert(status == napi_ok);
//      base_dir = (char*) malloc(bufsize + 1);
//      status = napi_get_value_string_utf8(env, value, base_dir, bufsize + 1, NULL);
//      en_assert(status == napi_ok);
//      params->base_dir = base_dir;
//
//      // fetch .voice string
//      char* voice;
//      status = napi_get_named_property(env, argv[1], "voice", &value);
//      en_assert(status == napi_ok);
//      status = napi_get_value_string_utf8(env, value, NULL, NULL, &bufsize);
//      en_assert(status == napi_ok);
//      voice = (char*) malloc(bufsize + 1);
//      status = napi_get_value_string_utf8(env, value, voice, bufsize + 1, NULL);
//      en_assert(status == napi_ok);
//      params->voice = voice;
//
//      // fetch .volume float
//      double volume;
//      status = napi_get_named_property(env, argv[1], "volume", &value);
//      en_assert(status == napi_ok);
//      status = napi_get_value_double(env, value, &volume);
//      en_assert(status == napi_ok);
//      params->volume = (float) volume;
//
//    } else {
//      params->base_dir = NULL;
//      params->voice = NULL;
//    }
//  }
//
//  char* workname;
//  switch (worktype) {
//    case WORK_HIRAGANA:
//      workname = "Input Text Reinterpretor";
//      break;
//    case WORK_SPEECH:
//      workname = "Reinterpreted Text To PCM Converter";
//      break;
//    case WORK_CONVERT:
//      workname = "Raw Text To PCM Converter";
//      break;
//  }
//
//  // create name identifier
//  napi_value async_work_name;
//  status = napi_create_string_utf8(env, workname, NAPI_AUTO_LENGTH, &async_work_name);
//  en_assert(status == napi_ok);
//
//  // create reference for the callback fucntion
//  // because it otherwise will soon get GC'd
//  napi_ref callback_ref;
//  status = napi_create_reference(env, argv[2], 1, &callback_ref);
//  en_assert(status == napi_ok);
//
//  // create working data
//  work_data* work = (work_data*) malloc(sizeof(*work));
//  work->input = buffer;
//  work->input_size = node_buffer_size;
//  work->javascript_callback_ref = callback_ref;
//  work->worktype = worktype;
//  work->output = NULL;
//  work->error_message = NULL;
//  work->convert_params = params;
//
//  // create async work object
//  status = napi_create_async_work(
//      env, NULL, async_work_name, async_work_on_execute, async_work_on_complete, work, &work->self);
//  en_assert(status == napi_ok);
//
//  // queue the async work
//  status = napi_queue_async_work(env, work->self);
//  en_assert(status == napi_ok);
//
//  return NULL;
//}
//
////
//// JS Signature:
////   convert(inbytes: Buffer, options: object, done: function(err, pcm: Int16Array) -> none) -> none
////
//static napi_value export_func_convert(napi_env env, napi_callback_info info) {
//  return do_async_work(env, info, WORK_CONVERT);
//}
//
////
//// JS Signature:
////   speech(inbytes: Buffer, options={}, done: function(err, pcm: Int16Array) -> none) -> none
////
//static napi_value export_func_speech(napi_env env, napi_callback_info info) {
//  return do_async_work(env, info, WORK_SPEECH);
//}
//
////
//// JS Signature:
////   reinterpret(inbytes: Buffer, options={}, done: function(err, outbytes: Buffer) -> none) -> none
////
//static napi_value export_func_reinterpret(napi_env env, napi_callback_info info) {
//  return do_async_work(env, info, WORK_HIRAGANA);
//}
//
////
//// JS Signature: init(baseDir: string, voice: string, volume: number) -> none
////
//static napi_value export_func_init(napi_env env, napi_callback_info info) {
//  if (module->ebyroid == NULL) {
//    return NULL;
//  }
//
//  napi_status status;
//
//  size_t argc = 3;
//  napi_value argv[3];
//  status = napi_get_cb_info(env, info, &argc, argv, NULL, NULL);
//  en_assert(status == napi_ok);
//
//  napi_valuetype valuetype;
//  status = napi_typeof(env, argv[0], &valuetype);
//  en_assert(status == napi_ok && valuetype == napi_string);
//
//  status = napi_typeof(env, argv[1], &valuetype);
//  en_assert(status == napi_ok && valuetype == napi_string);
//
//  status = napi_typeof(env, argv[2], &valuetype);
//  en_assert(status == napi_ok && valuetype == napi_number);
//
//  // fetch necessary buffer size
//  size_t size;
//  status = napi_get_value_string_utf8(env, argv[0], NULL, 0, &size);
//  // NOTE: 'size' doesn't count the NULL character of the end, it seems
//  en_assert(status == napi_ok);
//
//  // allocate
//  char* install_dir_buffer = (char*) malloc(size + 1);
//  status = napi_get_value_string_utf8(env, argv[0], install_dir_buffer, size + 1, NULL);
//  en_assert(status == napi_ok);
//
//  // fetch necessary buffer size
//  status = napi_get_value_string_utf8(env, argv[1], NULL, 0, &size);
//  en_assert(status == napi_ok);
//
//  // allocate
//  char* voice_dir_buffer = (char*) malloc(size + 1);
//  status = napi_get_value_string_utf8(env, argv[1], voice_dir_buffer, size + 1, NULL);
//  en_assert(status == napi_ok);
//
//  // fetch volume
//  double volume;
//  status = napi_get_value_double(env, argv[2], &volume);
//  en_assert(status == napi_ok);
//
//  // initialize ebyroid
//  try {
//    module->ebyroid = Ebyroid::Create(install_dir_buffer, voice_dir_buffer, (float) volume);
//  } catch (std::exception& e) {
//    const char* location = "(ebyroid::Ebyroid::Create)";
//    napi_fatal_error(location, strlen(location), e.what(), strlen(e.what()));
//  }
//
//  // finalize ebyroid in the cleanup hook
//  status = napi_add_env_cleanup_hook(env, [](void* arg) { delete module->ebyroid; }, NULL);
//  en_assert(status == napi_ok);
//
//  free(install_dir_buffer);
//  free(voice_dir_buffer);
//
//  return NULL;
//}
//
//static napi_value module_main(napi_env env, napi_value exports) {
//  napi_property_descriptor props[] = {
//      {"speech", NULL, export_func_speech, NULL, NULL, NULL, napi_enumerable, NULL},
//      {"reinterpret", NULL, export_func_reinterpret, NULL, NULL, NULL, napi_enumerable, NULL},
//      {"convert", NULL, export_func_convert, NULL, NULL, NULL, napi_enumerable, NULL},
//      {"init", NULL, export_func_init, NULL, NULL, NULL, napi_enumerable, NULL},
//  };
//
//  napi_status status = napi_define_properties(env, exports, sizeof(props) / sizeof(*props), props);
//  en_assert(status == napi_ok);
//
//  module = (module_context*) malloc(sizeof(*module));
//
//  // clean heap in the cleanup hook
//  status = napi_add_env_cleanup_hook(env, [](void* arg) { free(module); }, NULL);
//  en_assert(status == napi_ok);
//
//  return exports;
//}
//
//NAPI_MODULE(ebyroid, module_main)
