import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './components/AuthContext'
import SyncIndicator from './components/SyncIndicator'

import LoginPage           from './pages/LoginPage'
import PatientHomePage     from './pages/PatientHomePage'
import OnboardingPage      from './pages/OnboardingPage'
import GameShell           from './pages/GameShell'
import RemindersPage       from './pages/RemindersPage'
import CaregiverRemindersPage from './pages/CaregiverRemindersPage'
import CaregiverDashboard  from './pages/CaregiverDashboard'
import SettingsPage        from './pages/SettingsPage'
import NotificationsPage   from './pages/NotificationsPage'
import EmergencyContactsPage from './pages/EmergencyContactsPage'
import SafetyCheckInPage   from './pages/SafetyCheckInPage'
import MedicationsPage     from './pages/MedicationsPage'
import SafetyGuidancePage  from './pages/SafetyGuidancePage'
import AuditLogPage        from './pages/AuditLogPage'
import BackupPage          from './pages/BackupPage'
import CaregiverAccessPage from './pages/CaregiverAccessPage'
import CaregiverNotesPage  from './pages/CaregiverNotesPage'
import ReminiscencePage    from './pages/ReminiscencePage'
import SocialPage          from './pages/SocialPage'
import DailyLivingPage     from './pages/DailyLivingPage'
import MoodPage             from './pages/MoodPage'
import ActivityPage         from './pages/ActivityPage'
import EducationPage        from './pages/EducationPage'
import CaregiverWellbeingPage from './pages/CaregiverWellbeingPage'
import VisitPlanningPage from './pages/VisitPlanningPage'
import AppointmentPrepPage from './pages/AppointmentPrepPage'
import TransportNotesPage from './pages/TransportNotesPage'

function RequireAuth({ children, roles }) {
  const { user, loading } = useAuth()
  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading…</div>
  if (!user) return <Navigate to="/login" replace />
  if (roles && !roles.includes(user.role)) return <Navigate to="/dashboard" replace />
  return children
}

function AppRoutes() {
  const { user, loading } = useAuth()

  if (loading) return null

  return (
    <>
      <SyncIndicator />
      <Routes>
        <Route path="/login" element={user ? <Navigate to={user.role === 'patient' ? '/home' : '/dashboard'} replace /> : <LoginPage />} />
        <Route path="/onboarding" element={
          <RequireAuth roles={['patient']}>
            <OnboardingPage />
          </RequireAuth>
        } />
        <Route path="/home" element={
          <RequireAuth roles={['patient']}>
            <PatientHomePage />
          </RequireAuth>
        } />
        <Route path="/game/:gameType" element={
          <RequireAuth roles={['patient']}>
            <GameShell />
          </RequireAuth>
        } />
        <Route path="/reminders" element={
          <RequireAuth>
            <RemindersPage />
          </RequireAuth>
        } />
        <Route path="/dashboard" element={
          <RequireAuth roles={['caregiver', 'health_worker', 'admin']}>
            <CaregiverDashboard />
          </RequireAuth>
        } />
        <Route path="/dashboard/reminders" element={
          <RequireAuth roles={['caregiver', 'health_worker', 'admin']}>
            <CaregiverRemindersPage />
          </RequireAuth>
        } />
        <Route path="/settings" element={
          <RequireAuth>
            <SettingsPage />
          </RequireAuth>
        } />
        <Route path="/notifications" element={
          <RequireAuth>
            <NotificationsPage />
          </RequireAuth>
        } />
        <Route path="/emergency-contacts" element={
          <RequireAuth>
            <EmergencyContactsPage />
          </RequireAuth>
        } />
        <Route path="/safety-check-in" element={
          <RequireAuth>
            <SafetyCheckInPage />
          </RequireAuth>
        } />
        <Route path="/medications" element={
          <RequireAuth>
            <MedicationsPage />
          </RequireAuth>
        } />
        <Route path="/safety-guidance" element={
          <RequireAuth>
            <SafetyGuidancePage />
          </RequireAuth>
        } />
        <Route path="/audit-log" element={
          <RequireAuth>
            <AuditLogPage />
          </RequireAuth>
        } />
        <Route path="/backup" element={
          <RequireAuth>
            <BackupPage />
          </RequireAuth>
        } />
        <Route path="/caregiver-access" element={
          <RequireAuth>
            <CaregiverAccessPage />
          </RequireAuth>
        } />
        <Route path="/caregiver-notes" element={
          <RequireAuth roles={['caregiver', 'health_worker', 'admin']}>
            <CaregiverNotesPage />
          </RequireAuth>
        } />
        <Route path="/reminiscence" element={
          <RequireAuth>
            <ReminiscencePage />
          </RequireAuth>
        } />
        <Route path="/social" element={
          <RequireAuth>
            <SocialPage />
          </RequireAuth>
        } />
        <Route path="/daily-living" element={
          <RequireAuth>
            <DailyLivingPage />
          </RequireAuth>
        } />
        <Route path="/mood" element={
          <RequireAuth>
            <MoodPage />
          </RequireAuth>
        } />
        <Route path="/activity" element={
          <RequireAuth>
            <ActivityPage />
          </RequireAuth>
        } />
        <Route path="/education" element={
          <RequireAuth roles={['caregiver', 'health_worker', 'admin']}>
            <EducationPage />
          </RequireAuth>
        } />
        <Route path="/caregiver-wellbeing" element={
          <RequireAuth roles={['caregiver', 'health_worker', 'admin']}>
            <CaregiverWellbeingPage />
          </RequireAuth>
        } />
        <Route path="/visit-planning" element={
          <RequireAuth roles={['health_worker', 'admin']}>
            <VisitPlanningPage />
          </RequireAuth>
        } />
        <Route path="/appointment-prep" element={
          <RequireAuth roles={['patient', 'caregiver', 'health_worker', 'admin']}>
            <AppointmentPrepPage />
          </RequireAuth>
        } />
        <Route path="/transport-notes" element={
          <RequireAuth roles={['patient', 'caregiver', 'health_worker', 'admin']}>
            <TransportNotesPage />
          </RequireAuth>
        } />
        <Route path="*" element={
          <Navigate to={user ? (user.role === 'patient' ? '/home' : '/dashboard') : '/login'} replace />
        } />
      </Routes>
    </>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}
