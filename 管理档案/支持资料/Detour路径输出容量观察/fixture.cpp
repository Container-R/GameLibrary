// Original finite observation fixture; upstream Detour is linked unchanged.
#include "DetourNavMeshBuilder.h"
#include "DetourNavMeshQuery.h"
#include "DetourNode.h"
#include <cstdlib>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <vector>
#include <new>

static std::string setup = "null";
static std::vector<std::string> cases;
static std::vector<std::string> completed;
static std::ostringstream* partialCapture=0;
static std::string failureDetail;
static void quoted(const std::string& value) {
    std::cout << '"';
    for(size_t i=0;i<value.size();++i) {
        unsigned char c=static_cast<unsigned char>(value[i]);
        if(c=='"' || c=='\\') std::cout << '\\' << char(c);
        else if(c=='\n') std::cout << "\\n";
        else if(c=='\r') std::cout << "\\r";
        else if(c=='\t') std::cout << "\\t";
        else if(c<32) std::cout << "?";
        else std::cout << char(c);
    }
    std::cout << '"';
}
static int queryCalls = 0;
static int builderCalls=0, navCalls=0, initCalls=0;
static void emit(const char* status, const char* stage) {
    std::cout << "{\"protocol\":\"detour-capacity-v1\",\"commit\":\"6dc1667f580357e8a2154c28b7867bea7e8ad3a7\",\"status\":\"" << status
              << "\",\"stage\":\"" << stage << "\",\"completed\":[";
    for (size_t i=0;i<completed.size();++i) { if(i) std::cout<<','; std::cout<<'"'<<completed[i]<<'"'; }
    std::cout << "],\"query_calls\":" << queryCalls << ",\"setup\":" << setup << ",\"cases\":[";
    for(size_t i=0;i<cases.size();++i) { if(i) std::cout<<','; std::cout<<cases[i]; }
    std::cout << ']';
    if(std::string(status)=="fail") {
        std::cout << ",\"partial_setup_text\":";
        quoted(partialCapture ? partialCapture->str() : "");
        std::cout << ",\"failure_detail\":"; quoted(failureDetail);
    }
    std::cout << "}\n" << std::flush;
}
static void require(bool ok,const char* stage) {
    if(!ok) { emit("fail",stage); std::_Exit(1); }
}
static int refIndex(dtPolyRef ref,const dtPolyRef refs[3]) {
    for(int i=0;i<3;++i) if(ref==refs[i]) return i;
    return -1;
}
int main() {
    const unsigned short verts[24]={0,0,0, 1,0,0, 2,0,0, 3,0,0, 0,0,1, 1,0,1, 2,0,1, 3,0,1};
    const unsigned short polys[24]={0,4,5,1, 65535,65535,1,65535,
                                    1,5,6,2, 0,65535,2,65535,
                                    2,6,7,3, 1,65535,65535,65535};
    const unsigned short flags[3]={1,1,1}; const unsigned char areas[3]={0,0,0};
    const unsigned short neis[3][4]={{0,0,2,0},{1,0,3,0},{2,0,0,0}};
    dtNavMeshCreateParams params={};
    params.verts=verts; params.vertCount=8; params.polys=polys; params.polyCount=3; params.nvp=4;
    params.polyFlags=flags; params.polyAreas=areas; params.cs=1; params.ch=1;
    params.bmax[0]=3;params.bmax[1]=1;params.bmax[2]=1;params.walkableHeight=2;
    unsigned char* data=0; int dataSize=0;
    ++builderCalls;const bool built=dtCreateNavMeshData(&params,&data,&dataSize);
    failureDetail="builderResult="+std::to_string(built)+",dataSize="+std::to_string(dataSize);
    require(built && data && dataSize>0,"builder"); completed.push_back("builder");
    // Heap ownership deliberately avoids destructing uncertain partial init on failure.
    dtNavMesh* nav=new(std::nothrow) dtNavMesh(); require(nav!=0,"nav_allocate");
    ++navCalls;const dtStatus navStatus=nav->init(data,dataSize,DT_TILE_FREE_DATA);
    failureDetail="navStatus="+std::to_string(navStatus);require(navStatus==DT_SUCCESS,"nav_init"); completed.push_back("nav_init");
    const dtNavMesh* constNav=nav;
    const dtMeshTile* tile=constNav->getTile(0);
    require(tile && tile->header,"tile_header");
    const dtMeshHeader* header=tile->header;
    failureDetail="polyCount="+std::to_string(header->polyCount)+",vertCount="+std::to_string(header->vertCount)+",offMeshConCount="+std::to_string(header->offMeshConCount);
    require(header->polyCount==3 && header->vertCount==8 && header->offMeshConCount==0,"tile_shape");
    dtPolyRef refs[3];
    for(int i=0;i<3;++i) refs[i]=nav->getPolyRefBase(tile)|dtPolyRef(i);
    bool valid=true;
    for(int i=0;i<3;++i) valid=valid && refs[i]!=0 && nav->isValidPolyRef(refs[i]);
    valid=valid && refs[0]!=refs[1] && refs[0]!=refs[2] && refs[1]!=refs[2];
    dtQueryFilter filter;
    std::ostringstream s; partialCapture=&s; s << std::showpoint << std::setprecision(9);
    s << "{\"builder_calls\":"<<builderCalls<<",\"nav_init_calls\":"<<navCalls<<",\"data_size\":" << dataSize
      << ",\"header\":["<<header->polyCount<<','<<header->vertCount<<','<<header->detailMeshCount<<','<<header->detailTriCount<<','<<header->offMeshConCount<<','<<header->bvNodeCount<<','<<header->maxLinkCount<<"]"
      << ",\"nav_status\":"<<navStatus
      << ",\"filter\":["<<filter.getIncludeFlags()<<','<<filter.getExcludeFlags()<<','<<filter.getAreaCost(0)<<"]"
      << ",\"input\":{\"nvp\":"<<params.nvp<<",\"cs\":"<<params.cs<<",\"ch\":"<<params.ch
      << ",\"bounds\":[["<<params.bmin[0]<<','<<params.bmin[1]<<','<<params.bmin[2]<<"],["<<params.bmax[0]<<','<<params.bmax[1]<<','<<params.bmax[2]<<"]],\"walkable\":["<<params.walkableHeight<<','<<params.walkableRadius<<','<<params.walkableClimb
      << "],\"build_bv_tree\":"<<(params.buildBvTree?"true":"false")<<",\"detail_count\":"<<params.detailTriCount<<",\"offmesh_count\":"<<params.offMeshConCount<<",\"polys\":[";
    for(int i=0;i<3;++i) {if(i)s<<',';s<<'[';for(int j=0;j<8;++j){if(j)s<<',';s<<polys[i*8+j];}s<<']';}
    s<<"]},\"refs\":[";for(int i=0;i<3;++i){if(i)s<<',';s<<'"'<<refs[i]<<'"';}s<<"],\"refs_valid\":"<<(valid?"true":"false")<<",\"vertices\":[";
    for(int i=0;i<8;++i){if(i)s<<',';s<<'[';for(int j=0;j<3;++j){if(j)s<<',';s<<tile->verts[3*i+j];valid=valid && tile->verts[3*i+j]==float(verts[3*i+j]);}s<<']';}
    s<<"],\"polygons\":[";
    for(int i=0;i<3;++i){
        const dtPoly& p=tile->polys[i]; if(i)s<<',';
        s<<"{\"index\":"<<i<<",\"type\":"<<int(p.getType())<<",\"flags\":"<<p.flags<<",\"area\":"<<int(p.getArea())<<",\"vertices\":[";
        failureDetail="poly="+std::to_string(i)+",vertCount="+std::to_string(p.vertCount);require(p.vertCount==4,"poly_vertex_count");
        for(int j=0;j<4;++j){if(j)s<<',';s<<p.verts[j];valid=valid && p.verts[j]==polys[i*8+j];}
        s<<"],\"neis\":[";for(int j=0;j<4;++j){if(j)s<<',';s<<p.neis[j];valid=valid && p.neis[j]==neis[i][j];}s<<"],\"links\":[";
        unsigned int link=p.firstLink; int count=0; bool first=true; bool seenEdges[4]={false,false,false,false};
        while(link!=DT_NULL_LINK){
            failureDetail="poly="+std::to_string(i)+",link="+std::to_string(link)+",steps="+std::to_string(count)+",maxLinkCount="+std::to_string(header->maxLinkCount);
            require(link<unsigned(header->maxLinkCount) && count<header->maxLinkCount,"link_bounds_or_cycle");
            const dtLink& l=tile->links[link];if(!first)s<<',';first=false;
            const int target=refIndex(l.ref,refs);
            s<<"{\"target\":"<<target<<",\"ref\":\""<<l.ref<<"\",\"edge\":"<<int(l.edge)<<",\"side\":"<<int(l.side)<<'}';
            valid=valid && l.edge<4 && target>=0 && l.side==255;
            if(l.edge<4 && target>=0){valid=valid && !seenEdges[l.edge] && neis[i][l.edge]==target+1;seenEdges[l.edge]=true;}
            ++count;link=l.next;
        }
        valid=valid && count==(i==1?2:1) && p.flags==1 && p.getArea()==0 && p.getType()==DT_POLYTYPE_GROUND;
        s<<"]}";
    }
    s<<"]";
    valid=valid && filter.getIncludeFlags()==65535 && filter.getExcludeFlags()==0 && filter.getAreaCost(0)==1;
    valid=valid && header->detailMeshCount==3 && header->detailTriCount==6 && header->bvNodeCount==0 && header->maxLinkCount==12;
    require(valid,"mesh_setup_values");completed.push_back("mesh_checked");
    dtNavMeshQuery* query=new(std::nothrow) dtNavMeshQuery(); require(query!=0,"query_allocate");
    ++initCalls;const dtStatus queryStatus=query->init(nav,16);
    failureDetail="queryStatus="+std::to_string(queryStatus);
    require(queryStatus==DT_SUCCESS,"query_init"); completed.push_back("query_init");
    require(query->getNodePool()!=0,"node_pool");
    s<<",\"query_init_calls\":"<<initCalls<<",\"query_status\":"<<queryStatus<<",\"node_capacity\":"<<query->getNodePool()->getMaxNodes()<<'}';
    setup=s.str();
    require(query->getNodePool()->getMaxNodes()==16,"node_capacity");completed.push_back("setup_checked");
    failureDetail.clear();
    const float start[3]={.5f,0,.5f}, end[3]={2.5f,0,.5f};
    for(int iteration=0;iteration<2;++iteration){
        const int capacity=iteration+2;dtPolyRef path[3]={0,0,0};int count=-1;
        ++queryCalls;const dtStatus status=query->findPath(refs[0],refs[2],start,end,&filter,path,&count,capacity);
        std::ostringstream r;r<<"{\"name\":\""<<(iteration==0?"prefix":"full")<<"\",\"max_path\":"<<capacity<<",\"path_count\":"<<count
          <<",\"start\":[0.5,0.0,0.5],\"end\":[2.5,0.0,0.5],\"status\":"<<status<<",\"status_hex\":\"0x"<<std::hex<<status<<std::dec<<"\",\"path\":[";
        for(int j=0;j<3;++j){if(j)r<<',';r<<'"'<<path[j]<<'"';}r<<"],\"indices\":[";
        for(int j=0;j<3;++j){if(j)r<<',';if(path[j]==0)r<<"null";else r<<refIndex(path[j],refs);}r<<"]}";cases.push_back(r.str());
        const dtStatus expected=iteration==0?DT_SUCCESS|DT_BUFFER_TOO_SMALL:DT_SUCCESS;
        require(status==expected && count==capacity && path[0]==refs[0] && path[1]==refs[1] && path[2]==(iteration==0?0:refs[2]),"query_result");
        completed.push_back(iteration==0?"prefix_checked":"full_checked");
    }
    delete query; delete nav;
    completed.push_back("released");emit("pass","complete");return 0;
}
