
#include"define.h"
#include<iostream>
#include"cinterface.h"
#include<malloc.h>
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

size_t WriteMemoryToPipe(void *contents, size_t size, size_t nmemb, void *userp){
  size_t realsize = size * nmemb;
  auto mem=(MemoryStruct*)userp;
  auto hWrite=(HANDLE)mem->memory;
  mem->size+=1;
  DWORD _;
  WriteFile(hWrite,&realsize,4,&_,NULL);
  WriteFile(hWrite,contents,realsize,&_,NULL);
  return realsize;
}
