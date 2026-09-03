import { useState, useEffect } from 'react'
import styles from './SettingsPage.module.css'

export default function SettingsPage() {
  const [provider, setProvider] = useState(() => localStorage.getItem('llm_provider') ?? 'demo')
  const [apiKey, setApiKey] = useState(() => localStorage.getItem('watsonx_api_key') ?? '')
  const [projectId, setProjectId] = useState(() => localStorage.getItem('watsonx_project_id') ?? '')
  const [watsonUrl, setWatsonUrl] = useState(() => localStorage.getItem('watsonx_url') ?? 'https://us-south.ml.cloud.ibm.com')
  const [modelId, setModelId] = useState(() => localStorage.getItem('watsonx_model_id') ?? 'ibm/granite-13b-instruct-v2')

  const [autoSpeak, setAutoSpeak] = useState(() => localStorage.getItem('auto_speak') === 'true')
  const [theme, setTheme] = useState(() => localStorage.getItem('theme_mode') ?? 'dark')
  const [toast, setToast] = useState<string | null>(null)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  const showToast = (msg: string) => {
    setToast(msg)
    setTimeout(() => setToast(null), 3000)
  }

  const handleSave = () => {
    localStorage.setItem('llm_provider', provider)
    localStorage.setItem('watsonx_api_key', apiKey)
    localStorage.setItem('watsonx_project_id', projectId)
    localStorage.setItem('watsonx_url', watsonUrl)
    localStorage.setItem('watsonx_model_id', modelId)
    localStorage.setItem('auto_speak', String(autoSpeak))
    localStorage.setItem('theme_mode', theme)
    showToast('✓ Settings saved successfully!')
  }

  const handleReset = () => {
    if (window.confirm('Are you sure you want to reset settings to default?')) {
      localStorage.clear()
      setProvider('demo')
      setApiKey('')
      setProjectId('')
      setWatsonUrl('https://us-south.ml.cloud.ibm.com')
      setModelId('ibm/granite-13b-instruct-v2')
      setAutoSpeak(false)
      setTheme('dark')
      showToast('Settings reset to default.')
    }
  }

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Settings</h1>
      <p className={styles.subtitle}>Configure application options, LLM provider settings, and preferences.</p>

      {toast && <div className={styles.toast}>{toast}</div>}

      <div className={styles.sectionGrid}>
        {/* LLM Settings */}
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>🤖 LLM Provider Settings</h2>

          <div className={styles.field}>
            <label className={styles.label}>Active Provider</label>
            <select
              className={styles.select}
              value={provider}
              onChange={e => setProvider(e.target.value)}
            >
              <option value="demo">Demo Provider (Offline & Deterministic)</option>
              <option value="watsonx">IBM watsonx.ai</option>
            </select>
          </div>

          {provider === 'watsonx' && (
            <div className={styles.subFields}>
              <div className={styles.field}>
                <label className={styles.label}>IBM Cloud API Key</label>
                <input
                  type="password"
                  className={styles.input}
                  placeholder="Enter API Key"
                  value={apiKey}
                  onChange={e => setApiKey(e.target.value)}
                />
              </div>

              <div className={styles.field}>
                <label className={styles.label}>Project ID</label>
                <input
                  type="text"
                  className={styles.input}
                  placeholder="Enter Watsonx Project ID"
                  value={projectId}
                  onChange={e => setProjectId(e.target.value)}
                />
              </div>

              <div className={styles.field}>
                <label className={styles.label}>Watsonx Endpoint URL</label>
                <input
                  type="text"
                  className={styles.input}
                  value={watsonUrl}
                  onChange={e => setWatsonUrl(e.target.value)}
                />
              </div>

              <div className={styles.field}>
                <label className={styles.label}>Model ID</label>
                <input
                  type="text"
                  className={styles.input}
                  value={modelId}
                  onChange={e => setModelId(e.target.value)}
                />
              </div>
            </div>
          )}
        </div>

        {/* Audio & Voice */}
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>🔊 Speech & Audio Preferences</h2>
          <div className={styles.toggleRow}>
            <div>
              <strong className={styles.toggleLabel}>Auto Read-Aloud</strong>
              <p className={styles.toggleDesc}>Automatically read chatbot responses out loud using Text-to-Speech.</p>
            </div>
            <input
              type="checkbox"
              className={styles.checkbox}
              checked={autoSpeak}
              onChange={e => setAutoSpeak(e.target.checked)}
            />
          </div>
        </div>

        {/* Theme & Display */}
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>🎨 Appearance</h2>
          <div className={styles.field}>
            <label className={styles.label}>Theme Mode</label>
            <select
              className={styles.select}
              value={theme}
              onChange={e => setTheme(e.target.value)}
            >
              <option value="dark">Dark Theme (IBM Carbon Dark)</option>
              <option value="light">Light Theme (IBM Carbon Light)</option>
            </select>
          </div>
        </div>
      </div>

      <div className={styles.actions}>
        <button className={styles.saveBtn} onClick={handleSave}>
          💾 Save Settings
        </button>
        <button className={styles.resetBtn} onClick={handleReset}>
          🔄 Reset to Default
        </button>
      </div>
    </div>
  )
}
