import { useState, useEffect } from 'react'
import { api } from '../api/client'
import type { Material, MaterialDetail, Section, Concept } from '../api/types'
import styles from './StudyPage.module.css'

export default function StudyPage() {
  const [materials, setMaterials] = useState<Material[]>([])
  const [selectedId, setSelectedId] = useState<number | ''>('')
  const [detail, setDetail] = useState<MaterialDetail | null>(null)
  const [loadingList, setLoadingList] = useState(true)
  const [loadingDetail, setLoadingDetail] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [modalConcept, setModalConcept] = useState<Concept | null>(null)

  useEffect(() => {
    api
      .listMaterials()
      .then(ms => setMaterials(ms.filter(m => m.status === 'ready')))
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoadingList(false))
  }, [])

  useEffect(() => {
    if (!selectedId) { setDetail(null); return }
    setLoadingDetail(true)
    setError(null)
    api
      .getMaterial(selectedId as number)
      .then(setDetail)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoadingDetail(false))
  }, [selectedId])

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Study</h1>

      {loadingList && <div className={styles.spinner} />}
      {error && <div className={styles.error}>⚠ {error}</div>}

      {!loadingList && (
        <select
          className={styles.select}
          value={selectedId}
          onChange={e => setSelectedId(e.target.value ? Number(e.target.value) : '')}
        >
          <option value="">— Select a material to study —</option>
          {materials.map(m => (
            <option key={m.id} value={m.id}>{m.title}</option>
          ))}
        </select>
      )}

      {loadingDetail && <div className={styles.spinner} />}

      {detail && (
        <div className={styles.content}>
          {detail.summary && <p className={styles.summary}>{detail.summary}</p>}
          {detail.sections.length === 0 && (
            <p className={styles.empty}>No sections found in this material.</p>
          )}
          {detail.sections
            .slice()
            .sort((a, b) => a.order_index - b.order_index)
            .map(section => (
              <SectionAccordion
                key={section.id}
                section={section}
                onExplain={setModalConcept}
              />
            ))}
        </div>
      )}

      {!selectedId && !loadingList && materials.length === 0 && (
        <p className={styles.empty}>No ready materials found. Upload and process a material first.</p>
      )}

      {modalConcept && (
        <ConceptModal concept={modalConcept} onClose={() => setModalConcept(null)} />
      )}
    </div>
  )
}

function SectionAccordion({
  section,
  onExplain,
}: {
  section: Section
  onExplain: (c: Concept) => void
}) {
  const [open, setOpen] = useState(false)

  return (
    <div className={styles.section}>
      <button className={styles.sectionHeader} onClick={() => setOpen(o => !o)}>
        <span className={styles.sectionTitle}>{section.title}</span>
        <span className={styles.chevron}>{open ? '▲' : '▼'}</span>
      </button>

      {open && (
        <div className={styles.sectionBody}>
          {section.summary && <p className={styles.sectionSummary}>{section.summary}</p>}
          {section.concepts.length === 0 && (
            <p className={styles.noConcepts}>No concepts extracted for this section.</p>
          )}
          {section.concepts
            .slice()
            .sort((a, b) => a.order_index - b.order_index)
            .map(c => (
              <ConceptCard key={c.id} concept={c} onExplain={onExplain} />
            ))}
        </div>
      )}
    </div>
  )
}

function ConceptCard({
  concept,
  onExplain,
}: {
  concept: Concept
  onExplain: (c: Concept) => void
}) {
  return (
    <div className={styles.concept}>
      <div className={styles.conceptTop}>
        <h3 className={styles.conceptName}>{concept.name}</h3>
        <button className={styles.explainBtn} onClick={() => onExplain(concept)}>
          💡 Explain
        </button>
      </div>
      {concept.definition && (
        <p className={styles.conceptDef}>{concept.definition}</p>
      )}
      {concept.explanation && (
        <p className={styles.conceptExpl}>{concept.explanation}</p>
      )}
      {concept.examples.length > 0 && (
        <div className={styles.examples}>
          <span className={styles.examplesLabel}>Examples</span>
          {concept.examples.map((ex, i) => (
            <pre key={i} className={styles.exampleBlock}>{ex}</pre>
          ))}
        </div>
      )}
    </div>
  )
}

function ConceptModal({ concept, onClose }: { concept: Concept; onClose: () => void }) {
  const [level, setLevel] = useState<'eli10' | 'high_school' | 'exam_summary'>('high_school')
  const [aiExplain, setAiExplain] = useState<{
    explanation: string
    key_points: string[]
    analogies: string[]
  } | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setLoading(true)
    api
      .explainConcept(concept.name, concept.definition ?? '', level)
      .then(res => {
        setAiExplain({
          explanation: res.explanation,
          key_points: res.key_points,
          analogies: res.analogies,
        })
      })
      .catch(() => setAiExplain(null))
      .finally(() => setLoading(false))
  }, [concept, level])

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2 className={styles.modalTitle}>{concept.name}</h2>
          <button className={styles.closeBtn} onClick={onClose}>✕</button>
        </div>

        <div className={styles.levelButtons}>
          <button
            className={`${styles.levelBtn} ${level === 'eli10' ? styles.levelActive : ''}`}
            onClick={() => setLevel('eli10')}
          >
            🧒 ELI10 (Simple)
          </button>
          <button
            className={`${styles.levelBtn} ${level === 'high_school' ? styles.levelActive : ''}`}
            onClick={() => setLevel('high_school')}
          >
            🏫 High School
          </button>
          <button
            className={`${styles.levelBtn} ${level === 'exam_summary' ? styles.levelActive : ''}`}
            onClick={() => setLevel('exam_summary')}
          >
            📝 Exam Summary
          </button>
        </div>

        <div className={styles.modalBody}>
          {loading && <div className={styles.spinner} />}

          {!loading && aiExplain && (
            <div className={styles.modalSection}>
              <strong>AI Tutor Explanation ({level.replace('_', ' ').toUpperCase()})</strong>
              <p>{aiExplain.explanation}</p>

              {aiExplain.analogies.length > 0 && (
                <div className={styles.analogyBlock}>
                  💡 <em>Analogy:</em> {aiExplain.analogies[0]}
                </div>
              )}

              {aiExplain.key_points.length > 0 && (
                <div className={styles.keyPoints}>
                  <strong>Key Takeaways:</strong>
                  <ul>
                    {aiExplain.key_points.map((kp, i) => (
                      <li key={i}>{kp}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {concept.definition && (
            <div className={styles.modalSection}>
              <strong>Standard Definition</strong>
              <p>{concept.definition}</p>
            </div>
          )}
          {concept.examples.length > 0 && (
            <div className={styles.modalSection}>
              <strong>Examples</strong>
              {concept.examples.map((ex, i) => (
                <pre key={i} className={styles.exampleBlock}>{ex}</pre>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
