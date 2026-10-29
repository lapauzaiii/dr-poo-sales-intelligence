// Cloudflare Pages Function: fail closed until Access and D1 bindings are configured.
// Required env: PROPERTY_DB (D1), ACCESS_TEAM_DOMAIN (e.g. example.cloudflareaccess.com), ACCESS_AUD.
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
  if(!(await access(request,env)))return json({error:"Access authentication or private database configuration unavailable"},403);
  const u=new URL(request.url),county=u.searchParams.get("county"),type=u.searchParams.get("type"),limit=Math.min(100,Math.max(1,Number.parseInt(u.searchParams.get("limit")||"25",10)||25));
  const counties=["Baker","Clay","Duval","Nassau","St. Johns"];
  if(county&&!counties.includes(county))return json({error:"Invalid county"},400);
  if(type&&(!/^[a-z_]{1,40}$/.test(type)))return json({error:"Invalid system type"},400);
  // No names or addresses are exposed by this endpoint. Only reviewed evidence.
  const sql=`SELECT p.property_id,p.county,e.system_category,e.tank_capacity_gallons,e.design_flow_gpd,e.drainfield_type,e.installation_date,e.configuration_status,e.source_document_url,e.source_page FROM septic_evidence e JOIN properties p ON p.property_id=e.property_id JOIN source_registry s ON s.source_id=e.source_id LEFT JOIN outreach_suppression x ON x.property_id=p.property_id WHERE e.review_status='verified' AND s.rights_status='approved' AND x.property_id IS NULL AND (?1 IS NULL OR p.county=?1) AND (?2 IS NULL OR e.system_category=?2) ORDER BY e.reviewed_at DESC LIMIT ?3`;
  try{const result=await env.PROPERTY_DB.prepare(sql).bind(county,type,limit).all();return json({records:result.results||[],count:(result.results||[]).length,scope:"verified_source_authorized_only"})}catch{return json({error:"Private query unavailable"},503)}
}
