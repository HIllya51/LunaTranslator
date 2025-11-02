/*
// v8这样做比用剪贴板好，但。。。太难了，而且版本兼容性不太好

typedef void *(*FunctionTemplateNew_t)(void *, void *, void *, void *, void *, int, int, int);
typedef void *(*FunctionTemplateGetFunction_t)(void *, void *, void *);
typedef void *(*FunctionSetName_t)(void *, void *);
typedef void *(*Global_t)(void *, void *);
typedef void *(*SetObject_t)(void *, void *, void *, void *, void *);
Global_t Global;
SetObject_t SetObject;
FunctionTemplateNew_t FunctionTemplateNew;
FunctionTemplateGetFunction_t FunctionTemplateGetFunction;
FunctionSetName_t FunctionSetName;
#define fnFunctionTemplateNew "?New@FunctionTemplate@v8@@SA?AV?$Local@VFunctionTemplate@v8@@@2@PAVIsolate@2@P6AXABV?$FunctionCallbackInfo@VValue@v8@@@2@@ZV?$Local@VValue@v8@@@2@V?$Local@VSignature@v8@@@2@HW4ConstructorBehavior@2@@Z"
#define fnFunctionTemplateGetFunction "?GetFunction@FunctionTemplate@v8@@QAE?AV?$MaybeLocal@VFunction@v8@@@2@V?$Local@VContext@v8@@@2@@Z"
#define fnFunctionSetName "?SetName@Function@v8@@QAEXV?$Local@VString@v8@@@2@@Z"
#define fnGlobal "?Global@Context@v8@@QAE?AV?$Local@VObject@v8@@@2@XZ"
#define fnSetObject "?Set@Object@v8@@QAE?AV?$Maybe@_N@2@V?$Local@VContext@v8@@@2@V?$Local@VValue@v8@@@2@1@Z"
void tryinsertglobalfunction(void *isolate)
{
	SetObject = (SetObject_t)GetProcAddress(hmodule, fnSetObject);
	Global = (Global_t)GetProcAddress(hmodule, fnGlobal);
	FunctionTemplateNew = (FunctionTemplateNew_t)GetProcAddress(hmodule, fnFunctionTemplateNew);
	FunctionTemplateGetFunction = (FunctionTemplateGetFunction_t)GetProcAddress(hmodule, fnFunctionTemplateGetFunction);
	FunctionSetName = (FunctionSetName_t)GetProcAddress(hmodule, fnFunctionSetName);

	void *context;
	void *v8string;
	void *script;
	void *useless;
	void *FunctionTemplate;
	void *unknown;
	void *v12[7];
	ConsoleOutput("%p %p %p %p %p", SetObject, Global, FunctionTemplateNew, FunctionTemplateGetFunction, FunctionSetName);
	GetCurrentContext(isolate, &context);
	ConsoleOutput("context %p", context);
	auto f = FunctionTemplateNew(&FunctionTemplate, context, Method, v12[0], 0, 0, 1, 0);

	ConsoleOutput("FunctionTemplate %p %p", *(void **)f, unknown);
	void *Function = FunctionTemplateGetFunction(FunctionTemplate, &unknown, context);

	auto string = NewFromUtf8(&v8string, isolate, "hello", 1, -1);
	ConsoleOutput("%p %p", *(void **)string, v8string);
	FunctionSetName(*(void **)Function, *(void **)string);

	auto global = Global(context, &unknown);
	SetObject(*(void **)global, &unknown, context, *(void **)string, *(void **)Function);
}
*/
#include <node.h>

using namespace v8;

void NODE_SET_METHOD_X(const char *name,
					   v8::FunctionCallback callback)
{

	v8::Isolate *isolate = v8::Isolate::GetCurrent();
	v8::HandleScope handle_scope(isolate);
	v8::Local<v8::Context> context = isolate->GetCurrentContext();

	v8::Local<v8::FunctionTemplate> t = v8::FunctionTemplate::New(isolate,
																  callback);
	v8::Local<v8::Function> fn = t->GetFunction(context).ToLocalChecked();
	v8::Local<v8::String> fn_name = v8::String::NewFromUtf8(isolate, name,
															v8::NewStringType::kInternalized)
										.ToLocalChecked();
	fn->SetName(fn_name);
	context->Global()->Set(context, fn_name, fn).Check();
}
extern "C" __declspec(dllexport) void utf8interaction(char *utf8)
{
	// 用来和lunahook交互
	utf8[0] += 10;
}

void Method(const FunctionCallbackInfo<Value> &args)
{
	Isolate *isolate = Isolate::GetCurrent();
	HandleScope scope(isolate);
	auto locals = args[0]->ToString(isolate->GetCurrentContext()).ToLocalChecked();
	auto size = locals->Utf8Length(isolate);
	auto buff = std::make_unique<char[]>(size + 1);
	locals->WriteUtf8(isolate, buff.get());
	utf8interaction(buff.get());
	args.GetReturnValue().Set(String::NewFromUtf8(isolate, buff.get()).ToLocalChecked());
}
extern "C" __declspec(dllexport) void globalfunction()
{
	NODE_SET_METHOD_X("hello", Method);
}
