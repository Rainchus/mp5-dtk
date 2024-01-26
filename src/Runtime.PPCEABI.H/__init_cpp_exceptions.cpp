#include "Runtime.PPCEABI.H/NMWException.h"

#if __MWERKS__
#pragma exceptions off
#pragma internal on
#endif

#ifdef __cplusplus
extern "C" {
#endif

void __init_cpp_exceptions(void);
void __fini_cpp_exceptions(void);

typedef struct __eti_init_info {
    void* eti_start;
    void* eti_end;
    void* code_start;
    unsigned long code_size;
} __eti_init_info;

extern __eti_init_info _eti_init_info[];

#ifdef __cplusplus
}
#endif

static int fragmentID = -2;

/* clang-format off */
static asm char* GetR2() {
  nofralloc;
  mr r3, r2
  blr
}
/* clang-format on */

void __init_cpp_exceptions(void) {
    char* R2;
    if (fragmentID == -2) {
        R2 = GetR2();
        fragmentID = __register_fragment(_eti_init_info, R2);
    }
}

void __fini_cpp_exceptions(void) {
    if (fragmentID != -2) {
        __unregister_fragment(fragmentID);
        fragmentID = -2;
    }
}

/* clang-format off */
__declspec(section ".ctors")
extern void* const __init_cpp_exceptions_reference = __init_cpp_exceptions;
__declspec(section ".dtors")
extern void* const __destroy_global_chain_reference = __destroy_global_chain;
__declspec(section ".dtors")
extern void* const __fini_cpp_exceptions_reference = __fini_cpp_exceptions;
/* clang-format on */
