#include "NeXAS.h"

/** jichi 7/6/2014 NeXAS
 *  Sample game: BALDRSKYZERO EXTREME
 *
 *  Call graph:
 *  - GetGlyphOutlineA x 2 functions
 *  - Caller 503620: char = [arg1 + 0x1a8]
 *  - Caller: 500039, 4ffff0
 *    edi = [esi+0x1a0] # stack size 4x3
 *    arg1 = eax = [edi]
 *
 *  0050361f     cc             int3
 *  00503620  /$ 55             push ebp
 *  00503621  |. 8bec           mov ebp,esp
 *  00503623  |. 83e4 f8        and esp,0xfffffff8
 *  00503626  |. 64:a1 00000000 mov eax,dword ptr fs:[0]
 *  0050362c  |. 6a ff          push -0x1
 *  0050362e  |. 68 15815900    push bszex.00598115
 *  00503633  |. 50             push eax
 *  00503634  |. 64:8925 000000>mov dword ptr fs:[0],esp
 *  0050363b  |. 81ec 78010000  sub esp,0x178
 *  00503641  |. 53             push ebx
 *  00503642  |. 8b5d 08        mov ebx,dword ptr ss:[ebp+0x8]
 *  00503645  |. 80bb ed010000 >cmp byte ptr ds:[ebx+0x1ed],0x0
 *  0050364c  |. 56             push esi
 *  0050364d  |. 57             push edi
 *  0050364e  |. 0f85 6e0b0000  jnz bszex.005041c2
 *  00503654  |. 8db3 a8010000  lea esi,dword ptr ds:[ebx+0x1a8]
 *  0050365a  |. c683 ed010000 >mov byte ptr ds:[ebx+0x1ed],0x1
 *  00503661  |. 837e 14 10     cmp dword ptr ds:[esi+0x14],0x10
 *  00503665  |. 72 04          jb short bszex.0050366b
 *  00503667  |. 8b06           mov eax,dword ptr ds:[esi]
 *  00503669  |. eb 02          jmp short bszex.0050366d
 *  0050366b  |> 8bc6           mov eax,esi
 *  0050366d  |> 8038 20        cmp byte ptr ds:[eax],0x20
 *  00503670  |. 0f84 ef0a0000  je bszex.00504165
 *  00503676  |. b9 fcc97400    mov ecx,bszex.0074c9fc
 *  0050367b  |. 8bfe           mov edi,esi
 *  0050367d  |. e8 2e20f1ff    call bszex.004156b0
 *  00503682  |. 84c0           test al,al
 *  00503684  |. 0f85 db0a0000  jnz bszex.00504165
 *  0050368a  |. 8b93 38010000  mov edx,dword ptr ds:[ebx+0x138]
 *  00503690  |. 33c0           xor eax,eax
 *  00503692  |. 3bd0           cmp edx,eax
 *  00503694  |. 0f84 8d0a0000  je bszex.00504127
 *  0050369a  |. 8b8b 3c010000  mov ecx,dword ptr ds:[ebx+0x13c]
 *  005036a0  |. 3bc8           cmp ecx,eax
 *  005036a2  |. 0f84 7f0a0000  je bszex.00504127
 *  005036a8  |. 894424 40      mov dword ptr ss:[esp+0x40],eax
 *  005036ac  |. 894424 44      mov dword ptr ss:[esp+0x44],eax
 *  005036b0  |. 894424 48      mov dword ptr ss:[esp+0x48],eax
 *  005036b4  |. 898424 8c01000>mov dword ptr ss:[esp+0x18c],eax
 *  005036bb  |. 33ff           xor edi,edi
 *  005036bd  |. 66:897c24 60   mov word ptr ss:[esp+0x60],di
 *  005036c2  |. bf 01000000    mov edi,0x1
 *  005036c7  |. 66:897c24 62   mov word ptr ss:[esp+0x62],di
 *  005036cc  |. 33ff           xor edi,edi
 *  005036ce  |. 66:897c24 64   mov word ptr ss:[esp+0x64],di
 *  005036d3  |. 66:897c24 66   mov word ptr ss:[esp+0x66],di
 *  005036d8  |. 66:897c24 68   mov word ptr ss:[esp+0x68],di
 *  005036dd  |. 66:897c24 6a   mov word ptr ss:[esp+0x6a],di
 *  005036e2  |. 66:897c24 6c   mov word ptr ss:[esp+0x6c],di
 *  005036e7  |. bf 01000000    mov edi,0x1
 *  005036ec  |. 66:897c24 6e   mov word ptr ss:[esp+0x6e],di
 *  005036f1  |. 894424 0c      mov dword ptr ss:[esp+0xc],eax
 *  005036f5  |. 894424 10      mov dword ptr ss:[esp+0x10],eax
 *  005036f9  |. 3883 ec010000  cmp byte ptr ds:[ebx+0x1ec],al
 *  005036ff  |. 0f84 39010000  je bszex.0050383e
 *  00503705  |. c78424 f000000>mov dword ptr ss:[esp+0xf0],bszex.00780e>
 *  00503710  |. 898424 3001000>mov dword ptr ss:[esp+0x130],eax
 *  00503717  |. 898424 1001000>mov dword ptr ss:[esp+0x110],eax
 *  0050371e  |. 898424 1401000>mov dword ptr ss:[esp+0x114],eax
 *  00503725  |. c68424 8c01000>mov byte ptr ss:[esp+0x18c],0x1
 *  0050372d  |. 837e 14 10     cmp dword ptr ds:[esi+0x14],0x10
 *  00503731  |. 72 02          jb short bszex.00503735
 *  00503733  |. 8b36           mov esi,dword ptr ds:[esi]
 *  00503735  |> 51             push ecx
 *  00503736  |. 52             push edx
 *  00503737  |. 56             push esi
 *  00503738  |. 8d8424 ec00000>lea eax,dword ptr ss:[esp+0xec]
 *  0050373f  |. 68 00ca7400    push bszex.0074ca00                      ;  ascii "gaiji%s%02d%02d.fil"
 *  00503744  |. 50             push eax
 *  00503745  |. e8 cec6f7ff    call bszex.0047fe18
 *  0050374a  |. 83c4 14        add esp,0x14
 *  0050374d  |. 8d8c24 e000000>lea ecx,dword ptr ss:[esp+0xe0]
 *  00503754  |. 51             push ecx                                 ; /arg1
 *  00503755  |. 8d8c24 9400000>lea ecx,dword ptr ss:[esp+0x94]          ; |
 *  0050375c  |. e8 dfeaefff    call bszex.00402240                      ; \bszex.00402240
 *  00503761  |. 6a 00          push 0x0                                 ; /arg4 = 00000000
 *  00503763  |. 8d9424 9400000>lea edx,dword ptr ss:[esp+0x94]          ; |
 *  0050376a  |. c68424 9001000>mov byte ptr ss:[esp+0x190],0x2          ; |
 *  00503772  |. a1 a8a78200    mov eax,dword ptr ds:[0x82a7a8]          ; |
 *  00503777  |. 52             push edx                                 ; |arg3
 *  00503778  |. 50             push eax                                 ; |arg2 => 00000000
 *  00503779  |. 8d8c24 fc00000>lea ecx,dword ptr ss:[esp+0xfc]          ; |
 *  00503780  |. 51             push ecx                                 ; |arg1
 *  00503781  |. e8 2a0dfeff    call bszex.004e44b0                      ; \bszex.004e44b0
 *  00503786  |. 84c0           test al,al
 *  00503788  |. 8d8c24 9000000>lea ecx,dword ptr ss:[esp+0x90]
 *  0050378f  |. 0f95c3         setne bl
 *  00503792  |. c68424 8c01000>mov byte ptr ss:[esp+0x18c],0x1
 *  0050379a  |. e8 a1baf1ff    call bszex.0041f240
 *  0050379f  |. 84db           test bl,bl
 *  005037a1  |. 74 40          je short bszex.005037e3
 *  005037a3  |. 8db424 f000000>lea esi,dword ptr ss:[esp+0xf0]
 *  005037aa  |. e8 6106feff    call bszex.004e3e10
 *  005037af  |. 8bd8           mov ebx,eax
 *  005037b1  |. 895c24 0c      mov dword ptr ss:[esp+0xc],ebx
 *  005037b5  |. e8 5606feff    call bszex.004e3e10
 *  005037ba  |. 8bf8           mov edi,eax
 *  005037bc  |. 0faffb         imul edi,ebx
 *  005037bf  |. 894424 10      mov dword ptr ss:[esp+0x10],eax
 *  005037c3  |. 8bc7           mov eax,edi
 *  005037c5  |. 8d7424 40      lea esi,dword ptr ss:[esp+0x40]
 *  005037c9  |. e8 e219f1ff    call bszex.004151b0
 *  005037ce  |. 8b5424 40      mov edx,dword ptr ss:[esp+0x40]
 *  005037d2  |. 52             push edx                                 ; /arg1
 *  005037d3  |. 8bc7           mov eax,edi                              ; |
 *  005037d5  |. 8db424 f400000>lea esi,dword ptr ss:[esp+0xf4]          ; |
 *  005037dc  |. e8 8f03feff    call bszex.004e3b70                      ; \bszex.004e3b70
 *  005037e1  |. eb 10          jmp short bszex.005037f3
 *  005037e3  |> 8d8424 e000000>lea eax,dword ptr ss:[esp+0xe0]
 *  005037ea  |. 50             push eax
 *  005037eb  |. e8 60c5f2ff    call bszex.0042fd50
 *  005037f0  |. 83c4 04        add esp,0x4
 *  005037f3  |> 8b5c24 10      mov ebx,dword ptr ss:[esp+0x10]
 *  005037f7  |. 8b7c24 40      mov edi,dword ptr ss:[esp+0x40]
 *  005037fb  |. 8bcb           mov ecx,ebx
 *  005037fd  |. 0faf4c24 0c    imul ecx,dword ptr ss:[esp+0xc]
 *  00503802  |. 33c0           xor eax,eax
 *  00503804  |. 85c9           test ecx,ecx
 *  00503806  |. 7e 09          jle short bszex.00503811
 *  00503808  |> c02c07 02      /shr byte ptr ds:[edi+eax],0x2
 *  0050380c  |. 40             |inc eax
 *  0050380d  |. 3bc1           |cmp eax,ecx
 *  0050380f  |.^7c f7          \jl short bszex.00503808
 *  00503811  |> 8b4d 08        mov ecx,dword ptr ss:[ebp+0x8]
 *  00503814  |. 33c0           xor eax,eax
 *  00503816  |. 8db424 f000000>lea esi,dword ptr ss:[esp+0xf0]
 *  0050381d  |. 8981 dc010000  mov dword ptr ds:[ecx+0x1dc],eax
 *  00503823  |. 8981 e0010000  mov dword ptr ds:[ecx+0x1e0],eax
 *  00503829  |. c78424 f000000>mov dword ptr ss:[esp+0xf0],bszex.00780e>
 *  00503834  |. e8 4702feff    call bszex.004e3a80
 *  00503839  |. e9 68010000    jmp bszex.005039a6
 *  0050383e  |> 8b0d 08a58200  mov ecx,dword ptr ds:[0x82a508]
 *  00503844  |. 51             push ecx                                 ; /hwnd => null
 *  00503845  |. ff15 d4e26f00  call dword ptr ds:[<&user32.getdc>]      ; \getdc
 *  0050384b  |. 68 50b08200    push bszex.0082b050                      ; /facename = ""
 *  00503850  |. 6a 00          push 0x0                                 ; |pitchandfamily = default_pitch|ff_dontcare
 *  00503852  |. 6a 02          push 0x2                                 ; |quality = proof_quality
 *  00503854  |. 6a 00          push 0x0                                 ; |clipprecision = clip_default_precis
 *  00503856  |. 6a 07          push 0x7                                 ; |outputprecision = out_tt_only_precis
 *  00503858  |. 68 80000000    push 0x80                                ; |charset = 128.
 *  0050385d  |. 6a 00          push 0x0                                 ; |strikeout = false
 *  0050385f  |. 6a 00          push 0x0                                 ; |underline = false
 *  00503861  |. 8bf8           mov edi,eax                              ; |
 *  00503863  |. 8b83 38010000  mov eax,dword ptr ds:[ebx+0x138]         ; |
 *  00503869  |. 6a 00          push 0x0                                 ; |italic = false
 *  0050386b  |. 68 84030000    push 0x384                               ; |weight = fw_heavy
 *  00503870  |. 99             cdq                                      ; |
 *  00503871  |. 6a 00          push 0x0                                 ; |orientation = 0x0
 *  00503873  |. 2bc2           sub eax,edx                              ; |
 *  00503875  |. 8b93 3c010000  mov edx,dword ptr ds:[ebx+0x13c]         ; |
 *  0050387b  |. 6a 00          push 0x0                                 ; |escapement = 0x0
 *  0050387d  |. d1f8           sar eax,1                                ; |
 *  0050387f  |. 50             push eax                                 ; |width
 *  00503880  |. 52             push edx                                 ; |height
 *  00503881  |. ff15 48e06f00  call dword ptr ds:[<&gdi32.createfonta>] ; \createfonta
 *  00503887  |. 50             push eax                                 ; /hobject
 *  00503888  |. 57             push edi                                 ; |hdc
 *  00503889  |. 894424 30      mov dword ptr ss:[esp+0x30],eax          ; |
 *  0050388d  |. ff15 4ce06f00  call dword ptr ds:[<&gdi32.selectobject>>; \selectobject
 *  00503893  |. 894424 1c      mov dword ptr ss:[esp+0x1c],eax
 *  00503897  |. 8d8424 4801000>lea eax,dword ptr ss:[esp+0x148]
 *  0050389e  |. 50             push eax                                 ; /ptextmetric
 *  0050389f  |. 57             push edi                                 ; |hdc
 *  005038a0  |. ff15 50e06f00  call dword ptr ds:[<&gdi32.gettextmetric>; \gettextmetricsa
 *  005038a6  |. 837e 14 10     cmp dword ptr ds:[esi+0x14],0x10
 *  005038aa  |. 72 02          jb short bszex.005038ae
 *  005038ac  |. 8b36           mov esi,dword ptr ds:[esi]
 *  005038ae  |> 56             push esi                                 ; /arg1
 *  005038af  |. e8 deccf7ff    call bszex.00480592                      ; \bszex.00480592
 *  005038b4  |. 83c4 04        add esp,0x4
 *  005038b7  |. 8d4c24 60      lea ecx,dword ptr ss:[esp+0x60]
 *  005038bb  |. 51             push ecx                                 ; /pmat2
 *  005038bc  |. 6a 00          push 0x0                                 ; |buffer = null
 *  005038be  |. 6a 00          push 0x0                                 ; |bufsize = 0x0
 *  005038c0  |. 8d9424 d800000>lea edx,dword ptr ss:[esp+0xd8]          ; |
 *  005038c7  |. 52             push edx                                 ; |pmetrics
 *  005038c8  |. 6a 06          push 0x6                                 ; |format = ggo_gray8_bitmap
 *  005038ca  |. 50             push eax                                 ; |char
 *  005038cb  |. 57             push edi                                 ; |hdc
 *  005038cc  |. 894424 30      mov dword ptr ss:[esp+0x30],eax          ; |
 *  005038d0  |. ff15 54e06f00  call dword ptr ds:[<&gdi32.getglyphoutli>; \getglyphoutlinea
 *  005038d6  |. 8bd8           mov ebx,eax
 *  005038d8  |. 85db           test ebx,ebx
 *  005038da  |. 0f84 d5070000  je bszex.005040b5
 *  005038e0  |. 83fb ff        cmp ebx,-0x1
 *  005038e3  |. 0f84 cc070000  je bszex.005040b5
 *  005038e9  |. 8d7424 40      lea esi,dword ptr ss:[esp+0x40]
 *  005038ed  |. e8 be18f1ff    call bszex.004151b0
 *  005038f2  |. 8b4c24 40      mov ecx,dword ptr ss:[esp+0x40]
 *  005038f6  |. 8d4424 60      lea eax,dword ptr ss:[esp+0x60]
 *  005038fa  |. 50             push eax                                 ; /pmat2
 *  005038fb  |. 8b4424 18      mov eax,dword ptr ss:[esp+0x18]          ; |
 *  005038ff  |. 51             push ecx                                 ; |buffer
 *  00503900  |. 53             push ebx                                 ; |bufsize
 *  00503901  |. 8d9424 d800000>lea edx,dword ptr ss:[esp+0xd8]          ; |
 *  00503908  |. 52             push edx                                 ; |pmetrics
 *  00503909  |. 6a 06          push 0x6                                 ; |format = ggo_gray8_bitmap
 *  0050390b  |. 50             push eax                                 ; |char
 *  0050390c  |. 57             push edi                                 ; |hdc
 *  0050390d  |. ff15 54e06f00  call dword ptr ds:[<&gdi32.getglyphoutli>; \getglyphoutlinea
 *  00503913  |. 8b4c24 1c      mov ecx,dword ptr ss:[esp+0x1c]
 *  00503917  |. 51             push ecx                                 ; /hobject
 *  00503918  |. 57             push edi                                 ; |hdc
 *  00503919  |. ff15 4ce06f00  call dword ptr ds:[<&gdi32.selectobject>>; \selectobject
 *  0050391f  |. 8b15 08a58200  mov edx,dword ptr ds:[0x82a508]
 *  00503925  |. 57             push edi                                 ; /hdc
 *  00503926  |. 52             push edx                                 ; |hwnd => null
 *  00503927  |. ff15 a4e26f00  call dword ptr ds:[<&user32.releasedc>]  ; \releasedc
 *  0050392d  |. 8b4424 28      mov eax,dword ptr ss:[esp+0x28]
 *  00503931  |. 50             push eax                                 ; /hobject
 *  00503932  |. ff15 58e06f00  call dword ptr ds:[<&gdi32.deleteobject>>; \deleteobject
 *  00503938  |. 8bb424 cc00000>mov esi,dword ptr ss:[esp+0xcc]
 *  0050393f  |. 8b8c24 d000000>mov ecx,dword ptr ss:[esp+0xd0]
 *  00503946  |. 83c6 03        add esi,0x3
 *  00503949  |. 81e6 fcff0000  and esi,0xfffc
 *  0050394f  |. 8bd1           mov edx,ecx
 *  00503951  |. 0fafd6         imul edx,esi
 *  00503954  |. 897424 0c      mov dword ptr ss:[esp+0xc],esi
 *  00503958  |. 894c24 10      mov dword ptr ss:[esp+0x10],ecx
 *  0050395c  |. 3bda           cmp ebx,edx
 *  0050395e  |. 74 1a          je short bszex.0050397a
 */
