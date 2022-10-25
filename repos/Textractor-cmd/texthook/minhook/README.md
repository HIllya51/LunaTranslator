# MinHook

[![License](https://img.shields.io/badge/License-BSD%202--Clause-orange.svg)](https://opensource.org/licenses/BSD-2-Clause)

The Minimalistic x86/x64 API Hooking Library for Windows

http://www.codeproject.com/KB/winsdk/LibMinHook.aspx

### Version history

- **v1.3.3 - 8 Jan 2017**
  * Added a helper function ```MH_CreateHookApiEx```. (Thanks to asm256)
  * Support Visual Studio 2017 RC.

- **v1.3.2.1 - 9 Nov 2015**  (Nuget package only)
  * Fixed an insufficient support for Visual Studio 2015.

- **v1.3.2 - 1 Nov 2015**
  * Support Visual Studio 2015.
  * Support MinGW.

- **v1.3.2-beta3 - 21 Jul 2015**  (Nuget package only)
  * Support MinGW. (Experimental)

- **v1.3.2-beta2 - 18 May 2015**
  * Fixed some subtle bugs. (Thanks to RaMMicHaeL)
  * Added a helper function ```MH_StatusToString```. (Thanks to Jan Klass)

- **v1.3.2-beta - 12 May 2015**
  * Fixed a possible thread deadlock in x64 mode. (Thanks to Aleh Kazakevich)
  * Reduced the footprint a little more.
  * Support Visual Studio 2015 RC. (Experimental)

- **v1.3.1.1 - 7 Apr 2015**  (Nuget package only)
  * Support for WDK8.0 and 8.1.

- **v1.3.1 - 19 Mar 2015**
  * No major changes from v1.3.1-beta.

- **v1.3.1-beta - 11 Mar 2015**
  * Added a helper function ```MH_CreateHookApi```. (Thanks to uniskz).
  * Fixed a false memory leak reported by some tools.
  * Fixed a degradated compatibility issue.

- **v1.3 - 13 Sep 2014**
  * No major changes from v1.3-beta3.

- **v1.3-beta3 - 31 Jul 2014**
  * Fixed some small bugs.
  * Improved the memory management.

- **v1.3-beta2 - 21 Jul 2014**
  * Changed the parameters to Windows-friendly types. (void* to LPVOID)
  * Fixed some small bugs.
  * Reorganized the source files.
  * Reduced the footprint a little more.

- **v1.3-beta - 17 Jul 2014**
  * Rewrote in plain C to reduce the footprint and memory usage. (suggested by Andrey Unis)
  * Simplified the overall code base to make it more readable and maintainable.
  * Changed the license from 3-clause to 2-clause BSD License.

- **v1.2 - 28 Sep 2013**
  * Removed boost dependency ([jarredholman](https://github.com/jarredholman/minhook)).
  * Fixed a small bug in the GetRelativeBranchDestination function ([pillbug99](http://www.codeproject.com/Messages/4058892/Small-Bug-Found.aspx)).
  * Added the ```MH_RemoveHook``` function, which removes a hook created with the ```MH_CreateHook``` function.
  * Added the following functions to enable or disable multiple hooks in one go: ```MH_QueueEnableHook```, ```MH_QueueDisableHook```, ```MH_ApplyQueued```. This is the preferred way of handling multiple hooks as every call to `MH_EnableHook` or `MH_DisableHook` suspends and resumes all threads.
  * Made the functions ```MH_EnableHook``` and ```MH_DisableHook``` enable/disable all created hooks when the ```MH_ALL_HOOKS``` parameter is passed. This, too, is an efficient way of handling multiple hooks.
  * If the target function is too small to be patched with a jump, MinHook tries to place the jump above the function. If that fails as well, the ```MH_CreateHook``` function returns ```MH_ERROR_UNSUPPORTED_FUNCTION```. This fixes an issue of hooking the LoadLibraryExW function on Windows 7 x64 ([reported by Obble](http://www.codeproject.com/Messages/4578613/Re-Bug-LoadLibraryExW-hook-fails-on-windows-2008-r.aspx)).

- **v1.1 - 26 Nov 2009**
  * Changed the interface to create a hook and a trampoline function in one go to prevent the detour function from being called before the trampoline function is created. ([reported by xliqz](http://www.codeproject.com/Messages/3280374/Unsafe.aspx))
  * Shortened the function names from ```MinHook_*``` to ```MH_*``` to make them handier.

- **v1.0 - 22 Nov 2009**
  * Initial release.

### Building MinHook - Using vcpkg

You can download and install MinHook using the [vcpkg](https://github.com/Microsoft/vcpkg) dependency manager:

    git clone https://github.com/microsoft/vcpkg
    .\vcpkg\bootstrap-vcpkg.bat
    .\vcpkg\vcpkg integrate install
    .\vcpkg\vcpkg install minhook

The MinHook port in vcpkg is kept up to date by Microsoft team members and community contributors. If the version is out of date, please [create an issue or pull request](https://github.com/Microsoft/vcpkg) on the vcpkg repository.
