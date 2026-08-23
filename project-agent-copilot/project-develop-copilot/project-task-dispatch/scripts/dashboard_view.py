from __future__ import annotations

import html
import json
import os
import time
from pathlib import Path
from typing import Any, Mapping


STATE_LABELS = {
    "READY": "待派发",
    "WAITING_DEPENDENCY": "等待依赖",
    "ASSIGNED": "开发中",
    "SUBMITTED": "已提交",
    "REVIEWING": "复核中",
    "CHANGES_REQUESTED": "需要修改",
    "APPROVED": "已批准",
    "BLOCKED": "已阻塞",
    "STALE": "已失效",
}

CSS = r"""
:root{color-scheme:light;font-family:"Segoe UI","Microsoft YaHei",sans-serif;background:#f3f5f8;color:#172033}
*{box-sizing:border-box}body{margin:0}.shell{max-width:1500px;margin:auto;padding:22px}.bar{display:flex;justify-content:space-between;gap:16px;align-items:center;margin-bottom:18px}.bar h1{font-size:20px;margin:0}.connection{display:flex;align-items:center;gap:8px;font-size:13px;color:#586174}.dot{width:9px;height:9px;border-radius:50%;background:#94a3b8}.connected .dot{background:#16a34a}.reconnecting .dot{background:#d97706}.panel{background:white;border:1px solid #dfe4ec;border-radius:16px;box-shadow:0 8px 28px rgba(24,39,75,.06)}.manager{padding:20px;display:grid;grid-template-columns:1.4fr 1fr 1fr;gap:18px}.eyebrow{font-size:12px;color:#667085;text-transform:uppercase;letter-spacing:.08em}.value{font-size:18px;font-weight:700;margin-top:5px}.sub{font-size:13px;color:#667085;margin-top:5px}.flow-line{height:34px;width:2px;background:#cbd5e1;margin:auto;position:relative}.flow-line:after{content:"";position:absolute;bottom:-1px;left:-4px;border:5px solid transparent;border-top-color:#94a3b8}.sessions{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}.session{padding:17px;position:relative;transition:box-shadow .2s,border-color .2s}.session.changed{animation:flash .65s ease-out}.session-head{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}.session h2{font-size:16px;margin:3px 0}.id{font:12px Consolas,monospace;color:#667085}.badges{display:flex;gap:6px;flex-wrap:wrap;margin:14px 0}.badge{font-size:12px;font-weight:700;padding:4px 8px;border-radius:999px;background:#eef2ff;color:#4338ca}.badge.native{background:#eef6f3;color:#087f5b}.state-APPROVED{background:#eaf8ef;color:#137333}.state-BLOCKED,.state-CHANGES_REQUESTED{background:#fff0f0;color:#b42318}.state-REVIEWING,.state-SUBMITTED{background:#fff6e5;color:#a15c00}.facts{display:grid;grid-template-columns:90px 1fr;gap:7px 10px;font-size:13px}.facts dt{color:#667085}.facts dd{margin:0;overflow-wrap:anywhere}.progress{height:7px;background:#e9edf3;border-radius:8px;overflow:hidden;margin:14px 0 6px}.progress span{display:block;height:100%;background:#4f46e5}.attempts{border-top:1px solid #edf0f4;margin-top:13px;padding-top:11px;font-size:12px;color:#667085}.attempts strong{color:#172033}.final{padding:20px;text-align:center}.final .value{font-size:20px}.timeline{margin-top:18px;padding:18px}.timeline h2{font-size:15px;margin:0 0 12px}.timeline ol{margin:0;padding-left:22px}.timeline li{padding:5px 0;font-size:13px}.empty{color:#667085}.footer{text-align:center;color:#788196;font-size:12px;padding:18px}.attention{border-color:#f59e0b}.blocked{border-color:#ef4444}@keyframes flash{0%{box-shadow:0 0 0 4px rgba(79,70,229,.28)}100%{box-shadow:0 8px 28px rgba(24,39,75,.06)}}
@media(max-width:760px){.shell{padding:12px}.bar,.manager{display:block}.bar .connection{margin-top:8px}.manager>div+div{margin-top:14px}.sessions{grid-template-columns:1fr}}
@media(prefers-reduced-motion:reduce){.session{transition:none}.session.changed{animation:none}}
""".strip()

