// Private inspection events. Requires a valid Cloudflare Access JWT and approved source rights.
const json=(data,status=200)=>new Response(JSON.stringify(data),{status,headers:{"content-type":"application/json; charset=utf-8","cache-control":"no-store","x-content-type-options":"nosniff"}});
function b64(s){const x=s.replace(/-/g,"+").replace(/_/g,"/");return Uint8Array.from(atob(x.padEnd(Math.ceil(x.length/4)*4,"=")),c=>c.charCodeAt(0))}
async function access(request,env){
  const domain=String(env.ACCESS_TEAM_DOMAIN||"").replace(/^https?:\/\//,"").replace(/\/$/,"");
  const aud=String(env.ACCESS_AUD||"");
  if(!env.PROPERTY_DB||!domain||!aud||!/^[-a-z0-9.]+\.cloudflareaccess\.com$/i.test(domain))return false;
  const jwt=request.headers.get("Cf-Access-Jwt-Assertion");
  if(!jwt)return false;
  const parts=jwt.split(".");if(parts.length!==3)return false;
  let header,payload;try{header=JSON.parse(new TextDecoder().decode(b64(parts[0])));payload=JSON.parse(new TextDecoder().decode(b64(parts[1])))}catch{return false}
  if(header.alg!=="RS256"||!header.kid||payload.iss!=="https://"+domain||!(Array.isArray(payload.aud)?payload.aud.includes(aud):payload.aud===aud)||!Number.isFinite(payload.exp)||payload.exp<=Date.now()/1000||!Number.isFinite(payload.iat)||payload.iat>Date.now()/1000+60)return false;
  try{
    const response=await fetch("https://"+domain+"/cdn-cgi/access/certs");
    if(!response.ok)return false;
    const keys=await response.json(),jwk=keys.keys?.find(k=>k.kid===header.kid&&k.kty==="RSA"&&(!k.alg||k.alg==="RS256"));
    if(!jwk)return false;
    const key=await crypto.subtle.importKey("jwk",jwk,{name:"RSASSA-PKCS1-v1_5",hash:"SHA-256"},false,["verify"]);
    return await crypto.subtle.verify("RSASSA-PKCS1-v1_5",key,b64(parts[2]),new TextEncoder().encode(parts[0]+"."+parts[1]));
  }catch{return false}
}

export async function onRequestGet({request,env}){
 if(!(await access(request,env)))return json({error:"Access authentication or D1 unavailable"},403);
 const u=new URL(request.url),county=u.searchParams.get('county'),stage=u.searchParams.get('stage');
 if(county&&!['Baker','Clay','Duval','Nassau','St. Johns'].includes(county))return json({error:'Invalid county'},400);
 if(stage&&!['site_evaluation','pre_install','construction','final_review','reinspection','operating','other','unknown'].includes(stage))return json({error:'Invalid stage'},400);
 try{
 const sql="SELECT i.inspection_id,i.county,i.permit_reference,i.stage,i.outcome,i.inspected_at,i.inspector_type,i.contractor_registration,i.source_document_url,i.review_status FROM inspection_events i JOIN source_registry s ON s.source_id=i.source_id WHERE i.review_status='verified' AND s.rights_status='approved' AND (?1 IS NULL OR i.county=?1) AND (?2 IS NULL OR i.stage=?2) ORDER BY i.inspected_at DESC LIMIT 100";
 const r=await env.PROPERTY_DB.prepare(sql).bind(county,stage).all();
 return json({records:r.results||[],count:(r.results||[]).length,scope:'approved_source_verified_inspections_only',note:'An absent event is not evidence that an inspection did not occur.'});
 }catch{return json({error:'Inspection query unavailable'},503)}
}
