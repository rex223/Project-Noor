"use client"

import { motion } from "framer-motion"
import { Check, Zap, Crown, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export function PricingSection() {
  const betaFeatures = [
    "Complete personality assessment",
    "Unlimited conversations",
    "Basic mood tracking",
    "Gamified onboarding experience",
    "Privacy-first encryption",
    "24/7 availability",
    "Early access to new features",
  ]

  const premiumFeatures = [
    "Voice conversations",
    "Advanced personality analytics",
    "Group chat capabilities",
    "Therapist referral network",
    "Custom personality insights",
    "Priority support",
  ]

  return (
    <section id="pricing" className="py-20">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Start Your Journey Today
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Free beta access with premium features coming soon
          </p>
        </motion.div>

        <div className="max-w-4xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Beta Access - Free */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
            >
              <Card className="h-full relative overflow-hidden border-primary/20">
                <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary to-primary/50" />
                
                <CardHeader className="pb-4">
                  <div className="flex items-center justify-between">
                    <Badge variant="secondary" className="w-fit">
                      <Zap className="h-3 w-3 mr-1" />
                      Current Offer
                    </Badge>
                    <div className="text-right">
                      <div className="text-3xl font-bold">Free</div>
                      <div className="text-sm text-muted-foreground">Beta Access</div>
                    </div>
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold">Beta Access</h3>
                    <p className="text-muted-foreground">
                      Full access to Bondhu while we perfect the experience
                    </p>
                  </div>
                </CardHeader>

                <CardContent className="pt-0">
                  <div className="space-y-3 mb-6">
                    {betaFeatures.map((feature, index) => (
                      <motion.div
                        key={index}
                        className="flex items-center space-x-3"
                        initial={{ opacity: 0, x: -10 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.5, delay: index * 0.1 }}
                        viewport={{ once: true }}
                      >
                        <div className="w-5 h-5 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                          <Check className="h-3 w-3 text-primary" />
                        </div>
                        <span className="text-sm">{feature}</span>
                      </motion.div>
                    ))}
                  </div>

                  <Button size="lg" className="w-full">
                    Join Beta Now
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>

                  <div className="mt-4 text-center">
                    <p className="text-xs text-muted-foreground">
                      No credit card required • Join 10,000+ users
                    </p>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* Premium Features - Coming Soon */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              viewport={{ once: true }}
            >
              <Card className="h-full relative overflow-hidden bg-gradient-to-br from-primary/5 to-secondary/5 border-primary/30">
                <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-yellow-500 to-orange-500" />
                
                <CardHeader className="pb-4">
                  <div className="flex items-center justify-between">
                    <Badge className="w-fit bg-gradient-to-r from-yellow-500 to-orange-500 text-white border-0">
                      <Crown className="h-3 w-3 mr-1" />
                      Coming Soon
                    </Badge>
                    <div className="text-right">
                      <div className="text-3xl font-bold">₹299</div>
                      <div className="text-sm text-muted-foreground">/month</div>
                    </div>
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold">Premium Features</h3>
                    <p className="text-muted-foreground">
                      Advanced capabilities for the ultimate AI companion experience
                    </p>
                  </div>
                </CardHeader>

                <CardContent className="pt-0">
                  <div className="space-y-3 mb-6">
                    {premiumFeatures.map((feature, index) => (
                      <motion.div
                        key={index}
                        className="flex items-center space-x-3"
                        initial={{ opacity: 0, x: -10 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.5, delay: index * 0.1 }}
                        viewport={{ once: true }}
                      >
                        <div className="w-5 h-5 rounded-full bg-gradient-to-r from-yellow-500/20 to-orange-500/20 flex items-center justify-center flex-shrink-0">
                          <Crown className="h-3 w-3 text-yellow-600" />
                        </div>
                        <span className="text-sm">{feature}</span>
                      </motion.div>
                    ))}
                  </div>

                  <Button size="lg" variant="outline" className="w-full" disabled>
                    Coming Soon
                  </Button>

                  <div className="mt-4 text-center">
                    <p className="text-xs text-muted-foreground">
                      Get notified when premium features launch
                    </p>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* Value Proposition */}
          <motion.div
            className="mt-12 text-center"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            viewport={{ once: true }}
          >
            <Card className="max-w-2xl mx-auto p-6 bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-950/20 dark:to-blue-950/20 border-green-200 dark:border-green-800">
              <CardContent className="p-0 text-center">
                <div className="text-4xl mb-3">💡</div>
                <h3 className="text-xl font-bold mb-2">Why Start with Beta?</h3>
                <p className="text-muted-foreground mb-4">
                  Shape the future of AI mental health companions while getting full access for free
                </p>
                <div className="grid md:grid-cols-3 gap-4 text-sm">
                  <div className="flex flex-col items-center">
                    <div className="w-8 h-8 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mb-2">
                      <Check className="h-4 w-4 text-green-600" />
                    </div>
                    <span>Your feedback matters</span>
                  </div>
                  <div className="flex flex-col items-center">
                    <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center mb-2">
                      <Zap className="h-4 w-4 text-blue-600" />
                    </div>
                    <span>Early access benefits</span>
                  </div>
                  <div className="flex flex-col items-center">
                    <div className="w-8 h-8 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center mb-2">
                      <Crown className="h-4 w-4 text-purple-600" />
                    </div>
                    <span>Lifetime beta perks</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
