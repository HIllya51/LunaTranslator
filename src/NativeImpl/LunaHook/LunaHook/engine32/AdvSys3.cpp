#include "AdvSys3.h"

/**
 * AdvSys3 (MINS, ADVSYS3.EXE) — いちょう (icho, 1998)
 *
 * 逆向分析结论 (icho.exe, PE32, 固定基址 0x400000, 无ASLR, MFC4静态链接):
 *
 * 文本层对象 (vptr=0x44c4c0, vtable+8 = TextLayer::Draw):
 *   +0x84  VDim::data   单元格数组指针
 *   +0x88  VDim::size   数组字节数, 恒等于 rows*cols*12 (结构自校验用)
 *   +0x8c  VDim::ndims  维度数 (2)
 *   +0x90  VDim::dims   维度数组指针 -> [rows, cols] (本作 [12, 45])
 * 单元格 12 字节:
 *   +0     state (dword, 1=可见)
 *   +4     字符 (最多3字节: 一个SJIS全角字符 + '\0')
 *   +7/8/9 RGB
 * 索引 = col*rows + row;  row = 文本行号(0..rows), col = 水平位置(0..cols)。
 *
 * 文本绘制流程: TextLayer::Draw(0x419370, this=层ecx) 每帧遍历网格,
 * 对每个可见单元格调用 ExtTextOutA — 因此 GDI hook 只能读到逐字刷新的
 * 碎片。正确做法是 hook Draw 入口, 每次触发时重建整个网格文本,
 * 并等文本稳定(打字机效果结束)后再输出完整句子。
 */
namespace
{
    constexpr int GRID_DATA = 0x84;
    constexpr int GRID_BYTES = 0x88;
    constexpr int GRID_NDIMS = 0x8c;
    constexpr int GRID_DIMS = 0x90;
    constexpr int CELL = 12;

    // 从文本层网格重建完整文本; row=行, col=列, 跳过空格按行列序拼接
    bool readGrid(uintptr_t layer, std::string &out)
    {
        if (layer < 0x10000)
            return false;
        auto cells = *(uintptr_t *)(layer + GRID_DATA);
        auto bytes = *(uint32_t *)(layer + GRID_BYTES);
        auto ndims = *(uint32_t *)(layer + GRID_NDIMS);
        auto dims = *(uintptr_t *)(layer + GRID_DIMS);
        if (cells < 0x10000 || dims < 0x10000 || ndims != 2)
            return false;
        auto rows = *(uint32_t *)dims;
        auto cols = *(uint32_t *)(dims + 4);
        if (rows == 0 || rows > 0x200 || cols == 0 || cols > 0x800)
            return false;
        // 强校验: 字节数必须等于 rows*cols*12, 防止误把其它层当文本层
        if (bytes != (uint32_t)rows * cols * CELL)
            return false;
        auto base = (BYTE *)cells;
        out.clear();
        for (uint32_t row = 0; row < rows && out.size() < TEXT_BUFFER_SIZE; row++)
        {
            std::string line;
            for (uint32_t col = 0; col < cols; col++)
            {
                BYTE *cell = base + ((size_t)col * rows + row) * CELL;
                if (*(uint32_t *)cell != 1)
                    continue;
                for (int k = 0; k < 3 && cell[4 + k]; k++)
                    line.push_back((char)cell[4 + k]);
            }
            if (!line.empty())
            {
                if (!out.empty())
                    out.push_back('\n');
                out += line;
            }
        }
        return !out.empty();
    }

    // 文本稳定后(打字机效果结束)才输出完整的一行/一页
    void gridToBufferStable(TextBuffer *buffer, uintptr_t layer)
    {
        static std::string current, sent;
        static DWORD changed = 0;
        std::string text;
        if (!readGrid(layer, text))
            return;
        if (text != current)
        {
            current = text;
            changed = GetTickCount();
            return; // 仍在打字
        }
        if (GetTickCount() - changed < 400)
            return; // 变化后未稳定
        if (current.empty() || current == sent)
            return;
        sent = current;
        buffer->from(current);
    }
}

bool AdvSys3::attach_function()
{
    // TextLayer::Draw 入口 (0x419370), ecx=层; 每帧触发, 网格文本稳定后输出
    BYTE sig[] = {
        0x64, 0xA1, 0x00, 0x00, 0x00, 0x00,       // mov eax, fs:[0]
        0x55,                                     // push ebp
        0x8B, 0xEC,                               // mov ebp, esp
        0x6A, 0xFF,                               // push -1
        0x68, XX4,                                // push SEH
        0x50,                                     // push eax
        0x64, 0x89, 0x25, 0x00, 0x00, 0x00, 0x00, // mov fs:[0], esp
        0x81, 0xEC, 0xC8, 0x04, 0x00, 0x00,       // sub esp, 0x4c8
        0x83, 0x79, 0x20, 0x00                    // cmp [ecx+0x20], 0
    };
    auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr && processStartAddress <= 0x419370 && 0x419370 < processStopAddress)
        addr = 0x419370; // 本作无ASLR, 固定地址兜底
    if (!addr)
        return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | NO_CONTEXT | FULL_STRING;
    hp.codepage = SHIFT_JIS;
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        gridToBufferStable(buffer, context->ecx);
    };
    hp.filter_fun = [](TextBuffer *buffer, HookParam *)
    {
        static std::string last;
        auto s = buffer->strA();
        if (startWith(s, last))
        {
            auto _ = s.substr(last.size());
            buffer->from(strReplace(_, "\n"));
        }
        last = s;
    };
    return NewHook(hp, "AdvSys3Text");
}
