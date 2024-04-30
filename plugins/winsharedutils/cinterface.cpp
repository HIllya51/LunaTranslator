
#include "define.h"
#include <iostream>
#include "cinterface.h"
#include <malloc.h>
#include <mutex>
#include <queue>
#include <Windows.h>
void free_all(void *str)
{
  delete str;
}
void freewstringlist(wchar_t **strlist, int num)
{
  for (int i = 0; i < num; i++)
  {
    delete strlist[i];
  }
  delete strlist;
}
void freestringlist(char **strlist, int num)
{
  for (int i = 0; i < num; i++)
  {
    delete strlist[i];
  }
  delete strlist;
}

int *vecint2c(std::vector<int> &vs)
{
  int *argv = new int[vs.size() + 1];

  for (size_t i = 0; i < vs.size(); i++)
  {
    argv[i] = vs[i];
  }
  return argv;
}

char **vecstr2c(std::vector<std::string> &vs)
{
  char **argv = new char *[vs.size() + 1];

  for (size_t i = 0; i < vs.size(); i++)
  {
    argv[i] = new char[vs[i].size() + 1];
    strcpy_s(argv[i], vs[i].size() + 1, vs[i].c_str());
    argv[i][vs[i].size()] = 0;
  }
  return argv;
}

wchar_t **vecwstr2c(std::vector<std::wstring> &vs)
{
  wchar_t **argv = new wchar_t *[vs.size() + 1];

  for (size_t i = 0; i < vs.size(); i++)
  {
    argv[i] = new wchar_t[vs[i].size() + 1];
    wcscpy_s(argv[i], vs[i].size() + 1, vs[i].c_str());
    argv[i][vs[i].size()] = 0;
  }
  return argv;
}

void c_free(void *ptr)
{
  free(ptr);
}
