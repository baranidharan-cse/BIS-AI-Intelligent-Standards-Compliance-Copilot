export { BaseSpeechService } from './base';
export { BrowserSpeechService } from './browser';
export type { SpeechResult } from './base';

import type { BaseSpeechService } from './base';
import { BrowserSpeechService } from './browser';

/** Factory — returns BrowserSpeechService for now; swap for WatsonSpeechService when credentials exist */
export function getSpeechService(): BaseSpeechService {
  return new BrowserSpeechService();
}
