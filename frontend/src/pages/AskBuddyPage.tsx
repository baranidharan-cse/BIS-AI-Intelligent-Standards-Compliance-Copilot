import { useState, useEffect, useRef } from 'react'
import { api } from '../api/client'
import type { Material, ChatMessage } from '../api/types'
import { getSpeechService } from '../services/speech'
import type { BaseSpeechService } from '../services/speech'
import styles from './AskBuddyPage.module.css'

export default function AskBuddyPage() {
  const [sessionId] = useState(() => crypto.randomUUID())
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [materials, setMaterials] = useState<Material[]>([])
  const [selectedMaterialId, setSelectedMaterialId] = useState<number | ''>('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [listening, setListening] = useState(false)
  const [speaking, setSpeaking] = useState(false)
  const [autoSpeak, setAutoSpeak] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const speechRef = useRef<BaseSpeechService | null>(null)

  useEffect(() => {
    speechRef.current = getSpeechService()
  }, [])

  useEffect(() => {
    api
      .listMaterials()
      .then(ms => setMaterials(ms.filter(m => m.status === 'ready')))
      .catch(() => { /* materials are optional context */ })
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const sendMessage = async (text: string) => {
    const trimmed = text.trim()
    if (!trimmed || loading) return

    const userMsg: ChatMessage = { role: 'user', content: trimmed }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)
    setError(null)

    try {
      const reply = await api.sendMessage(
        sessionId,
        trimmed,
        selectedMaterialId ? (selectedMaterialId as number) : undefined
      )
      setMessages(prev => [...prev, reply])
      if (autoSpeak) {
        setSpeaking(true)
        speechRef.current?.speak(reply.content, () => setSpeaking(false))
      }
    } catch (e) {
      setError((e as Error).message)
      // Remove the optimistic user message on error
      setMessages(prev => prev.slice(0, -1))
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(input)
    }
  }

  const handleMicClick = () => {
    if (listening) {
      speechRef.current?.stopListening()
      setListening(false)
    } else {
      speechRef.current?.startListening(
        result => {
          if (result.isFinal) {
            sendMessage(result.transcript)
          }
        },
        () => setListening(false),
        err => {
          setListening(false)
          setError(`Speech recognition error: ${err}`)
        }
      )
      setListening(true)
    }
  }

  const handleStopSpeaking = () => {
    speechRef.current?.stopSpeaking()
    setSpeaking(false)
  }

  const lastAssistantMsg = [...messages].reverse().find(m => m.role === 'assistant')
  const speechSupported = speechRef.current?.isSupported ?? false

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>Ask Buddy</h1>
        <div className={styles.headerControls}>
          <select
            className={styles.contextSelect}
            value={selectedMaterialId}
            onChange={e => setSelectedMaterialId(e.target.value ? Number(e.target.value) : '')}
          >
            <option value="">No material context</option>
            {materials.map(m => (
              <option key={m.id} value={m.id}>{m.title}</option>
            ))}
          </select>
          {speechSupported && (
            <button
              className={`${styles.autoSpeakBtn}${autoSpeak ? ` ${styles.autoSpeakActive}` : ''}`}
              onClick={() => setAutoSpeak(v => !v)}
              title={autoSpeak ? 'Auto read-aloud on — click to disable' : 'Auto read-aloud off — click to enable'}
            >
              🔊
            </button>
          )}
        </div>
      </div>

      {error && <div className={styles.error}>⚠ {error}</div>}

      {speaking && (
        <div className={styles.speakingBar}>
          <span>🔊 Reading aloud…</span>
          <button className={styles.stopSpeakBtn} onClick={handleStopSpeaking}>Stop</button>
        </div>
      )}

      <div className={styles.chatWindow}>
        {messages.length === 0 && !loading && (
          <div className={styles.welcome}>
            <div className={styles.welcomeIcon}>💬</div>
            <p>Ask me anything about your study materials.</p>
            <p className={styles.hint}>Select a material for context, then type your question below.</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`${styles.bubble} ${msg.role === 'user' ? styles.bubbleUser : styles.bubbleAssistant}`}
          >
            <div className={styles.bubbleContent}>{msg.content}</div>
            {msg.role === 'assistant' &&
              msg.follow_up_suggestions &&
              msg === lastAssistantMsg &&
              msg.follow_up_suggestions.length > 0 && (
                <div className={styles.suggestions}>
                  {msg.follow_up_suggestions.map((s, j) => (
                    <button
                      key={j}
                      className={styles.suggestionChip}
                      onClick={() => sendMessage(s)}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              )}
          </div>
        ))}

        {loading && (
          <div className={`${styles.bubble} ${styles.bubbleAssistant}`}>
            <div className={styles.typing}>
              <span /><span /><span />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className={styles.inputRow}>
        <textarea
          ref={inputRef}
          className={styles.input}
          rows={1}
          placeholder="Ask a question… (Enter to send, Shift+Enter for newline)"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        {speechSupported && (
          <button
            className={`${styles.micBtn}${listening ? ` ${styles.micActive}` : ''}`}
            onClick={handleMicClick}
            title={listening ? 'Stop listening' : 'Start voice input'}
            disabled={loading}
          >
            🎤
          </button>
        )}
        <button
          className={styles.sendBtn}
          onClick={() => sendMessage(input)}
          disabled={loading || !input.trim()}
        >
          ➤
        </button>
      </div>
    </div>
  )
}
