// disasm.cc
// 1/27/2013 jichi
// Original source: http://hack-expo.void.ru/groups/blt/text/disasm.txt
//
// 7/19/2014 jichi: Need to add SSE instruction support for PCSX2
// Sample problematic input from Fate/Stay night PS2:
//     3024b80c  -0f88 ae58dbd2    js pcsx2.030010c0
//     3024b812   0f1201           movlps xmm0,qword ptr ds:[ecx] ; jichi: hook here
//     3024b815   0f1302           movlps qword ptr ds:[edx],xmm0

#include "disasm.h"
#include <windows.h>

// disasm_flag values:
enum : unsigned {
  C_66          = 0x00000001    // 66-prefix
  , C_67        = 0x00000002    // 67-prefix
  , C_LOCK      = 0x00000004    // lock
  , C_REP       = 0x00000008    // repz/repnz
  , C_SEG       = 0x00000010    // seg-prefix
  , C_OPCODE2   = 0x00000020    // 2nd opcode present (1st==0f)
  , C_MODRM     = 0x00000040    // modrm present
  , C_SIB       = 0x00000080    // sib present
  , C_ANYPREFIX = (C_66|C_67|C_LOCK|C_REP|C_SEG)
};

DISASM_BEGIN_NAMESPACE

// These values are served as the output of disasm
// But the are currently unused and could make disasm thread-unsafe
namespace { // unnamed

BYTE disasm_seg     // CS DS ES SS FS GS
   , disasm_rep     // REPZ/REPNZ
   , disasm_opcode  // opcode
   , disasm_opcode2 // used when opcode==0f
   , disasm_modrm   // modxxxrm
   , disasm_sib     // scale-index-base
   , disasm_mem[8]  // mem addr value
   , disasm_data[8] // data value
   ;

} // unnamed namespace

