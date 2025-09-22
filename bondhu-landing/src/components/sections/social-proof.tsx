"use client"

import { motion } from "framer-motion"
import { Star, Users, MessageCircle, Heart, GraduationCap } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"

export function SocialProof() {
  const testimonials = [
    {
      name: "Priya S.",
      age: 21,
      location: "Mumbai",
      quote: "Bondhu feels like talking to someone who actually knows me. It's not just another chatbot - it remembers our conversations and grows with me.",
      rating: 5,
      avatar: "PS",
    },
    {
      name: "Arjun K.",
      age: 20,
      location: "Delhi",
      quote: "I was skeptical at first, but Bondhu's personality assessment was scarily accurate. Now it's like having a friend who understands my anxiety.",
      rating: 5,
      avatar: "AK",
    },
    {
      name: "Sneha R.",
      age: 22,
      location: "Bangalore",
      quote: "The gamified onboarding was fun, and now Bondhu suggests activities that actually match my mood. It's become part of my daily routine.",
      rating: 5,
      avatar: "SR",
    },
  ]

  const statistics = [
    {
      icon: Users,
      value: "10,000+",
      label: "Active Users",
      description: "Gen Z students across India",
    },
    {
      icon: MessageCircle,
      value: "50,000+",
      label: "Conversations",
      description: "Meaningful exchanges daily",
    },
    {
      icon: Heart,
      value: "89%",
      label: "Satisfaction Rate",
      description: "Users feel genuinely supported",
    },
    {
      icon: GraduationCap,
      value: "15+",
      label: "Universities",
      description: "Across major Indian cities",
    },
  ]

  const StarRating = ({ rating }: { rating: number }) => {
    return (
      <div className="flex space-x-1">
        {[...Array(5)].map((_, i) => (
          <Star
            key={i}
            className={`h-4 w-4 ${
              i < rating
                ? "fill-yellow-400 text-yellow-400"
                : "text-gray-300"
            }`}
          />
        ))}
      </div>
    )
  }

  return (
    <section className="py-20 bg-secondary/20">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Trusted by Gen Z Across India
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Real stories from students who found their perfect AI companion
          </p>
        </motion.div>

        {/* Statistics */}
        <div className="grid md:grid-cols-4 gap-6 mb-16">
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
                <Card className="text-center p-6">
                  <CardContent className="p-0">
                    <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-primary/10 flex items-center justify-center">
                      <IconComponent className="h-6 w-6 text-primary" />
                    </div>
                    <div className="text-3xl font-bold text-primary mb-1">
                      {stat.value}
                    </div>
                    <div className="font-medium mb-1">{stat.label}</div>
                    <p className="text-sm text-muted-foreground">
                      {stat.description}
                    </p>
                  </CardContent>
                </Card>
              </motion.div>
            )
          })}
        </div>

        {/* Testimonials */}
        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: index * 0.2 }}
              viewport={{ once: true }}
            >
              <Card className="h-full">
                <CardContent className="p-6">
                  {/* Rating */}
                  <div className="mb-4">
                    <StarRating rating={testimonial.rating} />
                  </div>

                  {/* Quote */}
                  <blockquote className="text-muted-foreground mb-6 leading-relaxed">
                    &quot;{testimonial.quote}&quot;
                  </blockquote>

                  {/* Author */}
                  <div className="flex items-center space-x-3">
                    <Avatar className="w-10 h-10">
                      <AvatarFallback className="bg-primary/10 text-primary text-sm">
                        {testimonial.avatar}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <div className="font-medium">{testimonial.name}</div>
                      <div className="text-sm text-muted-foreground">
                        Age {testimonial.age} • {testimonial.location}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Community Highlight */}
        <motion.div
          className="mt-16 text-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          viewport={{ once: true }}
        >
          <Card className="max-w-3xl mx-auto p-8 bg-gradient-to-r from-primary/5 to-secondary/5 border-primary/20">
            <CardContent className="p-0">
              <div className="flex flex-col md:flex-row items-center space-y-4 md:space-y-0 md:space-x-6">
                <div className="text-6xl">🤝</div>
                <div className="text-center md:text-left">
                  <h3 className="text-2xl font-bold mb-2">
                    Join the Bondhu Community
                  </h3>
                  <p className="text-muted-foreground mb-4">
                    Connect with like-minded Gen Z individuals who prioritize mental wellness
                  </p>
                  <div className="flex flex-wrap justify-center md:justify-start gap-2">
                    <span className="text-sm bg-primary/10 text-primary px-3 py-1 rounded-full">
                      Daily check-ins
                    </span>
                    <span className="text-sm bg-primary/10 text-primary px-3 py-1 rounded-full">
                      Peer support
                    </span>
                    <span className="text-sm bg-primary/10 text-primary px-3 py-1 rounded-full">
                      Mental health resources
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </section>
  )
}
