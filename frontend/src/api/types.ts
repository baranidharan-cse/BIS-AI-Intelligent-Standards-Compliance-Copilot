export interface Material {
  id: number;
  title: string;
  description?: string;
  status: 'pending' | 'processing' | 'ready' | 'error';
  material_type: string;
  created_at: string;
  summary?: string;
}

export interface Concept {
  id: number;
  name: string;
  definition?: string;
  explanation?: string;
  examples: string[];
  order_index: number;
}

export interface Section {
  id: number;
  title: string;
  order_index: number;
  summary?: string;
  content?: string;
  concepts: Concept[];
}

export interface MaterialDetail extends Material {
  sections: Section[];
  raw_text?: string;
}

export interface LearningStep {
  id: number;
  title: string;
  description?: string;
  order_index: number;
  estimated_minutes: number;
  status: 'not_started' | 'in_progress' | 'completed' | 'skipped';
  prerequisites?: string;
}

export interface LearningPath {
  id: number;
  material_id: number;
  title: string;
  description?: string;
  estimated_duration_minutes: number;
}

export interface LearningPathDetail extends LearningPath {
  steps: LearningStep[];
}

export interface QuizQuestion {
  id: number;
  question_text: string;
  question_type: 'multiple_choice' | 'true_false' | 'short_answer';
  options?: string[];
  difficulty: string;
  order_index: number;
}

export interface QuizDetail {
  id: number;
  material_id: number;
  title: string;
  difficulty: string;
  questions: QuizQuestion[];
}

export interface AttemptResult {
  id: number;
  score: number;
  correct_count: number;
  total_questions: number;
  per_question: Array<{
    question_id: number;
    correct: boolean;
    correct_answer: string;
    explanation?: string;
  }>;
}

export interface RevisionPlan {
  id: number;
  material_id: number;
  title: string;
  created_at: string;
}

export interface RevisionTask {
  id: number;
  title: string;
  due_date: string;
  status: string;
  concept_name?: string;
  interval_days: number;
}

export interface ChatMessage {
  id?: number;
  role: 'user' | 'assistant';
  content: string;
  session_id?: string;
  follow_up_suggestions?: string[];
  created_at?: string;
}

export interface DashboardStats {
  total_materials: number;
  total_concepts: number;
  mastered_concepts: number;
  avg_mastery_pct: number;
  due_today: number;
  total_quizzes_taken: number;
  avg_quiz_score: number;
}

export interface Badge {
  id: string;
  title: string;
  icon: string;
  description: string;
  unlocked: boolean;
}

export interface MaterialProgressSummary {
  id: number;
  title: string;
  mastery_pct: number;
  completion_pct: number;
  time_studied_minutes: number;
}

export interface ProfileStats {
  dashboard: DashboardStats;
  materials_progress: MaterialProgressSummary[];
  total_study_time_minutes: number;
  total_tasks_completed: number;
  badges: Badge[];
}

