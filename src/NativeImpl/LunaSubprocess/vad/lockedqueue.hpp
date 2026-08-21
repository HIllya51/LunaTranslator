template <class T>
class lockedqueue
{
  std::mutex lock;
  std::queue<T> data;
  HANDLE hsema;

public:
  lockedqueue()
  {
    hsema = CreateSemaphore(NULL, 0, 65535, NULL);
  }
  ~lockedqueue()
  {
    CloseHandle(hsema);
  }
  void push(T &&_)
  {
    std::lock_guard _l(lock);
    data.push(std::move(_));
    ReleaseSemaphore(hsema, 1, NULL);
  }
  T pop()
  {
    WaitForSingleObject(hsema, INFINITE);
    std::lock_guard _l(lock);
    auto _ = data.front();
    data.pop();
    return _;
  }
  bool empty()
  {
    std::lock_guard _l(lock);
    return data.empty();
  }
};