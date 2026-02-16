import { motion } from 'framer-motion';
import { Loader2, CheckCircle2, AlertCircle, Radio } from 'lucide-react';

export type Status = 'idle' | 'listening' | 'processing' | 'generating' | 'error';

interface StatusIndicatorProps {
  status: Status;
  message?: string;
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({ status, message }) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'idle':
        return {
          icon: <CheckCircle2 className="w-5 h-5" />,
          text: '空闲',
          color: 'text-gray-400',
          bgColor: 'bg-gray-500/20',
        };
      case 'listening':
        return {
          icon: <Radio className="w-5 h-5 animate-pulse" />,
          text: '监听中',
          color: 'text-green-400',
          bgColor: 'bg-green-500/20',
        };
      case 'processing':
        return {
          icon: <Loader2 className="w-5 h-5 animate-spin" />,
          text: '识别中',
          color: 'text-blue-400',
          bgColor: 'bg-blue-500/20',
        };
      case 'generating':
        return {
          icon: <Loader2 className="w-5 h-5 animate-spin" />,
          text: '生成回复中',
          color: 'text-purple-400',
          bgColor: 'bg-purple-500/20',
        };
      case 'error':
        return {
          icon: <AlertCircle className="w-5 h-5" />,
          text: '错误',
          color: 'text-red-400',
          bgColor: 'bg-red-500/20',
        };
    }
  };

  const config = getStatusConfig();

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass-effect rounded-xl p-4"
    >
      <div className="flex items-center gap-3">
        <div className={`${config.bgColor} rounded-full p-2 ${config.color}`}>
          {config.icon}
        </div>
        <div className="flex-1">
          <div className={`font-medium ${config.color}`}>
            {config.text}
          </div>
          {message && (
            <div className="text-sm text-gray-400 mt-1">
              {message}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

