/* Original finite callback/receiver fixture. Uses unchanged MikkTSpace separately. */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "mikktspace.h"

static const float positions[4][3] = {{0,0,0},{1,0,0},{0,1,0},{0,-1,0}};
static const float uvs[4][2] = {{0,0},{1,0},{0,1},{0,1}};
static const int faces[2][3] = {{0,1,2},{0,3,1}};
typedef struct { float p[3], n[3], uv[2], t[3], sign; } Record;
typedef struct { Record corner[6]; int seen[6], order[6], count; } Capture;
static void fail(const char *message) { fprintf(stderr, "%s\n", message); exit(2); }
static int key(int face, int corner) {
    if (face < 0 || face >= 2 || corner < 0 || corner >= 3) fail("callback index out of range");
    return 3*face+corner;
}
static int count_faces(const SMikkTSpaceContext *ctx) { (void)ctx; return 2; }
static int count_corners(const SMikkTSpaceContext *ctx, int face) {
    (void)ctx; (void)key(face,0); return 3;
}
static void position(const SMikkTSpaceContext *ctx, float out[], int face, int corner) {
    (void)ctx; (void)key(face,corner); memcpy(out,positions[faces[face][corner]],3*sizeof(float));
}
static void normal(const SMikkTSpaceContext *ctx, float out[], int face, int corner) {
    (void)ctx; (void)key(face,corner); out[0]=0; out[1]=0; out[2]=1;
}
static void texcoord(const SMikkTSpaceContext *ctx, float out[], int face, int corner) {
    (void)ctx; (void)key(face,corner); memcpy(out,uvs[faces[face][corner]],2*sizeof(float));
}
static void receive(const SMikkTSpaceContext *ctx, const float tangent[], float sign, int face, int corner) {
    Capture *capture=(Capture *)ctx->m_pUserData;
    int k=key(face,corner), j;
    if (capture->seen[k] || capture->count>=6) fail("duplicate or excessive output callback");
    for (j=0;j<3;j++) if (!isfinite(tangent[j])) fail("nonfinite tangent");
    if (!isfinite(sign)) fail("nonfinite sign");
    position(ctx,capture->corner[k].p,face,corner);
    normal(ctx,capture->corner[k].n,face,corner);
    texcoord(ctx,capture->corner[k].uv,face,corner);
    memcpy(capture->corner[k].t,tangent,3*sizeof(float));
    capture->corner[k].sign=sign;
    capture->seen[k]=1; capture->order[capture->count++]=k;
}
/* Row: face,corner,old,P.xyz,N.xyz,UV.xy,T.xyz,sign. */
static void row(int k, const Record *r) {
    printf("[%d,%d,%d,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g]",
        k/3,k%3,faces[k/3][k%3],(double)r->p[0],(double)r->p[1],(double)r->p[2],
        (double)r->n[0],(double)r->n[1],(double)r->n[2],(double)r->uv[0],(double)r->uv[1],
        (double)r->t[0],(double)r->t[1],(double)r->t[2],(double)r->sign);
}
static void rows(const Record records[6]) {
    int k; putchar('['); for(k=0;k<6;k++) { if(k) putchar(','); row(k,&records[k]); } putchar(']');
}
int main(void) {
    Capture capture={0};
    SMikkTSpaceInterface api={0}; SMikkTSpaceContext ctx;
    Record correct[6], slots[4], forward[6], reverse[6];
    const int indices[2][3]={{0,1,2},{3,4,5}};
    int k, face, corner, generated;
    api.m_getNumFaces=count_faces; api.m_getNumVerticesOfFace=count_corners;
    api.m_getPosition=position; api.m_getNormal=normal; api.m_getTexCoord=texcoord;
    api.m_setTSpaceBasic=receive; api.m_setTSpace=NULL;
    ctx.m_pInterface=&api; ctx.m_pUserData=&capture;
    generated=genTangSpaceDefault(&ctx); /* The only generator invocation. */
    if (!generated || capture.count!=6) fail("generator failure or missing output");
    for(k=0;k<6;k++) if(capture.seen[k]!=1) fail("missing face corner");
    for(k=0;k<6;k++) correct[k]=capture.corner[k];
    for(k=0;k<6;k++) slots[faces[k/3][k%3]]=capture.corner[k];
    for(k=0;k<6;k++) forward[k]=slots[faces[k/3][k%3]];
    for(k=5;k>=0;k--) slots[faces[k/3][k%3]]=capture.corner[k];
    for(k=0;k<6;k++) reverse[k]=slots[faces[k/3][k%3]];
    printf("{\"schema\":1,\"generated\":%d,\"output_count\":%d,\"callback_order\":[",generated,capture.count);
    for(k=0;k<6;k++) { if(k) putchar(','); printf("%d",capture.order[k]); }
    printf("],\"raw\":"); rows(capture.corner);
    printf(",\"reindexed\":[");
    for(face=0;face<2;face++) for(corner=0;corner<3;corner++) {
        k=3*face+corner; if(k) putchar(','); row(k,&correct[indices[face][corner]]);
    }
    printf("],\"new_indices\":[[0,1,2],[3,4,5]],\"forward_readback\":"); rows(forward);
    printf(",\"reverse_readback\":"); rows(reverse); printf("}\n");
    if (fflush(stdout)!=0 || ferror(stdout)) return 3;
    return 0;
}
