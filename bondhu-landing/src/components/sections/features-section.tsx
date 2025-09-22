"use client"

import { motion } from "framer-motion"
import { Brain, Heart, Gamepad2, Zap, Shield, Clock } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export function FeaturesSection() {
  const features = [
    {
      icon: Brain,
      title: "Adaptive Intelligence",
      description: "Learns your communication style and adapts conversations to match your personality over time",
      benefits: ["Personalized responses", "Growing understanding", "Authentic interactions"],
      color: "from-blue-500/10 to-cyan-500/10",
      iconColor: "text-blue-600",
    },
    {
      icon: Heart,
      title: "Emotional Understanding",
      description: "Recognizes mood patterns and provides contextual emotional support when you need it most",
      benefits: ["Mood detection", "Contextual support", "Empathetic responses"],
      color: "from-pink-500/10 to-red-500/10",
      iconColor: "text-pink-600",
    },
    {
      icon: Gamepad2,
      title: "Gamified Discovery",
      description: "Fun RPG scenarios and interactive games help you discover your personality traits naturally",
      benefits: ["Engaging onboarding", "Self-discovery", "Personality insights"],
      color: "from-purple-500/10 to-indigo-500/10",
      iconColor: "text-purple-600",
    },
    {
      icon: Zap,
      title: "Proactive Care",
      description: "Initiates check-ins and suggests activities based on your well-being patterns and preferences",
      benefits: ["Proactive outreach", "Activity suggestions", "Wellness tracking"],
      color: "from-yellow-500/10 to-orange-500/10",
      iconColor: "text-yellow-600",
    },
    {
      icon: Shield,
      title: "Privacy First",
      description: "End-to-end encryption ensures your conversations remain completely private and secure",
      benefits: ["Data encryption", "Private conversations", "No data sharing"],
      color: "from-green-500/10 to-emerald-500/10",
      iconColor: "text-green-600",
    },
    {
      icon: Clock,
      title: "Always Available",
      description: "24/7 companion that fits your schedule, perfect for late-night thoughts or early morning clarity",
      benefits: ["Round-the-clock access", "Instant responses", "No appointment needed"],
      color: "from-slate-500/10 to-gray-500/10",
      iconColor: "text-slate-600",
    },
  ]

  return (
    <section id="features" className="py-20">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Why Choose Bondhu?
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Advanced AI technology meets genuine emotional understanding
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const IconComponent = feature.icon
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="h-full group hover:shadow-lg transition-all duration-300 relative overflow-hidden">
                  <div className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-100 transition-opacity duration-300`} />
                  
                  <CardContent className="p-6 relative z-10">
                    {/* Icon */}
                    <div className="w-14 h-14 mb-4 rounded-xl bg-gradient-to-br from-primary/10 to-primary/20 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                      <IconComponent className={`h-7 w-7 ${feature.iconColor}`} />
                    </div>

                    {/* Title */}
                    <h3 className="text-xl font-bold mb-3">{feature.title}</h3>

                    {/* Description */}
                    <p className="text-muted-foreground mb-4 leading-relaxed">
                      {feature.description}
                    </p>

                    {/* Benefits */}
                    <div className="space-y-2">
                      {feature.benefits.map((benefit, benefitIndex) => (
                        <motion.div
                          key={benefitIndex}
                          className="flex items-center space-x-2"
                          initial={{ opacity: 0, x: -10 }}
                          whileInView={{ opacity: 1, x: 0 }}
                          transition={{ duration: 0.5, delay: index * 0.1 + benefitIndex * 0.1 }}
                          viewport={{ once: true }}
                        >
                          <div className="w-1.5 h-1.5 bg-primary rounded-full" />
                          <Badge variant="secondary" className="text-xs">
                            {benefit}
                          </Badge>
                        </motion.div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )
          })}
        </div>

        {/* Bottom CTA */}
        <motion.div
          className="text-center mt-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          viewport={{ once: true }}
        >
          <Card className="max-w-2xl mx-auto p-8 bg-gradient-to-r from-primary/5 to-secondary/5 border-primary/20">
            <CardContent className="p-0 text-center">
              <div className="text-4xl mb-4">✨</div>
              <h3 className="text-2xl font-bold mb-3">
                Experience the Difference
              </h3>
              <p className="text-muted-foreground mb-6">
                Join thousands of users who&apos;ve found their perfect AI companion
              </p>
              <div className="flex flex-wrap justify-center gap-2">
                <Badge variant="outline">Personality-aware</Badge>
                <Badge variant="outline">Emotionally intelligent</Badge>
                <Badge variant="outline">Privacy-focused</Badge>
                <Badge variant="outline">Always learning</Badge>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </section>
  )
}
