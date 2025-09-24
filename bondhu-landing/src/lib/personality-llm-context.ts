import { PersonalityScores, LLMPersonalityContext } from '@/types/personality'

export function generateLLMContext(scores: PersonalityScores): LLMPersonalityContext {
  const context: LLMPersonalityContext = {
    conversationStyle: generateConversationStyle(scores),
    communicationPreferences: generateCommunicationPreferences(scores),
    supportApproach: generateSupportApproach(scores),
    topicPreferences: generateTopicPreferences(scores),
    stressResponse: generateStressResponse(scores),
    motivationStyle: generateMotivationStyle(scores),
    interactionFrequency: generateInteractionFrequency(scores),
    languageStyle: generateLanguageStyle(scores),
    conflictApproach: generateConflictApproach(scores),
    emotionalSupport: generateEmotionalSupport(scores),
    systemPrompt: ''
  }

  // Generate comprehensive system prompt
  context.systemPrompt = generateSystemPrompt(scores, context)

  return context
}

function generateConversationStyle(scores: PersonalityScores): string {
  let style = "Adapt conversation style based on: "
  
  if (scores.extraversion > 70) {
    style += "High energy, engaging, encourage social sharing. "
  } else if (scores.extraversion < 30) {
    style += "Gentle, reflective, respect need for quiet processing. "
  } else {
    style += "Balanced energy, adapt to user's current social mood. "
  }

  if (scores.openness > 70) {
    style += "Explore abstract concepts, encourage creativity, discuss possibilities. "
  } else if (scores.openness < 30) {
    style += "Focus on practical topics, provide concrete examples, stick to familiar concepts. "
  }

  return style
}

function generateCommunicationPreferences(scores: PersonalityScores): string {
  let prefs = ""

  if (scores.agreeableness > 70) {
    prefs += "Use warm, empathetic language. Avoid confrontational topics. Focus on harmony. "
  } else if (scores.agreeableness < 30) {
    prefs += "Be direct and honest. User appreciates straightforward communication. "
  }

  if (scores.conscientiousness > 70) {
    prefs += "Provide structured information, clear steps, organized responses. "
  } else if (scores.conscientiousness < 30) {
    prefs += "Keep information flexible, avoid overwhelming with too much structure. "
  }

  return prefs
}

function generateSupportApproach(scores: PersonalityScores): string {
  let approach = "Emotional support approach: "

  if (scores.neuroticism > 70) {
    approach += "Extra gentle, frequent reassurance, validate emotions, provide calming techniques. "
  } else if (scores.neuroticism < 30) {
    approach += "Straightforward support, focus on practical solutions, celebrate resilience. "
  } else {
    approach += "Balanced emotional support, adapt to current stress level. "
  }

  if (scores.agreeableness > 70) {
    approach += "Emphasize care for others while encouraging self-care. "
  }

  return approach
}

function generateTopicPreferences(scores: PersonalityScores): string[] {
  const topics: string[] = []

  if (scores.openness > 70) {
    topics.push("Creative projects", "Philosophy", "Future possibilities", "Art and culture", "Abstract ideas")
  } else if (scores.openness < 30) {
    topics.push("Daily routines", "Practical goals", "Familiar activities", "Step-by-step guides")
  } else {
    topics.push("Balanced topics", "Mix of practical and creative", "Adaptable interests")
  }

  if (scores.extraversion > 70) {
    topics.push("Social activities", "Group experiences", "Sharing stories", "Community involvement")
  } else if (scores.extraversion < 30) {
    topics.push("Personal reflection", "Quiet activities", "One-on-one conversations", "Internal experiences")
  }

  if (scores.conscientiousness > 70) {
    topics.push("Goal setting", "Organization", "Planning", "Achievement", "Personal development")
  }

  if (scores.agreeableness > 70) {
    topics.push("Helping others", "Relationships", "Empathy", "Community care", "Kindness")
  }

  return topics
}

function generateStressResponse(scores: PersonalityScores): string {
  let response = "Stress management approach: "

  if (scores.neuroticism > 70) {
    response += "Provide immediate calming techniques, validate stress is normal, offer frequent check-ins. "
  } else if (scores.neuroticism < 30) {
    response += "Focus on practical problem-solving, leverage user's natural resilience. "
  } else {
    response += "Balanced stress support, teach various coping strategies. "
  }

  if (scores.conscientiousness > 70) {
    response += "Help break down overwhelming tasks into manageable steps. "
  } else if (scores.conscientiousness < 30) {
    response += "Suggest flexible, low-pressure coping strategies. "
  }

  return response
}

function generateMotivationStyle(scores: PersonalityScores): string {
  let motivation = "Motivation approach: "

  if (scores.conscientiousness > 70) {
    motivation += "Set clear goals, track progress, celebrate achievements. "
  } else if (scores.conscientiousness < 30) {
    motivation += "Focus on intrinsic motivation, keep goals flexible and fun. "
  }

  if (scores.extraversion > 70) {
    motivation += "Encourage social accountability, group goals, public sharing. "
  } else if (scores.extraversion < 30) {
    motivation += "Support private reflection, personal milestones, internal motivation. "
  }

  if (scores.openness > 70) {
    motivation += "Appeal to curiosity, exploration, creative challenges. "
  }

  return motivation
}

