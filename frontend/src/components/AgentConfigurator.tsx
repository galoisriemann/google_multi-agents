
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Settings, Thermometer, Timer, Repeat, Shield, Bot, Workflow, Tool } from "lucide-react";
import { WorkflowConfig } from "@/lib/api";

interface AgentConfiguratorProps {
  config: any;
  onConfigChange: (config: any) => void;
  workflowConfig?: WorkflowConfig | null;
}

export const AgentConfigurator = ({ config, onConfigChange, workflowConfig }: AgentConfiguratorProps) => {
  const updateConfig = (key: string, value: any) => {
    onConfigChange({ ...config, [key]: value });
  };

  return (
    <div className="space-y-6">
      <div>
        <Label className="text-lg font-semibold">Workflow Configuration</Label>
        <p className="text-sm text-gray-600 mt-1">
          {workflowConfig ?
            `Review the ${workflowConfig.name} workflow configuration and adjust parameters` :
            "Loading workflow configuration..."
          }
        </p>
      </div>

      {/* Workflow Overview */}
      {workflowConfig && (
        <Card className="p-4 space-y-4">
          <div className="flex items-center space-x-2">
            <Workflow className="w-5 h-5 text-indigo-500" />
            <h3 className="font-semibold">Workflow Overview</h3>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <Label className="text-sm font-medium">Workflow Name</Label>
              <p className="text-sm text-gray-700">{workflowConfig.name}</p>
            </div>
            <div>
              <Label className="text-sm font-medium">Version</Label>
              <p className="text-sm text-gray-700">{workflowConfig.version}</p>
            </div>
            <div>
              <Label className="text-sm font-medium">Main Agent</Label>
              <p className="text-sm text-gray-700">{workflowConfig.main_agent}</p>
            </div>
            <div>
              <Label className="text-sm font-medium">Total Agents</Label>
              <p className="text-sm text-gray-700">{workflowConfig.agents.length}</p>
            </div>
          </div>

          <div>
            <Label className="text-sm font-medium">Description</Label>
            <p className="text-sm text-gray-700 mt-1">{workflowConfig.description}</p>
          </div>
        </Card>
      )}

      {/* Agents List */}
      {workflowConfig && (
        <Card className="p-4 space-y-4">
          <div className="flex items-center space-x-2">
            <Bot className="w-5 h-5 text-blue-500" />
            <h3 className="font-semibold">Configured Agents ({workflowConfig.agents.length})</h3>
          </div>

          <ScrollArea className="h-48 w-full">
            <div className="space-y-2">
              {workflowConfig.agents.map((agent, index) => (
                <div key={agent.name} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <div className="flex items-center space-x-2">
                    <Badge variant="outline">{index + 1}</Badge>
                    <div>
                      <p className="font-medium text-sm">{agent.name}</p>
                      <p className="text-xs text-gray-500">{agent.type}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    {agent.model && (
                      <Badge variant="secondary" className="text-xs">{agent.model}</Badge>
                    )}
                    {agent.tools.length > 0 && (
                      <p className="text-xs text-gray-500 mt-1">{agent.tools.length} tools</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        </Card>
      )}

      {/* Available Tools */}
      {workflowConfig && workflowConfig.available_tools.length > 0 && (
        <Card className="p-4 space-y-4">
          <div className="flex items-center space-x-2">
            <Tool className="w-5 h-5 text-green-500" />
            <h3 className="font-semibold">Available Tools ({workflowConfig.available_tools.length})</h3>
          </div>

          <div className="grid grid-cols-2 gap-2">
            {workflowConfig.available_tools.map((tool) => (
              <Badge key={tool.name} variant="outline" className="justify-start">
                {tool.name}
              </Badge>
            ))}
          </div>
        </Card>
      )}

      <div className="grid md:grid-cols-2 gap-6">
        {/* Model Parameters */}
        <Card className="p-4 space-y-4">
          <div className="flex items-center space-x-2">
            <Thermometer className="w-5 h-5 text-blue-500" />
            <h3 className="font-semibold">Model Parameters</h3>
          </div>

          <div className="space-y-4">
            <div>
              <div className="flex justify-between items-center mb-2">
                <Label>Temperature</Label>
                <Badge variant="outline">{config.temperature || 0.7}</Badge>
              </div>
              <Slider
                value={[config.temperature || 0.7]}
                onValueChange={(value) => updateConfig('temperature', value[0])}
                max={2}
                min={0}
                step={0.1}
                className="w-full"
              />
              <p className="text-xs text-gray-500 mt-1">Controls randomness in responses</p>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <Label>Max Tokens</Label>
                <Badge variant="outline">{config.maxTokens || 1000}</Badge>
              </div>
              <Slider
                value={[config.maxTokens || 1000]}
                onValueChange={(value) => updateConfig('maxTokens', value[0])}
                max={4000}
                min={100}
                step={100}
                className="w-full"
              />
              <p className="text-xs text-gray-500 mt-1">Maximum response length</p>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <Label>Top P</Label>
                <Badge variant="outline">{config.topP || 0.9}</Badge>
              </div>
              <Slider
                value={[config.topP || 0.9]}
                onValueChange={(value) => updateConfig('topP', value[0])}
                max={1}
                min={0}
                step={0.1}
                className="w-full"
              />
              <p className="text-xs text-gray-500 mt-1">Nucleus sampling parameter</p>
            </div>
          </div>
        </Card>

        {/* Execution Settings */}
        <Card className="p-4 space-y-4">
          <div className="flex items-center space-x-2">
            <Settings className="w-5 h-5 text-purple-500" />
            <h3 className="font-semibold">Execution Settings</h3>
          </div>

          <div className="space-y-4">
            <div>
              <Label htmlFor="timeout">Timeout (seconds)</Label>
              <Input
                id="timeout"
                type="number"
                value={config.timeout || 30}
                onChange={(e) => updateConfig('timeout', parseInt(e.target.value))}
                className="mt-1"
              />
            </div>

            <div>
              <Label htmlFor="retry">Retry Attempts</Label>
              <Select value={config.retryAttempts || "3"} onValueChange={(value) => updateConfig('retryAttempts', value)}>
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">1 attempt</SelectItem>
                  <SelectItem value="3">3 attempts</SelectItem>
                  <SelectItem value="5">5 attempts</SelectItem>
                  <SelectItem value="10">10 attempts</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="priority">Execution Priority</Label>
              <Select value={config.priority || "normal"} onValueChange={(value) => updateConfig('priority', value)}>
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="normal">Normal</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="urgent">Urgent</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </Card>
      </div>

      {/* Advanced Options */}
      <Card className="p-4 space-y-4">
        <div className="flex items-center space-x-2">
          <Shield className="w-5 h-5 text-green-500" />
          <h3 className="font-semibold">Advanced Options</h3>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div className="flex items-center justify-between">
            <div>
              <Label>Stream Response</Label>
              <p className="text-xs text-gray-500">Enable real-time response streaming</p>
            </div>
            <Switch
              checked={config.stream || false}
              onCheckedChange={(checked) => updateConfig('stream', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label>Enable Logging</Label>
              <p className="text-xs text-gray-500">Log execution details</p>
            </div>
            <Switch
              checked={config.logging || true}
              onCheckedChange={(checked) => updateConfig('logging', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label>Parallel Execution</Label>
              <p className="text-xs text-gray-500">Run multiple agents simultaneously</p>
            </div>
            <Switch
              checked={config.parallel || false}
              onCheckedChange={(checked) => updateConfig('parallel', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label>Auto-Save Results</Label>
              <p className="text-xs text-gray-500">Automatically save workflow outputs</p>
            </div>
            <Switch
              checked={config.autoSave || true}
              onCheckedChange={(checked) => updateConfig('autoSave', checked)}
            />
          </div>
        </div>
      </Card>
    </div>
  );
};
