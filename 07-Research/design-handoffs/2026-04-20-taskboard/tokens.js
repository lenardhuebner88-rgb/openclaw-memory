// Shared tokens + data for the Mission Control UI kit.
// Mirrors colors_and_type.css + assignee/priority/state metadata from the codebase.

window.MC = window.MC || {};

// 6 agents (JM = James, researcher). Operator is pieter_pan / PP.
window.MC.agents = {
  pieter_pan: { badge: "PP", display: "pieter_pan", color: "#3b82f6", tone: "bg-blue-500/20 text-blue-200 border-blue-400/30" },
  Atlas:      { badge: "AT", display: "Atlas",      color: "#14b8a6", tone: "bg-teal-500/20 text-teal-200 border-teal-400/30" },
  Forge:      { badge: "FO", display: "Forge",      color: "#f97316", tone: "bg-orange-500/20 text-orange-200 border-orange-400/30" },
  James:      { badge: "JM", display: "James",      color: "#10b981", tone: "bg-emerald-500/20 text-emerald-200 border-emerald-400/30" },
  Lens:       { badge: "LN", display: "Lens",       color: "#eab308", tone: "bg-yellow-500/20 text-yellow-200 border-yellow-400/30" },
  Pixel:      { badge: "PX", display: "Pixel",      color: "#d946ef", tone: "bg-fuchsia-500/20 text-fuchsia-200 border-fuchsia-400/30" },
  Spark:      { badge: "SP", display: "Spark",      color: "#ec4899", tone: "bg-pink-500/20 text-pink-200 border-pink-400/30" },
};

window.MC.priority = {
  low:    { label: "Low",    tone: "zinc"   },
  medium: { label: "Medium", tone: "sky"    },
  high:   { label: "High",   tone: "amber"  },
  urgent: { label: "Urgent", tone: "rose"   },
};

window.MC.execState = {
  draft:              { label: "Draft",          tone: "zinc",    icon: "○" },
  queued:             { label: "Queued",         tone: "sky",     icon: "◔" },
  "pending-pickup":   { label: "Pending Pickup", tone: "indigo",  icon: "◔" },
  blocked:            { label: "Blocked",        tone: "red",     icon: "⛔" },
  "dispatched-active":{ label: "Active",         tone: "emerald", icon: "◉" },
  "waiting-result":   { label: "Waiting",        tone: "amber",   icon: "◐" },
  review:             { label: "Review",         tone: "cyan",    icon: "◉" },
  done:               { label: "Done",           tone: "emerald", icon: "✓" },
};

window.MC.lanes = [
  { id: "needs",     name: "Needs attention", ornament: "requires operator" },
  { id: "active",    name: "Active now",       ornament: "dispatched" },
  { id: "ready",     name: "Ready",            ornament: "queue" },
  { id: "upcoming",  name: "Upcoming",         ornament: "backlog" },
  { id: "done",      name: "Done today",       ornament: "closed" },
];

