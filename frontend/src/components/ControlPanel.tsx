import { motion } from 'framer-motion';
import { Play, Square, Trash2, Settings } from 'lucide-react';

interface ControlPanelProps {
  isListening: boolean;
  onToggleListening: () => void;
  onClear: () => void;
  onSettings?: () => void;
}

export const ControlPanel: React.FC<ControlPanelProps> = ({
  isListening,
  onToggleListening,
  onClear,
  onSettings,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-effect rounded-xl p-6"
    >
      <h3 className="text-lg font-semibold text-gray-200 mb-4">控制面板</h3>
      
      <div className="space-y-3">
        <button
          onClick={onToggleListening}
          className={`w-full flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
            isListening
              ? 'bg-red-600 hover:bg-red-500 text-white shadow-lg shadow-red-500/20'
              : 'btn-primary'
          }`}
        >
          {isListening ? (
            <>
              <Square className="w-5 h-5" />
              停止监听
            </>
          ) : (
            <>
              <Play className="w-5 h-5" />
              开始监听
            </>
          )}
        </button>

        <button
          onClick={onClear}
          className="w-full btn-secondary flex items-center justify-center gap-2"
        >
          <Trash2 className="w-5 h-5" />
          清空历史
        </button>

        {onSettings && (
          <button
            onClick={onSettings}
            className="w-full btn-secondary flex items-center justify-center gap-2"
          >
            <Settings className="w-5 h-5" />
            设置
          </button>
        )}
      </div>

      <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
        <p className="text-sm text-blue-300 leading-relaxed">
          💡 <strong>提示：</strong>点击"开始监听"后，系统将实时识别语音并自动回复学生提问。
        </p>
      </div>
    </motion.div>
  );
};

