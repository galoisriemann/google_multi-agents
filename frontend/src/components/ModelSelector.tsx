
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Brain, Zap, Shield, Cpu } from "lucide-react";

interface ModelSelectorProps {
  selectedModel: string;
  onModelChange: (model: string) => void;
}

const models = [
  {
    id: "gpt-4-turbo",
    name: "GPT-4 Turbo",
    provider: "OpenAI",
    description: "Most capable model with excellent reasoning",
    icon: Brain,
    pricing: "$0.01/1K tokens",
    features: ["128K context", "Vision capable", "JSON mode"],
    performance: { speed: 85, accuracy: 95, cost: 70 }
  },
  {
    id: "claude-3-opus",
    name: "Claude 3 Opus",
    provider: "Anthropic",
    description: "Best for complex reasoning and analysis",
    icon: Shield,
    pricing: "$0.015/1K tokens",
    features: ["200K context", "Constitutional AI", "Helpful & harmless"],
    performance: { speed: 80, accuracy: 98, cost: 60 }
  },
  {
    id: "gemini-pro",
    name: "Gemini Pro",
    provider: "Google",
    description: "Fast and efficient for production use",
    icon: Zap,
    pricing: "$0.0025/1K tokens",
    features: ["32K context", "Multimodal", "Fast inference"],
    performance: { speed: 95, accuracy: 88, cost: 90 }
  },
  {
    id: "llama-2-70b",
    name: "LLaMA 2 70B",
    provider: "Meta",
    description: "Open source powerhouse",
    icon: Cpu,
    pricing: "$0.0008/1K tokens",
    features: ["4K context", "Open source", "Self-hostable"],
    performance: { speed: 75, accuracy: 85, cost: 95 }
  }
];

export const ModelSelector = ({ selectedModel, onModelChange }: ModelSelectorProps) => {
  return (
    <div className="space-y-6">
      <div>
        <Label className="text-lg font-semibold">Select AI Model</Label>
        <p className="text-sm text-gray-600 mt-1">Choose the AI model that best fits your workflow requirements</p>
      </div>

      <RadioGroup value={selectedModel} onValueChange={onModelChange} className="space-y-4">
        {models.map((model) => {
          const Icon = model.icon;
          const isSelected = selectedModel === model.id;
          
          return (
            <Card 
              key={model.id}
              className={`p-4 cursor-pointer transition-all hover:shadow-md ${
                isSelected ? 'ring-2 ring-purple-500 bg-purple-50' : 'hover:bg-gray-50'
              }`}
              onClick={() => onModelChange(model.id)}
            >
              <div className="flex items-start space-x-4">
                <RadioGroupItem value={model.id} id={model.id} className="mt-1" />
                <div className={`p-2 rounded-lg ${isSelected ? 'bg-purple-500' : 'bg-gray-200'}`}>
                  <Icon className={`w-5 h-5 ${isSelected ? 'text-white' : 'text-gray-600'}`} />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <h3 className="font-semibold text-gray-900">{model.name}</h3>
                      <p className="text-sm text-gray-500">{model.provider}</p>
                    </div>
                    <Badge variant="outline">{model.pricing}</Badge>
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-3">{model.description}</p>
                  
                  <div className="flex flex-wrap gap-2 mb-3">
                    {model.features.map((feature) => (
                      <Badge key={feature} variant="secondary" className="text-xs">
                        {feature}
                      </Badge>
                    ))}
                  </div>
                  
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Speed</span>
                        <span className="font-medium">{model.performance.speed}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                        <div 
                          className="bg-blue-500 h-1.5 rounded-full transition-all duration-300" 
                          style={{ width: `${model.performance.speed}%` }}
                        />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Accuracy</span>
                        <span className="font-medium">{model.performance.accuracy}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                        <div 
                          className="bg-green-500 h-1.5 rounded-full transition-all duration-300" 
                          style={{ width: `${model.performance.accuracy}%` }}
                        />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Cost Efficiency</span>
                        <span className="font-medium">{model.performance.cost}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                        <div 
                          className="bg-purple-500 h-1.5 rounded-full transition-all duration-300" 
                          style={{ width: `${model.performance.cost}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          );
        })}
      </RadioGroup>
    </div>
  );
};
