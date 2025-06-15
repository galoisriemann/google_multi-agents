
import { useState } from "react";
import { Header } from "@/components/Header";
import { WorkflowBuilder } from "@/components/WorkflowBuilder";
import { WorkflowResults } from "@/components/WorkflowResults";
import { Card } from "@/components/ui/card";

const Index = () => {
  const [currentWorkflow, setCurrentWorkflow] = useState(null);
  const [isExecuting, setIsExecuting] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <Header />
      
      <main className="container mx-auto px-4 py-8 space-y-8">
        {/* Hero Section */}
        <div className="text-center space-y-4 py-12">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
            AI Agent Workflow Builder
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Design, configure, and execute powerful AI agent workflows with our intuitive interface
          </p>
        </div>

        {/* Main Content */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Workflow Builder */}
          <div className="lg:col-span-2">
            <Card className="p-6 shadow-lg border-0 bg-white/70 backdrop-blur-sm">
              <WorkflowBuilder 
                onWorkflowChange={setCurrentWorkflow}
                isExecuting={isExecuting}
                onExecute={setIsExecuting}
              />
            </Card>
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-1">
            <Card className="p-6 shadow-lg border-0 bg-white/70 backdrop-blur-sm h-fit">
              <WorkflowResults 
                workflow={currentWorkflow}
                isExecuting={isExecuting}
              />
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Index;
