#define CGLTF_IMPLEMENTATION
#include "cgltf.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <float.h>
#include <limits.h>
#include <math.h>

static const unsigned char bytes[16] = {255,0,0,0,0,255,0,0,1,0,0,0,64,191,0,0};
static const char uri[] = "data:application/octet-stream;base64,/wAAAAD/AAABAAAAQL8AAA==";
#define CHECK(c, label) do { if (!(c)) { fprintf(stderr,"FAIL %s %s\n", name, label); goto done; } } while(0)
static int run_case(const char* name, int dense, int normalized)
{
    int ok=0; FILE* f=NULL; cgltf_data* data=NULL;
    cgltf_options options={0}; char json[4096]; size_t size; cgltf_result parsed, loaded, validated; cgltf_size queried, unpacked;
    cgltf_float out[8]={-91,-92,-93,-94,-95,-96,-97,-98};
    double expected[8]={0,0,0,0,64.0/255.0,191.0/255.0,0,0};
    if(dense) expected[0]=normalized?1:255;
    if(!normalized) { expected[4]=64; expected[5]=191; }
    f=fopen(name,"rb"); CHECK(f!=NULL,"open");
    size=fread(json,1,sizeof(json),f); CHECK(!ferror(f) && size>0 && size<sizeof(json),"json_size");
    CHECK(feof(f),"json_eof"); fclose(f); f=NULL;
    parsed=cgltf_parse(&options,json,size,&data); CHECK(parsed==cgltf_result_success,"parse");
    CHECK(data->file_type==cgltf_file_type_gltf && data->buffers_count==1 && data->buffer_views_count==3 && data->accessors_count==1,"counts");
    CHECK(data->meshes_count==0 && data->nodes_count==0 && data->scenes_count==0 && data->images_count==0 && data->textures_count==0 && data->materials_count==0 && data->skins_count==0 && data->animations_count==0 && data->cameras_count==0 && data->lights_count==0 && data->samplers_count==0 && data->extensions_used_count==0 && data->extensions_required_count==0,"asset_subset");
    CHECK(data->buffers[0].size==16 && data->buffers[0].data==NULL && data->buffers[0].uri && strcmp(data->buffers[0].uri,uri)==0,"buffer_uri");
    const size_t offsets[3]={0,8,12}, sizes[3]={8,1,4};
    for(size_t i=0;i<3;i++) {
        const cgltf_buffer_view* v=&data->buffer_views[i];
        CHECK(v->buffer==&data->buffers[0] && v->offset==offsets[i] && v->size==sizes[i] && v->stride==0 && v->type==cgltf_buffer_view_type_invalid && v->data==NULL && !v->has_meshopt_compression,"view_whitelist");
    }
    const cgltf_accessor* a=&data->accessors[0];
    CHECK(a->type==cgltf_type_vec4 && a->component_type==cgltf_component_type_r_8u && a->count==2 && a->offset==0 && a->stride==4 && a->normalized==normalized && !a->has_min && !a->has_max && a->is_sparse,"accessor_whitelist");
    CHECK(a->buffer_view==(dense?&data->buffer_views[0]:NULL),"base_source");
    CHECK(a->sparse.count==1 && a->sparse.indices_buffer_view==&data->buffer_views[1] && a->sparse.indices_byte_offset==0 && a->sparse.indices_component_type==cgltf_component_type_r_8u && a->sparse.values_buffer_view==&data->buffer_views[2] && a->sparse.values_byte_offset==0,"sparse_whitelist");
    loaded=cgltf_load_buffers(&options,data,NULL); CHECK(loaded==cgltf_result_success,"load_buffers");
    CHECK(data->buffers[0].data && memcmp(data->buffers[0].data,bytes,16)==0,"loaded_bytes");
    /* Exact metadata and bytes above establish all ranges, alignments and sparse index 1<2.
       Do not move validate before these checks or accept arbitrary inputs. */
    validated=cgltf_validate(data); CHECK(validated==cgltf_result_success,"validate");
    queried=cgltf_accessor_unpack_floats(a,NULL,0); CHECK(queried==8,"required_capacity");
    unpacked=cgltf_accessor_unpack_floats(a,out,8); CHECK(unpacked==8,"unpack_count");
    for(size_t i=0;i<8;i++) {
        double delta=(double)out[i]-expected[i];
        CHECK(isfinite(out[i]),"finite_output");
        CHECK((normalized && (i==4 || i==5)) ? fabs(delta)<=1e-7 : delta==0,"literal_oracle");
    }
    cgltf_float ignored[4]={123,124,125,126};
    CHECK(cgltf_accessor_read_float(a,0,ignored,4)==0,"read_float_sparse_boundary");
    /* ignored is never consumed after the failed API call. */
    printf("{\"case\":\"%s\",\"parse\":%d,\"load\":%d,\"validate\":%d,\"query_count\":%zu,\"unpack_count\":%zu,\"read_float\":false,\"values\":[",name,(int)parsed,(int)loaded,(int)validated,(size_t)queried,(size_t)unpacked);
    for(size_t i=0;i<8;i++) printf("%s%.9g",i?",":"",(double)out[i]);
    puts("]}"); fflush(stdout);
    ok=1;
done:
    if(f) fclose(f);
    if(data) cgltf_free(data);
    return ok;
}
int main(void)
{
    unsigned int endian=1;
    if(CHAR_BIT!=8 || sizeof(float)!=4 || FLT_RADIX!=2 || FLT_MANT_DIG!=24 || FLT_MAX_EXP!=128 || sizeof(unsigned short)!=2 || *((unsigned char*)&endian)!=1) {
        fputs("FAIL unsupported_host_representation\n",stderr); return 2;
    }
    if(!run_case("dense-normalized.json",1,1)) return 1;
    if(!run_case("zero-normalized.json",0,1)) return 1;
    if(!run_case("dense-raw.json",1,0)) return 1;
    return 0;
}
