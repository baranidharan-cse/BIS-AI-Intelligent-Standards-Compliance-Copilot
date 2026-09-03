/**
 * BrowserSpeechService — uses the Web Speech API.
 *
 * SpeechRecognition: continuous, interimResults=true, lang='en-US'
 * SpeechSynthesis: uses window.speechSynthesis, prefers a natural-sounding voice
 *
 * Feature-detects at construction time; isSupported is false if either API
 * is missing (e.g. Firefox without speech, or SSR environments).
 */

import { BaseSpeechService, SpeechResult } from './base';

export class BrowserSpeechService extends BaseSpeechService {
  readonly isSupported: boolean;
  private recognition: any = null;

  constructor() {
    super();
    this.isSupported =
      typeof window !== 'undefined' &&
      ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) &&
      'speechSynthesis' in window;
  }

  startListening(
    onResult: (result: SpeechResult) => void,
    onEnd: () => void,
    onError?: (error: string) => void
  ): void {
    if (!this.isSupported) return;

    const SR =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;

    this.recognition = new SR();
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    this.recognition.lang = 'en-US';

    this.recognition.onresult = (event: any) => {
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        onResult({
          transcript: result[0].transcript,
          isFinal: result.isFinal,
        });
      }
    };

    this.recognition.onend = () => {
      onEnd();
    };

    this.recognition.onerror = (event: any) => {
      onError?.(event.error);
    };

    this.recognition.start();
  }

  stopListening(): void {
    this.recognition?.stop();
    this.recognition = null;
  }

  speak(text: string, onEnd?: () => void): void {
    if (!this.isSupported) return;
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    const voices = window.speechSynthesis.getVoices();
    const preferred = voices.find(
      v => v.name.includes('Google') || v.name.includes('Natural')
    );
    if (preferred) utterance.voice = preferred;

    utterance.onend = () => onEnd?.();
    window.speechSynthesis.speak(utterance);
  }

  stopSpeaking(): void {
    window.speechSynthesis.cancel();
  }
}
