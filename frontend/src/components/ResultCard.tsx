import { Card } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";
import { ReactNode } from "react";

interface ResultCardProps {
  icon: LucideIcon;
  title: string;
  children: ReactNode;
  iconColor?: string;
}

export const ResultCard = ({ icon: Icon, title, children, iconColor = "text-primary" }: ResultCardProps) => {
  return (
    <Card className="p-6 shadow-lg animate-fade-in">
      <div className="flex items-start gap-4 mb-4">
        <div className={`p-3 rounded-full bg-${iconColor}/10`}>
          <Icon className={`w-8 h-8 ${iconColor}`} />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold">{title}</h3>
        </div>
      </div>
      <div className="ml-16">{children}</div>
    </Card>
  );
};
