import React from 'react';

export default function DashboardPage() {
  const agent_status = "Online";
  const last_tasks = [
    { id: 1, name: "Linting QAgent/core", status: "Completed", time: "2m ago" },
    { id: 2, name: "Unit Tests: Bot handlers", status: "Failed", time: "5m ago" },
    { id: 3, name: "Dependency Scan", status: "In Progress", time: "Just now" },
  ];

  return (
    <div className="flex min-h-screen bg-[#020617] text-slate-200">
      {/* Sidebar */}
      <aside className="w-72 border-r border-[#1e293b] bg-[#020617]/50 backdrop-blur-xl p-6 flex flex-col gap-8">
        <div className="flex items-center gap-3 px-2">
          <div className="w-10 h-10 bg-teal-500 rounded-xl flex items-center justify-center shadow-lg shadow-teal-500/20">
            <span className="font-bold text-white text-xl">Q</span>
          </div>
          <h1 className="text-xl font-bold tracking-tight text-white">QAgent Pro</h1>
        </div>

        <nav className="flex flex-col gap-2">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-widest px-4 mb-2">Principal</div>
          <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-teal-500/10 text-teal-400 border-l-2 border-teal-400 cursor-pointer">
            <span>🏠</span>
            <span className="font-medium">Dashboard</span>
          </div>
          <div className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-800 transition-all cursor-pointer text-slate-400">
            <span>🤖</span>
            <span>Agentes</span>
          </div>
          <div className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-800 transition-all cursor-pointer text-slate-400">
            <span>🛠️</span>
            <span>Ferramentas</span>
          </div>
          <div className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-800 transition-all cursor-pointer text-slate-400">
            <span>📋</span>
            <span>Logs</span>
          </div>
        </nav>

        <div className="mt-auto">
          <div className="p-4 bg-slate-900/50 rounded-2xl border border-white/5">
            <div className="text-xs text-slate-500 mb-1">Status do Sistema</div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-teal-500 animate-pulse"></div>
              <span className="text-sm font-medium text-teal-400">Tudo operacional</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-10 overflow-y-auto">
        <header className="flex justify-between items-center mb-10">
          <div>
            <h2 className="text-3xl font-bold text-white mb-2 tracking-tight">Monitor de Automação</h2>
            <p className="text-slate-400">Acompanhe as execuções de QA em tempo limitado.</p>
          </div>
          <button className="px-6 py-2 bg-teal-500 text-white rounded-xl hover:bg-teal-400 transition-all shadow-lg shadow-teal-500/20 font-medium">
            Nova Execução
          </button>
        </header>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          <div className="p-6 bg-[#0f172a]/50 backdrop-blur-xl border border-white/5 rounded-3xl">
            <div className="text-slate-500 text-sm mb-4 font-medium uppercase tracking-wider">Status do Agente</div>
            <div className="flex items-end justify-between">
              <span className="text-3xl font-bold text-teal-400">{agent_status}</span>
              <span className="text-xs text-slate-600">ID: #8421</span>
            </div>
          </div>
          <div className="p-6 bg-[#0f172a]/50 backdrop-blur-xl border border-white/5 rounded-3xl">
            <div className="text-slate-500 text-sm mb-4 font-medium uppercase tracking-wider">Tasks Hoje</div>
            <div className="flex items-end justify-between">
              <span className="text-3xl font-bold text-white">42</span>
              <span className="text-xs text-teal-500">+12% vs ontem</span>
            </div>
          </div>
          <div className="p-6 bg-[#0f172a]/50 backdrop-blur-xl border border-white/5 rounded-3xl">
            <div className="text-slate-500 text-sm mb-4 font-medium uppercase tracking-wider">Média de Cobertura</div>
            <div className="flex items-end justify-between">
              <span className="text-3xl font-bold text-sky-400">84.2%</span>
              <div className="w-24 h-2 bg-slate-800 rounded-full overflow-hidden mb-2">
                <div className="h-full bg-sky-400 w-[84%]"></div>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Tasks */}
        <div className="bg-[#0f172a]/50 backdrop-blur-xl border border-white/5 rounded-3xl p-8">
          <h3 className="text-xl font-bold text-white mb-6">Execuções Recentes</h3>
          <div className="flex flex-col gap-4">
            {last_tasks.map((task) => (
              <div key={task.id} className="flex items-center justify-between p-4 rounded-2xl hover:bg-white/5 transition-all group cursor-pointer border border-transparent hover:border-white/5">
                <div className="flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-xl shadow-inner ${
                    task.status === "Completed" ? "bg-teal-500/10 text-teal-400" : 
                    task.status === "Failed" ? "bg-rose-500/10 text-rose-400" : 
                    "bg-sky-500/10 text-sky-400 animate-pulse"
                  }`}>
                    {task.status === "Completed" ? "✓" : task.status === "Failed" ? "!" : "..."}
                  </div>
                  <div>
                    <div className="font-bold text-white group-hover:text-teal-400 transition-colors">{task.name}</div>
                    <div className="text-sm text-slate-500">{task.time}</div>
                  </div>
                </div>
                <div className={`px-4 py-1 rounded-full text-xs font-bold uppercase tracking-widest ${
                  task.status === "Completed" ? "bg-teal-500/10 text-teal-400" : 
                  task.status === "Failed" ? "bg-rose-500/10 text-rose-400" : 
                  "bg-sky-500/10 text-sky-400"
                }`}>
                  {task.status}
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