bool InsertNeXASHookA()
{
  // There are two GetGlyphOutlineA, both of which seem to have the same texts
  ULONG addr = MemDbg::findCallAddress((ULONG)::GetGlyphOutlineA, processStartAddress, processStopAddress);
  if (!addr)
    return false;
  BYTE sig[] = {
      /*
      .text:00467841                 cmp     dword ptr [esi+18h], 10h
  .text:00467845                 jb      short loc_46784C
  .text:00467847                 mov     esi, [esi+4]
  .text:0046784A                 jmp     short loc_46784F
  .text:0046784C ; ---------------------------------------------------------------------------
  .text:0046784C
  .text:0046784C loc_46784C:                             ; CODE XREF: sub_467540+305↑j
  .text:0046784C                 add     esi, 4
  .text:0046784F
  .text:0046784F loc_46784F:                             ; CODE XREF: sub_467540+30A↑j
  .text:0046784F                 push    esi             ; String
  .text:00467850                 call    __mbsnextc
      */
      /*
      if ( *(_DWORD *)(v1 + 288) < 0x10u )
         v9 = (const unsigned __int8 *)(v1 + 268);
       else
         v9 = *(const unsigned __int8 **)(v1 + 268);
       uChara = _mbsnextc(v9);
       GlyphOutlineA = GetGlyphOutlineA(DC, uChara, 6u, &gm, 0, 0, &mat2);
      */
      0x83, 0x7E, 0x18, 0x10,
      0x72, 0x05,
      0x8B, 0x76, 0x04,
      0xEB, 0x03,
      0x83, 0xC6, 0x04,
      0x56,
      0xE8, XX4};
  auto addr2 = reverseFindBytes(sig, sizeof(sig), addr - 0x40, addr);
  if (addr2)
  {
    addr2 = MemDbg::findEnclosingAlignedFunction(addr2);
    if (addr2)
    {
      HookParam hp;
      hp.address = addr2;
      hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
      {
        auto v1 = context->ecx;
        const unsigned __int8 *v9;
        if (*(DWORD *)(v1 + 288) < 0x10u)
          v9 = (const unsigned __int8 *)(v1 + 268);
        else
          v9 = *(const unsigned __int8 **)(v1 + 268);

        buffer->from((char *)v9);
      };
      if (NewHook(hp, "NeXAS_1"))
        return true;
    }
  }

  // BALDR HEART
  BYTE sig2[] = {
      0x72, 0x02,
      0x8b, 0x00,
      0x50,
      0x8d, 0x8d, 0x00, 0xfc, 0xff, 0xff,
      0x68, 0x00, 0x04, 0x00, 0x00,
      0x51,
      0xe8, XX4};
  auto addrx = MemDbg::findBytes(sig2, sizeof(sig2), processStartAddress, processStopAddress);
  if (addrx)
  {
    HookParam hp;
    hp.address = addrx + sizeof(sig2) - 5;
    hp.offset = regoffset(eax);
    hp.type = USING_STRING;
    hp.lineSeparator = L"@n";
    hp.filter_fun = [](TextBuffer *buffer, HookParam *)
    {
      auto s = buffer->strA();
      s = re::sub(s, "@r(.*?)@(.*?)@", "$1");
      s = re::sub(s, "@v\\d{8}");
      strReplace(s, "@k");
      strReplace(s, "@g");
      strReplace(s, "@d");
      buffer->from(s);
    };
    if (NewHook(hp, "NeXAS3"))
      return true;
  }
  // DWORD GetGlyphOutline(
  //   _In_   HDC hdc,
  //   _In_   UINT uChar,
  //   _In_   UINT uFormat,
  //   _Out_  LPGLYPHMETRICS lpgm,
  //   _In_   DWORD cbBuffer,
  //   _Out_  LPVOID lpvBuffer,
  //   _In_   const MAT2 *lpmat2
  // );

  HookParam hp;
  // hp.address = (DWORD)::GetGlyphOutlineA;
  hp.address = addr;
  // hp.type = USING_STRING|USING_SPLIT;
  hp.type = CODEC_ANSI_BE | NO_CONTEXT;
  hp.offset = stackoffset(1);

  // Either lpgm or lpmat2 are good choices
  // hp.split = stackoffset(3); //虽然可以将人名分开，但也会把一个句子点击快进的文本也给分开，还不如不分。
  // hp.split = arg7_lpmat2; // = 0x18, arg7

  ConsoleOutput("INSERT NeXAS");
  return NewHook(hp, "NeXAS");
}
struct nexassomeinfo
{
  DWORD off1, off2;
  DWORD split;
};
bool InsertNeXASHookW()
{
  //[240926][1287246][エンターグラム] 制服カノジョ まよいごエンゲージ DL版 (files)
  // char sig[] = "Gaiji%s%02d%02d.fil";或者也可以找所有的push这个的地址
  auto addrs = findiatcallormov_all((DWORD)GetGlyphOutlineW, processStartAddress, processStartAddress, processStopAddress, PAGE_EXECUTE);
  bool succ = false;
  for (auto addr1 : addrs)
  {
    auto addr = MemDbg::findEnclosingAlignedFunction(addr1);
    if (!addr)
      continue;
    BYTE check[] = {
        0x83, XX, XX4, 0x10, // cmp     dword ptr [edi+0BCh], 10h; XX4:0xbc, 0x00, 0x00, 0x00
        0x8d, XX, XX4,       // lea     edx, [edi+0A8h], XX4:0xa8, 0x00, 0x00, 0x00
        0x89, XX, XX,
        0x72, 0x06,
        0x8b, XX, XX4, // mov     edx, [edi+0A8h], XX4:0xa8, 0x00, 0x00, 0x00

    };
    auto addrx = MemDbg::findBytes(check, sizeof(check), addr, addr1);
    if (!addrx)
      continue;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | CODEC_UTF8; // utf8编码的单字符
    hp.user_value = (DWORD) new nexassomeinfo{*(DWORD *)(addrx + 2), *(DWORD *)(addrx + 9), 0};
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      /*
       v17 = *(_DWORD *)(this + 188) < 0x10u;
    v18 = (const CHAR *)(this + 168);
    h = v16;
    if ( !v17 )
      v18 = *(const CHAR **)(this + 168);
    sub_42A120(v34, v18, *(_DWORD *)(this + 184));//utf8转utf16
      */
      auto v1 = context->ecx;
      const unsigned __int8 *v9;
      auto off1 = ((nexassomeinfo *)hp->user_value)->off1; // 188,0xbc
      auto off2 = ((nexassomeinfo *)hp->user_value)->off2; // 168,0xa8
      if (*(DWORD *)(v1 + off1) < 0x10u)
        v9 = (const unsigned __int8 *)(v1 + off2);
      else
        v9 = *(const unsigned __int8 **)(v1 + off2);

      buffer->from((char *)v9);
      if (((nexassomeinfo *)hp->user_value)->split == 0)
        ((nexassomeinfo *)hp->user_value)->split = context->stack[1];
      *split = std::abs((long long)((nexassomeinfo *)hp->user_value)->split - (long long)context->stack[1]) < 0x10;
      // 文本会被分成两个线程，原因未知。人名线程是比文本小很多的，两个文本线程离得很近
      // 不能不分，不分会导致沾到一起。
    };
    succ |= NewHook(hp, "NeXASW");
  }
  return succ;
}
namespace
{
  bool _2()
  {
    // 飛ぶ山羊はさかさまの木の夢を見るか
    BYTE bs[] = {
        0x8B, 0x56, 0x68,
        0x8a, 0x04, 0x3a,
        0x8d, 0x0c, 0x3a,
        0x33, 0xdb,
        0x3c, 0x40};
    auto addr = MemDbg::findBytes(bs, sizeof(bs), processStartAddress, processStopAddress);
    if (!addr)
      return 0;
    HookParam hp;
    hp.address = addr + 9;
    hp.type = DATA_INDIRECT;
    hp.index = 0;
    hp.offset = regoffset(ecx);
    hp.filter_fun = [](TextBuffer *buffer, HookParam *)
    {
      auto text = reinterpret_cast<LPSTR>(buffer->buff);
      if (text[0] == '@')
      {
        return buffer->clear();
      }
    };

    return NewHook(hp, "NeXAS2");
  }
}
namespace
{
  bool _3()
  {
    // 真剣で私に恋しなさい！Ａ－５
    char atv[] = "@v";
    auto aV = MemDbg::findBytes(atv, sizeof(atv), processStartAddress, processStopAddress);
    if (!aV)
      return false;
    aV = MemDbg::findBytes(atv, sizeof(atv), aV + 1, processStopAddress); // 第一个是历史，第二个才是当前文本
    if (!aV)
      return false;
    auto addr = MemDbg::findPushAddress(aV, processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return false;
    // 彼女はオレからはなれない
    // 这个地址不正确，跳过。
    if (*(BYTE *)addr == 0xf9)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING;
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      auto a2 = (TextUnionA *)context->stack[1]; // std::string*
      buffer->from(a2->getText());
    };
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      auto s = buffer->strA();
      if (startWith(s, "@"))
      {
        if (startWith(s, "@v"))
        {
          // S001_L1_0001
          s = re::sub(s, "@v[a-zA-Z0-9]{4}_[a-zA-Z0-9]{2}_[a-zA-Z0-9]{4}");
          buffer->from(s);
        }
        else
        {
          buffer->clear();
        }
      }
    };
    hp.lineSeparator = L"@n";
    return NewHook(hp, "NeXAS4");
  }
}
namespace
{
  //[241219][1299663][エンターグラム] この青空に約束を― Refine
  bool b4()
  {
    BYTE bs[] = {
        0x8b, 0x45, XX,
        0x3b, 0xd0,
        0x0f, 0x84, XX4,
        0x83, 0x78, 0x14, 0x0f,
        0x8b, 0x48, 0x10,
        0x76, 0x02,
        0x8b, 0x00};
    auto aV = MemDbg::findBytes(bs, sizeof(bs), processStartAddress, processStopAddress);
    if (!aV)
      return false;
    HookParam hp;
    hp.address = aV + 3;
    hp.type = USING_STRING | CODEC_UTF8 | NO_CONTEXT;
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      auto _ = (TextUnionA *)context->eax;
      buffer->from(_->getText(), _->size);
    };
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      auto s = buffer->strA();
      s = re::sub(s, R"(@v[_\w\d]{8})");
      s = re::sub(s, R"(@t\d{4})");
      s = re::sub(s, R"(@s\d{4})");
      s = re::sub(s, R"(@m\d{2})");
      s = re::sub(s, R"(@f\d{2})");
      s = re::sub(s, R"(@h[_\d\w]+)");
      s = re::sub(s, R"(@r(.*?)@(.*?)@)", "$1");
      strReplace(s, "@n");
      strReplace(s, "@e");
      strReplace(s, "@k");
      strReplace(s, "@p");
      buffer->from(s);
    };
    return NewHook(hp, "NeXAS4");
  }
}
bool NeXAS::attach_function()
{
  auto _ = _2() || _3() || b4();
  return InsertNeXASHookA() || InsertNeXASHookW() || _;
}