JS = r"""
(()=>{
const $=(s)=>document.querySelector(s);let revision=Number(document.body.dataset.revision||0);let retry=1000;let poll;let terminal=false;let channel;
const text=(tag,value,cls)=>{const n=document.createElement(tag);if(cls)n.className=cls;n.textContent=value??"-";return n};
function status(mode,label){const box=$("#connection");box.className="connection "+mode;box.querySelector("span:last-child").textContent=label}
function badge(value,cls=""){const n=text("span",value,"badge "+cls);return n}
function fact(dl,k,v){dl.append(text("dt",k));dl.append(text("dd",v))}
function card(s,changed){const a=document.createElement("article");a.className="panel session "+(s.attention?"attention ":"")+(s.pdcState==="BLOCKED"?"blocked ":"")+(changed?"changed":"");a.dataset.session=s.projectSessionKey;
 const head=document.createElement("div");head.className="session-head";const titles=document.createElement("div");titles.append(text("div",s.repositoryId,"eyebrow"));titles.append(text("h2",s.title));titles.append(text("div",s.taskIds.join(" · "),"id"));head.append(titles);head.append(text("div",s.shortThreadId,"id"));a.append(head);
 const bs=document.createElement("div");bs.className="badges";bs.append(badge(s.pdcLabel,"state-"+s.pdcState));bs.append(badge("Codex "+s.nativeStatus,"native"));a.append(bs);
 const dl=document.createElement("dl");dl.className="facts";fact(dl,"Project",s.projectId);fact(dl,"分支",s.expectedBranch);fact(dl,"批次/尝试",s.batch+" / "+s.attempt);fact(dl,"验收",s.acceptancePassed+" / "+s.acceptanceTotal);fact(dl,"Finding",String(s.openFindings));fact(dl,"下一动作",s.nextAction);a.append(dl);
 const p=document.createElement("div");p.className="progress";const fill=document.createElement("span");fill.style.width=(s.acceptanceTotal?Math.round(100*s.acceptancePassed/s.acceptanceTotal):0)+"%";p.append(fill);a.append(p);
 const attempts=text("div","", "attempts");attempts.append(text("strong","最近判断："));attempts.append(document.createTextNode(s.lastDecision));a.append(attempts);return a}
function render(s,changed=[]){revision=s.revision;terminal=s.status==="CLOSED";document.body.dataset.revision=revision;$("#revision").textContent="Revision "+revision;$("#dispatch-status").textContent=s.status;$("#gate").textContent=s.manager.currentGate;$("#next-action").textContent=s.manager.nextAction;$("#updated-at").textContent=s.updatedAt;
 const cards=$("#sessions");cards.replaceChildren(...s.sessions.map(x=>card(x,changed.includes(x.projectSessionKey))));$("#final-state").textContent=s.finalReview.label;$("#final-detail").textContent=s.finalReview.detail;
 const list=$("#timeline-list");list.replaceChildren(...s.timeline.map(e=>{const li=text("li",e.at+" · "+e.label);return li}));}
async function refresh(changed=[]){try{const r=await fetch("/api/snapshot",{cache:"no-store"});if(!r.ok)throw Error(r.status);const s=await r.json();if(s.revision>=revision)render(s,changed);const ack={type:"revision-applied",revision:s.revision,visible:document.visibilityState==="visible"};if(channel&&channel.readyState===WebSocket.OPEN)channel.send(JSON.stringify(ack));else await fetch("/api/ack",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(ack)});status("connected","已连接 · Revision "+revision);retry=1000}catch(_){status("reconnecting","静态快照 · 正在重连")}}
function connect(){if(terminal){status("","终态静态快照 · Revision "+revision);return}clearInterval(poll);try{channel=new WebSocket((location.protocol==="https:"?"wss":"ws")+"://"+location.host+"/ws")}catch(_){fallback();return}channel.onopen=()=>{status("connected","已连接 · Revision "+revision);retry=1000};channel.onmessage=(e)=>{try{const m=JSON.parse(e.data);if(m.type==="revision-available")refresh(m.changedProjectSessionKeys||[])}catch(_){}};channel.onclose=()=>{if(terminal){status("","终态静态快照 · Revision "+revision);return}status("reconnecting","正在重连");setTimeout(connect,retry);retry=Math.min(retry*2,15000)};channel.onerror=()=>channel.close()}
function fallback(){poll=setInterval(refresh,3000);refresh()}
refresh();connect();
})();
""".strip()


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(value)
        stream.flush()
        os.fsync(stream.fileno())
    _replace_with_retry(temporary, path)


