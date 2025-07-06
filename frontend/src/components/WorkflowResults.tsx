
import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Progress } from "@/components/ui/progress";
import {
  CheckCircle,
  Clock,
  AlertCircle,
  Download,
  Share,
  Eye,
  Activity,
  FileText,
  BarChart3,
  XCircle,
  RefreshCw
} from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { apiService, WorkflowStatus, WorkflowResponse, ApiError } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface WorkflowResultsProps {
  workflow: any;
  isExecuting: boolean;
  workflowId?: string;
  onExecutionComplete: () => void;
}

export const WorkflowResults = ({ workflow, isExecuting, workflowId, onExecutionComplete }: WorkflowResultsProps) => {
  const [workflowStatus, setWorkflowStatus] = useState<WorkflowStatus | null>(null);
  const [workflowResult, setWorkflowResult] = useState<WorkflowResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);
  const { toast } = useToast();

  // Poll workflow status when executing
  useEffect(() => {
    if (workflowId && isExecuting) {
      startPolling();
    } else {
      stopPolling();
    }

    return () => stopPolling();
  }, [workflowId, isExecuting]);

  const startPolling = () => {
    if (pollingInterval) {
      clearInterval(pollingInterval);
    }

    const interval = setInterval(async () => {
      try {
        if (!workflowId) return;

        const status = await apiService.getWorkflowStatus(workflowId);
        setWorkflowStatus(status);

        if (status.status === 'completed') {
          const result = await apiService.getWorkflowResult(workflowId);
          setWorkflowResult(result);
          stopPolling();
          onExecutionComplete();

          toast({
            title: "Workflow Completed",
            description: "Your workflow has been executed successfully!",
          });
        } else if (status.status === 'failed' || status.status === 'cancelled') {
          stopPolling();
          onExecutionComplete();

          toast({
            title: "Workflow Failed",
            description: `Workflow ${status.status}`,
            variant: "destructive",
          });
        }
      } catch (error) {
        const errorMessage = error instanceof ApiError
          ? `API Error (${error.status}): ${error.message}`
          : error instanceof Error
            ? error.message
            : 'Failed to get workflow status';

        setError(errorMessage);
        stopPolling();
        onExecutionComplete();
      }
    }, 1000);

    setPollingInterval(interval);
  };

  const stopPolling = () => {
    if (pollingInterval) {
      clearInterval(pollingInterval);
      setPollingInterval(null);
    }
  };

  const handleRefreshStatus = async () => {
    if (!workflowId) return;

    try {
      setError(null);
      const status = await apiService.getWorkflowStatus(workflowId);
      setWorkflowStatus(status);

      if (status.status === 'completed') {
        const result = await apiService.getWorkflowResult(workflowId);
        setWorkflowResult(result);
      }
    } catch (error) {
      const errorMessage = error instanceof ApiError
        ? `API Error (${error.status}): ${error.message}`
        : error instanceof Error
          ? error.message
          : 'Failed to refresh status';

      setError(errorMessage);
    }
  };

  // Get current progress
  const progress = workflowStatus?.progress || (isExecuting ? 35 : 100);
  const currentStatus = workflowStatus?.status || (isExecuting ? "running" : "pending");

  // Calculate execution metrics
  const executionTime = workflowStatus?.execution_time || workflowResult?.metadata?.execution_time || 0;
  const executedAgents = workflowStatus?.executed_agents || [];
  const currentAgent = workflowStatus?.current_agent;

  if (!workflow && !isExecuting) {
    return (
      <div className="space-y-4">
        <h3 className="text-xl font-semibold text-gray-900">Workflow Results</h3>
        <Card className="p-8 text-center">
          <div className="space-y-4">
            <Activity className="w-12 h-12 text-gray-400 mx-auto" />
            <div>
              <h4 className="font-medium text-gray-900">No Active Workflow</h4>
              <p className="text-sm text-gray-500 mt-1">
                Configure and execute a workflow to see results here
              </p>
            </div>
          </div>
        </Card>
      </div>
    );
  }

  const getStatusIcon = () => {
    switch (currentStatus) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'cancelled':
        return <XCircle className="w-5 h-5 text-gray-500" />;
      case 'running':
        return <Clock className="w-5 h-5 text-blue-500 animate-spin" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusBadge = () => {
    switch (currentStatus) {
      case 'completed':
        return <Badge className="bg-green-100 text-green-800">Completed</Badge>;
      case 'failed':
        return <Badge className="bg-red-100 text-red-800">Failed</Badge>;
      case 'cancelled':
        return <Badge className="bg-gray-100 text-gray-800">Cancelled</Badge>;
      case 'running':
        return <Badge className="bg-blue-100 text-blue-800">Running</Badge>;
      default:
        return <Badge variant="secondary">Pending</Badge>;
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-semibold text-gray-900">Workflow Results</h3>
        <div className="flex space-x-2">
          {workflowId && (
            <Button variant="outline" size="sm" onClick={handleRefreshStatus}>
              <RefreshCw className="w-4 h-4 mr-1" />
              Refresh
            </Button>
          )}
          {currentStatus === 'completed' && (
            <>
              <Button variant="outline" size="sm">
                <Download className="w-4 h-4 mr-1" />
                Export
              </Button>
              <Button variant="outline" size="sm">
                <Share className="w-4 h-4 mr-1" />
                Share
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Workflow Status */}
      {(isExecuting || workflowStatus) && (
        <Card className="p-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {getStatusIcon()}
                <span className="font-medium">
                  {currentStatus === 'running' ? 'Executing Workflow' : `Workflow ${currentStatus}`}
                </span>
                {workflowId && (
                  <span className="text-xs text-gray-500 font-mono">
                    {workflowId.slice(0, 8)}
                  </span>
                )}
              </div>
              {getStatusBadge()}
            </div>

            {(isExecuting || currentStatus === 'running') && (
              <Progress value={progress} className="w-full" />
            )}

            <div className="text-sm text-gray-600 space-y-1">
              {currentAgent && (
                <p>Current Agent: <span className="font-medium">{currentAgent}</span></p>
              )}
              {executedAgents.length > 0 && (
                <p>Executed Agents: {executedAgents.length} / {workflow?.metadata?.total_agents || '?'}</p>
              )}
              {executionTime > 0 && (
                <p>Execution Time: <span className="font-medium">{executionTime.toFixed(2)}s</span></p>
              )}
            </div>
          </div>
        </Card>
      )}

      {/* Results Tabs */}
      {(workflowResult || (currentStatus === 'completed' && workflow)) && (
        <Tabs defaultValue="output" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="output">Output</TabsTrigger>
            <TabsTrigger value="agents">Agents</TabsTrigger>
            <TabsTrigger value="details">Details</TabsTrigger>
            <TabsTrigger value="raw">Raw Data</TabsTrigger>
          </TabsList>

          <TabsContent value="output" className="space-y-4">
            <Card className="p-4">
              <div className="flex items-center space-x-2 mb-3">
                {getStatusIcon()}
                <span className="font-medium">Workflow Output</span>
                {executionTime > 0 && (
                  <Badge variant="secondary">{executionTime.toFixed(2)}s</Badge>
                )}
              </div>

              <ScrollArea className="h-64 w-full rounded border p-3 bg-gray-50">
                <div className="whitespace-pre-wrap text-sm">
                  {workflowResult?.content || "No output content available"}
                </div>
              </ScrollArea>

              <div className="flex justify-between items-center mt-3 text-sm text-gray-500">
                <span>Workflow ID: {workflowId?.slice(0, 8)}</span>
                <span>Status: {currentStatus}</span>
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="agents" className="space-y-4">
            <Card className="p-4">
              <div className="flex items-center space-x-2 mb-3">
                <Activity className="w-4 h-4 text-gray-500" />
                <span className="font-medium">Agent Execution</span>
              </div>

              <div className="space-y-2">
                {executedAgents.map((agent, index) => (
                  <div key={agent} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline">{index + 1}</Badge>
                      <span className="font-medium">{agent}</span>
                    </div>
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  </div>
                ))}

                {currentAgent && currentStatus === 'running' && (
                  <div className="flex items-center justify-between p-2 bg-blue-50 rounded">
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline">{executedAgents.length + 1}</Badge>
                      <span className="font-medium">{currentAgent}</span>
                    </div>
                    <Clock className="w-4 h-4 text-blue-500 animate-spin" />
                  </div>
                )}
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="details" className="space-y-4">
            <Card className="p-4 space-y-3">
              <div className="flex items-center space-x-2">
                <FileText className="w-4 h-4 text-gray-500" />
                <span className="font-medium">Execution Details</span>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Workflow ID:</span>
                  <span className="font-mono">{workflowId}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Status:</span>
                  {getStatusBadge()}
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Execution Time:</span>
                  <span>{executionTime > 0 ? `${executionTime.toFixed(2)}s` : 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Start Time:</span>
                  <span>{workflowStatus?.start_time ? new Date(workflowStatus.start_time).toLocaleString() : 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Agents Executed:</span>
                  <span>{executedAgents.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Original Request:</span>
                  <span className="text-right max-w-xs truncate">{workflow?.user_request || 'N/A'}</span>
                </div>
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="raw" className="space-y-4">
            <Card className="p-4">
              <div className="flex items-center space-x-2 mb-3">
                <BarChart3 className="w-4 h-4 text-gray-500" />
                <span className="font-medium">Raw Response Data</span>
              </div>

              <ScrollArea className="h-64 w-full rounded border p-3 bg-gray-50">
                <pre className="text-xs">
                  {JSON.stringify({
                    status: workflowStatus,
                    result: workflowResult,
                    workflow: workflow
                  }, null, 2)}
                </pre>
              </ScrollArea>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
};
