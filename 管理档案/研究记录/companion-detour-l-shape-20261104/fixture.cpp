// Original fixed observation harness. Links unchanged, manifest-bound Detour.
#include "DetourNavMeshBuilder.h"
#include "DetourNavMeshQuery.h"
#include "DetourNode.h"
#include <cfloat>
#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <new>
#include <sstream>
#include <string>
#include <vector>

static const char* commit="6dc1667f580357e8a2154c28b7867bea7e8ad3a7";
static int builders=0,navInits=0,queryInits=0,rays=0,paths=0;
static std::string setup="null", detail;
static std::vector<std::string> completed,cases;
static std::ostringstream* partial=0;
static std::string quote(const std::string& value) {
    std::ostringstream s;s<<'"';
    for(size_t i=0;i<value.size();++i) {
        const unsigned char c=static_cast<unsigned char>(value[i]);
        if(c=='"'||c=='\\') s<<'\\'<<char(c);
        else if(c=='\n')s<<"\\n";else if(c=='\r')s<<"\\r";else if(c=='\t')s<<"\\t";
        else if(c<32)s<<'?';else s<<char(c);
    }
    s<<'"';return s.str();
}
static void emit(bool success,const char* stage) {
    std::cout<<"{\"protocol\":\"companion-detour-v1\",\"commit\":"<<quote(commit)
      <<",\"status\":"<<quote(success?"pass":"fail")<<",\"stage\":"<<quote(stage)<<",\"completed\":[";
    for(size_t i=0;i<completed.size();++i){if(i)std::cout<<',';std::cout<<quote(completed[i]);}
    std::cout<<"],\"calls\":{\"builder\":"<<builders<<",\"nav_init\":"<<navInits<<",\"query_init\":"<<queryInits
      <<",\"raycast\":"<<rays<<",\"findPath\":"<<paths<<"},\"setup\":"<<setup<<",\"cases\":[";
    for(size_t i=0;i<cases.size();++i){if(i)std::cout<<',';std::cout<<cases[i];}
    std::cout<<']';
    if(!success)std::cout<<",\"failure_detail\":"<<quote(detail)<<",\"partial_setup_text\":"<<quote(partial?partial->str():"");
    std::cout<<"}\n"<<std::flush;
}
static void require(bool ok,const char* stage) {if(!ok){emit(false,stage);std::_Exit(1);}}
static int indexOf(dtPolyRef ref,const dtPolyRef refs[3]) {for(int i=0;i<3;++i)if(ref==refs[i])return i;return -1;}
static void number(std::ostream& s,float value) {
    if(std::isfinite(value))s<<double(value);
    else s<<quote(std::isnan(value)?"NaN":(value>0?"Infinity":"-Infinity"));
}
static void vec(std::ostream& s,const float* p) {s<<'[';number(s,p[0]);s<<',';number(s,p[1]);s<<',';number(s,p[2]);s<<']';}
static void pathOut(std::ostream& s,const dtPolyRef p[3]) {s<<'[';for(int i=0;i<3;++i){if(i)s<<',';s<<'"'<<p[i]<<'"';}s<<']';}
int main() {
    const unsigned short verts[24]={0,0,0,1,0,0,2,0,0,0,0,1,1,0,1,2,0,1,1,0,2,2,0,2};
    const unsigned short polys[24]={0,3,4,1,65535,65535,1,65535,
                                    1,4,5,2,0,2,65535,65535,
                                    4,6,7,5,65535,65535,65535,1};
    const unsigned short flags[3]={1,1,1};const unsigned char areas[3]={0,0,0};
    const unsigned short expectedNeis[3][4]={{0,0,2,0},{1,3,0,0},{0,0,0,2}};
    dtNavMeshCreateParams params={};params.verts=verts;params.vertCount=8;params.polys=polys;params.polyCount=3;params.nvp=4;
    params.polyFlags=flags;params.polyAreas=areas;params.cs=1;params.ch=1;
    params.bmax[0]=2;params.bmax[1]=1;params.bmax[2]=2;params.walkableHeight=2;
    unsigned char* data=0;int dataSize=0;
    ++builders;const bool built=dtCreateNavMeshData(&params,&data,&dataSize);
    detail="builder="+std::to_string(built)+",dataSize="+std::to_string(dataSize);
    require(built&&data&&dataSize>0,"builder");completed.push_back("builder");
    dtNavMesh* nav=new(std::nothrow) dtNavMesh();require(nav!=0,"nav_allocate");
    ++navInits;const dtStatus navStatus=nav->init(data,dataSize,DT_TILE_FREE_DATA);
    detail="navStatus="+std::to_string(navStatus);require(navStatus==DT_SUCCESS,"nav_init");completed.push_back("nav_init");
    const dtNavMesh* constNav=nav;const dtMeshTile* tile=constNav->getTile(0);
    require(tile&&tile->header,"tile_header");const dtMeshHeader* h=tile->header;
    std::ostringstream s;s<<std::setprecision(17);partial=&s;
    s<<"{\"data_size\":"<<dataSize<<",\"nav_status\":"<<navStatus<<",\"header\":{\"poly_count\":"<<h->polyCount
     <<",\"vert_count\":"<<h->vertCount<<",\"detail_mesh_count\":"<<h->detailMeshCount<<",\"detail_vert_count\":"<<h->detailVertCount
     <<",\"detail_tri_count\":"<<h->detailTriCount<<",\"offmesh_count\":"<<h->offMeshConCount<<",\"bv_node_count\":"<<h->bvNodeCount
     <<",\"max_link_count\":"<<h->maxLinkCount<<'}';
    detail="actual header is in partial_setup_text";
    require(h->polyCount==3&&h->vertCount==8&&h->detailMeshCount==3&&h->detailVertCount==0&&h->detailTriCount==6&&h->offMeshConCount==0&&h->bvNodeCount==0&&h->maxLinkCount==12,"tile_shape");
    dtPolyRef refs[3];bool valid=true;
    for(int i=0;i<3;++i){refs[i]=nav->getPolyRefBase(tile)|dtPolyRef(i);valid=valid&&refs[i]!=0&&nav->isValidPolyRef(refs[i]);}
    valid=valid&&refs[0]!=refs[1]&&refs[0]!=refs[2]&&refs[1]!=refs[2];
    s<<",\"refs\":";pathOut(s,refs);s<<",\"refs_valid\":"<<(valid?"true":"false");
    require(valid,"refs");
    s<<",\"input\":{\"nvp\":"<<params.nvp<<",\"cs\":"<<double(params.cs)<<",\"ch\":"<<double(params.ch)<<",\"bounds\":[";
    vec(s,params.bmin);s<<',';vec(s,params.bmax);
    s<<"],\"walkable\":["<<double(params.walkableHeight)<<','<<double(params.walkableRadius)<<','<<double(params.walkableClimb)
     <<"],\"build_bv_tree\":"<<(params.buildBvTree?"true":"false")<<",\"detail_tri_count\":"<<params.detailTriCount
     <<",\"offmesh_count\":"<<params.offMeshConCount<<",\"vertices\":[";
    for(int i=0;i<8;++i){if(i)s<<',';s<<'['<<verts[3*i]<<','<<verts[3*i+1]<<','<<verts[3*i+2]<<']';}
    s<<"],\"polys\":[";for(int i=0;i<3;++i){if(i)s<<',';s<<'[';for(int j=0;j<8;++j){if(j)s<<',';s<<polys[i*8+j];}s<<']';}
    s<<"],\"flags\":["<<flags[0]<<','<<flags[1]<<','<<flags[2]<<"],\"areas\":["<<int(areas[0])<<','<<int(areas[1])<<','<<int(areas[2])<<"]}";
    s<<",\"vertices\":[";for(int i=0;i<8;++i){if(i)s<<',';vec(s,tile->verts+3*i);for(int j=0;j<3;++j)valid=valid&&tile->verts[3*i+j]==float(verts[3*i+j]);}
    s<<"],\"polygons\":[";
    for(int i=0;i<3;++i){
        const dtPoly& p=tile->polys[i];if(i)s<<',';
        detail="poly="+std::to_string(i)+",vertCount="+std::to_string(p.vertCount);
        require(p.vertCount==4,"poly_vertex_count");
        s<<"{\"index\":"<<i<<",\"type\":"<<int(p.getType())<<",\"flags\":"<<p.flags<<",\"area\":"<<int(p.getArea())<<",\"vertices\":[";
        for(int j=0;j<4;++j){if(j)s<<',';s<<p.verts[j];valid=valid&&p.verts[j]==polys[i*8+j];}
        s<<"],\"neis\":[";for(int j=0;j<4;++j){if(j)s<<',';s<<p.neis[j];valid=valid&&p.neis[j]==expectedNeis[i][j];}s<<"],\"links\":[";
        bool seen[12]={false};bool edges[4]={false};int count=0,lastEdge=-1;unsigned int link=p.firstLink;
        while(link!=DT_NULL_LINK){
            detail="poly="+std::to_string(i)+",link="+std::to_string(link)+",steps="+std::to_string(count);
            require(link<12&&count<12,"link_bounds");require(!seen[link],"link_cycle");seen[link]=true;
            const dtLink& l=tile->links[link];const int target=indexOf(l.ref,refs);if(count)s<<',';
            s<<"{\"edge\":"<<int(l.edge)<<",\"target\":"<<target<<",\"ref\":\""<<l.ref<<"\",\"side\":"<<int(l.side)<<",\"bmin\":"<<int(l.bmin)<<",\"bmax\":"<<int(l.bmax)<<'}';
            valid=valid&&l.edge<4&&target>=0&&l.side==255&&l.bmin==0&&l.bmax==0&&int(l.edge)>lastEdge;
            if(l.edge<4&&target>=0){valid=valid&&!edges[l.edge]&&expectedNeis[i][l.edge]==target+1;edges[l.edge]=true;}
            lastEdge=l.edge;++count;link=l.next;
        }
        valid=valid&&count==(i==1?2:1)&&p.flags==1&&p.getArea()==0&&p.getType()==DT_POLYTYPE_GROUND;s<<"]}";
    }
    s<<']';detail="actual mesh is in partial_setup_text";require(valid,"mesh_values");completed.push_back("mesh_checked");
    dtNavMeshQuery* query=new(std::nothrow) dtNavMeshQuery();require(query!=0,"query_allocate");
    ++queryInits;const dtStatus queryStatus=query->init(nav,16);detail="queryStatus="+std::to_string(queryStatus);
    require(queryStatus==DT_SUCCESS,"query_init");completed.push_back("query_init");require(query->getNodePool()!=0,"node_pool");
    dtQueryFilter filter;
    s<<",\"query_status\":"<<queryStatus<<",\"node_capacity\":"<<query->getNodePool()->getMaxNodes()
     <<",\"filter\":["<<filter.getIncludeFlags()<<','<<filter.getExcludeFlags()<<','<<double(filter.getAreaCost(0))
     <<"],\"float_format\":["<<FLT_RADIX<<','<<FLT_MANT_DIG<<','<<FLT_MAX_EXP<<"],\"float_max\":"<<double(FLT_MAX)<<'}';
    setup=s.str();detail="setup values";
    require(query->getNodePool()->getMaxNodes()==16&&filter.getIncludeFlags()==65535&&filter.getExcludeFlags()==0&&filter.getAreaCost(0)==1,"query_setup");
    require(FLT_RADIX==2&&FLT_MANT_DIG==24&&FLT_MAX_EXP==128&&double(FLT_MAX)==3.4028234663852886e38,"float_format");completed.push_back("setup_checked");
    const float L[3]={.25f,0,.5f},C[3]={1.25f,0,.5f},F[3]={1.25f,0,1.5f};
    const float* starts[3]={L,C,L};const float* ends[3]={C,F,F};const int startIndices[3]={0,1,0};const char* names[3]={"LC","CF","LF"};
    for(int i=0;i<3;++i){
        dtPolyRef path[3]={0,0,0};dtRaycastHit hit={};hit.path=path;hit.maxPath=3;
        ++rays;const dtStatus status=query->raycast(refs[startIndices[i]],starts[i],ends[i],&filter,0,&hit,0);
        std::ostringstream r;r<<std::setprecision(17)<<"{\"name\":"<<quote(names[i])<<",\"api\":\"raycast\",\"start_ref\":\""<<refs[startIndices[i]]<<"\",\"start\":";
        vec(r,starts[i]);r<<",\"end\":";vec(r,ends[i]);r<<",\"options\":0,\"prev_ref\":\"0\",\"max_path\":"<<hit.maxPath
         <<",\"status\":"<<status<<",\"path_count\":"<<hit.pathCount<<",\"path\":";pathOut(r,path);r<<",\"t\":";number(r,hit.t);
        if(hit.t>0&&hit.t<1){r<<",\"hit_edge\":"<<hit.hitEdgeIndex<<",\"hit_normal\":";vec(r,hit.hitNormal);}
        else r<<",\"hit_edge\":null,\"hit_normal\":null";
        r<<'}';cases.push_back(r.str());detail=std::string(names[i])+" raw result captured";
        bool ok=status==DT_SUCCESS&&hit.maxPath==3;
        if(i<2)ok=ok&&hit.pathCount==2&&path[0]==refs[i]&&path[1]==refs[i+1]&&path[2]==0&&hit.t==FLT_MAX;
        else ok=ok&&hit.pathCount==1&&path[0]==refs[0]&&path[1]==0&&path[2]==0&&hit.t==.5f&&hit.hitEdgeIndex==1&&hit.hitNormal[0]==0&&hit.hitNormal[1]==0&&hit.hitNormal[2]==-1;
        require(ok,names[i]);completed.push_back(std::string(names[i])+"_checked");
    }
    dtPolyRef path[3]={0,0,0};int count=-1;++paths;
    const dtStatus status=query->findPath(refs[0],refs[2],L,F,&filter,path,&count,3);
    std::ostringstream r;r<<std::setprecision(17)<<"{\"name\":\"route_LF\",\"api\":\"findPath\",\"start_ref\":\""<<refs[0]<<"\",\"end_ref\":\""<<refs[2]<<"\",\"start\":";
    vec(r,L);r<<",\"end\":";vec(r,F);r<<",\"max_path\":3,\"status\":"<<status<<",\"path_count\":"<<count<<",\"path\":";pathOut(r,path);r<<'}';cases.push_back(r.str());detail="route_LF raw result captured";
    require(status==DT_SUCCESS&&count==3&&path[0]==refs[0]&&path[1]==refs[1]&&path[2]==refs[2],"route_LF");completed.push_back("route_LF_checked");
    delete query;delete nav;completed.push_back("released");emit(true,"complete");return 0;
}
