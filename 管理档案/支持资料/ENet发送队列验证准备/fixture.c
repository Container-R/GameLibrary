/* Original finite observer; all ENet behavior is linked from unchanged upstream. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "enet/enet.h"

typedef struct { int length, flags, u, channel, cmd, r_end, u_end, g_end; } Case;
static const Case cases[] = {
 {1364,0,65534,0,7,42,65535,7}, {1364,0,65535,0,134,43,0,7},
 {1364,8,65534,0,7,42,65535,7}, {1364,8,65535,0,134,43,0,7},
 {1364,1,65534,0,134,43,0,7}, {1364,1,65535,0,134,43,0,7},
 {1364,2,65534,0,73,42,65534,8}, {1364,2,65535,0,73,42,65535,8},
 {1365,0,65534,0,136,44,0,7}, {1365,0,65535,0,136,44,0,7},
 {1365,8,65534,0,12,42,65535,7}, {1365,8,65535,0,136,44,0,7},
 {1365,1,65534,0,136,44,0,7}, {1365,1,65535,0,136,44,0,7},
 {1365,2,65534,0,136,44,0,7}, {1365,2,65535,0,136,44,0,7},
 {1365,1,65535,1,-1,42,65535,7}
};
typedef struct { int count; size_t refs, length; enet_uint32 flags; } Freed;
static const char * boolean(int b) { return b ? "true" : "false"; }
static void ENET_CALLBACK observed_free(ENetPacket *p) {
 Freed *f=(Freed *)p->userData;
 ++f->count; f->refs=p->referenceCount; f->flags=p->flags; f->length=p->dataLength;
}
static int peer_empty(ENetPeer *p) {
 return enet_list_empty(&p->acknowledgements) && enet_list_empty(&p->sentReliableCommands)
 && enet_list_empty(&p->outgoingCommands) && enet_list_empty(&p->outgoingSendReliableCommands)
 && enet_list_empty(&p->dispatchedCommands);
}
static int setup(ENetHost *h, ENetPeer *p, int u) {
 memset(h,0,sizeof(*h)); memset(p,0,sizeof(*p));
 h->socket=ENET_SOCKET_NULL; h->mtu=1392;
 h->maximumPacketSize=ENET_HOST_DEFAULT_MAXIMUM_PACKET_SIZE;
 h->maximumWaitingData=ENET_HOST_DEFAULT_MAXIMUM_WAITING_DATA;
 h->peers=p; h->peerCount=1; h->channelLimit=1; enet_list_clear(&h->dispatchQueue);
 p->host=h; p->incomingSessionID=p->outgoingSessionID=0xFF;
 enet_list_clear(&p->acknowledgements); enet_list_clear(&p->sentReliableCommands);
 enet_list_clear(&p->outgoingCommands); enet_list_clear(&p->outgoingSendReliableCommands);
 enet_list_clear(&p->dispatchedCommands);
 enet_peer_reset(p);
 p->channels=(ENetChannel *)enet_malloc(sizeof(ENetChannel));
 if (!p->channels) return 0;
 p->channelCount=1; memset(p->channels,0,sizeof(ENetChannel));
 enet_list_clear(&p->channels[0].incomingReliableCommands);
 enet_list_clear(&p->channels[0].incomingUnreliableCommands);
 p->channels[0].outgoingReliableSequenceNumber=42;
 p->channels[0].outgoingUnreliableSequenceNumber=(enet_uint16)u;
 p->outgoingUnsequencedGroup=7;
 enet_peer_on_connect(p); p->state=ENET_PEER_STATE_CONNECTED;
 return p->mtu==1392 && h->checksum==NULL && h->connectedPeers==1
 && h->bandwidthLimitedPeers==0 && h->totalQueued==0 && p->outgoingDataTotal==0
 && p->incomingBandwidth==0 && p->channelCount==1 && p->channels[0].usedReliableWindows==0
 && p->channels[0].incomingReliableSequenceNumber==0 && p->channels[0].incomingUnreliableSequenceNumber==0
 && peer_empty(p) && enet_list_empty(&h->dispatchQueue)
 && enet_list_empty(&p->channels[0].incomingReliableCommands)
 && enet_list_empty(&p->channels[0].incomingUnreliableCommands);
}
/* Reads only initialized members for the observed command kind; never dumps unions. */
static int print_queue(ENetList *q, ENetPacket *packet, const Case *c, int wanted) {
 int i=0, ok=1;
 ENetListIterator it;
 printf("[");
 for(it=enet_list_begin(q); it!=enet_list_end(q); it=enet_list_next(it)) {
  ENetOutgoingCommand *o=(ENetOutgoingCommand *)it;
  unsigned int cmd=o->command.header.command, base=cmd & ENET_PROTOCOL_COMMAND_MASK;
  unsigned int er=(c->cmd==134 || c->cmd==136)?43+i:(c->cmd==73?0:42);
  unsigned int eu=(c->cmd==7 || c->cmd==12)?65535:0;
  unsigned int offset=i?1364:0, length=i?1:1364;
  if(i>=2) { ok=0; break; } /* bounded traversal on a malformed result */
  if(i) printf(",");
  printf("[%u,%u,%u,%u,%u,%u,%u,%s,%u,%u,%u,%u,[",
   cmd,o->command.header.channelID,ENET_NET_TO_HOST_16(o->command.header.reliableSequenceNumber),
   o->reliableSequenceNumber,o->unreliableSequenceNumber,o->fragmentOffset,o->fragmentLength,
   boolean(o->packet==packet),o->sendAttempts,o->sentTime,o->roundTripTimeout,o->queueTime);
  ok=ok && cmd==(unsigned)c->cmd && o->command.header.channelID==0
    && ENET_NET_TO_HOST_16(o->command.header.reliableSequenceNumber)==er
    && o->reliableSequenceNumber==er && o->unreliableSequenceNumber==eu
    && o->fragmentOffset==offset && o->fragmentLength==length && o->packet==packet
    && o->sendAttempts==0 && o->sentTime==0 && o->roundTripTimeout==0 && o->queueTime==(unsigned)i+1;
  if(base==ENET_PROTOCOL_COMMAND_SEND_FRAGMENT || base==ENET_PROTOCOL_COMMAND_SEND_UNRELIABLE_FRAGMENT) {
   ENetProtocolSendFragment *f=&o->command.sendFragment;
   unsigned int start=ENET_NET_TO_HOST_16(f->startSequenceNumber), len=ENET_NET_TO_HOST_16(f->dataLength);
   unsigned int count=ENET_NET_TO_HOST_32(f->fragmentCount), number=ENET_NET_TO_HOST_32(f->fragmentNumber);
   unsigned int total=ENET_NET_TO_HOST_32(f->totalLength), off=ENET_NET_TO_HOST_32(f->fragmentOffset);
   printf("%u,%u,%u,%u,%u,%u",start,len,count,number,total,off);
   ok=ok && start==(c->cmd==136?43u:65535u) && len==length && count==2 && number==(unsigned)i && total==1365 && off==offset;
  } else if(base==ENET_PROTOCOL_COMMAND_SEND_RELIABLE) {
   unsigned int len=ENET_NET_TO_HOST_16(o->command.sendReliable.dataLength);
   printf("%u",len); ok=ok && len==1364;
  } else if(base==ENET_PROTOCOL_COMMAND_SEND_UNRELIABLE) {
   unsigned int seq=ENET_NET_TO_HOST_16(o->command.sendUnreliable.unreliableSequenceNumber);
   unsigned int len=ENET_NET_TO_HOST_16(o->command.sendUnreliable.dataLength);
   printf("%u,%u",seq,len); ok=ok && seq==65535 && len==1364;
  } else if(base==ENET_PROTOCOL_COMMAND_SEND_UNSEQUENCED) {
   unsigned int group=ENET_NET_TO_HOST_16(o->command.sendUnsequenced.unsequencedGroup);
   unsigned int len=ENET_NET_TO_HOST_16(o->command.sendUnsequenced.dataLength);
   printf("%u,%u",group,len); ok=ok && group==8 && len==1364;
  } else ok=0;
  printf("]]"); ++i;
 }
 printf("]"); return ok && i==wanted;
}
static int run_case(int id) {
 const Case *c=&cases[id]; ENetHost h; ENetPeer p; ENetPacket *packet;
 Freed freed={0,0,0,0}; unsigned char input[1365]; int j,rc,ok,other;
 int n=c->channel?0:(c->length==1364?1:2);
 unsigned int data_total=n==0?0:(n==2?1413:(c->cmd==134?1370:1372));
 if(!setup(&h,&p,c->u)) { fprintf(stderr,"setup failed at row %d\n",id); enet_peer_reset(&p); return 0; }
 for(j=0;j<c->length;++j) input[j]=(unsigned char)(j%251);
 packet=enet_packet_create(input,(size_t)c->length,(enet_uint32)c->flags);
 if(!packet) { enet_peer_reset(&p); fprintf(stderr,"allocation failed\n"); return 0; }
 packet->userData=&freed; packet->freeCallback=observed_free;
 if(packet->referenceCount!=0 || packet->dataLength!=(size_t)c->length || packet->flags!=(unsigned)c->flags) {
  enet_packet_destroy(packet); enet_peer_reset(&p); fprintf(stderr,"packet setup failed\n"); return 0;
 }
 printf("{\"kind\":\"row\",\"id\":%d,\"input\":[%d,%d,%d,%d],\"before\":[%u,%u,%u,%u,%u,%zu],",
 id,c->length,c->flags,c->u,c->channel,p.channels[0].outgoingReliableSequenceNumber,
 p.channels[0].outgoingUnreliableSequenceNumber,p.outgoingUnsequencedGroup,h.totalQueued,p.outgoingDataTotal,packet->referenceCount);
 rc=enet_peer_send(&p,(enet_uint8)c->channel,packet);
 ok=rc==(c->channel?-1:0) && packet->referenceCount==(size_t)n && packet->flags==(unsigned)c->flags
 && packet->dataLength==(size_t)c->length && memcmp(packet->data,input,c->length)==0;
 printf("\"result\":%d,\"packet\":[%zu,%u,%zu,%s],\"state\":[%u,%u,%u,%u,%u,%zu],\"ordinary\":",
 rc,packet->referenceCount,packet->flags,packet->dataLength,boolean(memcmp(packet->data,input,c->length)==0),
 p.channels[0].outgoingReliableSequenceNumber,p.channels[0].outgoingUnreliableSequenceNumber,
 p.outgoingUnsequencedGroup,h.totalQueued,p.outgoingDataTotal,h.connectedPeers);
 ok=print_queue(&p.outgoingCommands,packet,c,(c->cmd==7||c->cmd==73||c->cmd==12)?n:0) && ok;
 printf(",\"reliable\":");
 ok=print_queue(&p.outgoingSendReliableCommands,packet,c,(c->cmd==134||c->cmd==136)?n:0) && ok;
 other=enet_list_empty(&p.acknowledgements) && enet_list_empty(&p.sentReliableCommands)
 && enet_list_empty(&p.dispatchedCommands) && enet_list_empty(&h.dispatchQueue)
 && enet_list_empty(&p.channels[0].incomingReliableCommands) && enet_list_empty(&p.channels[0].incomingUnreliableCommands);
 ok=ok && other && p.channels[0].outgoingReliableSequenceNumber==c->r_end
 && p.channels[0].outgoingUnreliableSequenceNumber==c->u_end && p.outgoingUnsequencedGroup==c->g_end
 && h.totalQueued==(unsigned)n && p.outgoingDataTotal==data_total && h.connectedPeers==1 && freed.count==0;
 printf(",\"other_empty\":%s,\"freed_before\":%d,",boolean(other),freed.count);
 /* Preserve observations before any cleanup; never repair ambiguous ownership. */
 fflush(stdout);
 if(!ok) {
  printf("\"cleanup\":null}\n"); fflush(stdout);
  fprintf(stderr,"row %d mismatch; ownership cleanup skipped, stopped\n",id);
  return 0; /* process exit reclaims storage; this is not a leak-proof claim */
 }
 if(packet->referenceCount==0) {
  if(!enet_list_empty(&p.outgoingCommands) || !enet_list_empty(&p.outgoingSendReliableCommands)) {
   printf("\"cleanup\":null}\n"); fflush(stdout);
   fprintf(stderr,"ambiguous packet ownership; stopped\n"); return 0;
  }
  enet_packet_destroy(packet);
 }
 enet_peer_reset(&p); /* packet must not be accessed after this point */
 printf("\"cleanup\":[%d,%zu,%u,%zu,%s,%zu,%s,%zu,%s,%u,%u]}\n",
 freed.count,freed.refs,freed.flags,freed.length,boolean(p.channels==NULL),p.channelCount,
 boolean(p.state==ENET_PEER_STATE_DISCONNECTED),h.connectedPeers,
 boolean(peer_empty(&p)&&enet_list_empty(&h.dispatchQueue)),h.totalQueued,p.outgoingDataTotal);
 ok=ok && freed.count==1 && freed.refs==0 && freed.flags==(unsigned)c->flags && freed.length==(size_t)c->length
 && p.channels==NULL && p.channelCount==0 && p.state==ENET_PEER_STATE_DISCONNECTED && h.connectedPeers==0
 && peer_empty(&p) && enet_list_empty(&h.dispatchQueue) && h.totalQueued==(unsigned)n && p.outgoingDataTotal==0;
 fflush(stdout); if(!ok) fprintf(stderr,"row %d mismatch; stopped\n",id); return ok;
}
int main(int argc,char **argv) {
 int i; size_t n;
 if(argc!=2 || strlen(argv[1])!=36) return 2;
 for(n=0;n<36;++n) if(!((argv[1][n]>='0'&&argv[1][n]<='9')||(argv[1][n]>='a'&&argv[1][n]<='f')||argv[1][n]=='-')) return 2;
 if(ENET_VERSION!=66322 || enet_linked_version()!=66322 || sizeof(enet_uint16)!=2 || sizeof(enet_uint32)!=4
 || sizeof(ENetProtocolHeader)!=4 || sizeof(ENetProtocolSendFragment)!=24 || sizeof(ENetProtocolSendReliable)!=6
 || sizeof(ENetProtocolSendUnreliable)!=8 || sizeof(ENetProtocolSendUnsequenced)!=8) { fprintf(stderr,"ABI/version mismatch\n"); return 2; }
 printf("{\"kind\":\"start\",\"run\":\"%s\",\"version\":%u,\"sizes\":[%zu,%zu,%zu,%zu,%zu,%zu,%zu],\"F\":1364}\n",argv[1],enet_linked_version(),sizeof(enet_uint16),sizeof(enet_uint32),sizeof(ENetProtocolHeader),sizeof(ENetProtocolSendFragment),sizeof(ENetProtocolSendReliable),sizeof(ENetProtocolSendUnreliable),sizeof(ENetProtocolSendUnsequenced));
 for(i=0;i<17;++i) if(!run_case(i)) return 1;
 printf("{\"kind\":\"end\",\"run\":\"%s\",\"rows\":17}\n",argv[1]);
 return ferror(stdout)?3:0;
}
