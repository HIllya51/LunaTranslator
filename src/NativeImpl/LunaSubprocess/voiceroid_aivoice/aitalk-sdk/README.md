# AITalk®5 SDK 6.4.0 — C/C++ Header Files

Reconstructed from the official AITalk®5 SDK 6.4.0 library reference
(Doxygen) at:

<https://www.ai-j.jp/manual/business/sdk/6.4.0/library_reference/files.html>

## Layout

The directory layout mirrors the `#include` paths used inside the headers
(`#include "aitalk-sdk/core/tts.h"`, etc.), so the headers resolve to each
other when their **parent** directory is on the include path:

```
aitalk-sdk/
├─ core.h                # aggregates the core (TTS) library headers
├─ common.h              # aggregates the common headers
├─ audio_encoder.h       # aggregates the audio-encoder library headers
├─ common/               # return codes, types, values, macros (incl. AITALK_BEGIN_EXTERN_C, dllexport/dllimport)
├─ core/                 # TTS, license, initialization, marker, tts_parameter, version, ...
└─ audio_encoder/        # wave, μ-law, bit-depth, resampling, audio_config encoders
```

Usage (Windows, against `AITalk_SDK.dll`):

```bash
cl /I. /c my_app.c aitalk-sdk/core.h
# or, to call into the DLL, define AITALK_SDK_DLLIMPORT before including,
# then link against AITalk_SDK.lib / AITalk_SDK.dll
```

## Notes

- These are the **verbatim** header sources as rendered by Doxygen's source
  view. Doxygen consumes `@`-prefixed documentation commands inside comments
  (e.g. `// @addtogroup` is rendered as `// addtogroup`), so doc-only
  comment lines may lose their leading `@`. This does not affect any
  declaration, type, enum, or macro — the API surface is intact.
- 29 headers total: 3 aggregate headers + 7 audio_encoder + 4 common + 15 core.
- Re-run `python download_aitalk_headers.py` to re-fetch/refresh.
