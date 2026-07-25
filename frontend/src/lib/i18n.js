// Tier 2: Bengali (Bangla) UI support. Deliberately covers the chrome a
// low-literacy farmer actually navigates by (nav labels/page headers, chat
// input, common buttons) rather than every microcopy string in the app —
// the agent's own replies are translated server-side (see backend
// app/agent/i18n.py), which is the part that actually carries information.
export const TRANSLATIONS = {
  en: {
    appName: 'AgriSense AI',
    nav_dashboard: 'Dashboard',
    nav_profile: 'Farmer Profile',
    nav_assistant: 'AI Assistant',
    nav_crops: 'Crop Recommendations',
    nav_timeline: 'Season Planner',
    nav_financials: 'Financial Dashboard',
    nav_marketplace: 'Marketplace',
    nav_prices: 'Price Intelligence',
    nav_disease: 'Disease Detection',
    nav_alerts: 'Smart Alerts',
    nav_weather: 'Weather Analysis',
    nav_trace: 'Agent Activity',
    chatPlaceholder: 'Tell the agent about your farm...',
    send: 'Send',
    newChat: '+ New Chat',
    chats: 'Chats',
    noPreviousChats: 'No previous conversations yet.',
    welcomeMessage:
      "Hi! I'm AgriSense AI. Tell me about your farm — location, size, budget, soil type, water availability, and target season — and I'll build you a costed, weather-aware season plan.",
    speak: 'Speak your message',
    listening: 'Listening…',
    readAloud: 'Read aloud',
    stopReading: 'Stop reading',
  },
  bn: {
    appName: 'এগ্রিসেন্স এআই',
    nav_dashboard: 'ড্যাশবোর্ড',
    nav_profile: 'কৃষকের প্রোফাইল',
    nav_assistant: 'এআই সহকারী',
    nav_crops: 'ফসলের সুপারিশ',
    nav_timeline: 'মৌসুম পরিকল্পনা',
    nav_financials: 'আর্থিক ড্যাশবোর্ড',
    nav_marketplace: 'বাজার',
    nav_prices: 'বাজারদর তথ্য',
    nav_disease: 'রোগ শনাক্তকরণ',
    nav_alerts: 'স্মার্ট সতর্কতা',
    nav_weather: 'আবহাওয়া বিশ্লেষণ',
    nav_trace: 'এজেন্ট কার্যকলাপ',
    chatPlaceholder: 'আপনার খামার সম্পর্কে বলুন...',
    send: 'পাঠান',
    newChat: '+ নতুন চ্যাট',
    chats: 'চ্যাট সমূহ',
    noPreviousChats: 'এখনো কোনো পূর্ববর্তী কথোপকথন নেই।',
    welcomeMessage:
      'হ্যালো! আমি এগ্রিসেন্স এআই। আপনার খামার সম্পর্কে বলুন — অবস্থান, আকার, বাজেট, মাটির ধরন, পানির প্রাপ্যতা এবং লক্ষ্য মৌসুম — আমি আপনার জন্য একটি খরচসহ, আবহাওয়া-সচেতন মৌসুম পরিকল্পনা তৈরি করে দেব।',
    speak: 'কথা বলে লিখুন',
    listening: 'শুনছি…',
    readAloud: 'পড়ে শোনান',
    stopReading: 'থামান',
  },
}

export function translate(language, key) {
  return TRANSLATIONS[language]?.[key] ?? TRANSLATIONS.en[key] ?? key
}

// Web Speech API language tags.
export const SPEECH_LANG = { en: 'en-US', bn: 'bn-BD' }
