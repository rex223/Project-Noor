import { PersonalityTrait, PersonalityQuestion } from '@/types/personality'

export const personalityQuestions: PersonalityQuestion[] = [
  // Openness (Questions 1-3)
  {
    id: 1,
    traitId: 'openness',
    scenario: "You discover new realms of possibility beyond the portal...",
    questionText: "I see myself as someone who is original and comes up with new ideas.",
    isReversed: false
  },
  {
    id: 2,
    traitId: 'openness',
    scenario: "Deep in a cave, you find ancient artifacts that spark endless questions...",
    questionText: "I see myself as someone who is curious about many different things.",
    isReversed: false
  },
  {
    id: 3,
    traitId: 'openness',
    scenario: "A magical weaver invites you to spin dreams into reality. Your mind races with vivid visions...",
    questionText: "I see myself as someone who has an active imagination.",
    isReversed: false
  },

  // Extraversion (Questions 4-6)
  {
    id: 4,
    traitId: 'extraversion',
    scenario: "The festival energy is infectious, everyone's laughing and connecting...",
    questionText: "I see myself as someone who is outgoing and sociable.",
    isReversed: false
  },
  {
    id: 5,
    traitId: 'extraversion',
    scenario: "You notice a peaceful path away from all the noise and activity...",
    questionText: "I see myself as someone who tends to be quiet.",
    isReversed: true
  },
  {
    id: 6,
    traitId: 'extraversion',
    scenario: "Villagers gather around a fire, sharing tales and stories...",
    questionText: "I see myself as someone who is talkative.",
    isReversed: false
  },

  // Agreeableness (Questions 7-9)
  {
    id: 7,
    traitId: 'agreeableness',
    scenario: "Your companion trips and gets hurt on the rocky path...",
    questionText: "I see myself as someone who is compassionate and has a soft heart.",
    isReversed: false
  },
  {
    id: 8,
    traitId: 'agreeableness',
    scenario: "A shady trader tries to cheat you at the marketplace...",
    questionText: "I see myself as someone who tends to find fault with others.",
    isReversed: true
  },
  {
    id: 9,
    traitId: 'agreeableness',
    scenario: "A bridge guarded by strangers—do you believe they'll guide you safely?",
    questionText: "I see myself as someone who is generally trusting.",
    isReversed: false
  },

  // Conscientiousness (Questions 10-12)
  {
    id: 10,
    traitId: 'conscientiousness',
    scenario: "The steep ascent requires careful planning of every step...",
    questionText: "I see myself as someone who does a thorough job.",
    isReversed: false
  },
  {
    id: 11,
    traitId: 'conscientiousness',
    scenario: "Halfway up, a comfy spot tempts you to take a long break...",
    questionText: "I see myself as someone who tends to be lazy.",
    isReversed: true
  },
  {
    id: 12,
    traitId: 'conscientiousness',
    scenario: "You spot the peak and feel the drive to reach the summit...",
    questionText: "I see myself as someone who is efficient and gets things done.",
    isReversed: false
  },

  // Neuroticism (Questions 13-15)
  {
    id: 13,
    traitId: 'neuroticism',
    scenario: "The winds howl around you, but you find your inner calm...",
    questionText: "I see myself as someone who is relaxed and handles stress well.",
    isReversed: true
  },
  {
    id: 14,
    traitId: 'neuroticism',
    scenario: "Thunder rumbles overhead, and doubts swirl in your mind...",
    questionText: "I see myself as someone who worries a lot.",
    isReversed: false
  },
  {
    id: 15,
    traitId: 'neuroticism',
    scenario: "The path down is slippery and uncertain...",
    questionText: "I see myself as someone who gets nervous easily.",
    isReversed: false
  }
]

export const personalityTraits: PersonalityTrait[] = [
  {
    id: 'openness',
    displayName: 'Openness to Experience',
    storyTitle: 'The Enchanted Forest of Ideas',
    storyDescription: "You're wandering a glowing forest where trees whisper secrets. A mysterious portal opens, offering wild, uncharted paths. How do you react?",
    color: '#22c55e', // green - creativity/growth
    questions: personalityQuestions.filter(q => q.traitId === 'openness'),
    imageUrl: '/images/personality/enchanted-forest.jpg',
    completedQuestions: 0,
    totalQuestions: 3
  },
  {
    id: 'extraversion',
    displayName: 'Extraversion',
    storyTitle: 'The Village Social Hub',
    storyDescription: "At a lively festival, crowds are chatting and dancing. The party noise fades as you spot a serene, hidden trail. Do you jump into the fun or find your quiet space?",
    color: '#8b5cf6', // purple - social energy
    questions: personalityQuestions.filter(q => q.traitId === 'extraversion'),
    imageUrl: '/images/personality/village-festival.jpg',
    completedQuestions: 0,
    totalQuestions: 3
  },
  {
    id: 'agreeableness',
    displayName: 'Agreeableness',
    storyTitle: 'The Compassion Temple',
    storyDescription: "A fellow traveler needs help—how compassionate are you? Your choices reveal how you connect with and trust others on this journey.",
    color: '#f59e0b', // amber - warmth/empathy
    questions: personalityQuestions.filter(q => q.traitId === 'agreeableness'),
    imageUrl: '/images/personality/compassion-temple.jpg',
    completedQuestions: 0,
    totalQuestions: 3
  },
  {
    id: 'conscientiousness',
    displayName: 'Conscientiousness',
    storyTitle: 'The Mountain of Achievement',
    storyDescription: "Time to tackle a challenging mountain climb. The path is tough, but victory awaits at the summit. How do you approach this test of determination?",
    color: '#3b82f6', // blue - reliability/structure
    questions: personalityQuestions.filter(q => q.traitId === 'conscientiousness'),
    imageUrl: '/images/personality/mountain-achievement.jpg',
    completedQuestions: 0,
    totalQuestions: 3
  },
  {
    id: 'neuroticism',
    displayName: 'Emotional Sensitivity',
    storyTitle: 'The Emotional Weather Station',
    storyDescription: "Storm clouds gather as you face the final challenge. Thunder rumbles and winds howl. How do you handle the pressure and uncertainty?",
    color: '#f97316', // softer orange-red for mental health sensitivity
    questions: personalityQuestions.filter(q => q.traitId === 'neuroticism'),
    imageUrl: '/images/personality/weather-station.jpg',
    completedQuestions: 0,
    totalQuestions: 3
  }
]

export const introCard = {
  id: 'intro',
  storyTitle: 'Welcome to Neuron Valley',
  storyDescription: "Welcome, traveler! You're about to embark on a unique journey through Neuron Valley, where every path reveals something special about who you are. This isn't just any quest—it's a discovery of your inner self, helping your AI companion Bondhu understand how to support you best.",
  instructions: [
    "🎭 Experience 5 immersive scenarios",
    "⚡ Answer honestly—there are no wrong choices",
    "🌱 Help Bondhu learn your unique personality",
    "⏱️ Takes about 5-7 minutes to complete"
  ],
  imageUrl: '/images/personality/neuron-valley.jpg'
}



