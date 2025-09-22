"use client"

import { motion } from "framer-motion"
import { Brain, Zap, Heart } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

export function SolutionSection() {
  const steps = [
    {
      number: "01",
      title: "Personality Discovery",
      description: "Interactive RPG scenarios and games reveal your unique traits",
      icon: Brain,
      color: "from-blue-500/20 to-cyan-500/20",
      iconColor: "text-blue-600",
    },
    {
      number: "02",
      title: "Adaptive Learning",
      description: "AI continuously learns your communication style and preferences",
      icon: Zap,
      color: "from-yellow-500/20 to-orange-500/20",
      iconColor: "text-yellow-600",
    },
    {
      number: "03",
      title: "Proactive Support",
      description: "Bondhu initiates check-ins and suggests activities when you need them most",
      icon: Heart,
      color: "from-pink-500/20 to-red-500/20",
      iconColor: "text-pink-600",
    },
  ]

  return (
    <section className="py-20">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            How Bondhu is Different
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Not just another chatbot - an AI that truly understands and grows with you
          </p>
        </motion.div>

        <div className="max-w-5xl mx-auto">
          <div className="grid lg:grid-cols-3 gap-8">
            {steps.map((step, index) => {
              const IconComponent = step.icon
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.8, delay: index * 0.2 }}
                  viewport={{ once: true }}
                  className="relative"
                >
                  <Card className="h-full relative overflow-hidden group hover:shadow-lg transition-all duration-300">
                    <div className={`absolute inset-0 bg-gradient-to-br ${step.color} opacity-0 group-hover:opacity-100 transition-opacity duration-300`} />
                    
                    <CardContent className="p-8 relative z-10">
                      {/* Step Number */}
                      <div className="text-4xl font-bold text-muted-foreground/30 mb-4">
                        {step.number}
                      </div>

                      {/* Icon */}
                      <div className="w-16 h-16 mb-6 rounded-2xl bg-gradient-to-br from-primary/10 to-primary/20 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                        <IconComponent className={`h-8 w-8 ${step.iconColor}`} />
                      </div>

                      {/* Content */}
                      <h3 className="text-xl font-bold mb-3">{step.title}</h3>
                      <p className="text-muted-foreground leading-relaxed">
                        {step.description}
                      </p>

                      {/* Connection Line (except for last item) */}
                      {index < steps.length - 1 && (
                        <div className="hidden lg:block absolute top-1/2 -right-4 w-8 h-0.5 bg-gradient-to-r from-primary/50 to-transparent" />
                      )}
                    </CardContent>
                  </Card>

                  {/* Animated Connecting Arrow for Mobile */}
                  {index < steps.length - 1 && (
                    <motion.div
                      className="lg:hidden flex justify-center my-6"
                      initial={{ opacity: 0, y: -10 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.5, delay: index * 0.2 + 0.3 }}
                      viewport={{ once: true }}
                    >
                      <div className="w-0.5 h-8 bg-gradient-to-b from-primary to-primary/30" />
                    </motion.div>
                  )}
                </motion.div>
              )
            })}
          </div>
        </div>

        {/* Bottom CTA */}
        <motion.div
          className="text-center mt-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          viewport={{ once: true }}
        >
          <div className="max-w-md mx-auto">
            <div className="text-6xl mb-4">🌱</div>
            <p className="text-lg text-muted-foreground">
              &quot;Finally, someone who gets me and grows with me...&quot;
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
