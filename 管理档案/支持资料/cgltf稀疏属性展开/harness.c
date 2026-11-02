#define CGLTF_IMPLEMENTATION
#include "cgltf.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <float.h>
#include <limits.h>

static const unsigned char bytes[44] = {
0x00,0x00,0x20,0x41,0x00,0x00,0xa0,0x41,0x00,0x00,0xf0,0x41,0x00,0x00,0x20,0x42,
0xab,0xcd,0x01,0x00,0x03,0x00,0xef,0x12,
0xaa,0xbb,0xcc,0xdd,0x00,0x00,0xe0,0x40,0x00,0x00,0x10,0x41,0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88};
static const char uri[] = "data:application/octet-stream;base64,AAAgQQAAoEEAAPBBAAAgQqvNAQADAO8SqrvM3QAA4EAAABBBESIzRFVmd4g=";
#define CHECK(c, label) do { if (!(c)) { fprintf(stderr,"FAIL %s %s\n", name, label); goto done; } } while(0)
static int run_case(const char* name, int dense)
{
    int ok=0; FILE* f=NULL; cgltf_data* data=NULL;
    cgltf_options options={0}; char json[4096]; size_t size;
    cgltf_float out[4]={-91,-92,-93,-94};
    const cgltf_float expected_dense[4]={10,7,30,9};
    const cgltf_float expected_zero[4]={0,7,0,9};
    const cgltf_float* expected=dense?expected_dense:expected_zero;
    f=fopen(name,"rb"); CHECK(f!=NULL,"open");
    size=fread(json,1,sizeof(json),f); CHECK(!ferror(f) && size>0 && size<sizeof(json),"json_size");
    CHECK(feof(f),"json_eof"); fclose(f); f=NULL;
    CHECK(cgltf_parse(&options,json,size,&data)==cgltf_result_success,"parse");
    CHECK(data->file_type==cgltf_file_type_gltf && data->buffers_count==1 && data->buffer_views_count==3 && data->accessors_count==1,"counts");
    CHECK(data->meshes_count==0 && data->nodes_count==0 && data->scenes_count==0 && data->images_count==0 && data->textures_count==0 && data->materials_count==0 && data->skins_count==0 && data->animations_count==0 && data->cameras_count==0 && data->lights_count==0 && data->samplers_count==0 && data->extensions_used_count==0 && data->extensions_required_count==0,"asset_subset");
    CHECK(data->buffers[0].size==44 && data->buffers[0].data==NULL && data->buffers[0].uri && strcmp(data->buffers[0].uri,uri)==0,"buffer_uri");
    const size_t offsets[3]={0,16,24}, sizes[3]={16,8,20};
    for(size_t i=0;i<3;i++) {
        const cgltf_buffer_view* v=&data->buffer_views[i];
        CHECK(v->buffer==&data->buffers[0] && v->offset==offsets[i] && v->size==sizes[i] && v->stride==0 && v->type==cgltf_buffer_view_type_invalid && v->data==NULL && !v->has_meshopt_compression,"view_whitelist");
    }
    const cgltf_accessor* a=&data->accessors[0];
    CHECK(a->type==cgltf_type_scalar && a->component_type==cgltf_component_type_r_32f && a->count==4 && a->offset==0 && a->stride==4 && !a->normalized && !a->has_min && !a->has_max && a->is_sparse,"accessor_whitelist");
    CHECK(a->buffer_view==(dense?&data->buffer_views[0]:NULL),"base_source");
    CHECK(a->sparse.count==2 && a->sparse.indices_buffer_view==&data->buffer_views[1] && a->sparse.indices_byte_offset==2 && a->sparse.indices_component_type==cgltf_component_type_r_16u && a->sparse.values_buffer_view==&data->buffer_views[2] && a->sparse.values_byte_offset==4,"sparse_whitelist");
    CHECK(cgltf_load_buffers(&options,data,NULL)==cgltf_result_success,"load_buffers");
    CHECK(data->buffers[0].data && memcmp(data->buffers[0].data,bytes,44)==0,"loaded_bytes");
    /* Exact metadata and bytes above establish all ranges, alignments and 1<3<4.
       Do not move validate before these checks or accept arbitrary inputs. */
    CHECK(cgltf_validate(data)==cgltf_result_success,"validate");
    CHECK(cgltf_accessor_unpack_floats(a,NULL,0)==4,"required_capacity");
    CHECK(cgltf_accessor_unpack_floats(a,out,4)==4,"unpack_count");
    for(size_t i=0;i<4;i++) CHECK(out[i]==expected[i],"literal_oracle");
    cgltf_float ignored=123;
    CHECK(cgltf_accessor_read_float(a,0,&ignored,1)==0,"read_float_sparse_boundary");
    /* ignored is never consumed after the failed API call. */
    printf("%s parse=success load=success validate=success count=4 values=[%.0f,%.0f,%.0f,%.0f] read_float=false\n",name,out[0],out[1],out[2],out[3]);
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
    if(!run_case("dense.json",1)) return 1;
    if(!run_case("zero.json",0)) return 1;
    puts("PASS two_fixtures_only"); return 0;
}
