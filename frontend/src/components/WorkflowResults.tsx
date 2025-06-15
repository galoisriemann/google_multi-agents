
import { useState } from "react";
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
  BarChart3
} from "lucide-react";

interface WorkflowResultsProps {
  workflow: any;
  isExecuting: boolean;
}

export const WorkflowResults = ({ workflow, isExecuting }: WorkflowResultsProps) => {
  const [progress, setProgress] = useState(isExecuting ? 35 : 100);

  // Simulate progress updates
  if (isExecuting && progress < 100) {
    setTimeout(() => setProgress(progress + 10), 300);
  }

  const mockResults = {
    execution: {
      status: isExecuting ? "running" : "completed",
      duration: "2.3s",
      tokens: 1247,
      cost: "$0.0031"
    },
    output: `Based on the provided prompt and configuration, I've analyzed the data and generated the following insights:

## Key Findings
- The primary trend shows a 23% increase in user engagement
- Customer satisfaction scores have improved by 15%
- Revenue growth is trending upward with a 12% increase month-over-month

## Recommendations
1. Continue current engagement strategies
2. Implement feedback loops for continuous improvement
3. Scale successful initiatives to other segments

## Next Steps
The analysis suggests focusing on retention strategies and expanding the customer base through targeted campaigns.`,
    metrics: {
      accuracy: 94,
      confidence: 87,
      relevance: 91
    }
  };

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

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-semibold text-gray-900">Workflow Results</h3>
        {!isExecuting && (
          <div className="flex space-x-2">
            <Button variant="outline" size="sm">
              <Download className="w-4 h-4 mr-1" />
              Export
            </Button>
            <Button variant="outline" size="sm">
              <Share className="w-4 h-4 mr-1" />
              Share
            </Button>
          </div>
        )}
      </div>

      {isExecuting && (
        <Card className="p-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-blue-500 animate-spin" />
                <span className="font-medium">Executing Workflow</span>
              </div>
              <Badge variant="secondary">In Progress</Badge>
            </div>
            <Progress value={progress} className="w-full" />
            <p className="text-sm text-gray-600">
              Processing with {workflow?.model || "selected model"}...
            </p>
          </div>
        </Card>
      )}

      {!isExecuting && workflow && (
        <Tabs defaultValue="output" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="output">Output</TabsTrigger>
            <TabsTrigger value="metrics">Metrics</TabsTrigger>
            <TabsTrigger value="details">Details</TabsTrigger>
          </TabsList>
          
          <TabsContent value="output" className="space-y-4">
            <Card className="p-4">
              <div className="flex items-center space-x-2 mb-3">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <span className="font-medium">Execution Complete</span>
                <Badge variant="secondary">{mockResults.execution.duration}</Badge>
              </div>
              
              <ScrollArea className="h-64 w-full rounded border p-3 bg-gray-50">
                <div className="whitespace-pre-wrap text-sm">
                  {mockResults.output}
                </div>
              </ScrollArea>
              
              <div className="flex justify-between items-center mt-3 text-sm text-gray-500">
                <span>{mockResults.execution.tokens} tokens used</span>
                <span>Cost: {mockResults.execution.cost}</span>
              </div>
            </Card>
          </TabsContent>
          
          <TabsContent value="metrics" className="space-y-4">
            <div className="grid gap-4">
              {Object.entries(mockResults.metrics).map(([key, value]) => (
                <Card key={key} className="p-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-medium capitalize">{key}</span>
                    <span className="text-lg font-bold">{value}%</span>
                  </div>
                  <Progress value={value} className="w-full" />
                </Card>
              ))}
            </div>
          </TabsContent>
          
          <TabsContent value="details" className="space-y-4">
            <Card className="p-4 space-y-3">
              <div className="flex items-center space-x-2">
                <FileText className="w-4 h-4 text-gray-500" />
                <span className="font-medium">Execution Details</span>
              </div>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Model:</span>
                  <span className="font-medium">{workflow.model}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Status:</span>
                  <Badge variant="secondary">{mockResults.execution.status}</Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Duration:</span>
                  <span>{mockResults.execution.duration}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Timestamp:</span>
                  <span>{new Date(workflow.timestamp).toLocaleString()}</span>
                </div>
              </div>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
};
