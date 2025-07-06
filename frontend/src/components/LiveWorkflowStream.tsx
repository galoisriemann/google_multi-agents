import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
    Play,
    Square,
    Clock,
    CheckCircle2,
    XCircle,
    AlertCircle,
    Bot,
    Activity,
    Timer,
    Loader2,
    FileText,
    Download
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface LiveWorkflowStreamProps {
    workflowId?: string;
    isRunning: boolean;
    onStop: () => void;
    onRestart: () => void;
    userRequest: string;
    progress?: number;
    currentAgent?: string;
    workflowResult?: string | null;
    status?: string;
    onConfigurationRefresh?: () => void; // Optional callback for parent to know when config is refreshed
}

interface AgentInfo {
    name: string;
    type: string;
    description?: string;
}

interface WorkflowConfig {
    agents: AgentInfo[];
    name: string;
    description: string;
    version: string;
    main_agent: string;
}

export const LiveWorkflowStream = ({
    workflowId,
    isRunning,
    onStop,
    onRestart,
    userRequest,
    progress = 0,
    currentAgent = '',
    workflowResult = null,
    status = 'idle',
    onConfigurationRefresh
}: LiveWorkflowStreamProps) => {
    const [activeTab, setActiveTab] = useState("progress");
    const [interimOutputs, setInterimOutputs] = useState<any[]>([]);
    const [loadingInterim, setLoadingInterim] = useState(false);
    const [agentList, setAgentList] = useState<AgentInfo[]>([]);
    const [executedAgents, setExecutedAgents] = useState<string[]>([]);
    const [loadingConfig, setLoadingConfig] = useState(true);
    const { toast } = useToast();

    // Fetch workflow configuration and agent list
    const fetchWorkflowConfig = async () => {
        try {
            setLoadingConfig(true);
            console.log('🔄 Fetching workflow configuration...');
            const response = await fetch('http://localhost:8000/api/v1/workflow/config');
            if (response.ok) {
                const config: WorkflowConfig = await response.json();
                console.log('📋 Raw config received:', config);

                // Extract sequential agents from main orchestrator
                const sequentialAgents = config.agents.filter(agent =>
                    agent.type === 'LlmAgent' && agent.name !== config.main_agent
                );

                console.log('🔍 Filtered agents:', sequentialAgents.map(a => `${a.name} (${a.type})`));
                console.log('🎯 Main agent:', config.main_agent);

                setAgentList(sequentialAgents);
                console.log('✅ Loaded workflow config:', sequentialAgents.length, 'agents');
            } else {
                console.error('❌ Failed to fetch workflow config, status:', response.status);
                // Fallback to empty array - show no agents rather than wrong ones
                setAgentList([]);
            }
        } catch (error) {
            console.error('❌ Error fetching workflow config:', error);
            setAgentList([]);
        } finally {
            setLoadingConfig(false);
        }
    };

    // Fetch workflow status to get executed agents
    const fetchWorkflowStatus = async () => {
        if (!workflowId) return;

        try {
            const response = await fetch(`http://localhost:8000/api/v1/workflow/status/${workflowId}`);
            if (response.ok) {
                const statusData = await response.json();
                const executed = statusData.executed_agents || [];

                // Only log if there's a change to avoid spam
                if (JSON.stringify(executed) !== JSON.stringify(executedAgents)) {
                    console.log('📊 Executed agents updated:', executed);
                    console.log('🎯 Current agent:', statusData.current_agent);
                    console.log('📈 Progress:', statusData.progress);
                }

                setExecutedAgents(executed);
            }
        } catch (error) {
            console.error('❌ Error fetching workflow status:', error);
        }
    };

    // Load workflow configuration on mount and when needed
    useEffect(() => {
        fetchWorkflowConfig();
    }, []);

    // Refresh configuration when YAML files might have changed
    // This can be triggered by parent component if needed
    const refreshConfiguration = async () => {
        console.log('🔄 Refreshing workflow configuration...');
        await fetchWorkflowConfig();
        // Notify parent component that configuration was refreshed
        if (onConfigurationRefresh) {
            onConfigurationRefresh();
        }
    };

    // Refresh configuration when workflow is restarted (user might have changed YAML)
    useEffect(() => {
        if (isRunning && workflowId) {
            console.log('🔄 Workflow restarted, refreshing configuration...');
            fetchWorkflowConfig();
        }
    }, [workflowId]); // Trigger when workflowId changes (new workflow started)

    // Fetch status periodically while running
    useEffect(() => {
        if (isRunning && workflowId) {
            fetchWorkflowStatus();
            const interval = setInterval(fetchWorkflowStatus, 1000);
            return () => clearInterval(interval);
        }
    }, [isRunning, workflowId]);

    useEffect(() => {
        if (status === 'completed' && workflowResult) {
            setActiveTab("results");
        }
    }, [status, workflowResult]);

    // Fetch interim outputs
    const fetchInterimOutputs = async () => {
        if (!workflowId) return;

        setLoadingInterim(true);
        try {
            const response = await fetch(`http://localhost:8000/api/v1/workflow/${workflowId}/interim-outputs`);
            if (response.ok) {
                const data = await response.json();
                setInterimOutputs(data.outputs || []);
            }
        } catch (error) {
            console.error('Failed to fetch interim outputs:', error);
        } finally {
            setLoadingInterim(false);
        }
    };

    // Fetch interim outputs when workflow completes or when tab is switched
    useEffect(() => {
        if (activeTab === "interim" && workflowId) {
            fetchInterimOutputs();
        }
    }, [activeTab, workflowId]);

    // Auto-refresh interim outputs while running
    useEffect(() => {
        if (isRunning && workflowId) {
            const interval = setInterval(fetchInterimOutputs, 5000); // Every 5 seconds
            return () => clearInterval(interval);
        }
    }, [isRunning, workflowId]);

    const getStatusIcon = (currentStatus: string) => {
        switch (currentStatus) {
            case 'running': return <Activity className="w-4 h-4 text-blue-500 animate-pulse" />;
            case 'completed': return <CheckCircle2 className="w-4 h-4 text-green-500" />;
            case 'failed': return <XCircle className="w-4 h-4 text-red-500" />;
            case 'cancelled': return <Square className="w-4 h-4 text-gray-500" />;
            default: return <Clock className="w-4 h-4 text-gray-400" />;
        }
    };

    const getStatusBadge = (currentStatus: string) => {
        const variants = {
            running: 'bg-blue-100 text-blue-800',
            completed: 'bg-green-100 text-green-800',
            failed: 'bg-red-100 text-red-800',
            cancelled: 'bg-gray-100 text-gray-800',
            idle: 'bg-gray-100 text-gray-800'
        };
        return <Badge className={variants[currentStatus as keyof typeof variants] || variants.idle}>
            {currentStatus.charAt(0).toUpperCase() + currentStatus.slice(1)}
        </Badge>;
    };

    const downloadResult = () => {
        if (!workflowResult) return;

        const blob = new Blob([workflowResult], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `workflow-result-${workflowId || 'result'}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        toast({
            title: "Downloaded",
            description: "Workflow result has been downloaded",
        });
    };

    return (
        <div className="space-y-6">
            {/* Header with Progress Overview */}
            <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                        {getStatusIcon(status)}
                        <h2 className="text-xl font-bold">Live Workflow Stream</h2>
                        {getStatusBadge(status)}
                    </div>
                    <div className="flex items-center space-x-2">
                        {isRunning && status === 'running' && (
                            <Button variant="destructive" size="sm" onClick={onStop}>
                                <Square className="w-4 h-4 mr-1" />
                                Stop
                            </Button>
                        )}
                        {!isRunning && status !== 'running' && (
                            <Button onClick={onRestart} className="bg-green-600 hover:bg-green-700">
                                <Play className="w-4 h-4 mr-1" />
                                Restart Workflow
                            </Button>
                        )}
                        {workflowResult && status === 'completed' && (
                            <Button variant="outline" onClick={downloadResult}>
                                <Download className="w-4 h-4 mr-1" />
                                Download Result
                            </Button>
                        )}
                    </div>
                </div>

                {/* Progress Bar */}
                <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                        <span>Overall Progress: {Math.round(progress)}%</span>
                        <span>Status: {status}</span>
                    </div>
                    <Progress value={progress} className="h-2" />
                </div>

                {/* Current Agent */}
                {currentAgent && status === 'running' && (
                    <div className="mt-4 p-3 bg-blue-50 rounded-lg border-l-4 border-blue-400">
                        <div className="flex items-center space-x-2">
                            <Loader2 className="w-4 h-4 text-blue-600 animate-spin" />
                            <span className="font-medium text-blue-900">
                                Currently Running: {currentAgent}
                            </span>
                        </div>
                    </div>
                )}

                {/* Completion Message */}
                {status === 'completed' && (
                    <div className="mt-4 p-3 bg-green-50 rounded-lg border-l-4 border-green-400">
                        <div className="flex items-center space-x-2">
                            <CheckCircle2 className="w-4 h-4 text-green-600" />
                            <span className="font-medium text-green-900">
                                ✅ Workflow completed successfully!
                            </span>
                        </div>
                    </div>
                )}
            </Card>

            {/* Request Details */}
            <Card className="p-6">
                <h3 className="font-semibold mb-3 flex items-center">
                    <FileText className="w-4 h-4 mr-2" />
                    User Request
                </h3>
                <div className="p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm">{userRequest}</p>
                </div>
                {workflowId && (
                    <div className="mt-3 text-xs text-gray-500">
                        Workflow ID: {workflowId}
                    </div>
                )}
            </Card>

            {/* Tabs for different views */}
            <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="progress">Agent Progress</TabsTrigger>
                    <TabsTrigger value="interim" disabled={!workflowId}>
                        Interim Outputs ({interimOutputs.length})
                    </TabsTrigger>
                    <TabsTrigger value="results" disabled={!workflowResult}>Results</TabsTrigger>
                </TabsList>

                <TabsContent value="progress" className="space-y-4">
                    <Card className="p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="font-semibold">Agent Execution Status</h3>
                            <div className="flex items-center space-x-2">
                                <Badge variant="outline" className="text-xs">
                                    {agentList.length} agents loaded
                                </Badge>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={refreshConfiguration}
                                    disabled={loadingConfig}
                                >
                                    {loadingConfig ? (
                                        <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                                    ) : (
                                        <Download className="w-4 h-4 mr-1" />
                                    )}
                                    Refresh Config
                                </Button>
                            </div>
                        </div>
                        <div className="space-y-3">
                            {loadingConfig ? (
                                <div className="flex items-center justify-center py-8">
                                    <Loader2 className="w-5 h-5 animate-spin mr-2" />
                                    <span>Loading workflow configuration...</span>
                                </div>
                            ) : agentList.length === 0 ? (
                                <div className="text-center py-8">
                                    <div className="text-gray-500">
                                        <Clock className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                                        <p>No agents configured in the workflow.</p>
                                        <p className="text-sm mt-1">Check your workflow configuration file.</p>
                                    </div>
                                </div>
                            ) : (
                                agentList.map((agent, index) => {
                                    // Fix: Use actual execution status instead of flawed percentage calculation
                                    const isCompleted = status === 'completed' || executedAgents.includes(agent.name);
                                    const isCurrent = currentAgent === agent.name;

                                    return (
                                        <div key={agent.name} className={`flex items-center space-x-3 p-3 rounded-lg ${isCurrent ? 'bg-blue-50 border-l-4 border-blue-400' :
                                            isCompleted ? 'bg-green-50' : 'bg-gray-50'
                                            }`}>
                                            <div className="flex-shrink-0">
                                                {isCurrent ? (
                                                    <Loader2 className="w-4 h-4 text-blue-600 animate-spin" />
                                                ) : isCompleted ? (
                                                    <CheckCircle2 className="w-4 h-4 text-green-600" />
                                                ) : (
                                                    <Clock className="w-4 h-4 text-gray-400" />
                                                )}
                                            </div>
                                            <div className="flex-1">
                                                <span className={`font-medium ${isCurrent ? 'text-blue-900' :
                                                    isCompleted ? 'text-green-900' : 'text-gray-600'
                                                    }`}>
                                                    {agent.name}
                                                </span>
                                                {agent.description && (
                                                    <div className="text-xs text-gray-500 mt-1">
                                                        {agent.description}
                                                    </div>
                                                )}
                                                {isCurrent && (
                                                    <div className="text-sm text-blue-700 mt-1">
                                                        Currently processing...
                                                    </div>
                                                )}
                                            </div>
                                            <div>
                                                <Badge variant={isCurrent ? "default" : isCompleted ? "secondary" : "outline"}>
                                                    {isCurrent ? "Running" : isCompleted ? "Completed" : "Pending"}
                                                </Badge>
                                            </div>
                                        </div>
                                    );
                                })
                            )}
                        </div>
                    </Card>
                </TabsContent>

                <TabsContent value="interim" className="space-y-4">
                    <Card className="p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="font-semibold">Interim Agent Outputs</h3>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={fetchInterimOutputs}
                                disabled={loadingInterim}
                            >
                                {loadingInterim ? (
                                    <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                                ) : (
                                    <Download className="w-4 h-4 mr-1" />
                                )}
                                Refresh
                            </Button>
                        </div>

                        {interimOutputs.length > 0 ? (
                            <div className="space-y-4">
                                {interimOutputs.map((output, index) => (
                                    <div key={index} className="border rounded-lg">
                                        <div className="flex items-center justify-between p-3 bg-gray-50 border-b">
                                            <div className="flex items-center space-x-2">
                                                <Bot className="w-4 h-4 text-blue-600" />
                                                <span className="font-medium">{output.agent_name}</span>
                                                <Badge variant="outline" className="text-xs">
                                                    {output.filename}
                                                </Badge>
                                            </div>
                                            <span className="text-xs text-gray-500">
                                                {new Date(output.timestamp).toLocaleString()}
                                            </span>
                                        </div>
                                        <ScrollArea className="h-64 p-4">
                                            <pre className="whitespace-pre-wrap text-sm text-gray-700">
                                                {output.content}
                                            </pre>
                                        </ScrollArea>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-8">
                                {loadingInterim ? (
                                    <div className="flex items-center justify-center space-x-2">
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                        <span>Loading interim outputs...</span>
                                    </div>
                                ) : (
                                    <div className="text-gray-500">
                                        <FileText className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                                        <p>No interim outputs available yet.</p>
                                        <p className="text-sm mt-1">Outputs will appear here as agents complete their work.</p>
                                    </div>
                                )}
                            </div>
                        )}
                    </Card>
                </TabsContent>

                <TabsContent value="results" className="space-y-4">
                    {workflowResult ? (
                        <Card className="p-6">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="font-semibold">Workflow Results</h3>
                                <Button variant="outline" onClick={downloadResult}>
                                    <Download className="w-4 h-4 mr-1" />
                                    Download
                                </Button>
                            </div>
                            <ScrollArea className="h-96 w-full">
                                <div className="p-4 bg-gray-50 rounded-lg">
                                    <pre className="whitespace-pre-wrap text-sm">{workflowResult}</pre>
                                </div>
                            </ScrollArea>
                        </Card>
                    ) : (
                        <Card className="p-6">
                            <Alert>
                                <AlertCircle className="h-4 w-4" />
                                <AlertDescription>
                                    Results will be available once the workflow completes successfully.
                                </AlertDescription>
                            </Alert>
                        </Card>
                    )}
                </TabsContent>
            </Tabs>
        </div>
    );
}; 