# User Guide: SIH PS 26003 Cognitive Gaming & Memory Assistance Platform

This document outlines how to use the implemented features of the **AI-Based Cognitive Gaming & Memory Assistance Platform** for elderly dementia patients in the North Eastern Region (NER). The platform is a Progressive Web App (PWA) designed to work offline, with distinct interfaces for Patients, Caregivers, and Health Workers.

---

## 1. Getting Started & Setup

### Accounts (Mock Setup)
The prototype uses seeded mock accounts. Log in with the following credentials at the `/login` page:
- **Patients**: `patient1@ner.in` / `patient1pass` (Assam), `patient2@ner.in` / `patient2pass` (Meghalaya), `patient3@ner.in` / `patient3pass` (Manipur)
- **Caregivers**: `caregiver1@ner.in` / `cg1pass`, `caregiver2@ner.in` / `cg2pass`
- **Health Worker**: `hw1@ner.in` / `hw1pass`

### Offline & PWA Usage
The application is a Progressive Web App. When opened in a browser (Chrome/Edge/Safari), you can "Add to Home Screen" to install it. Once loaded, the core gameplay and patient workflows function fully offline. Data syncs automatically in the background when connectivity returns.

---

## 2. Patient Experience

The patient interface is highly simplified: large tap targets, semantic icons, high contrast, and reduced complexity.

### Core Cognitive Games
Patients access four distinct offline-capable games from their home screen:
1. **Memory Improvement**: Card-flip matching.
2. **Attention & Concentration**: Tap the odd-one-out among similar items.
3. **Daily Routine Recall**: Sequence the events of a typical day.
4. **Pattern & Object Recognition**: Identify familiar, culturally relevant objects.
*Features: Games automatically adjust difficulty (Easy/Medium/Hard) based on recent performance. Patients can pause games mid-session or request in-game hints.*

### Patient Home Screen Actions
- **Safety Check-in**: A one-tap button to log current status ("Home", "With Caregiver", "Out") and optionally share location.
- **Medications**: View current medications and instructions.
- **My Day (Daily Living)**: A checklist of daily activities (e.g., meals, hygiene) to tick off.
- **Sleep & Mood**: Daily self-reported mood rating (1-5) and sleep logging.
- **Movement (Activity)**: Log physical activities (e.g., walking, stretching) and duration.
- **Emergency Help**: One-tap access to primary caregiver and emergency contacts.
- **Memory Lane (Reminiscence Therapy)**: View structured prompts created by the caregiver (e.g., "Tell me about a festival you enjoyed") and record personal memories.
- **Messages (Social)**: Read and reply to asynchronous messages from the care team.
- **Doctor Visit Prep**: Read-only view of transport notes and preparation details for upcoming appointments.

### Accessibility & Navigation
- **Voice Support**: Language-specific TTS (Text-to-Speech) reads out screens and reminders. STT (Speech-to-Text) allows voice answers.
- **Regional Themes**: The visual palette adjusts to the patient's region (Assam, Meghalaya, Manipur) for cultural familiarity.

---

## 3. Caregiver Experience

Caregivers have a comprehensive dashboard to monitor their linked patients, configure settings, and provide support.

### Dashboard & Monitoring
- **Patient Selection**: Use the search bar or region filter at the top of the dashboard to find a specific patient.
- **Summary & Trends**: View the patient's streak, reminder adherence, and inactivity status. Trend charts show game accuracy and scores over time.
- **Plain-Language Explanations**: Below the charts, read a simple text explanation of whether the patient's accuracy is improving, stable, or declining.

### Care Coordination
- **Reminders**: Create scheduled prompts (Medicine, Hydration, Activity, Appointment) that appear on the patient's device. Critical missed reminders trigger escalation alerts.
- **Appointment Preparation**: Add structured notes for upcoming doctor visits (questions to ask, items to bring).
- **Transport Notes**: Coordinate travel logistics (pickup time, driver contact, mode of transport).
- **Care Notes**: Maintain a handover log visible to other care team members.

### Caregiver Support
- **Caregiver Learning (Education)**: Access a library of articles on dementia care, communication, and safety. Progress is tracked.
- **My Wellbeing**: Log personal energy and stress levels, and request support if overwhelmed.
- **Alert Quiet Hours**: In **Settings**, configure "Quiet Hours" (e.g., 22:00 to 07:00) during which push/SMS alerts are held.

### Data Management
- **Consent & Access**: View which caregivers are linked to a patient. Patients or primary caregivers can revoke access.
- **Audit Log**: View a secure trail of who accessed the patient's data and when.
- **Backup & Restore**: Export local IndexedDB data to a JSON file and restore it if switching devices.

---

## 4. Health Worker / Admin Experience

Health workers have similar dashboard access to caregivers but across a broader scope of patients in their community cluster.

### Route & Visit Planning
- **Plan Visits**: From the dashboard, click **"Plan visits"** to access the Visit Planning module.
- **Schedule**: Create planned visits specifying the patient, date/time, purpose, location, and notes.
- **Status Updates**: Mark visits as "Completed" or "Cancelled" as the day progresses.
- **Care Summaries**: Export a formal CSV summary of a patient's activity, adherence, and medications to share with visiting clinicians.

---

## 5. Security & Safety Boundaries

- **Not a Diagnostic Tool**: All trend explanations and summary reports include clear disclaimers that the application provides organisational and engagement support only, not medical diagnosis.
- **Offline Authoritative Sync**: Data is cached securely in the browser. When syncing with the backend, conflicts are resolved via last-write-wins (server timestamp), preventing data loss.
- **RBAC (Role-Based Access Control)**: Strict isolation prevents caregivers from viewing patients they are not linked to. Patients cannot modify clinical parameters like medication schedules.
