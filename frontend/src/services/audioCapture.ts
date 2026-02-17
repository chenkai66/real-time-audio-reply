/**
 * 音频采集服务
 * 支持麦克风和系统音频（屏幕共享音频）
 */

export type AudioSource = 'microphone' | 'system' | 'both';

export interface AudioCaptureConfig {
  sampleRate: number;
  channelCount: number;
  echoCancellation: boolean;
  noiseSuppression: boolean;
  autoGainControl: boolean;
}

export class AudioCaptureService {
  private audioContext: AudioContext | null = null;
  private micStream: MediaStream | null = null;
  private systemStream: MediaStream | null = null;
  private processor: ScriptProcessorNode | null = null;
  private isCapturing = false;

  private config: AudioCaptureConfig = {
    sampleRate: 16000,
    channelCount: 1,
    echoCancellation: true,
    noiseSuppression: true,
    autoGainControl: true,
  };

  /**
   * 开始音频采集
   * @param source 音频源类型
   * @param onAudioData 音频数据回调
   */
  async startCapture(
    source: AudioSource,
    onAudioData: (data: Int16Array) => void
  ): Promise<void> {
    if (this.isCapturing) {
      console.warn('音频采集已在进行中');
      return;
    }

    try {
      // 创建音频上下文
      this.audioContext = new AudioContext({ sampleRate: this.config.sampleRate });

      // 根据音频源类型采集
      if (source === 'microphone' || source === 'both') {
        await this.captureMicrophone();
      }

      if (source === 'system' || source === 'both') {
        await this.captureSystemAudio();
      }

      // 创建音频处理器
      this.setupAudioProcessor(onAudioData);

      this.isCapturing = true;
      console.log(`✅ 音频采集已启动 (${source})`);
    } catch (error) {
      console.error('音频采集失败:', error);
      this.stopCapture();
      throw error;
    }
  }

  /**
   * 采集麦克风音频
   */
  private async captureMicrophone(): Promise<void> {
    try {
      this.micStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: this.config.sampleRate,
          channelCount: this.config.channelCount,
          echoCancellation: this.config.echoCancellation,
          noiseSuppression: this.config.noiseSuppression,
          autoGainControl: this.config.autoGainControl,
        },
      });
      console.log('✅ 麦克风采集成功');
    } catch (error) {
      console.error('麦克风采集失败:', error);
      throw new Error('无法访问麦克风，请检查权限设置');
    }
  }

  /**
   * 采集系统音频（通过屏幕共享）
   */
  private async captureSystemAudio(): Promise<void> {
    try {
      // @ts-ignore - getDisplayMedia 支持音频
      this.systemStream = await navigator.mediaDevices.getDisplayMedia({
        video: false,
        audio: {
          sampleRate: this.config.sampleRate,
          channelCount: this.config.channelCount,
          echoCancellation: false, // 系统音频不需要回声消除
          noiseSuppression: false,
          autoGainControl: false,
        },
      });
      console.log('✅ 系统音频采集成功');
    } catch (error) {
      console.error('系统音频采集失败:', error);
      // 系统音频采集失败不抛出错误，允许只使用麦克风
      console.warn('将只使用麦克风音频');
    }
  }

  /**
   * 设置音频处理器
   */
  private setupAudioProcessor(onAudioData: (data: Int16Array) => void): void {
    if (!this.audioContext) return;

    // 创建音频源
    const sources: MediaStreamAudioSourceNode[] = [];

    if (this.micStream) {
      sources.push(this.audioContext.createMediaStreamSource(this.micStream));
    }

    if (this.systemStream) {
      sources.push(this.audioContext.createMediaStreamSource(this.systemStream));
    }

    if (sources.length === 0) {
      throw new Error('没有可用的音频源');
    }

    // 创建混音器（如果有多个音频源）
    const destination = this.audioContext.createMediaStreamDestination();
    sources.forEach(source => source.connect(destination));

    // 创建处理器节点
    this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);

    // 连接音频流
    const finalSource = this.audioContext.createMediaStreamSource(destination.stream);
    finalSource.connect(this.processor);
    this.processor.connect(this.audioContext.destination);

    // 处理音频数据
    this.processor.onaudioprocess = (e) => {
      const audioData = e.inputBuffer.getChannelData(0);
      const pcmData = this.floatTo16BitPCM(audioData);
      onAudioData(pcmData);
    };
  }

  /**
   * 将 Float32Array 转换为 Int16Array (PCM 格式)
   */
  private floatTo16BitPCM(float32Array: Float32Array): Int16Array {
    const int16Array = new Int16Array(float32Array.length);

    for (let i = 0; i < float32Array.length; i++) {
      // 限制在 [-1, 1] 范围内
      const s = Math.max(-1, Math.min(1, float32Array[i]));
      // 转换为 16 位整数
      int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
    }

    return int16Array;
  }

  /**
   * 停止音频采集
   */
  stopCapture(): void {
    // 断开处理器
    if (this.processor) {
      this.processor.disconnect();
      this.processor = null;
    }

    // 停止麦克风流
    if (this.micStream) {
      this.micStream.getTracks().forEach(track => track.stop());
      this.micStream = null;
    }

    // 停止系统音频流
    if (this.systemStream) {
      this.systemStream.getTracks().forEach(track => track.stop());
      this.systemStream = null;
    }

    // 关闭音频上下文
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }

    this.isCapturing = false;
    console.log('✅ 音频采集已停止');
  }

  /**
   * 获取可用的音频设备列表
   */
  async getAudioDevices(): Promise<MediaDeviceInfo[]> {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      return devices.filter(device => device.kind === 'audioinput');
    } catch (error) {
      console.error('获取音频设备失败:', error);
      return [];
    }
  }

  /**
   * 检查浏览器是否支持音频采集
   */
  static isSupported(): boolean {
    return !!(
      navigator.mediaDevices &&
      navigator.mediaDevices.getUserMedia &&
      window.AudioContext
    );
  }

  /**
   * 获取当前状态
   */
  getStatus() {
    return {
      isCapturing: this.isCapturing,
      hasMicrophone: !!this.micStream,
      hasSystemAudio: !!this.systemStream,
      sampleRate: this.audioContext?.sampleRate || 0,
    };
  }
}

// 导出单例
export const audioCaptureService = new AudioCaptureService();

