"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Card, CardContent } from "@/components/ui/card"
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog"
import Link from "next/link"

export function InteractiveDemo() {
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)

  const messages = [
    {
      sender: "bondhu",
      avatar: "বন্ধু",
      message: "Hey! I noticed you seemed quiet today. Want to talk about what's on your mind? 🌱",
      timestamp: "2:34 PM",
    },
    {
      sender: "user",
      message: "Just feeling overwhelmed with studies and social pressure...",
      timestamp: "2:35 PM",
    },
    {
      sender: "bondhu",
      avatar: "বন্ধু",
      message: "I understand that feeling completely. Let's break this down together - what specific part feels most overwhelming right now? Sometimes naming it makes it less scary.",
      timestamp: "2:35 PM",
    },
    {
      sender: "typing",
      message: "Bondhu is typing...",
      animated: true,
    },
  ]

  useEffect(() => {
    if (isPlaying && currentMessageIndex < messages.length - 1) {
      const timer = setTimeout(() => {
        setCurrentMessageIndex(prev => prev + 1)
      }, 2000)
      return () => clearTimeout(timer)
    }
  }, [currentMessageIndex, isPlaying, messages.length])

  const resetDemo = () => {
    setCurrentMessageIndex(0)
    setIsPlaying(true)
  }

  interface Message {
    sender: string;
    avatar?: string;
    message: string;
    timestamp?: string;
    animated?: boolean;
  }

  const ChatMessage = ({ message }: { message: Message; index: number }) => {
    const isUser = message.sender === "user"
    const isTyping = message.sender === "typing"

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}
      >
        <div className={`flex items-start max-w-[80%] ${isUser ? "flex-row-reverse" : "flex-row"}`}>
          {!isUser && (
            <Avatar className="w-8 h-8 mr-2">
              <AvatarImage
                src="/Light mode logo.svg"
                alt="Bondhu"
                className="object-contain p-1"
              />
              <AvatarFallback className="text-xs bg-primary/10 text-primary">
                {message.avatar || "B"}
              </AvatarFallback>
            </Avatar>
          )}

          <div className={`rounded-2xl px-4 py-2 ${isUser
              ? "bg-primary text-primary-foreground"
              : isTyping
                ? "bg-muted"
                : "bg-secondary"
            }`}>
            {isTyping ? (
              <div className="flex space-x-1">
                {[0, 1, 2].map((i) => (
                  <motion.div
                    key={i}
                    className="w-2 h-2 bg-muted-foreground rounded-full"
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{
                      duration: 0.8,
                      repeat: Infinity,
                      delay: i * 0.2,
                    }}
                  />
                ))}
              </div>
            ) : (
              <p className="text-sm">{message.message}</p>
            )}

            {message.timestamp && (
              <p className={`text-xs mt-1 ${isUser ? "text-primary-foreground/70" : "text-muted-foreground"}`}>
                {message.timestamp}
              </p>
            )}
          </div>
        </div>
      </motion.div>
    )
  }

  return (
    <section id="demo" className="py-20 bg-secondary/10">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            See Bondhu in Action
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Experience a real conversation with your AI companion
          </p>
        </motion.div>

        <div className="max-w-4xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Chat Interface */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
            >
              <Card className="h-[400px] flex flex-col">
                {/* Chat Header */}
                <div className="border-b p-4 flex items-center space-x-3">
                  <Avatar className="w-10 h-10">
                    <AvatarImage
                      src="/Light mode logo.svg"
                      alt="Bondhu"
                      className="object-contain p-1"
                    />
                    <AvatarFallback className="bg-primary/10 text-primary">
                      বন্ধু
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <h3 className="font-semibold">Bondhu</h3>
                    <p className="text-sm text-muted-foreground">Your AI companion</p>
                  </div>
                  <div className="ml-auto">
                    <div className="flex items-center space-x-1">
                      <div className="w-2 h-2 bg-green-500 rounded-full" />
                      <span className="text-xs text-muted-foreground">Online</span>
                    </div>
                  </div>
                </div>

                {/* Chat Messages */}
                <CardContent className="flex-1 overflow-y-auto p-4">
                  <AnimatePresence>
                    {messages.slice(0, currentMessageIndex + 1).map((message, index) => (
                      <ChatMessage key={index} message={message} index={index} />
                    ))}
                  </AnimatePresence>
                </CardContent>

                {/* Demo Controls */}
                <div className="border-t p-4">
                  <Button
                    onClick={resetDemo}
                    className="w-full"
                    disabled={isPlaying && currentMessageIndex < messages.length - 1}
                  >
                    {isPlaying && currentMessageIndex < messages.length - 1 ? "Playing..." : "Replay Demo"}
                  </Button>
                </div>
              </Card>
            </motion.div>

            {/* Demo Features */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              viewport={{ once: true }}
            >
              <div className="space-y-6">
                <div>
                  <h3 className="text-2xl font-bold mb-4">What You Just Saw</h3>
                  <div className="space-y-4">
                    <div className="flex items-start space-x-3">
                      <div className="w-2 h-2 bg-primary rounded-full mt-2" />
                      <div>
                        <p className="font-medium">Proactive Check-ins</p>
                        <p className="text-sm text-muted-foreground">Bondhu notices patterns and reaches out when you need support</p>
                      </div>
                    </div>
                    <div className="flex items-start space-x-3">
                      <div className="w-2 h-2 bg-primary rounded-full mt-2" />
                      <div>
                        <p className="font-medium">Empathetic Responses</p>
                        <p className="text-sm text-muted-foreground">Understands emotional context and responds with genuine care</p>
                      </div>
                    </div>
                    <div className="flex items-start space-x-3">
                      <div className="w-2 h-2 bg-primary rounded-full mt-2" />
                      <div>
                        <p className="font-medium">Solution-Oriented</p>
                        <p className="text-sm text-muted-foreground">Helps break down problems into manageable steps</p>
                      </div>
                    </div>
                  </div>
                </div>

                <Button size="lg" className="w-full" asChild>
                  <Link href="/sign-up">
                    Try a Full Conversation
                  </Link>
                </Button>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  )
}
