
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { PromptSelector } from "@/components/PromptSelector";
import { ModelSelector } from "@/components/ModelSelector";
import { AgentConfigurator } from "@/components/AgentConfigurator";
import { Play, Save, Download } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface WorkflowBuilderProps {
  onWorkflowChange: (workflow: any) => void;
  isExecuting: boolean;
  onExecute: (executing: boolean) => void;
}

export const WorkflowBuilder = ({ onWorkflowChange, isExecuting, onExecute }: WorkflowBuilderProps) => {
  const [selectedPrompt, setSelectedPrompt] = useState("");
  const [selectedModel, setSelectedModel] = useState("");
  const [agentConfig, setAgentConfig] = useState({});
  const { toast } = useToast();

  const handleExecuteWorkflow = async () => {
    if (!selectedPrompt || !selectedModel) {
      toast({
        title: "Missing Configuration",
        description: "Please select both a prompt and model before executing.",
        variant: "destructive",
      });
      return;
    }

    onExecute(true);
    
    const workflow = {
      prompt: selectedPrompt,
      model: selectedModel,
      config: agentConfig,
      timestamp: new Date().toISOString(),
    };
    
    onWorkflowChange(workflow);

    // Simulate workflow execution
    setTimeout(() => {
      onExecute(false);
      toast({
        title: "Workflow Completed",
        description: "Your agentic workflow has been executed successfully!",
      });
    }, 3000);
  };

  const handleSaveWorkflow = () => {
    toast({
      title: "Workflow Saved",
      description: "Your workflow configuration has been saved.",
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Build Your Workflow</h2>
        <div className="flex space-x-2">
          <Button variant="outline" onClick={handleSaveWorkflow}>
            <Save className="w-4 h-4 mr-2" />
            Save
          </Button>
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      <Tabs defaultValue="prompt" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="prompt">1. Prompt</TabsTrigger>
          <TabsTrigger value="model">2. Model</TabsTrigger>
          <TabsTrigger value="agent">3. Agent Config</TabsTrigger>
        </TabsList>
        
        <TabsContent value="prompt" className="space-y-4">
          <PromptSelector 
            selectedPrompt={selectedPrompt}
            onPromptChange={setSelectedPrompt}
          />
        </TabsContent>
        
        <TabsContent value="model" className="space-y-4">
          <ModelSelector 
            selectedModel={selectedModel}
            onModelChange={setSelectedModel}
          />
        </TabsContent>
        
        <TabsContent value="agent" className="space-y-4">
          <AgentConfigurator 
            config={agentConfig}
            onConfigChange={setAgentConfig}
          />
        </TabsContent>
      </Tabs>

      <div className="pt-4 border-t">
        <Button 
          onClick={handleExecuteWorkflow}
          disabled={isExecuting || !selectedPrompt || !selectedModel}
          className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
          size="lg"
        >
          <Play className="w-5 h-5 mr-2" />
          {isExecuting ? "Executing Workflow..." : "Execute Workflow"}
        </Button>
      </div>
    </div>
  );
};
