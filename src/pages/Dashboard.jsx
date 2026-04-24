import FormPanel from "../components/FormPanel";
import ChatPanel from "../components/ChatPanel";

const Dashboard = () => {
  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-950 to-slate-900 font-[Inter]">
      
      {/* LEFT FORM PANEL */}
      <div className="w-1/2 p-6 border-r border-slate-700 overflow-y-auto bg-gradient-to-br from-slate-900 to-slate-800">
        <div className="max-w-2xl">
          <FormPanel />
        </div>
      </div>

      {/* RIGHT AI CHAT PANEL */}
      <div className="w-1/2 p-6 overflow-hidden bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <ChatPanel />
      </div>

    </div>
  );
};

export default Dashboard;