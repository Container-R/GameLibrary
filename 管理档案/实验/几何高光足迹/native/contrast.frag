#version 330
uniform float phase;
uniform bool flat_control;
out vec4 result;
const float pitch=.04;
const float a2=.015*.015;
const float pi=3.14159265358979323846;
vec3 shape(vec2 p) {
    if(flat_control) return vec3(0,0,1);
    float r2=dot(p,p);
    // Extend as horizon normal beyond sphere for well-defined quad derivatives.
    // This analytic extension is not equivalent to mesh/helper coverage.
    return vec3(p/max(sqrt(r2),1.),sqrt(max(0.,1.-r2)));
}
float D(float z,float alpha2) {
    float z2=z*z;
    float q=(1.-z2)+z2*alpha2;
    return alpha2/(pi*q*q);
}
void main(){
    vec2 p=(gl_FragCoord.xy-vec2(32.5))*pitch+vec2(phase,.007);
    vec3 n=shape(p);
    vec3 dx=dFdx(n),dy=dFdy(n);
    float extra=min((dot(dx,dx)+dot(dy,dy))/pi,.18);
    float cov=float(flat_control || dot(p,p)<=1.);
    float ref=0.;
    for(int j=0;j<32;++j) for(int i=0;i<32;++i){
        vec2 s=p+pitch*((vec2(i,j)+.5)/32.-.5);
        if(flat_control || dot(s,s)<=1.) ref+=D(shape(s).z,a2);
    }
    result=vec4(cov*D(n.z,a2),cov*D(n.z,a2+extra),ref/1024.,cov);
}
