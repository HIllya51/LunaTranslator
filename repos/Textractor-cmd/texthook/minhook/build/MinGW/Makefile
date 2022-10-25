WINDRES:=$(CROSS_PREFIX)windres
DLLTOOL:=$(CROSS_PREFIX)dlltool
AR:=$(CROSS_PREFIX)ar
CC:=$(CROSS_PREFIX)gcc
CCLD:=$(CC)
SRCS:=$(wildcard src/*.c src/hde/*.c)
OBJS:=$(SRCS:%.c=%.o)
DEPS:=$(SRCS:%.c=%.d)
INCS:=-Isrc -Iinclude
CFLAGS:=-masm=intel -Wall -Werror -std=c11
LDFLAGS:=-Wl,-enable-stdcall-fixup -s -static-libgcc

all: MinHook.dll libMinHook.dll.a libMinHook.a

-include $(DEPS)

libMinHook.a: $(OBJS)
	$(AR) r $@ $^
libMinHook.dll.a: MinHook.dll dll_resources/MinHook.def
	$(DLLTOOL) --dllname MinHook.dll --def dll_resources/MinHook.def --output-lib $@
MinHook.dll: $(OBJS) dll_resources/MinHook.res dll_resources/MinHook.def
	$(CCLD) -o $@ -shared $(LDFLAGS) $^

.rc.res:
	$(WINDRES) -o $@ --input-format=rc --output-format=coff $<
.c.o:
	$(CC) -o $@ -c -MMD -MP $(INCS) $(CFLAGS) $<

clean:
	rm -f $(OBJS) $(DEPS) MinHook.dll libMinHook.dll.a libMinHook.a dll_resources/MinHook.res

.PHONY: clean
.SUFFIXES: .rc .res
