Shader "Meridian/CoastWater" {
 Properties { _BaseColor("Deep water",Color)=(.025,.18,.23,1) }
 SubShader {
  Tags { "RenderPipeline"="UniversalPipeline" "RenderType"="Opaque" "Queue"="Geometry" }
  Pass {
   HLSLPROGRAM
   #pragma vertex vert
   #pragma fragment frag
   #pragma multi_compile_fog
   #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
   #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
   CBUFFER_START(UnityPerMaterial) float4 _BaseColor; CBUFFER_END
   struct Attributes { float4 positionOS:POSITION; };
   struct Varyings { float4 positionCS:SV_POSITION; float3 world:TEXCOORD0; float fog:TEXCOORD1; };
   Varyings vert(Attributes i) { Varyings o; o.world=TransformObjectToWorld(i.positionOS.xyz);o.positionCS=TransformWorldToHClip(o.world);o.fog=ComputeFogFactor(o.positionCS.z);return o; }
   half4 frag(Varyings i):SV_Target {
    float t=_Time.y;float2 p=i.world.xz;
    float3 n=normalize(float3(sin(p.x*1.8+t*1.7)*.075+sin(p.y*.43+t*.8)*.12,1,cos(p.y*2.3+t*1.4)*.07+cos(p.x*.31-t*.7)*.13));
    float3 v=GetWorldSpaceNormalizeViewDir(i.world);Light sun=GetMainLight();float fresnel=pow(1-saturate(dot(n,v)),4);float spec=pow(saturate(dot(n,normalize(v+sun.direction))),180);
    half3 sky=half3(.32,.48,.59);half3 col=lerp(_BaseColor.rgb,sky,fresnel*.8)+sun.color*spec*.9;col*=.55+saturate(sun.color.r)*.45;
    float crest=pow(saturate(sin(p.x*.8+p.y*.32+t)*cos(p.y*.47-t*.6)),12);col+=crest*.035;
    return half4(MixFog(col,i.fog),1);
   }
   ENDHLSL
  }
 }
}
