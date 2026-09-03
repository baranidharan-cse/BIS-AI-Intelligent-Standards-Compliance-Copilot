/**
 * BaseSpeechService — interface contract for all speech providers.
 *
 * Implementations:
 *   BrowserSpeechService  — Web Speech API (SpeechRecognition + SpeechSynthesis)
 *   WatsonSpeechService   — IBM Watson STT + TTS (future)
 *
 * The interface is intentionally minimal:
 *   - startListening(onResult, onEnd) — mic input
 *   - stopListening()
 *   - speak(text, onEnd?)            — read aloud
 *   - stopSpeaking()
 *   - isSupported: boolean           — feature detection
 */

export interface SpeechResult {
  transcript: string;
  isFinal: boolean;
}

export abstract class BaseSpeechService {
  abstract readonly isSupported: boolean;

  /** Start continuous speech recognition. onResult called for each recognised phrase. */
  abstract startListening(
    onResult: (result: SpeechResult) => void,
    onEnd: () => void,
    onError?: (error: string) => void
  ): void;

  abstract stopListening(): void;

  /** Synthesise text to speech. */
  abstract speak(text: string, onEnd?: () => void): void;

  abstract stopSpeaking(): void;
}
