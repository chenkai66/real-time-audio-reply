import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

interface AudioVisualizerProps {
  isActive: boolean;
}

export const AudioVisualizer: React.FC<AudioVisualizerProps> = ({ isActive }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    const barCount = 50;
    const barWidth = width / barCount;

    let phase = 0;

    const draw = () => {
      ctx.clearRect(0, 0, width, height);

      if (isActive) {
        // 绘制波形
        for (let i = 0; i < barCount; i++) {
          const barHeight = Math.sin(phase + i * 0.2) * 30 + 40;
          const x = i * barWidth;
          const y = (height - barHeight) / 2;

          // 渐变色
          const gradient = ctx.createLinearGradient(0, 0, 0, height);
          gradient.addColorStop(0, '#0ea5e9');
          gradient.addColorStop(1, '#a855f7');

          ctx.fillStyle = gradient;
          ctx.fillRect(x, y, barWidth - 2, barHeight);
        }

        phase += 0.1;
      } else {
        // 静止状态 - 平线
        ctx.fillStyle = '#374151';
        ctx.fillRect(0, height / 2 - 2, width, 4);
      }

      animationRef.current = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isActive]);

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-effect rounded-xl p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-200">音频波形</h3>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isActive ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`} />
          <span className="text-sm text-gray-400">
            {isActive ? '监听中' : '未激活'}
          </span>
        </div>
      </div>
      <canvas
        ref={canvasRef}
        width={800}
        height={120}
        className="w-full h-[120px] rounded-lg"
      />
    </motion.div>
  );
};

