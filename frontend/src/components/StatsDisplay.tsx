import { motion } from 'framer-motion';
import { Database, MessageSquare, Zap } from 'lucide-react';

interface StatsDisplayProps {
  stats: {
    total_turns: number;
    total_tokens: number;
    l1_size: number;
    l2_size: number;
    l1_tokens: number;
    l2_tokens: number;
  };
}

export const StatsDisplay: React.FC<StatsDisplayProps> = ({ stats }) => {
  const compressionRate = stats.total_tokens > 0
    ? ((1 - (stats.l1_tokens + stats.l2_tokens) / stats.total_tokens) * 100).toFixed(1)
    : '0';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-effect rounded-xl p-6"
    >
      <h3 className="text-lg font-semibold text-gray-200 mb-4">系统统计</h3>
      
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white/5 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <MessageSquare className="w-4 h-4 text-primary-400" />
            <span className="text-xs text-gray-400">对话轮数</span>
          </div>
          <div className="text-2xl font-bold text-gray-200">
            {stats.total_turns}
          </div>
        </div>

        <div className="bg-white/5 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Database className="w-4 h-4 text-accent-400" />
            <span className="text-xs text-gray-400">Token 使用</span>
          </div>
          <div className="text-2xl font-bold text-gray-200">
            {stats.total_tokens}
          </div>
        </div>

        <div className="bg-white/5 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="w-4 h-4 text-green-400" />
            <span className="text-xs text-gray-400">压缩率</span>
          </div>
          <div className="text-2xl font-bold text-gray-200">
            {compressionRate}%
          </div>
        </div>
      </div>

      <div className="mt-4 space-y-2 text-sm">
        <div className="flex justify-between text-gray-400">
          <span>L1 缓存 (完整):</span>
          <span className="text-gray-300">{stats.l1_size} 轮 / {stats.l1_tokens} tokens</span>
        </div>
        <div className="flex justify-between text-gray-400">
          <span>L2 缓存 (摘要):</span>
          <span className="text-gray-300">{stats.l2_size} 轮 / {stats.l2_tokens} tokens</span>
        </div>
      </div>
    </motion.div>
  );
};