def _replace_with_retry(source: Path, destination: Path, attempts: int = 12) -> None:
    """Tolerate short Windows reader/AV locks without abandoning the revision."""
    for attempt in range(attempts):
        try:
            os.replace(source, destination)
            return
        except PermissionError:
            if attempt + 1 == attempts:
                raise
            time.sleep(min(0.01 * (2 ** attempt), 0.2))


def _next_action(state: str, native: str) -> str:
    if native == "attention":
        return "等待用户处理 Codex 请求"
    return {
        "READY": "派发当前批次",
        "WAITING_DEPENDENCY": "等待上游批准",
        "ASSIGNED": "继续监控",
        "SUBMITTED": "Manager 深读交付",
        "REVIEWING": "完成复核",
        "CHANGES_REQUESTED": "原 Session 继续修改",
        "APPROVED": "无",
        "BLOCKED": "解除阻塞",
        "STALE": "确认后重新排队",
    }.get(state, "核实状态")


def build_dashboard_snapshot(
    manifest: Mapping[str, Any], runtime_cache: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    cache = (runtime_cache or {}).get("threads", {})
    tasks_by_session: dict[str, list[Mapping[str, Any]]] = {}
    unassigned: list[Mapping[str, Any]] = []
    for task in manifest["workItems"]:
        key = task.get("projectSessionKey")
        (tasks_by_session.setdefault(key, []) if key else unassigned).append(task)

    sessions = []
    for session in manifest["projectSessions"]:
        key = session["projectSessionKey"]
        tasks = tasks_by_session.get(key, [])
        observation = cache.get(key, {})
        native = observation.get("nativeStatus", "unobserved")
        states = [task["state"] for task in tasks]
        state = next((candidate for candidate in (
            "BLOCKED", "CHANGES_REQUESTED", "REVIEWING", "SUBMITTED", "ASSIGNED",
            "READY", "WAITING_DEPENDENCY", "STALE", "APPROVED"
        ) if candidate in states), "READY")
        criteria = [criterion for task in tasks for criterion in task["acceptanceCriteria"]]
        open_findings = sum(
            1 for finding in manifest["findings"]
            if finding["status"] == "OPEN" and finding["taskId"] in {task["taskId"] for task in tasks}
        )
        attempts = max([max(1, task["review"].get("round", 0)) for task in tasks] or [1])
        binding = session["binding"]
        thread_id = binding.get("threadId") or binding.get("clientThreadId") or "-"
        sessions.append({
            "projectSessionKey": key,
            "repositoryId": session["repositoryId"],
            "projectId": session["projectId"],
            "expectedBranch": session["expectedBranch"],
            "title": "、".join(task["title"] for task in tasks) or binding["title"],
            "taskIds": [task["taskId"] for task in tasks],
            "pdcState": state,
            "pdcLabel": STATE_LABELS.get(state, state),
            "nativeStatus": native,
            "bindingState": binding["state"],
            "shortThreadId": thread_id if len(thread_id) <= 16 else thread_id[:8] + "…" + thread_id[-4:],
            "batch": max(1, len(tasks)),
            "attempt": attempts,
            "acceptancePassed": sum(1 for item in criteria if item["status"] in {"PASS", "WAIVED"}),
            "acceptanceTotal": len(criteria),
            "openFindings": open_findings,
            "attention": native == "attention" or open_findings > 0,
            "lastDecision": max(tasks, key=lambda item: item["updatedAt"])["lastTransition"]["reason"] if tasks else "等待任务",
            "nextAction": _next_action(state, native),
        })

    required = [task for task in manifest["workItems"] if task["required"]]
    approved = sum(task["state"] == "APPROVED" for task in required)
    if manifest["status"] in {"APPROVED", "CLOSED"}:
        final = {"label": "最终复核已通过", "detail": f"{approved}/{len(required)} 个必需任务已批准"}
    elif manifest["status"] == "BLOCKED":
        final = {"label": "最终复核受阻", "detail": "先解除阻塞，再执行跨仓库一致性检查"}
    else:
        final = {"label": "等待最终复核", "detail": f"已批准 {approved}/{len(required)}；Worker final 不等于批准"}

    active = next((item for item in sessions if item["pdcState"] != "APPROVED"), None)
    timeline = sorted(
        ({"at": task["lastTransition"]["at"], "label": f"{task['taskId']} · {task['lastTransition']['reason']}"}
         for task in manifest["workItems"]), key=lambda item: item["at"], reverse=True
    )[:20]
    return {
        "schemaVersion": "pdc-dashboard-2.0",
        "dispatchId": manifest["dispatchId"],
        "revision": manifest["revision"],
        "status": manifest["status"],
        "updatedAt": manifest["updatedAt"],
        "manager": {
            "currentGate": active["pdcLabel"] if active else "跨仓库最终复核",
            "nextAction": active["nextAction"] if active else "完成 Dispatch closeout",
        },
        "sessions": sessions,
        "unassignedTaskIds": [task["taskId"] for task in unassigned],
        "finalReview": final,
        "timeline": timeline,
    }


def _static_cards(snapshot: Mapping[str, Any]) -> str:
    cards = []
    for session in snapshot["sessions"]:
        cards.append(
            '<article class="panel session">'
            f'<div class="eyebrow">{html.escape(str(session["repositoryId"]))}</div>'
            f'<h2>{html.escape(str(session["title"]))}</h2>'
            f'<div class="id">{html.escape(" · ".join(session["taskIds"]))}</div>'
            '<div class="badges">'
            f'<span class="badge state-{html.escape(str(session["pdcState"]))}">{html.escape(str(session["pdcLabel"]))}</span>'
            f'<span class="badge native">Codex {html.escape(str(session["nativeStatus"]))}</span></div>'
            f'<p class="sub">{html.escape(str(session["projectId"]))} · {html.escape(str(session["expectedBranch"]))}</p>'
            f'<p class="sub">下一动作：{html.escape(str(session["nextAction"]))}</p></article>'
        )
    return "".join(cards) or '<p class="empty">尚无 Project Session</p>'


def render_dashboard_html(snapshot: Mapping[str, Any]) -> str:
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>PDC Dispatch {html.escape(str(snapshot['dispatchId']))}</title><link rel="stylesheet" href="/assets/dashboard.css"></head>
<body data-revision="{int(snapshot['revision'])}"><main class="shell">
<header class="bar"><h1>PDC 任务分发实时看板</h1><div id="connection" class="connection"><i class="dot"></i><span>静态快照</span></div></header>
<section class="panel manager"><div><div class="eyebrow">Manager</div><div class="value">{html.escape(str(snapshot['dispatchId']))}</div><div class="sub"><span id="dispatch-status">{html.escape(str(snapshot['status']))}</span> · <span id="revision">Revision {int(snapshot['revision'])}</span></div></div><div><div class="eyebrow">当前 Gate</div><div id="gate" class="value">{html.escape(str(snapshot['manager']['currentGate']))}</div></div><div><div class="eyebrow">下一动作</div><div id="next-action" class="value">{html.escape(str(snapshot['manager']['nextAction']))}</div></div></section>
<div class="flow-line"></div><section id="sessions" class="sessions">{_static_cards(snapshot)}</section><div class="flow-line"></div>
<section class="panel final"><div class="eyebrow">Manager 最终复核</div><div id="final-state" class="value">{html.escape(str(snapshot['finalReview']['label']))}</div><div id="final-detail" class="sub">{html.escape(str(snapshot['finalReview']['detail']))}</div></section>
<section class="panel timeline"><h2>最近状态变化</h2><ol id="timeline-list">{''.join(f'<li>{html.escape(str(item["at"]))} · {html.escape(str(item["label"]))}</li>' for item in snapshot['timeline'])}</ol></section>
<footer class="footer">1 Manager → {len(snapshot['sessions'])} Project Sessions → 1 Manager final · <span id="updated-at">{html.escape(str(snapshot['updatedAt']))}</span></footer>
</main><script src="/assets/dashboard.js" defer></script></body></html>\n"""


def render_dashboard(root: Path | str, manifest: Mapping[str, Any], runtime_cache: Mapping[str, Any] | None = None) -> dict[str, str]:
    live = Path(root) / "views" / "live"
    snapshot = build_dashboard_snapshot(manifest, runtime_cache)
    paths = {
        "dashboardHtml": live / "index.html",
        "dashboardSnapshot": live / "snapshot.json",
        "dashboardScript": live / "assets" / "dashboard.js",
        "dashboardStyle": live / "assets" / "dashboard.css",
    }
    _write_text(paths["dashboardHtml"], render_dashboard_html(snapshot))
    _write_text(paths["dashboardSnapshot"], json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n")
    _write_text(paths["dashboardScript"], JS + "\n")
    _write_text(paths["dashboardStyle"], CSS + "\n")
    return {key: str(value) for key, value in paths.items()}
