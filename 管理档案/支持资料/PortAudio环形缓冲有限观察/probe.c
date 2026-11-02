/* Original finite test driver, not a queue implementation. */
#include <stdio.h>
#include <string.h>
#include "pa_ringbuffer.h"

#define REQUIRE(c, id, phase) do { if (!(c)) { \
    fprintf(stderr,"{\"case\":%d,\"failure\":\"%s\"}\n",id,phase); return 1; \
} } while (0)
static int slot(void *p, int *storage) {
    for (int i=0;i<8;i++) if(p==(void *)&storage[i]) return i;
    return -1;
}
static int counts(PaUtilRingBuffer *q, long r, long w) {
    return PaUtil_GetRingBufferReadAvailable(q)==r &&
           PaUtil_GetRingBufferWriteAvailable(q)==w && r>=0 && w>=0 && r+w==8;
}
static void state(const char *phase,int id,long result,PaUtilRingBuffer *q) {
    printf("{\"case\":%d,\"phase\":\"%s\",\"returned\":%ld,\"readable\":%ld,\"writable\":%ld}\n",
        id,phase,result,(long)PaUtil_GetRingBufferReadAvailable(q),
        (long)PaUtil_GetRingBufferWriteAvailable(q));
}
static void sequence(const char *phase,int id,const char *quantity,long returned, const int *out,int n,PaUtilRingBuffer *q) {
    printf("{\"case\":%d,\"phase\":\"%s\",\"%s\":%ld,\"values\":[",id,phase,quantity,returned);
    for(int i=0;i<n;i++) printf("%s%d",i?",":"",out[i]);
    printf("],\"readable\":%ld,\"writable\":%ld}\n",
        (long)PaUtil_GetRingBufferReadAvailable(q),(long)PaUtil_GetRingBufferWriteAvailable(q));
}
static void regions(const char *phase,int id,long returned,long n1,long n2,void *p1,void *p2,int *s,PaUtilRingBuffer *q) {
    printf("{\"case\":%d,\"phase\":\"%s\",\"returned\":%ld,\"lengths\":[%ld,%ld],\"slots\":[%d,%d],\"readable\":%ld,\"writable\":%ld}\n",
        id,phase,returned,n1,n2,slot(p1,s),slot(p2,s),
        (long)PaUtil_GetRingBufferReadAvailable(q),(long)PaUtil_GetRingBufferWriteAvailable(q));
}
int main(void) {
    PaUtilRingBuffer a={0},b={0}; int sa[8]={0},sb[8]={0};
    const int a_in[9]={0,1,2,3,4,5,6,7,8}; int a_out[9];
    for(int i=0;i<9;i++) a_out[i]=-999;
    long ret=PaUtil_InitializeRingBuffer(&a,sizeof(int),8,sa);
    if(ret!=0) { printf("{\"case\":1,\"phase\":\"A_init\",\"returned\":%ld}\n",ret); REQUIRE(0,1,"A_init"); }
    state("A_init",1,ret,&a); REQUIRE(counts(&a,0,8),1,"A_init_counts");
    ret=PaUtil_WriteRingBuffer(&a,a_in,9);
    state("A_write",1,ret,&a); REQUIRE(ret==8 && counts(&a,8,0),1,"A_write");
    ret=PaUtil_ReadRingBuffer(&a,a_out,9);
    sequence("A_read",2,"returned",ret,a_out,9,&a);
    REQUIRE(ret==8 && counts(&a,0,8) && a_out[8]==-999,2,"A_read_counts");
    for(int i=0;i<8;i++) REQUIRE(a_out[i]==i,2,"A_read_values");

    const int b_in[6]={10,11,12,13,14,15}; int first[5];
    for(int i=0;i<5;i++) first[i]=-999;
    ret=PaUtil_InitializeRingBuffer(&b,sizeof(int),8,sb);
    if(ret!=0) { printf("{\"case\":3,\"phase\":\"B_init\",\"returned\":%ld}\n",ret); REQUIRE(0,3,"B_init"); }
    state("B_init",3,ret,&b); REQUIRE(counts(&b,0,8),3,"B_init_counts");
    ret=PaUtil_WriteRingBuffer(&b,b_in,6);
    state("B_write",3,ret,&b); REQUIRE(ret==6 && counts(&b,6,2),3,"B_write");
    ret=PaUtil_ReadRingBuffer(&b,first,5);
    sequence("B_read",3,"returned",ret,first,5,&b);
    REQUIRE(ret==5 && counts(&b,1,7),3,"B_read_counts");
    for(int i=0;i<5;i++) REQUIRE(first[i]==10+i,3,"B_read_values");

    void *p1=NULL,*p2=NULL; ring_buffer_size_t n1=-1,n2=-1;
    ret=PaUtil_GetRingBufferWriteRegions(&b,5,&p1,&n1,&p2,&n2);
    regions("B_get_write",4,ret,n1,n2,p1,p2,sb,&b);
    REQUIRE(ret==5 && n1==2 && n2==3 && p1==&sb[6] && p2==&sb[0] && counts(&b,1,7),4,"B_write_regions");
    const int later[5]={20,21,22,23,24};
    memcpy(p1,later,2*sizeof(int)); memcpy(p2,later+2,3*sizeof(int));
    printf("{\"case\":4,\"phase\":\"B_fill\",\"filled\":5,\"readable\":%ld,\"writable\":%ld}\n",(long)PaUtil_GetRingBufferReadAvailable(&b),(long)PaUtil_GetRingBufferWriteAvailable(&b)); REQUIRE(counts(&b,1,7),4,"B_fill_counts");
    ret=PaUtil_AdvanceRingBufferWriteIndex(&b,5);
    state("B_advance_write",5,ret,&b); REQUIRE(ret==11 && counts(&b,6,2),5,"B_advance_write");
    p1=NULL;p2=NULL;n1=-1;n2=-1;
    ret=PaUtil_GetRingBufferReadRegions(&b,6,&p1,&n1,&p2,&n2);
    regions("B_get_read",5,ret,n1,n2,p1,p2,sb,&b);
    REQUIRE(ret==6 && n1==3 && n2==3 && p1==&sb[5] && p2==&sb[0] && counts(&b,6,2),5,"B_read_regions");
    int out[6];for(int i=0;i<6;i++) out[i]=-999;
    memcpy(out,p1,3*sizeof(int));memcpy(out+3,p2,3*sizeof(int));
    sequence("B_copy_read",5,"copied",6,out,6,&b);
    const int expected[6]={15,20,21,22,23,24};
    REQUIRE(counts(&b,6,2),5,"B_copy_counts");
    for(int i=0;i<6;i++) REQUIRE(out[i]==expected[i],5,"B_copy_values");
    ret=PaUtil_AdvanceRingBufferReadIndex(&b,6);
    state("B_advance_read",6,ret,&b); REQUIRE(ret==11 && counts(&b,0,8),6,"B_advance_read");
    p1=NULL;p2=NULL; /* Old region pointers are no longer used. */
    int empty=-999;ret=PaUtil_ReadRingBuffer(&b,&empty,1);
    sequence("B_empty",6,"returned",ret,&empty,1,&b);
    REQUIRE(ret==0 && empty==-999 && counts(&b,0,8),6,"B_empty");
    return 0;
}
