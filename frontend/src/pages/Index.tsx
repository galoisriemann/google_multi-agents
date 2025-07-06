import { useState, useEffect, useRef } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Separator } from "@/components/ui/separator";
import {
  FileText,
  Settings,
  Play,
  Activity,
  CheckCircle,
  AlertCircle,
  Rocket,
  Upload,
  Clock,
  Zap,
  ArrowRight
} from "lucide-react";
import { YamlConfigManager } from "@/components/YamlConfigManager";
import { LiveWorkflowStream } from "@/components/LiveWorkflowStream";
import { useToast } from "@/hooks/use-toast";

interface YamlFile {
  name: string;
  content: string;
  isValid: boolean;
  error?: string;
  lastModified?: Date;
  warnings?: string[];
}

interface InputFile {
  name: string;
  content: string;
  type: string;
  size: number;
  lastModified: Date;
}

type WorkflowStatus = 'idle' | 'validating' | 'running' | 'completed' | 'failed';

const Index = () => {
  const [configurations, setConfigurations] = useState<Record<string, YamlFile>>({});
  const [inputFiles, setInputFiles] = useState<InputFile[]>([]);
  const [isConfigReady, setIsConfigReady] = useState(false);
  const [activeTab, setActiveTab] = useState<string>("configuration");
  const [userRequest, setUserRequest] = useState(`Create a comprehensive LLM guided Gartner style market research report generating framework that includes:

1. Industry analysis and competitive landscape mapping
2. Market trends identification and future predictions  
3. Technology adoption analysis and recommendations
4. Strategic insights and actionable recommendations
5. Executive summary with key findings

The framework should be modular, scalable, and provide detailed documentation for implementation.`);
  const [workflowId, setWorkflowId] = useState<string | null>(null);
  const [workflowStatus, setWorkflowStatus] = useState<WorkflowStatus>('idle');
  const [executionStartTime, setExecutionStartTime] = useState<Date | null>(null);
  const [workflowProgress, setWorkflowProgress] = useState<number>(0);
  const [currentAgent, setCurrentAgent] = useState<string>('');
  const [workflowResult, setWorkflowResult] = useState<string | null>(null);
  const { toast } = useToast();
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Check if all configurations are valid
  useEffect(() => {
    const allValid = Object.values(configurations).every(config => config.isValid);
    const hasConfigs = Object.keys(configurations).length >= 3; // workflow, gemini, prompts
    setIsConfigReady(allValid && hasConfigs);
  }, [configurations]);

  // Status polling effect
  useEffect(() => {
    const pollWorkflowStatus = async () => {
      if (!workflowId || workflowStatus !== 'running') return;

      try {
        const response = await fetch(`http://localhost:8000/api/v1/workflow/status/${workflowId}`);
        if (response.ok) {
          const statusData = await response.json();

          setWorkflowProgress(statusData.progress || 0);
          setCurrentAgent(statusData.current_agent || '');

          if (statusData.status === 'completed') {
            setWorkflowStatus('completed');
            setWorkflowProgress(100);
            setCurrentAgent('Completed');

            // Fetch the final result
            try {
              console.log('Fetching workflow result for ID:', workflowId);
              const resultResponse = await fetch(`http://localhost:8000/api/v1/workflow/result/${workflowId}`);
              if (resultResponse.ok) {
                const resultData = await resultResponse.json();
                console.log('Result data received:', {
                  hasContent: !!resultData.content,
                  contentLength: resultData.content?.length || 0,
                  status: resultData.status
                });

                if (resultData.content) {
                  setWorkflowResult(resultData.content);
                  // Switch to stream tab to show the result
                  setActiveTab("stream");
                } else {
                  setWorkflowResult('Workflow completed but no content was generated.');
                }
              } else {
                console.error('Failed to fetch result:', resultResponse.status, resultResponse.statusText);
                setWorkflowResult('Failed to retrieve workflow result.');
              }
            } catch (error) {
              console.error('Failed to fetch workflow result:', error);
              setWorkflowResult('Error occurred while retrieving workflow result.');
            }

            // Clear polling
            if (pollingIntervalRef.current) {
              clearInterval(pollingIntervalRef.current);
              pollingIntervalRef.current = null;
            }

            toast({
              title: "Workflow Completed",
              description: `Your workflow has completed successfully in ${statusData.execution_time?.toFixed(1) || 'unknown'}s!`,
            });
          } else if (statusData.status === 'failed') {
            setWorkflowStatus('failed');
            // Clear polling
            if (pollingIntervalRef.current) {
              clearInterval(pollingIntervalRef.current);
              pollingIntervalRef.current = null;
            }

            toast({
              title: "Workflow Failed",
              description: statusData.error || "Workflow execution failed",
              variant: "destructive",
            });
          }
        }
      } catch (error) {
        console.error('Failed to poll workflow status:', error);
      }
    };

    if (workflowId && workflowStatus === 'running') {
      // Start polling every 1 second for better responsiveness
      pollingIntervalRef.current = setInterval(pollWorkflowStatus, 1000);

      // Initial poll
      pollWorkflowStatus();
    } else {
      // Clear polling if not running
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    }

    // Cleanup on unmount
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    };
  }, [workflowId, workflowStatus, toast]);

  const handleConfigurationReady = (configs: Record<string, YamlFile>, inputFilesParam?: InputFile[]) => {
    setConfigurations(configs);
    if (inputFilesParam) {
      setInputFiles(inputFilesParam);
    }
  };

  const validateRequest = (): { isValid: boolean; error?: string } => {
    if (!userRequest.trim()) {
      return { isValid: false, error: "Please enter a request for the workflow" };
    }

    if (userRequest.trim().length < 10) {
      return { isValid: false, error: "Request must be at least 10 characters long" };
    }

    if (!isConfigReady) {
      return { isValid: false, error: "Please ensure all YAML configurations are valid" };
    }

    return { isValid: true };
  };

  const startWorkflow = async () => {
    const validation = validateRequest();

    if (!validation.isValid) {
      toast({
        title: "Validation Error",
        description: validation.error,
        variant: "destructive",
      });
      return;
    }

    setWorkflowStatus('validating');

    try {
      // Create a new workflow execution request
      const response = await fetch('http://localhost:8000/api/v1/workflow/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_request: userRequest.trim(),
          config: configurations
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (result.id) {
        setWorkflowId(result.id);
        setWorkflowStatus('running');
        setExecutionStartTime(new Date());
        setActiveTab("stream");

        toast({
          title: "Workflow Started",
          description: `Workflow execution started with ID: ${result.id}`,
        });
      } else {
        throw new Error("No workflow ID returned from server");
      }

    } catch (error) {
      console.error('Error starting workflow:', error);
      setWorkflowStatus('failed');

      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to start workflow. Please check your connection and try again.",
        variant: "destructive",
      });
    }
  };

  const stopWorkflow = async () => {
    if (!workflowId) return;

    try {
      await fetch(`http://localhost:8000/api/v1/workflow/${workflowId}`, {
        method: 'DELETE',
      });

      setWorkflowStatus('idle');
      setWorkflowId(null);
      setExecutionStartTime(null);
      setWorkflowProgress(0);
      setCurrentAgent('');
      setWorkflowResult(null);

      toast({
        title: "Workflow Stopped",
        description: "Workflow execution has been stopped",
      });

    } catch (error) {
      console.error('Error stopping workflow:', error);
      toast({
        title: "Error",
        description: "Failed to stop workflow",
        variant: "destructive",
      });
    }
  };

  const restartWorkflow = () => {
    setWorkflowStatus('idle');
    setWorkflowId(null);
    setExecutionStartTime(null);
    setWorkflowProgress(0);
    setCurrentAgent('');
    setWorkflowResult(null);
    setActiveTab("execution");
  };

  const handleWorkflowComplete = () => {
    setWorkflowStatus('completed');
  };

  const getTabIcon = (tab: string) => {
    switch (tab) {
      case 'configuration': return <Settings className="w-4 h-4" />;
      case 'execution': return <Play className="w-4 h-4" />;
      case 'stream': return <Activity className="w-4 h-4" />;
      default: return null;
    }
  };

  const getStatusBadge = () => {
    switch (workflowStatus) {
      case 'running':
        return <Badge className="bg-blue-100 text-blue-800 animate-pulse">Running</Badge>;
      case 'completed':
        return <Badge className="bg-green-100 text-green-800">Completed</Badge>;
      case 'failed':
        return <Badge className="bg-red-100 text-red-800">Failed</Badge>;
      case 'validating':
        return <Badge className="bg-yellow-100 text-yellow-800">Validating</Badge>;
      default:
        return <Badge variant="outline">Ready</Badge>;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg">
                <Rocket className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Multi-agent Workflow Engine
                </h1>
                <p className="text-sm text-gray-600">
                  Advanced AI-driven workflow orchestration with live monitoring
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              {getStatusBadge()}
              {workflowId && (
                <Badge 
                  variant="outline" 
                  className="font-mono text-xs cursor-pointer hover:bg-gray-50" 
                  title={`Click to copy full ID: ${workflowId}`}
                  onClick={() => {
                    navigator.clipboard.writeText(workflowId);
                    toast({
                      title: "Copied!",
                      description: "Workflow ID copied to clipboard",
                    });
                  }}
                >
                  ID: {workflowId}
                </Badge>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          {/* Tab Navigation */}
          <TabsList className="grid w-full grid-cols-3 max-w-md mx-auto">
            <TabsTrigger
              value="configuration"
              disabled={workflowStatus === 'running'}
              className="flex items-center space-x-2"
            >
              {getTabIcon('configuration')}
              <span>Configure</span>
              {isConfigReady && <CheckCircle className="w-4 h-4 text-green-500 ml-1" />}
            </TabsTrigger>
            <TabsTrigger
              value="execution"
              disabled={!isConfigReady || workflowStatus === 'running'}
              className="flex items-center space-x-2"
            >
              {getTabIcon('execution')}
              <span>Execute</span>
              {userRequest.trim() && <CheckCircle className="w-4 h-4 text-green-500 ml-1" />}
            </TabsTrigger>
            <TabsTrigger
              value="stream"
              disabled={!workflowId}
              className="flex items-center space-x-2"
            >
              {getTabIcon('stream')}
              <span>Live Stream</span>
              {workflowStatus === 'completed' && <CheckCircle className="w-4 h-4 text-green-500 ml-1" />}
            </TabsTrigger>
          </TabsList>

          {/* Configuration Tab */}
          <TabsContent value="configuration" className="space-y-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {isConfigReady ? (
                    <Badge className="bg-green-100 text-green-800">
                      <CheckCircle className="w-4 h-4 mr-1" />
                      Ready
                    </Badge>
                  ) : (
                    <Badge variant="outline">
                      <AlertCircle className="w-4 h-4 mr-1" />
                      Configuration Required
                    </Badge>
                  )}
                </div>
              </div>

              <YamlConfigManager
                onConfigurationReady={handleConfigurationReady}
                isDisabled={workflowStatus === 'running'}
              />

              {isConfigReady && (
                <Alert className="border-green-200 bg-green-50">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-800">
                    <div className="space-y-1">
                      <div className="font-semibold">Configuration Complete!</div>
                      <div>All YAML files are valid and {inputFiles.length} input files are ready for workflow execution.</div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setActiveTab("execution")}
                        className="mt-2 bg-green-600 text-white hover:bg-green-700"
                      >
                        Proceed to Execution <ArrowRight className="w-4 h-4 ml-1" />
                      </Button>
                    </div>
                  </AlertDescription>
                </Alert>
              )}
            </div>
          </TabsContent>

          {/* Execution Tab */}
          <TabsContent value="execution" className="space-y-6">
            <Card className="p-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-semibold">Workflow Execution</h2>
                    <p className="text-gray-600">Enter your request and start the workflow</p>
                  </div>
                  {isConfigReady && (
                    <Badge className="bg-green-100 text-green-800">
                      <CheckCircle className="w-4 h-4 mr-1" />
                      Configuration Valid
                    </Badge>
                  )}
                </div>

                {/* Pre-execution Checklist */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-2">
                    {isConfigReady ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-red-500" />
                    )}
                    <span className={`text-sm font-medium ${isConfigReady ? 'text-green-700' : 'text-red-700'}`}>
                      YAML Configuration
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    {userRequest.trim() ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-red-500" />
                    )}
                    <span className={`text-sm font-medium ${userRequest.trim() ? 'text-green-700' : 'text-red-700'}`}>
                      User Request
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    {workflowStatus === 'idle' ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : (
                      <Clock className="w-5 h-5 text-yellow-500" />
                    )}
                    <span className={`text-sm font-medium ${workflowStatus === 'idle' ? 'text-green-700' : 'text-yellow-700'}`}>
                      System Ready
                    </span>
                  </div>
                </div>

                {/* Request Input */}
                <div className="space-y-2">
                  <Label htmlFor="user-request">User Request</Label>
                  <Textarea
                    id="user-request"
                    placeholder="Enter your workflow request here... (e.g., 'Create a comprehensive market analysis report for the AI industry')"
                    value={userRequest}
                    onChange={(e) => setUserRequest(e.target.value)}
                    disabled={workflowStatus === 'running' || workflowStatus === 'validating'}
                    className="min-h-24"
                  />
                  <p className="text-sm text-gray-500">
                    Minimum 10 characters required. Be specific about your requirements.
                  </p>
                </div>

                {/* Current Configuration Summary */}
                <div className="p-4 bg-blue-50 rounded-lg space-y-2">
                  <h4 className="font-medium text-blue-900">Configuration Summary</h4>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-blue-700">YAML Files:</span>
                      <span className="ml-2 text-blue-600">
                        {Object.keys(configurations).length} loaded
                      </span>
                    </div>
                    <div>
                      <span className="font-medium text-blue-700">Input Files:</span>
                      <span className="ml-2 text-blue-600">
                        {inputFiles.length} uploaded
                      </span>
                    </div>
                    <div>
                      <span className="font-medium text-blue-700">Status:</span>
                      <span className="ml-2 text-blue-600">
                        {isConfigReady ? 'All Valid' : 'Validation Required'}
                      </span>
                    </div>
                    <div>
                      <span className="font-medium text-blue-700">Request:</span>
                      <span className="ml-2 text-blue-600">
                        {userRequest.trim() ? `${userRequest.length} chars` : 'Not provided'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center justify-between pt-4">
                  <Button
                    variant="outline"
                    onClick={() => setActiveTab("configuration")}
                    disabled={workflowStatus === 'running'}
                  >
                    <Settings className="w-4 h-4 mr-2" />
                    Back to Configuration
                  </Button>
                  <Button
                    onClick={startWorkflow}
                    disabled={!isConfigReady || !userRequest.trim() || workflowStatus === 'running' || workflowStatus === 'validating'}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    {workflowStatus === 'validating' ? (
                      <>
                        <Clock className="w-4 h-4 mr-2 animate-spin" />
                        Validating...
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4 mr-2" />
                        Start Workflow
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </Card>
          </TabsContent>

          {/* Live Stream Tab */}
          <TabsContent value="stream" className="space-y-6">
            {workflowId ? (
              <LiveWorkflowStream
                workflowId={workflowId}
                isRunning={workflowStatus === 'running'}
                onStop={stopWorkflow}
                onRestart={restartWorkflow}
                userRequest={userRequest}
                progress={workflowProgress}
                currentAgent={currentAgent}
                workflowResult={workflowResult}
                status={workflowStatus}
              />
            ) : (
              <Card className="p-12 text-center">
                <Activity className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  No Active Workflow
                </h3>
                <p className="text-gray-600 mb-4">
                  Start a workflow from the execution tab to see live updates here
                </p>
                <Button onClick={() => setActiveTab("execution")}>
                  <Play className="w-4 h-4 mr-2" />
                  Go to Execution
                </Button>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

export default Index;
