import { motion, AnimatePresence } from 'framer-motion';
import { User, Bot, Sparkles } from 'lucide-react';

export interface Message {
  id: string;
  role: 'teacher' | 'student' | 'system';
  text: string;
  timestamp: string;
}

interface ConversationPanelProps {
  messages: Message[];
}

export const ConversationPanel: React.FC<ConversationPanelProps> = ({ messages }) => {
  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'teacher':
        return <User className="w-5 h-5" />;
      case 'student':
        return <Bot className="w-5 h-5" />;
      case 'system':
        return <Sparkles className="w-5 h-5" />;
      default:
        return null;
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'teacher':
        return 'from-primary-600 to-primary-500';
      case 'student':
        return 'from-accent-600 to-accent-500';
      case 'system':
        return 'from-gray-600 to-gray-500';
      default:
        return 'from-gray-600 to-gray-500';
    }
  };

  const getRoleName = (role: string) => {
    switch (role) {
      case 'teacher':
        return '教师';
      case 'student':
        return '学生';
      case 'system':
        return '系统';
      default:
        return '未知';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-effect rounded-xl p-6 h-[500px] flex flex-col"
    >
      <h3 className="text-lg font-semibold text-gray-200 mb-4">对话历史</h3>
      
      <div className="flex-1 overflow-y-auto space-y-4 pr-2 scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-transparent">
        <AnimatePresence>
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full text-gray-500">
              <p>暂无对话记录</p>
            </div>
          ) : (
            messages.map((message, index) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: index * 0.05 }}
                className="flex gap-3"
              >
                <div className={`flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br ${getRoleColor(message.role)} flex items-center justify-center text-white`}>
                  {getRoleIcon(message.role)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium text-gray-300">
                      {getRoleName(message.role)}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(message.timestamp).toLocaleTimeString('zh-CN')}
                    </span>
                  </div>
                  <div className="bg-white/5 rounded-lg p-3 text-gray-200 text-sm leading-relaxed">
                    {message.text}
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