// return: length if success, 0 if error
size_t disasm(const void *opcode0)
{
  const BYTE *opcode = (const BYTE *)opcode0;

  DWORD disasm_len = 0,      // 0 if error
        disasm_flag = 0,     // C_xxx
        disasm_memsize = 0,  // value = disasm_mem
        disasm_datasize = 0, // value = disasm_data
        disasm_defdata = 4,  // == C_66 ? 2 : 4
        disasm_defmem = 4;   // == C_67 ? 2 : 4

retry:
  disasm_opcode = *opcode++;

  switch (disasm_opcode) {
    case 0x99: // 7/20/2014 jichi: CDQ, size = 1
      break;

    case 0x00: case 0x01: case 0x02: case 0x03:
    case 0x08: case 0x09: case 0x0a: case 0x0b:
    case 0x10: case 0x11: case 0x12: case 0x13:
    case 0x18: case 0x19: case 0x1a: case 0x1b:
    case 0x20: case 0x21: case 0x22: case 0x23:
    case 0x28: case 0x29: case 0x2a: case 0x2b:
    case 0x30: case 0x31: case 0x32: case 0x33:
    case 0x38: case 0x39: case 0x3a: case 0x3b:
    case 0x62: case 0x63:
    case 0x84: case 0x85: case 0x86: case 0x87:
    case 0x88: case 0x89: case 0x8a: case 0x8b:
    case 0x8c: case 0x8d: case 0x8e: case 0x8f:
    case 0xc4: case 0xc5:
    case 0xd0: case 0xd1: case 0xd2: case 0xd3:
    case 0xd8: case 0xd9: case 0xda: case 0xdb:
    case 0xdc: case 0xdd: case 0xde: case 0xdf:
    case 0xfe: case 0xff:
               disasm_flag |= C_MODRM;
               break;
    case 0xcd: disasm_datasize += *opcode==0x20 ? 1+4 : 1;
               break;
    case 0xf6:
    case 0xf7: disasm_flag |= C_MODRM;
               if (*opcode & 0x38) break;
               // continue if <test ..., xx>
    case 0x04: case 0x05: case 0x0c: case 0x0d:
    case 0x14: case 0x15: case 0x1c: case 0x1d:
    case 0x24: case 0x25: case 0x2c: case 0x2d:
    case 0x34: case 0x35: case 0x3c: case 0x3d:
               if (disasm_opcode & 1)
                 disasm_datasize += disasm_defdata;
               else
                 disasm_datasize++;
               break;
    case 0x6a:
    case 0xa8:
    case 0xb0: case 0xb1: case 0xb2: case 0xb3:
    case 0xb4: case 0xb5: case 0xb6: case 0xb7:
    case 0xd4: case 0xd5:
    case 0xe4: case 0xe5: case 0xe6: case 0xe7:
    case 0x70: case 0x71: case 0x72: case 0x73:
    case 0x74: case 0x75: case 0x76: case 0x77:
    case 0x78: case 0x79: case 0x7a: case 0x7b:
    case 0x7c: case 0x7d: case 0x7e: case 0x7f:
    case 0xeb:
    case 0xe0: case 0xe1: case 0xe2: case 0xe3:
               disasm_datasize++;
               break;
    case 0x26: case 0x2e: case 0x36: case 0x3e:
    case 0x64: case 0x65:
               if (disasm_flag & C_SEG) return 0;
               disasm_flag |= C_SEG;
               disasm_seg = disasm_opcode;
               goto retry;
    case 0xf0:
               if (disasm_flag & C_LOCK) return 0;
               disasm_flag |= C_LOCK;
               goto retry;
    case 0xf2: case 0xf3:
               if (disasm_flag & C_REP) return 0;
               disasm_flag |= C_REP;
               disasm_rep = disasm_opcode;
               goto retry;
    case 0x66:
               if (disasm_flag & C_66) return 0;
               disasm_flag |= C_66;
               disasm_defdata = 2;
               goto retry;
    case 0x67:
               if (disasm_flag & C_67) return 0;
               disasm_flag |= C_67;
               disasm_defmem = 2;
               goto retry;
    case 0x6b:
    case 0x80:
    case 0x82:
    case 0x83:
    case 0xc0:
    case 0xc1:
    case 0xc6: disasm_datasize++;
               disasm_flag |= C_MODRM;
               break;
    case 0x69:
    case 0x81:
    case 0xc7:
               disasm_datasize += disasm_defdata;
               disasm_flag |= C_MODRM;
               break;
    case 0x9a:
    case 0xea: disasm_datasize += 2 + disasm_defdata;
               break;
    case 0xa0:
    case 0xa1:
    case 0xa2:
    case 0xa3: disasm_memsize += disasm_defmem;
               break;
    case 0x68:
    case 0xa9:
    case 0xb8: case 0xb9: case 0xba: case 0xbb:
    case 0xbc: case 0xbd: case 0xbe: case 0xbf:
    case 0xe8:
    case 0xe9:
               disasm_datasize += disasm_defdata;
               break;
    case 0xc2:
    case 0xca: disasm_datasize += 2;
               break;
    case 0xc8:
               disasm_datasize += 3;
               break;
    case 0xf1:
               return 0;
    case 0x0f:
      // 7/19/2014 jichi: 0x0f1201 = movlps xmm0,qword ptr ds:[ecx]
      // Given 0x0f1201, 0x0f will be strip off here and left 0x1201
      disasm_flag |= C_OPCODE2;
      disasm_opcode2 = *opcode++;
      switch (disasm_opcode2) {
        case 0x00: case 0x01: case 0x02: case 0x03:
        case 0x90: case 0x91: case 0x92: case 0x93:
        case 0x94: case 0x95: case 0x96: case 0x97:
        case 0x98: case 0x99: case 0x9a: case 0x9b:
        case 0x9c: case 0x9d: case 0x9e: case 0x9f:
        case 0xa3:
        case 0xa5:
        case 0xab:
        case 0xad:
        case 0xaf:
        case 0xb0: case 0xb1: case 0xb2: case 0xb3:
        case 0xb4: case 0xb5: case 0xb6: case 0xb7:
        case 0xbb:
        case 0xbc: case 0xbd: case 0xbe: case 0xbf:
        case 0xc0:
        case 0xc1:
        // 7/19/2014 jichi: Add more cases for SSE instructions
        // Sample instructions I need to consider
        //     0f1201           movlps xmm0,qword ptr ds:[ecx] ; jichi: hook here
        //     0f1302           movlps qword ptr ds:[edx],xmm0
        case 0x12:
        case 0x13:
                   disasm_flag |= C_MODRM;
                   break;
        case 0x06:
        case 0x08: case 0x09: case 0x0a: case 0x0b:
        case 0xa0: case 0xa1: case 0xa2: case 0xa8:
        case 0xa9:
        case 0xaa:
        case 0xc8: case 0xc9: case 0xca: case 0xcb:
        case 0xcc: case 0xcd: case 0xce: case 0xcf:
                   break;
        case 0x80: case 0x81: case 0x82: case 0x83:
        case 0x84: case 0x85: case 0x86: case 0x87:
        case 0x88: case 0x89: case 0x8a: case 0x8b:
        case 0x8c: case 0x8d: case 0x8e: case 0x8f:
                   disasm_datasize += disasm_defdata;
                   break;
        case 0xa4:
        case 0xac:
        case 0xba:
        default: return 0; // 7/19/2014 jichi: error
      } // 0F-switch
      break;

  } // switch

  if (disasm_flag & C_MODRM) {
    disasm_modrm = *opcode++;
    BYTE mod = disasm_modrm & 0xc0;
    BYTE rm  = disasm_modrm & 0x07;
    if (mod != 0xc0) {
      if (mod == 0x40)
        disasm_memsize++;
      if (mod == 0x80)
        disasm_memsize += disasm_defmem;
      if (disasm_defmem == 2) {         // modrm16
        if (mod == 0x00 && rm == 0x06)
          disasm_memsize += 2;
      } else {                            // modrm32
        if (rm == 0x04) {
          disasm_flag |= C_SIB;
          disasm_sib = *opcode++;
          rm = disasm_sib & 0x07;
        }
        if (rm == 0x05 && mod == 0x00)
          disasm_memsize += 4;
      }
    }
  } // C_MODRM

  for (DWORD i = 0; i < disasm_memsize; i++)
    disasm_mem[i] = *opcode++;
  for (DWORD i = 0; i < disasm_datasize; i++)
    disasm_data[i] = *opcode++;

  disasm_len = opcode - (const BYTE *)opcode0;

  return disasm_len;
} // disasm

DISASM_END_NAMESPACE

// EOF
