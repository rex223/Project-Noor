"use client"

import { motion } from "framer-motion"
import { TrendingDown, Users, Brain } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

export function ProblemSection() {
  const statistics = [
    {
      number: "43%",
      description: "of young Indians report feeling lonely despite digital connectivity",
      icon: Users,
    },
    {
      number: "24.8%",
      description: "of students exhibit high levels of social anxiety",
      icon: Brain,
    },
    {
      number: "13.5%",
      description: "mental health disorder prevalence in urban metros vs 7.3% national average",
      icon: TrendingDown,
    },
  ]

  const painPoints = [
    "Social media amplifies fear of judgment",
    "Traditional therapy feels intimidating and expensive",
    "Existing chatbots lack real personality understanding",
    "No one to talk to during late-night overthinking",
  ]

  return (
    <section id="about" className="py-20 bg-secondary/20">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            The Gen Z Mental Health Crisis
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            You&apos;re more connected than ever, yet loneliness feels overwhelming
          </p>
        </motion.div>

        {/* Statistics Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {statistics.map((stat, index) => {
            const IconComponent = stat.icon
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="text-center p-6 h-full">
                  <CardContent className="p-0">
                    <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-destructive/10 flex items-center justify-center">
                      <IconComponent className="h-6 w-6 text-destructive" />
                    </div>
                    <div className="text-4xl font-bold text-destructive mb-2">
                      {stat.number}
                    </div>
                    <p className="text-muted-foreground">{stat.description}</p>
                  </CardContent>
                </Card>
              </motion.div>
            )
          })}
        </div>

        {/* Pain Points */}
        <motion.div
          className="max-w-4xl mx-auto"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <h3 className="text-2xl font-bold text-center mb-8">
            The Reality You Face Every Day
          </h3>
          <div className="grid md:grid-cols-2 gap-6">
            {painPoints.map((point, index) => (
              <motion.div
                key={index}
                className="flex items-start space-x-3"
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <div className="w-2 h-2 rounded-full bg-destructive mt-2 flex-shrink-0" />
                <p className="text-muted-foreground">{point}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Emotional Impact Visual */}
        <motion.div
          className="mt-16 text-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 1 }}
          viewport={{ once: true }}
        >
          <div className="max-w-md mx-auto relative">
            <div className="text-6xl mb-4">😔</div>
            <p className="text-lg text-muted-foreground">
              &quot;I&apos;m surrounded by people online, but I still feel alone...&quot;
            </p>
            <div className="absolute -top-4 -right-4 w-8 h-8 rounded-full border-2 border-destructive/30 animate-ping" />
          </div>
        </motion.div>
      </div>
    </section>
  )
}
