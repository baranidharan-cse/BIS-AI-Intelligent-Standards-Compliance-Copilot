import { BrowserRouter, Route, Routes, Navigate } from 'react-router-dom'
import AppShell from './components/layout/AppShell'

// Placeholder pages — each will be replaced with a real implementation
// in the corresponding feature session.
import DashboardPage from './pages/DashboardPage'
import MyMaterialsPage from './pages/MyMaterialsPage'
import LearningPathPage from './pages/LearningPathPage'
import StudyPage from './pages/StudyPage'
import PracticePage from './pages/PracticePage'
import RevisionPage from './pages/RevisionPage'
import AskBuddyPage from './pages/AskBuddyPage'
import SettingsPage from './pages/SettingsPage'
import ProfilePage from './pages/ProfilePage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppShell />}>
          {/* Redirect root to dashboard */}
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="materials" element={<MyMaterialsPage />} />
          <Route path="learning-path" element={<LearningPathPage />} />
          <Route path="study" element={<StudyPage />} />
          <Route path="practice" element={<PracticePage />} />
          <Route path="revision" element={<RevisionPage />} />
          <Route path="ask-buddy" element={<AskBuddyPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="profile" element={<ProfilePage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
