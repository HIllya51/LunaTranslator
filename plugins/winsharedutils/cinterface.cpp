
#include"define.h"
#include<iostream>
#include"cinterface.h"
#include<malloc.h>
#include<mutex>
#include<queue>
#include<Windows.h>
void free_all(void* str) {
    delete str;
}
void freewstringlist(wchar_t** strlist, int num) {
    for (int i = 0; i < num; i++) {
        delete strlist[i];
    }
    delete strlist;
}
void freestringlist(char** strlist, int num) {
    for (int i = 0; i < num; i++) {
        delete strlist[i];
    }
    delete strlist;
}
 
int* vecint2c(std::vector<int>& vs) {
    int* argv = new int [vs.size() + 1];

    for (size_t i = 0; i < vs.size(); i++) {
        argv[i] = vs[i]; 
    }
    return argv;
}

char** vecstr2c(std::vector<std::string>& vs) {
    char** argv = new char* [vs.size() + 1];

    for (size_t i = 0; i < vs.size(); i++) {
        argv[i] = new char[vs[i].size() + 1];
        strcpy_s(argv[i], vs[i].size()+1, vs[i].c_str());
        argv[i][vs[i].size()] = 0;
    }
    return argv;
}


wchar_t** vecwstr2c(std::vector<std::wstring>& vs) {
    wchar_t** argv = new wchar_t* [vs.size() + 1];

    for (size_t i = 0; i < vs.size(); i++) {
        argv[i] = new wchar_t[vs[i].size() + 1];
        wcscpy_s(argv[i], vs[i].size()+1, vs[i].c_str());
        argv[i][vs[i].size()] = 0;
    }
    return argv;
}

struct MemoryStruct {
  char *memory;
  size_t size;
};
size_t WriteMemoryCallback(void *contents, size_t size, size_t nmemb, void *userp){
  size_t realsize = size * nmemb;
  struct MemoryStruct *mem = (struct MemoryStruct *)userp;

  char *ptr;
  if(mem->memory)
    ptr=(char*)realloc(mem->memory, mem->size + realsize + 1);
  else
    ptr=(char*)malloc( mem->size + realsize + 1);
  if(!ptr) {
    /* out of memory! */
    printf("not enough memory (realloc returned NULL)\n");
    return 0;
  }

  mem->memory = ptr;
  memcpy(&(mem->memory[mem->size]), contents, realsize);
  mem->size += realsize;
  mem->memory[mem->size] = 0;

  return realsize;
}
void c_free(void* ptr){
    free(ptr);
}

class lockedqueue{
  std::mutex lock;
  std::queue<std::string>data;
  HANDLE hsema;
  public:
  lockedqueue(){
    hsema=CreateSemaphore(NULL,0,65535,NULL);
  }
  ~lockedqueue(){
    CloseHandle(hsema);
  }
  void push(std::string&& _){
    std::lock_guard _l(lock);
    data.push(std::move(_));
    ReleaseSemaphore(hsema,1,NULL);
  }
  std::string pop(){
    WaitForSingleObject(hsema,INFINITE);
    std::lock_guard _l(lock);
    auto _=data.front();
    data.pop();
    return _;
  }
  bool empty(){
    return data.empty();
  }
};
void* lockedqueuecreate(){
  return new lockedqueue();
}
void lockedqueuefree(void* q){
  delete reinterpret_cast<lockedqueue*>(q);
}
void* lockedqueueget(void* q,size_t* l){
  auto data=reinterpret_cast<lockedqueue*>(q)->pop();
  auto datastatic=new char[data.size()];
  memcpy(datastatic,data.data(),data.size());
  *l=data.size();
  return datastatic;
}
void lockedqueuepush(void* q,size_t l,void*ptr){
  reinterpret_cast<lockedqueue*>(q)->push(std::string((char*)ptr,l));
}
bool lockedqueueempty(void* q){
  return reinterpret_cast<lockedqueue*>(q)->empty();
}

size_t WriteMemoryToQueue(void *contents, size_t size, size_t nmemb, void *userp){
  size_t realsize = size * nmemb;
  auto queue=reinterpret_cast<lockedqueue*>(userp);
  queue->push(std::string((char*)contents,realsize));
  return realsize;
}
