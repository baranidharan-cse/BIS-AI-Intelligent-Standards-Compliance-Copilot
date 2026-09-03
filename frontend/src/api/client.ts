import type {
  Material,
  MaterialDetail,
  LearningPath,
  LearningPathDetail,
  LearningStep,
  QuizDetail,
  AttemptResult,
  RevisionPlan,
  RevisionTask,
  ChatMessage,
  DashboardStats,
  ProfileStats,
} from './types';

const BASE_URL = import.meta.env.VITE_API_URL ?? '';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? 'Request failed');
  }
  return res.json();
}

export const api = {
  // materials
  listMaterials: () => request<Material[]>('/api/materials'),
  createMaterial: (body: { title: string; raw_text: string; description?: string }) =>
    request<Material>('/api/materials', { method: 'POST', body: JSON.stringify(body) }),
  uploadMaterial: (formData: FormData) =>
    fetch(`${BASE_URL}/api/materials/upload`, { method: 'POST', body: formData }).then(r =>
      r.ok ? r.json() : r.json().then((e: { detail?: string }) => Promise.reject(new Error(e.detail ?? 'Upload failed')))
    ),
  getMaterial: (id: number) => request<MaterialDetail>(`/api/materials/${id}`),
  deleteMaterial: (id: number) =>
    request<{ deleted: boolean }>(`/api/materials/${id}`, { method: 'DELETE' }),
  explainConcept: (topic_name: string, context?: string, difficulty_level?: string) =>
    request<{
      topic: string;
      explanation: string;
      examples: string[];
      key_points: string[];
      analogies: string[];
    }>('/api/materials/explain', {
      method: 'POST',
      body: JSON.stringify({
        topic_name,
        context: context ?? '',
        difficulty_level: difficulty_level ?? 'high_school',
      }),
    }),

  // learning paths
  generateLearningPath: (material_id: number, learner_goal?: string) =>
    request<LearningPath>('/api/learning-paths/generate', {
      method: 'POST',
      body: JSON.stringify({ material_id, learner_goal: learner_goal ?? '' }),
    }),
  getLearningPath: (id: number) => request<LearningPathDetail>(`/api/learning-paths/${id}`),
  updateStepStatus: (step_id: number, status: string) =>
    request<LearningStep>(`/api/learning-paths/steps/${step_id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    }),

  // quizzes
  generateQuiz: (material_id: number, num_questions?: number, difficulty?: string) =>
    request<QuizDetail>('/api/quizzes/generate', {
      method: 'POST',
      body: JSON.stringify({
        material_id,
        num_questions: num_questions ?? 5,
        difficulty: difficulty ?? 'mixed',
      }),
    }),
  getQuiz: (id: number) => request<QuizDetail>(`/api/quizzes/${id}`),
  submitAttempt: (quiz_id: number, answers: Record<string, string>) =>
    request<AttemptResult>(`/api/quizzes/${quiz_id}/attempts`, {
      method: 'POST',
      body: JSON.stringify({ answers }),
    }),

  // revision
  generateRevisionPlan: (material_id: number) =>
    request<RevisionPlan>('/api/revision/plans/generate', {
      method: 'POST',
      body: JSON.stringify({ material_id }),
    }),
  getDueTasks: () => request<RevisionTask[]>('/api/revision/tasks/due'),
  completeTask: (task_id: number) =>
    request<RevisionTask>(`/api/revision/tasks/${task_id}/complete`, { method: 'PATCH' }),

  // chat
  sendMessage: (session_id: string, message: string, material_id?: number) =>
    request<ChatMessage>('/api/chat/message', {
      method: 'POST',
      body: JSON.stringify({ session_id, message, material_id }),
    }),
  getSessionHistory: (session_id: string) =>
    request<ChatMessage[]>(`/api/chat/sessions/${session_id}`),

  // progress
  getDashboardStats: () => request<DashboardStats>('/api/progress/dashboard'),
  getProfileStats: () => request<ProfileStats>('/api/progress/profile'),
};

