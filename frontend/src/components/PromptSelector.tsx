
import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { FileText, Sparkles, MessageSquare, BarChart3 } from "lucide-react";

interface PromptSelectorProps {
  selectedPrompt: string;
  onPromptChange: (prompt: string) => void;
}

const promptTemplates = [
  {
    id: "data-analysis",
    title: "Data Analysis Agent",
    description: "Analyze datasets and provide insights",
    icon: BarChart3,
    template: "You are a data analysis expert. Analyze the provided dataset and create comprehensive insights including trends, patterns, and recommendations.",
    category: "Analytics"
  },
  {
    id: "content-writer",
    title: "Content Writer Agent",
    description: "Generate high-quality content",
    icon: FileText,
    template: "You are a professional content writer. Create engaging, well-structured content that is informative and tailored to the target audience.",
    category: "Content"
  },
  {
    id: "customer-support",
    title: "Customer Support Agent",
    description: "Handle customer inquiries professionally",
    icon: MessageSquare,
    template: "You are a helpful customer support agent. Provide clear, empathetic, and solution-focused responses to customer inquiries.",
    category: "Support"
  },
  {
    id: "creative-assistant",
    title: "Creative Assistant",
    description: "Generate creative ideas and solutions",
    icon: Sparkles,
    template: "You are a creative assistant. Generate innovative ideas, creative solutions, and help brainstorm unique approaches to challenges.",
    category: "Creative"
  }
];

export const PromptSelector = ({ selectedPrompt, onPromptChange }: PromptSelectorProps) => {
  const [customPrompt, setCustomPrompt] = useState("");
  const [selectedTemplate, setSelectedTemplate] = useState("");

  const handleTemplateSelect = (template: any) => {
    setSelectedTemplate(template.id);
    setCustomPrompt(template.template);
    onPromptChange(template.template);
  };

  const handleCustomPromptChange = (value: string) => {
    setCustomPrompt(value);
    onPromptChange(value);
    setSelectedTemplate("");
  };

  return (
    <div className="space-y-6">
      <div>
        <Label className="text-lg font-semibold">Choose a Prompt Template</Label>
        <p className="text-sm text-gray-600 mt-1">Select a pre-built template or create your own custom prompt</p>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {promptTemplates.map((template) => {
          const Icon = template.icon;
          const isSelected = selectedTemplate === template.id;
          
          return (
            <Card 
              key={template.id}
              className={`p-4 cursor-pointer transition-all hover:shadow-md ${
                isSelected ? 'ring-2 ring-purple-500 bg-purple-50' : 'hover:bg-gray-50'
              }`}
              onClick={() => handleTemplateSelect(template)}
            >
              <div className="flex items-start space-x-3">
                <div className={`p-2 rounded-lg ${isSelected ? 'bg-purple-500' : 'bg-gray-200'}`}>
                  <Icon className={`w-5 h-5 ${isSelected ? 'text-white' : 'text-gray-600'}`} />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-gray-900">{template.title}</h3>
                    <Badge variant="secondary" className="text-xs">{template.category}</Badge>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{template.description}</p>
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      <div className="space-y-3">
        <Label htmlFor="custom-prompt" className="text-lg font-semibold">Custom Prompt</Label>
        <Textarea
          id="custom-prompt"
          placeholder="Enter your custom prompt here..."
          value={customPrompt}
          onChange={(e) => handleCustomPromptChange(e.target.value)}
          className="min-h-[150px] resize-none"
        />
        <div className="flex justify-between items-center text-sm text-gray-500">
          <span>{customPrompt.length} characters</span>
          <Button variant="ghost" size="sm" onClick={() => handleCustomPromptChange("")}>
            Clear
          </Button>
        </div>
      </div>
    </div>
  );
};
