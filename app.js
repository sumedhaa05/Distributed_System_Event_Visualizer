let processNames = ["P1","P2","P3"];
let eventQueue = [];

const $ = id => document.getElementById(id);
function showError(message=""){ $("error").textContent = message; }

function refreshSelectors(){
  $("processSelect").innerHTML = processNames.map(n=>`<option>${n}</option>`).join("");
  $("receiverSelect").innerHTML = processNames.map(n=>`<option>${n}</option>`).join("");
  updateReceiverVisibility();
}
function updateReceiverVisibility(){
  $("receiverWrap").classList.toggle("hidden", $("kindSelect").value !== "Send");
}
function setProcesses(){
  const names = $("processNames").value.split(",").map(x=>x.trim()).filter(Boolean);
  if(!names.length || names.length>8 || new Set(names).size!==names.length){
    showError("Enter 1–8 unique process names separated by commas."); return;
  }
  processNames=names; eventQueue=[]; refreshSelectors(); renderEmpty(); showError("");
}
function renderEmpty(){
  $("clockCards").innerHTML=processNames.map(n=>`<div class="clock-card"><strong>${n} · LOGICAL CLOCK</strong><b>0</b></div>`).join("");
  $("timelines").innerHTML="Add an event or load the demo to see the timelines.";
  $("timelines").classList.add("empty");
  $("eventRows").innerHTML='<tr><td colspan="4" class="empty-cell">No events yet.</td></tr>';
  $("consistency").className="check-result neutral";
  $("consistency").textContent="Run a simulation to check message ordering.";
  $("checks").innerHTML="";
}
async function runSimulation(){
  const response=await fetch("/api/simulate",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({processes:processNames,events:eventQueue})});
  const data=await response.json();
  if(!response.ok){showError(data.error||"Simulation failed.");return;}
  showError(""); render(data);
}
function render(data){
  $("clockCards").innerHTML=data.processes.map(p=>`<div class="clock-card"><strong>${p.name} · LOGICAL CLOCK</strong><b>${p.clock}</b><small>${p.events.length} events</small></div>`).join("");
  $("timelines").classList.remove("empty");
  $("timelines").innerHTML=data.processes.map(p=>`<div class="lane"><div class="lane-name">${p.name}</div><div class="lane-events">${p.events.length?p.events.map(e=>`<div class="event-dot ${e.kind}"><b>LC ${e.timestamp}</b><small>${e.kind} · e${e.sequence}</small></div>`).join(""):'<span class="muted">No events</span>'}</div></div>`).join("");
  $("eventRows").innerHTML=data.events.length?data.events.map(e=>`<tr><td><b>${e.timestamp}</b></td><td>${e.process}</td><td><span class="tag ${e.kind}">${e.kind}</span></td><td>${escapeHtml(e.detail)}</td></tr>`).join(""):'<tr><td colspan="4" class="empty-cell">No events yet.</td></tr>';
  $("consistency").className="check-result "+(data.consistent?"pass":"fail");
  $("consistency").textContent=data.consistent?"✓ All message causality checks passed.":"✕ One or more message checks failed.";
  $("checks").innerHTML=data.checks.length?data.checks.map(c=>`<p>${c.sender} → ${c.receiver}: send LC ${c.send_timestamp}, receive LC ${c.receive_timestamp} — ${c.passed?"PASS":"FAIL"}</p>`).join(""):"<p>No messages have been exchanged yet.</p>";
}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
$("applyProcesses").addEventListener("click",setProcesses);
$("kindSelect").addEventListener("change",updateReceiverVisibility);
$("addEvent").addEventListener("click",async()=>{
  const process=$("processSelect").value,kind=$("kindSelect").value,detail=$("detailInput").value.trim()||`${kind} event`;
  const item={process,kind,detail};
  if(kind==="Send") item.receiver=$("receiverSelect").value;
  eventQueue.push(item); $("detailInput").value=""; await runSimulation();
});
$("demoBtn").addEventListener("click",async()=>{
  const response=await fetch("/api/demo"); const data=await response.json();
  processNames=data.processes.map(p=>p.name); $("processNames").value=processNames.join(", ");
  eventQueue=[]; refreshSelectors(); render(data); showError("");
});
refreshSelectors(); renderEmpty();
