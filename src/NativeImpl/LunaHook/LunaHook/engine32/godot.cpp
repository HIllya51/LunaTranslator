#include "godot.h"

namespace
{
  bool godot35()
  {
    // https://store.steampowered.com/app/1713610/__Purrgatory/
    // 喵的炼狱 / Purrgatory
    /*
    int __userpurge sub_C49270@<eax>(
          int a1@<ecx>,
          int a2,
          int a3,
          float *a4,
          int *a5,
          int a6,
          int a7,
          int a8,
          int *a9,
          float *a10,
          float *a11,
          char a12,
          float *a13,
          int *a14,
          int *a15,
          int *a16,
          _BYTE *a17,
          int a18)
   */
    /*
    特征
      v90 = *v81;
              if ( (unsigned __int16)(v90 - 11784) > 0x71F7u
                && (unsigned __int16)(v90 + 21504) > 0x2BFFu
                && (unsigned __int16)(v90 + 1792) > 0x1FFu
                && (unsigned __int16)(v90 + 464) > 0x1Fu
                && (unsigned __int16)(v90 + 155) > 0x77u )


                */
    /*
    const CharType current = c[end];
     const bool separatable = (current >= 0x2E08 && current <= 0x9FFF) || // CJK scripts and symbols.
         (current >= 0xAC00 && current <= 0xD7FF) || // Hangul Syllables and Hangul Jamo Extended-B.
         (current >= 0xF900 && current <= 0xFAFF) || // CJK Compatibility Ideographs.
         (current >= 0xFE30 && current <= 0xFE4F) || // CJK Compatibility Forms.
         (current >= 0xFF65 && current <= 0xFF9F) || // Halfwidth forms of katakana
         (current >= 0xFFA0 && current <= 0xFFDC) || // Halfwidth forms of compatibility jamo characters for Hangul
         (current >= 0x20000 && current <= 0x2FA1F) || // CJK Unified Ideographs Extension B ~ F and CJK Compatibility Ideographs Supplement.
         (current >= 0x30000 && current <= 0x3134F); // CJK Unified Ideographs Extension G.
    */
    /*
    这个函数是scene/gui/rich_text_label.cpp
    int RichTextLabel::_process_line(ItemFrame *p_frame, const Vector2 &p_ofs, int &y, int p_width, int p_line, ProcessMode p_mode, const Ref<Font> &p_base_font, const Color &p_base_color, const Color &p_font_color_shadow, bool p_shadow_as_outline, const Point2 &shadow_ofs, const Point2i &p_click_pos, Item **r_click_item, int *r_click_char, bool *r_outside, int p_char_count)
    */
    BYTE sig[] = {
        /*
        .text:017FA34C                 movzx   eax, word ptr [esi]
      .text:017FA34F                 lea     edx, [eax-2E08h]
      .text:017FA355                 cmp     dx, 71F7h
      .text:017FA35A                 lea     edx, [eax+5400h]
      .text:017FA360                 setbe   cl
      .text:017FA363                 cmp     dx, 2BFFh
      .text:017FA368                 setbe   dl
      .text:017FA36B                 or      dl, cl
      .text:017FA36D                 jz      loc_17FA230
        */
        0x0f,
        0xb7,
        0x06,
        0x8D,
        0x90,
        0xF8,
        0xD1,
        0xFF,
        0xFF,
        0x66,
        0x81,
        0xFA,
        0xF7,
        0x71,
        0x8D,
        0x90,
        0x00,
        0x54,
        0x00,
        0x00,
        0x0F,
        0x96,
        0xC1,
        0x66,
        0x81,
        0xFA,
        0xFF,
        0x2B,
        0x0F,
        0x96,
        0xc2,
        0x08,
        0xca,
        0x0f,
        0x84,
    };
    auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    BYTE sig2[] = {
        // shl     esi, 6
        0xC1, 0xE6, 0x06};
    addr = reverseFindBytes(sig2, sizeof(sig2), addr - 0x1800, addr);
    if (!addr)
      return false;
    BYTE sig3[] = {0x01, 0xF0}; // add     eax, esi
    addr = MemDbg::findBytes(sig3, sizeof(sig3), addr, addr + 0x40);

    if (!addr)
      return false;

    HookParam hp;
    hp.address = addr + sizeof(sig3);

    hp.type = USING_STRING | CODEC_UTF16;
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      /*
      Line &l = p_frame->lines.write[p_line];
    Item *it = l.from;
    */
      /*
      while (it) {
       switch (it->type) {
         case ITEM_ALIGN: {
           ItemAlign *align_it = static_cast<ItemAlign *>(it);

           align = align_it->align;

         } break;
         case ITEM_INDENT: {
           if (it != l.from) {
             ItemIndent *indent_it = static_cast<ItemIndent *>(it);

             float indent = indent_it->level * tab_size * cfont->get_char_size(' ').width;
             margin += indent;
             begin += indent;
             wofs += indent;
           }

         } break;
         case ITEM_TEXT: {
           ItemText *text = static_cast<ItemText *>(it);

           Ref<Font> font = _find_font(it);
           if (font.is_null()) {
             font = p_base_font;
           }

           const CharType *c = text->text.c_str();
           const CharType *cf = c;
           */
      /*
      struct ItemText : public Item {
          String text;
          ItemText() { type = ITEM_TEXT; }
        };
      */
      /*
      const CharType *String::c_str() const {
 static const CharType zero = 0;

 return size() ? &operator[](0) : &zero;
}
      */

      // Line &l = p_frame->lines.write[p_line];
      // Item *it = l.from;

      // auto v471 = (int *)((a7 << 6) + *(DWORD *)(a3 + 40));

      if (context->retaddr != 1)
        return; // 不懂为什么这个是1，按理说返回地址应该一样才对。不管了无所谓
      auto v471 = (DWORD *)context->eax;
      auto v481 = *v471;
      auto ptr = *(WCHAR **)(v481 + 28);
      buffer->from(ptr);
    };

    return NewHook(hp, "godot35");
  }
}
bool godot::attach_function()
{
  auto version = queryversion();
  if (version && std::get<0>(version.value()) == 3 && std::get<1>(version.value()) == 5)
  {
    return godot35();
  }
  return false;
}