// Demo tasks
window.MC.tasks = [
  { id: "t1", title: "Reconcile taskboard audit receipts",        lane: "needs",    agent: "Pixel", priority: "high",   state: "blocked",            age: "4m",  meta: "Age 3h · mission-control · 2/3 retries",    callout: "Blocked · waiting on lock #4821",    ruleId: "candidate-for-operatorLock" },
  { id: "t2", title: "Retry ready — nightly research crawl",      lane: "needs",    agent: "James", priority: "medium", state: "waiting-result",     age: "12m", meta: "Age 1d · james · 2/3 retries used",         callout: "Failure reason preserved for triage", ruleId: "ready-for-retry" },
  { id: "t3", title: "Dispatch new analytics report",             lane: "active",   agent: "Lens",  priority: "medium", state: "dispatched-active",  age: "just now", meta: "Age 14m · analytics" },
  { id: "t4", title: "Kick off design review for taskboard v3",   lane: "active",   agent: "Pixel", priority: "high",   state: "dispatched-active",  age: "2m",  meta: "Age 22m · mission-control" },
  { id: "t5", title: "Compile weekly ops digest",                 lane: "active",   agent: "Atlas", priority: "low",    state: "waiting-result",     age: "8m",  meta: "Age 1h · ops" },
  { id: "t6", title: "Summarize competitor launch threads",       lane: "ready",    agent: "James", priority: "low",    state: "queued",             age: "—",   meta: "Queued 20m ago · research" },
  { id: "t7", title: "Rotate scratch vault keys",                 lane: "ready",    agent: "Forge", priority: "medium", state: "pending-pickup",     age: "—",   meta: "Dispatched 4m ago · vault" },
  { id: "t8", title: "Draft incident comms for auth flake",       lane: "upcoming", agent: "Spark", priority: "urgent", state: "draft",              age: "—",   meta: "Created 2d ago · incident" },
  { id: "t9", title: "Port admin cleanup modal to shadcn dialog", lane: "upcoming", agent: "Pixel", priority: "low",    state: "draft",              age: "—",   meta: "Backlog · mission-control" },
  { id: "t10", title: "Close daily budget review",                lane: "done",     agent: "Atlas", priority: "low",    state: "done",               age: "1h",  meta: "Closed 11/04 05:32" },
  { id: "t11", title: "Patch Forge rate-limit regression",        lane: "done",     agent: "Forge", priority: "high",   state: "done",               age: "2h",  meta: "Closed 11/04 03:58" },
];

// Agent load (percent)
window.MC.agentLoad = [
  { name: "Atlas", badge: "AT", color: "#14b8a6", load: 62, tasks: 4 },
  { name: "Forge", badge: "FO", color: "#f97316", load: 88, tasks: 7 },
  { name: "James", badge: "JM", color: "#10b981", load: 24, tasks: 2 },
  { name: "Lens",  badge: "LN", color: "#eab308", load: 44, tasks: 3 },
  { name: "Pixel", badge: "PX", color: "#d946ef", load: 71, tasks: 5 },
  { name: "Spark", badge: "SP", color: "#ec4899", load: 12, tasks: 1 },
];

window.MC.activity = [
  { t: "just now", agent: "Lens",  kind: "dispatch", text: "Dispatched analytics report" },
  { t: "2m",       agent: "Pixel", kind: "review",   text: "Flagged taskboard audit for operator review" },
  { t: "8m",       agent: "Atlas", kind: "waiting",  text: "Waiting on rate-limit reset from Forge" },
  { t: "14m",      agent: "James", kind: "retry",    text: "Retry ready · nightly research crawl" },
  { t: "22m",      agent: "Forge", kind: "done",     text: "Closed rate-limit patch" },
  { t: "1h",       agent: "Spark", kind: "draft",    text: "Drafted incident comms for auth flake" },
];

window.MC.nav = [
  { key:"dashboard", icon:"🏠", label:"Dashboard", href:"#/overview" },
  { key:"tasks",     icon:"☑️", label:"Tasks",     href:"#/taskboard" },
  { key:"alerts",    icon:"🚨", label:"Alerts",    href:"#/alerts" },
  { key:"team",      icon:"👥", label:"Team",      href:"#/team" },
  { key:"analytics", icon:"📊", label:"Analytics", href:"#/analytics" },
  { key:"more",      icon:"➕", label:"More",      href:"#/more" },
];

// Subroutes for desktop secondary row
window.MC.subnav = {
  dashboard: [{label:"Overview", href:"#/overview", icon:"🏠"}, {label:"Monitoring", href:"#/monitoring", icon:"🩺"}],
  tasks:     [{label:"Taskboard", href:"#/taskboard", icon:"☑️"}, {label:"Kanban", href:"#/kanban", icon:"🚀"}],
  more:      [{label:"Analytics", href:"#/analytics", icon:"📊"}, {label:"Ops", href:"#/ops", icon:"🛠️"}, {label:"Costs", href:"#/costs", icon:"💰"}, {label:"Trends", href:"#/trends", icon:"📈"}, {label:"Files", href:"#/files", icon:"📂"}],
};
