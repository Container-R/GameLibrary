/* Original bounded observation harness; no network or arbitrary input paths. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include "vendor/zstddeclib.c"

static const unsigned char literal[] = "abcdefghijklmnopqrstuvwxyz0123456";
static int hexval(int c) {
    if (c >= '0' && c <= '9') return c-'0';
    if (c >= 'a' && c <= 'f') return c-'a'+10;
    if (c >= 'A' && c <= 'F') return c-'A'+10;
    return -1;
}
static int fixture(const char *name, unsigned char *dst, size_t expected,
                   unsigned char block0, size_t payload) {
    FILE *f = fopen(name, "rb");
    size_t n=0; int c, hi=-1;
    const unsigned char head[6]={0x28,0xb5,0x2f,0xfd,0,0};
    if (!f) return 0;
    while ((c=fgetc(f)) != EOF) {
        int v;
        if (c==' ' || c=='\n' || c=='\r' || c=='\t') continue;
        v=hexval(c);
        if (v<0 || n>=64) { fclose(f); return 0; }
        if (hi<0) hi=v;
        else { dst[n++]=(unsigned char)(hi*16+v); hi=-1; }
    }
    c=ferror(f); if (fclose(f)!=0) return 0;
    return !c && hi<0 && n==expected && expected==9+payload &&
        memcmp(dst,head,6)==0 && dst[6]==block0 && dst[7]==1 && dst[8]==0 &&
        memcmp(dst+9,literal,payload)==0;
}
static int observe(const char *id, const char *path, size_t n,
                   unsigned char block0, size_t payload, int wanted) {
    unsigned char input_bytes[64], out[8], accepted_bytes[32];
    ZSTD_DStream *stream;
    ZSTD_inBuffer input;
    size_t accepted=0, produced_total=0, calls;
    int complete=0, status=0; /* 1 accepted; 2 budget; 3 incomplete; 4 library error */
    if (!fixture(path,input_bytes,n,block0,payload)) return 0;
    if (ZSTD_getFrameContentSize(input_bytes,n)!=ZSTD_CONTENTSIZE_UNKNOWN) return 0;
    stream=ZSTD_createDStream(); if (!stream) return 0;
    if (ZSTD_isError(ZSTD_initDStream(stream))) { ZSTD_freeDStream(stream); return 0; }
    input.src=input_bytes; input.size=n; input.pos=0;
    for (calls=1; calls<=64; ++calls) {
        size_t before=input.pos, ret;
        ZSTD_outBuffer output={out,sizeof(out),0};
        const char *kind;
        ret=ZSTD_decompressStream(stream,&output,&input);
        if (input.pos>input.size || output.pos>sizeof(out)) { status=0; break; }
        kind=ZSTD_isError(ret)?"error":(ret==0?"frame_end":"pending");
        if (ZSTD_isError(ret)) {
            printf("case=%s call=%zu in_before=%zu in_after=%zu produced=%zu accepted=%zu return=%s\n",
                   id,calls,before,input.pos,output.pos,accepted,kind);
            status=4; break; /* Error output is not consumed. */
        }
        complete=(ret==0);
        if (produced_total>payload || output.pos>payload-produced_total ||
            memcmp(out,literal+produced_total,output.pos)!=0) { status=0; break; }
        if (produced_total>512-output.pos) { status=0; break; }
        produced_total+=output.pos;
        if (accepted>32 || output.pos>32-accepted) status=2;
        else {
            memcpy(accepted_bytes+accepted,out,output.pos);
            accepted+=output.pos;
        }
        printf("case=%s call=%zu in_before=%zu in_after=%zu produced=%zu accepted=%zu return=%s\n",
               id,calls,before,input.pos,output.pos,accepted,kind);
        if (status==2) break; /* Whole new block refused; old prefix not published. */
        if (complete) {
            status=(input.pos==input.size && accepted==32 &&
                    memcmp(accepted_bytes,literal,32)==0)?1:0;
            break;
        }
        if (input.pos==input.size && output.pos<output.size) {
            status=3; break; /* EOF, pending, and all available output flushed. */
        }
        if (input.pos==before && output.pos==0) { status=0; break; }
    }
    if (calls>64) status=0;
    /* Distinct acceptance oracles: never turn partial output into an asset. */
    if (wanted==1 && !(status==1 && complete && accepted==32 && produced_total==32)) status=0;
    if (wanted==2 && !(status==2 && accepted<=32 && produced_total>32 &&
                      memcmp(accepted_bytes,literal,accepted)==0)) status=0;
    if (wanted==3 && !((status==3 || status==4) && !complete && accepted<=31 &&
                      memcmp(accepted_bytes,literal,accepted)==0)) status=0;
    printf("case=%s final=%s frame_complete=%d asset_accepted=%d produced_total=%zu accepted_total=%zu input_consumed=%zu input_size=%zu\n",
           id,status==1?"accepted":status==2?"budget_rejected":status==3?"incomplete":status==4?"library_error":"unexpected",
           complete,status==1,produced_total,accepted,input.pos,input.size);
    if (ZSTD_isError(ZSTD_freeDStream(stream))) return 0;
    return status!=0 && (wanted==3 ? (status==3 || status==4) : status==wanted);
}
int main(void) {
    if (CHAR_BIT!=8 || ZSTD_versionNumber()!=10507) return 1;
    if (!observe("R32","fixtures/r32.hex",41,0x01,32,1)) return 1;
    if (!observe("R33","fixtures/r33.hex",42,0x09,33,2)) return 1;
    if (!observe("R32_truncated","fixtures/r32-truncated.hex",40,0x01,31,3)) return 1;
    puts("PASS three bounded cases");
    return 0;
}
