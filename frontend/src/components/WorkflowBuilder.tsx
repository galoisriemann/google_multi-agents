
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { PromptSelector } from "@/components/PromptSelector";
import { ModelSelector } from "@/components/ModelSelector";
import { AgentConfigurator } from "@/components/AgentConfigurator";
import { Play, Save, Download, RefreshCw, AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useToast } from "@/hooks/use-toast";
import { apiService, WorkflowConfig, ApiError } from "@/lib/api";

interface WorkflowBuilderProps {
  onWorkflowChange: (workflow: any) => void;
  isExecuting: boolean;
  onExecute: (executing: boolean) => void;
  onWorkflowStart: (workflowId: string) => void;
}

export const WorkflowBuilder = ({ onWorkflowChange, isExecuting, onExecute, onWorkflowStart }: WorkflowBuilderProps) => {
  const [userRequest, setUserRequest] = useState("Create a comprehensive LLM guided Gartner style market research report generating framework");
  const [selectedPrompt, setSelectedPrompt] = useState("");
  const [selectedModel, setSelectedModel] = useState("");
  const [agentConfig, setAgentConfig] = useState({});
  const [workflowConfig, setWorkflowConfig] = useState<WorkflowConfig | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  // Load workflow configuration on component mount
  useEffect(() => {
    loadWorkflowConfig();
  }, []);

  const loadWorkflowConfig = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const config = await apiService.getWorkflowConfig();
      setWorkflowConfig(config);
      toast({
        title: "Configuration Loaded",
        description: `Loaded ${config.name} v${config.version} with ${config.agents.length} agents`,
      });
    } catch (error) {
      const errorMessage = error instanceof ApiError 
        ? `API Error (${error.status}): ${error.message}`
        : error instanceof Error 
        ? error.message 
        : 'Failed to load workflow configuration';
      
      setError(errorMessage);
      toast({
        title: "Configuration Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleExecuteWorkflow = async () => {
    if (!userRequest.trim()) {
      toast({
        title: "Missing Request",
        description: "Please enter a request for the workflow to process.",
        variant: "destructive",
      });
      return;
    }

    onExecute(true);
    
    try {
      const workflowRequest = {
        user_request: userRequest,
        prompt: selectedPrompt || undefined,
        model: selectedModel || undefined,
        config: agentConfig,
      };

      const response = await apiService.executeWorkflow(workflowRequest);
      
      const workflow = {
        id: response.id,
        user_request: userRequest,
        prompt: selectedPrompt,
        model: selectedModel,
        config: agentConfig,
        timestamp: new Date().toISOString(),
        status: response.status,
        metadata: response.metadata,
      };
      
      onWorkflowChange(workflow);
      onWorkflowStart(response.id);
      
      toast({
        title: "Workflow Started",
        description: `Workflow ${response.id} has been started successfully!`,
      });
      
    } catch (error) {
      onExecute(false);
      
      const errorMessage = error instanceof ApiError 
        ? `API Error (${error.status}): ${error.message}`
        : error instanceof Error 
        ? error.message 
        : 'Failed to execute workflow';
      
      toast({
        title: "Execution Error",
        description: errorMessage,
        variant: "destructive",
      });
    }
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
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Build Your Workflow</h2>
          {workflowConfig && (
            <p className="text-sm text-gray-600 mt-1">
              {workflowConfig.name} v{workflowConfig.version} • {workflowConfig.agents.length} agents
            </p>
          )}
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" onClick={loadWorkflowConfig} disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
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

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* User Request */}
      <div className="space-y-2">
        <Label htmlFor="user-request">Your Request</Label>
        <Textarea
          id="user-request"
          placeholder="Describe what you want the AI workflow to accomplish..."
          value={userRequest}
          onChange={(e) => setUserRequest(e.target.value)}
          rows={3}
          className="min-h-[80px]"
        />
        <p className="text-sm text-gray-500">
          This is the main request that will be processed by the flexible agent workflow.
        </p>
      </div>

      <Tabs defaultValue="request" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="request">1. Request</TabsTrigger>
          <TabsTrigger value="prompt">2. Prompt</TabsTrigger>
          <TabsTrigger value="model">3. Model</TabsTrigger>
          <TabsTrigger value="agent">4. Config</TabsTrigger>
        </TabsList>
        
        <TabsContent value="request" className="space-y-4">
          <Card className="p-4">
            <h3 className="font-semibold mb-3">Workflow Overview</h3>
            {workflowConfig ? (
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Workflow:</span>
                  <span>{workflowConfig.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Version:</span>
                  <span>{workflowConfig.version}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Main Agent:</span>
                  <span>{workflowConfig.main_agent}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Agents:</span>
                  <span>{workflowConfig.agents.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Available Tools:</span>
                  <span>{workflowConfig.available_tools.length}</span>
                </div>
              </div>
            ) : (
              <p className="text-gray-500">Loading workflow configuration...</p>
            )}
          </Card>
        </TabsContent>
        
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
            workflowConfig={workflowConfig}
          />
        </TabsContent>
      </Tabs>

      <div className="pt-4 border-t">
        <Button 
          onClick={handleExecuteWorkflow}
          disabled={isExecuting || !userRequest.trim() || !workflowConfig}
          className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
          size="lg"
        >
          <Play className="w-5 h-5 mr-2" />
          {isExecuting ? "Executing Workflow..." : "Execute Workflow"}
        </Button>
        {!workflowConfig && (
          <p className="text-sm text-gray-500 text-center mt-2">
            Waiting for configuration to load...
          </p>
        )}
      </div>
    </div>
  );
};
