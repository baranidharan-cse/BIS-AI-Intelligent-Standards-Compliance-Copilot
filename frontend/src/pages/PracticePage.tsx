import { useState, useEffect } from 'react'
import { api } from '../api/client'
import type { Material, QuizDetail, QuizQuestion, AttemptResult } from '../api/types'
import styles from './PracticePage.module.css'

type Phase = 'setup' | 'quiz' | 'results'

export default function PracticePage() {
  const [materials, setMaterials] = useState<Material[]>([])
  const [selectedId, setSelectedId] = useState<number | ''>('')
  const [numQ, setNumQ] = useState(5)
  const [difficulty, setDifficulty] = useState('mixed')
  const [phase, setPhase] = useState<Phase>('setup')
  const [quiz, setQuiz] = useState<QuizDetail | null>(null)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [result, setResult] = useState<AttemptResult | null>(null)
  const [loadingList, setLoadingList] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .listMaterials()
      .then(ms => setMaterials(ms.filter(m => m.status === 'ready')))
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoadingList(false))
  }, [])

  const generateQuiz = async () => {
    if (!selectedId) return
    setGenerating(true)
    setError(null)
    try {
      const q = await api.generateQuiz(selectedId as number, numQ, difficulty)
      setQuiz(q)
      setAnswers({})
      setResult(null)
      setPhase('quiz')
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setGenerating(false)
    }
  }

  const submitQuiz = async () => {
    if (!quiz) return
    setSubmitting(true)
    setError(null)
    try {
      const r = await api.submitAttempt(quiz.id, answers)
      setResult(r)
      setPhase('results')
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setSubmitting(false)
    }
  }

  const reset = () => {
    setPhase('setup')
    setQuiz(null)
    setAnswers({})
    setResult(null)
  }

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Practice</h1>
      {error && <div className={styles.error}>⚠ {error}</div>}

      {/* Setup phase */}
      {phase === 'setup' && (
        <div className={styles.setupCard}>
          {loadingList && <div className={styles.spinner} />}
          {!loadingList && (
            <>
              <div className={styles.field}>
                <label className={styles.label}>Material</label>
                <select
                  className={styles.select}
                  value={selectedId}
                  onChange={e => setSelectedId(e.target.value ? Number(e.target.value) : '')}
                >
                  <option value="">— Select a material —</option>
                  {materials.map(m => (
                    <option key={m.id} value={m.id}>{m.title}</option>
                  ))}
                </select>
              </div>

              <div className={styles.field}>
                <label className={styles.label}>
                  Number of questions: <strong>{numQ}</strong>
                </label>
                <input
                  type="range"
                  min={3}
                  max={10}
                  value={numQ}
                  onChange={e => setNumQ(Number(e.target.value))}
                  className={styles.range}
                />
              </div>

              <div className={styles.field}>
                <label className={styles.label}>Difficulty</label>
                <select
                  className={styles.select}
                  value={difficulty}
                  onChange={e => setDifficulty(e.target.value)}
                >
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                  <option value="mixed">Mixed</option>
                </select>
              </div>

              <button
                className={styles.primaryBtn}
                onClick={generateQuiz}
                disabled={!selectedId || generating}
              >
                {generating ? 'Generating quiz…' : '✏️ Generate Quiz'}
              </button>
            </>
          )}
        </div>
      )}

      {/* Quiz phase */}
      {phase === 'quiz' && quiz && (
        <div className={styles.quizArea}>
          <div className={styles.quizHeader}>
            <h2 className={styles.quizTitle}>{quiz.title}</h2>
            <span className={styles.quizMeta}>
              {quiz.questions.length} questions · {quiz.difficulty}
            </span>
          </div>

          {quiz.questions
            .slice()
            .sort((a, b) => a.order_index - b.order_index)
            .map((q, i) => (
              <QuestionCard
                key={q.id}
                question={q}
                index={i}
                answer={answers[String(q.id)] ?? ''}
                onChange={val =>
                  setAnswers(prev => ({ ...prev, [String(q.id)]: val }))
                }
              />
            ))}

          <div className={styles.quizFooter}>
            <button
              className={styles.primaryBtn}
              onClick={submitQuiz}
              disabled={submitting}
            >
              {submitting ? 'Submitting…' : '📤 Submit Quiz'}
            </button>
            <button className={styles.secondaryBtn} onClick={reset}>
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Results phase */}
      {phase === 'results' && result && quiz && (
        <div className={styles.results}>
          <div className={styles.scoreBox}>
            <span className={styles.scoreBig}>
              {result.correct_count}/{result.total_questions}
            </span>
            <span className={styles.scorePct}>{Math.round(result.score * 100)}%</span>
            <span className={styles.scoreLabel}>
              {result.score >= 0.8 ? '🎉 Great job!' : result.score >= 0.5 ? '📚 Keep studying!' : "💪 Don't give up!"}
            </span>
          </div>

          <div className={styles.perQuestion}>
            {quiz.questions
              .slice()
              .sort((a, b) => a.order_index - b.order_index)
              .map((q, i) => {
                const pq = result.per_question.find(p => p.question_id === q.id)
                return (
                  <ResultItem
                    key={q.id}
                    question={q}
                    index={i}
                    userAnswer={answers[String(q.id)] ?? ''}
                    pq={pq}
                  />
                )
              })}
          </div>

          <div className={styles.quizFooter}>
            <button className={styles.primaryBtn} onClick={generateQuiz} disabled={generating}>
              {generating ? 'Generating…' : '🔄 Generate New Quiz'}
            </button>
            <button className={styles.secondaryBtn} onClick={() => setPhase('quiz')}>
              ↩ Try Again
            </button>
            <button className={styles.secondaryBtn} onClick={reset}>
              Change Material
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

function QuestionCard({
  question,
  index,
  answer,
  onChange,
}: {
  question: QuizQuestion
  index: number
  answer: string
  onChange: (v: string) => void
}) {
  return (
    <div className={styles.questionCard}>
      <div className={styles.questionTop}>
        <span className={styles.qNum}>Q{index + 1}</span>
        <span className={styles.qDiff}>{question.difficulty}</span>
      </div>
      <p className={styles.questionText}>{question.question_text}</p>

      {question.question_type === 'multiple_choice' && question.options && (
        <div className={styles.options}>
          {question.options.map(opt => (
            <label key={opt} className={`${styles.option} ${answer === opt ? styles.optionSelected : ''}`}>
              <input
                type="radio"
                name={`q-${question.id}`}
                value={opt}
                checked={answer === opt}
                onChange={() => onChange(opt)}
              />
              <span>{opt}</span>
            </label>
          ))}
        </div>
      )}

      {question.question_type === 'true_false' && (
        <div className={styles.tfRow}>
          {['True', 'False'].map(v => (
            <button
              key={v}
              className={`${styles.tfBtn} ${answer === v ? styles.tfSelected : ''}`}
              onClick={() => onChange(v)}
            >
              {v}
            </button>
          ))}
        </div>
      )}

      {question.question_type === 'short_answer' && (
        <input
          className={styles.shortInput}
          placeholder="Your answer…"
          value={answer}
          onChange={e => onChange(e.target.value)}
        />
      )}
    </div>
  )
}

function ResultItem({
  question,
  index,
  userAnswer,
  pq,
}: {
  question: QuizQuestion
  index: number
  userAnswer: string
  pq?: AttemptResult['per_question'][number]
}) {
  const correct = pq?.correct ?? false
  return (
    <div className={`${styles.resultItem} ${correct ? styles.resultCorrect : styles.resultWrong}`}>
      <div className={styles.resultTop}>
        <span className={styles.resultIcon}>{correct ? '✓' : '✗'}</span>
        <span className={styles.qNum}>Q{index + 1}</span>
        <p className={styles.resultQuestion}>{question.question_text}</p>
      </div>
      <div className={styles.resultDetail}>
        <span>Your answer: <strong>{userAnswer || '(no answer)'}</strong></span>
        {!correct && pq && (
          <span>Correct answer: <strong className={styles.correctAns}>{pq.correct_answer}</strong></span>
        )}
        {pq?.explanation && <span className={styles.explanation}>{pq.explanation}</span>}
      </div>
    </div>
  )
}