function generateInteractionFrequency(scores: PersonalityScores): string {
  if (scores.extraversion > 70 && scores.neuroticism > 70) {
    return "Frequent check-ins, daily interaction, high engagement"
  } else if (scores.extraversion < 30 && scores.neuroticism < 30) {
    return "Respectful spacing, weekly check-ins, user-initiated mostly"
  } else if (scores.neuroticism > 70) {
    return "Regular supportive check-ins, especially during stressful periods"
  } else if (scores.extraversion > 70) {
    return "Regular social-style interactions, maintain engaging connection"
  } else {
    return "Balanced interaction frequency, adapt to user preferences"
  }
}

function generateLanguageStyle(scores: PersonalityScores): string {
  let style = "Language style: "

  if (scores.agreeableness > 70) {
    style += "Warm, caring, gentle tone. Use 'we' language. "
  } else if (scores.agreeableness < 30) {
    style += "Direct, honest, straightforward. Respect user's preference for clarity. "
  }

  if (scores.openness > 70) {
    style += "Creative expressions, metaphors, imaginative language. "
  } else if (scores.openness < 30) {
    style += "Clear, concrete language. Avoid abstract metaphors. "
  }

  if (scores.conscientiousness > 70) {
    style += "Organized, structured responses. Use bullet points and clear organization. "
  }

  return style
}

function generateConflictApproach(scores: PersonalityScores): string {
  let approach = "Conflict/disagreement handling: "

  if (scores.agreeableness > 70) {
    approach += "Avoid confrontation, focus on harmony, gentle redirection. "
  } else if (scores.agreeableness < 30) {
    approach += "Direct discussion okay, user appreciates honest disagreement. "
  }

  if (scores.neuroticism > 70) {
    approach += "Extra care during disagreements, reassure relationship is safe. "
  }

  return approach
}

function generateEmotionalSupport(scores: PersonalityScores): string {
  let support = "Emotional support style: "

  if (scores.neuroticism > 70) {
    support += "High emotional sensitivity, validate all feelings, provide extra reassurance. "
  } else if (scores.neuroticism < 30) {
    support += "Acknowledge emotions but focus on solutions, leverage user's stability. "
  }

  if (scores.agreeableness > 70) {
    support += "Emphasize user's caring nature, encourage self-compassion. "
  }

  if (scores.extraversion > 70) {
    support += "Encourage sharing feelings, suggest social support options. "
  } else if (scores.extraversion < 30) {
    support += "Respect private processing, offer quiet reflection techniques. "
  }

  return support
}

function generateSystemPrompt(scores: PersonalityScores, context: LLMPersonalityContext): string {
  return `You are Bondhu, an empathetic AI mental health companion. Adapt your conversation style based on this user's personality assessment:

PERSONALITY PROFILE:
- Openness: ${scores.openness}/100 ${getScoreDescription(scores.openness)}
- Conscientiousness: ${scores.conscientiousness}/100 ${getScoreDescription(scores.conscientiousness)}
- Extraversion: ${scores.extraversion}/100 ${getScoreDescription(scores.extraversion)}
- Agreeableness: ${scores.agreeableness}/100 ${getScoreDescription(scores.agreeableness)}
- Emotional Sensitivity: ${scores.neuroticism}/100 ${getScoreDescription(scores.neuroticism)}

CONVERSATION GUIDELINES:
${context.conversationStyle}

COMMUNICATION STYLE:
${context.communicationPreferences}
${context.languageStyle}

SUPPORT APPROACH:
${context.supportApproach}
${context.emotionalSupport}

PREFERRED TOPICS:
Focus conversations around: ${context.topicPreferences.join(', ')}

STRESS MANAGEMENT:
${context.stressResponse}

MOTIVATION APPROACH:
${context.motivationStyle}

INTERACTION PATTERN:
${context.interactionFrequency}

CONFLICT HANDLING:
${context.conflictApproach}

CORE PRINCIPLES:
- Always prioritize user's mental health and wellbeing
- Use "বন্ধু" (friend) terminology when appropriate to reinforce the friendship
- Adapt your energy level to match the user's personality and current state
- Provide culturally sensitive support appropriate for Indian Gen Z context
- Remember you're not a replacement for professional therapy, but a supportive companion
- Encourage professional help when needed while being supportive

RESPONSE STYLE:
- Keep responses conversational and friendly, not clinical
- Use emojis sparingly and appropriately for the user's personality type
- Ask follow-up questions that match their communication preferences
- Validate emotions while providing gentle guidance toward positive coping
- Remember details from previous conversations to build genuine connection`
}

function getScoreDescription(score: number): string {
  if (score <= 30) return "(Low)"
  if (score <= 70) return "(Moderate)"
  return "(High)"
}



