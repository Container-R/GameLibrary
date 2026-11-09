// Experiment code: CC0. Linked meshoptimizer code retains its MIT license.
#include "meshoptimizer.h"
#include <vector>
#include <iostream>
#include <cassert>
#include <algorithm>
using V=std::vector<unsigned>;
void arr(const V&a){std::cout<<"[";for(size_t i=0;i<a.size();i++)std::cout<<(i?",":"")<<a[i];std::cout<<"]";}
V identity(const V&i,const V&v){V r;for(auto x:i)r.push_back(v.at(x));return r;}
int main(){
 // 4x4 grid, 18 unique triangles, deterministically interleaved order.
 V canonical;for(unsigned y=0;y<3;y++)for(unsigned x=0;x<3;x++){unsigned a=y*4+x;for(unsigned k:{a,a+1,a+4,a+1,a+5,a+4})canonical.push_back(k);}
 V input;for(unsigned t=0;t<18;t++){unsigned p=(t*7)%18;input.insert(input.end(),canonical.begin()+3*p,canonical.begin()+3*p+3);}
 V vertices(17);for(unsigned i=0;i<17;i++)vertices[i]=i; // vertex 16 unused
 V fetch=input,fv(17);size_t used=meshopt_optimizeVertexFetch(fv.data(),fetch.data(),fetch.size(),vertices.data(),vertices.size(),sizeof(unsigned));fv.resize(used);
 V cache(input.size());meshopt_optimizeVertexCache(cache.data(),input.data(),input.size(),vertices.size());
 V order;for(size_t i=0;i<cache.size();i+=3){unsigned found=999;for(size_t j=0;j<input.size();j+=3)if(std::equal(cache.begin()+i,cache.begin()+i+3,input.begin()+j))found=j/3;assert(found!=999);order.push_back(found);}
 V sortedOrder=order;std::sort(sortedOrder.begin(),sortedOrder.end());
 assert(sortedOrder.size()==18);for(unsigned t=0;t<18;t++)assert(sortedOrder[t]==t);
 assert(identity(fetch,fv)==input);assert(cache!=input);
 // Two draw ranges refer to one shared vertex buffer. Each local call overwrites it.
 V a={4,1,3},b={1,4,2},badA=a,badB=b,shared(17);
 meshopt_optimizeVertexFetch(shared.data(),badA.data(),3,vertices.data(),17,sizeof(unsigned));
 meshopt_optimizeVertexFetch(shared.data(),badB.data(),3,vertices.data(),17,sizeof(unsigned));
 V badIdentity=identity(badA,shared);assert(badIdentity!=a);
 V both=a;both.insert(both.end(),b.begin(),b.end());V good=both,gv(17);size_t n=meshopt_optimizeVertexFetch(gv.data(),good.data(),good.size(),vertices.data(),17,sizeof(unsigned));gv.resize(n);assert(identity(good,gv)==both);
 // Small graphics fixture: same-position triangles with distinct identities/colors.
 V rasterInput={3,4,5,0,1,2},rasterFetch=rasterInput,rv(6),rasterVertices={0,1,2,3,4,5};
 meshopt_optimizeVertexFetch(rv.data(),rasterFetch.data(),6,rasterVertices.data(),6,sizeof(unsigned));
 std::cout<<"{\n\"input\":";arr(input);std::cout<<",\n\"fetch_indices\":";arr(fetch);std::cout<<",\n\"fetch_vertex_old_ids\":";arr(fv);std::cout<<",\n\"fetch_reconstructed\":";arr(identity(fetch,fv));std::cout<<",\n\"cache_indices\":";arr(cache);std::cout<<",\n\"cache_triangle_original_positions\":";arr(order);
 std::cout<<",\n\"ranges\":{\"input\":";arr(both);std::cout<<",\"bad_first_range_ids_after_second_overwrite\":";arr(badIdentity);std::cout<<",\"unified_indices\":";arr(good);std::cout<<",\"unified_vertex_old_ids\":";arr(gv);std::cout<<",\"unified_reconstructed\":";arr(identity(good,gv));
 std::cout<<"},\n\"raster_fixture\":{\"input\":";arr(rasterInput);std::cout<<",\"fetch_indices\":";arr(rasterFetch);std::cout<<",\"fetch_vertex_old_ids\":";arr(rv);std::cout<<"},\n\"all_assertions_passed\":true}\n";
}
