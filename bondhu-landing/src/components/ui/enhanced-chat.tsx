"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Mic, MoreVertical, Heart, Sparkles, Volume2, VolumeX, Copy, ThumbsUp, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { GlowingEffect } from "@/components/ui/glowing-effect";
import { BondhuAvatar } from "@/components/ui/bondhu-avatar";
import { cn } from "@/lib/utils";
import { useChat, useChatSession } from "@/hooks/use-chat";
import type { Profile } from "@/types/auth";
import type { ChatMessage } from "@/lib/api-client";

interface Message {
  id?: string;
  sender_type: 'user' | 'ai';
  message_text: string;
  timestamp?: string;
  isTyping?: boolean;
  reactions?: string[];
  mood?: 'happy' | 'caring' | 'thinking' | 'excited';
}

interface EnhancedChatProps {
  profile: Profile;
}

export function EnhancedChat({ profile }: EnhancedChatProps) {
  const { sessionId } = useChatSession();
  const { messages, isLoading, error, sendMessage, clearMessages } = useChat({
    userId: profile.id,
    sessionId
  });

  const [newMessage, setNewMessage] = useState('');
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(false);
  const [conversationContext, setConversationContext] = useState<string[]>([
    "mental wellness", "daily goals", "stress management"
  ]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Add welcome message if no messages exist
  const displayMessages = messages.length === 0 ? [
    {
      id: 'welcome',
      sender_type: 'ai' as const,
      message_text: `Hello ${profile.full_name?.split(' ')[0] || 'Friend'}! 🌟 I'm Bondhu, your AI companion. I've been looking forward to continuing our conversation. How are you feeling today?`,
      timestamp: new Date().toISOString(),
    }
  ] : messages;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!newMessage.trim() || isLoading) return;

    const messageText = newMessage.trim();
    setNewMessage('');

    // Add context from conversation keywords
    const context = {
      conversation_context: conversationContext,
      user_name: profile.full_name?.split(' ')[0] || 'Friend'
    };

    try {
      await sendMessage(messageText, context);
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  };

  // Personality-adaptive quick responses
  const getQuickMessages = () => {
    const baseMessages = [
      { text: "How are you feeling today?", emoji: "💭", traits: ["all"] },
      { text: "I need some motivation", emoji: "✨", traits: ["low_extraversion", "neuroticism"] },
      { text: "Let's explore something creative", emoji: "🎨", traits: ["openness"] },
      { text: "Help me stay organized", emoji: "📋", traits: ["conscientiousness"] },
      { text: "I want to connect with others", emoji: "🤝", traits: ["extraversion"] },
      { text: "Let's work on my goals", emoji: "🎯", traits: ["conscientiousness"] },
      { text: "I'm feeling anxious", emoji: "🫂", traits: ["neuroticism"] },
      { text: "Tell me something positive", emoji: "🌟", traits: ["all"] },
      { text: "Help me relax", emoji: "🌊", traits: ["neuroticism"] }
    ];

    // In a real implementation, you'd analyze the user's personality profile
    // For now, we'll show a mix of responses
    return baseMessages.slice(0, 6);
  };

  const quickMessages = getQuickMessages();

  const handleQuickMessage = (message: string) => {
    setNewMessage(message);
    inputRef.current?.focus();
  };

  const copyMessage = (message: string) => {
    navigator.clipboard.writeText(message);
  };

  const addReaction = (messageId: number, reaction: string) => {
    setMessages(prev => prev.map(msg => 
      msg.id === messageId 
        ? { ...msg, reactions: [...(msg.reactions || []), reaction] }
        : msg
    ));
  };

  const reactionEmojis = ['👍', '❤️', '😊', '🤗', '✨', '🎉'];

  return (
    <div className="w-full">
      <div className="relative rounded-[1.25rem] border-[0.75px] border-border p-3">
        <GlowingEffect
          spread={35}
          glow={true}
          disabled={false}
          proximity={100}
          inactiveZone={0.1}
          borderWidth={2}
        />
        <Card className="relative border-[0.75px] bg-card backdrop-blur-sm shadow-lg">
          {/* Chat Header */}
          <CardHeader className="border-b bg-gradient-to-r from-primary/5 to-primary/8 dark:from-primary/10 dark:to-primary/15 rounded-t-xl p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <BondhuAvatar 
                  size="md" 
                  isTyping={isLoading}
                  mood="caring"
                  showAnimation={true}
                />
                <div>
                  <h3 className="text-lg font-semibold flex items-center space-x-2">
                    <span>Bondhu AI Companion</span>
                    <Sparkles className="h-4 w-4 text-primary" />
                  </h3>
                  <p className="text-sm text-muted-foreground flex items-center space-x-2">
                    <span className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                    <span>Always here for you</span>
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsVoiceEnabled(!isVoiceEnabled)}
                  className="h-8 w-8 p-0"
                >
                  {isVoiceEnabled ? 
                    <Volume2 className="h-4 w-4 text-emerald-500" /> : 
                    <VolumeX className="h-4 w-4 text-muted-foreground" />
                  }
                </Button>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardHeader>

          {/* Conversation Context */}
          {conversationContext.length > 0 && (
            <div className="px-6 py-3 border-b bg-primary/3 text-center">
              <p className="text-xs text-muted-foreground mb-2">Continuing our conversation about:</p>
              <div className="flex flex-wrap justify-center gap-1">
                {conversationContext.map((context, index) => (
                  <span key={index} className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">
                    {context}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Messages Area */}
          <CardContent className="p-0">
            <div className="h-[50vh] max-h-[500px] min-h-[400px] overflow-y-auto p-6 space-y-6 scroll-smooth">
              {error && (
                <div className="flex items-center space-x-2 p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
                  <AlertCircle className="h-4 w-4 text-destructive" />
                  <p className="text-sm text-destructive">{error}</p>
                </div>
              )}
              
              {displayMessages.map((msg) => (
                <div
                  key={msg.id || `${msg.sender_type}-${msg.timestamp}`}
                  className={`flex ${msg.sender_type === 'user' ? 'justify-end' : 'justify-start'} group`}
                >
                  <div
                    className={cn(
                      "max-w-xs lg:max-w-md relative",
                      msg.sender_type === 'user' ? 'order-2' : 'order-1'
                    )}
                  >
                    {msg.sender_type === 'ai' && (
                      <div className="flex items-center space-x-2 mb-3">
                        <BondhuAvatar 
                          size="sm" 
                          isTyping={false}
                          mood="happy"
                          showAnimation={false}
                        />
                        <span className="text-xs text-muted-foreground font-medium">Bondhu</span>
                      </div>
                    )}
                    
                    <div
                      className={cn(
                        "px-4 py-3 relative group/message max-w-[85%] transition-all duration-200",
                        msg.sender_type === 'user'
                          ? 'bg-gradient-to-br from-primary to-primary/90 text-primary-foreground ml-4 rounded-[1.25rem] rounded-br-md shadow-lg shadow-primary/20'
                          : 'bg-muted mr-4 border border-border/50 rounded-[1.25rem] rounded-bl-md shadow-md shadow-muted-foreground/5'
                      )}
                    >
                      <p className="text-sm leading-[1.5]">{msg.message_text}</p>
                      <div className="flex items-center justify-between mt-2">
                        <p className={cn(
                          "text-xs",
                          msg.sender_type === 'user' ? "text-primary-foreground/70" : "text-muted-foreground"
                        )}>
                          {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString() : new Date().toLocaleTimeString()}
                        </p>
                        
                        {msg.sender_type === 'ai' && (
                          <div className="flex items-center space-x-1 opacity-0 group-hover/message:opacity-100 transition-opacity">
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-6 w-6 p-0 hover:bg-background/80"
                              onClick={() => copyMessage(msg.message_text)}
                            >
                              <Copy className="h-3 w-3" />
                            </Button>
                            <div className="flex items-center space-x-1">
                              {reactionEmojis.slice(0, 3).map((emoji) => (
                                <Button
                                  key={emoji}
                                  variant="ghost"
                                  size="sm"
                                  className="h-6 w-6 p-0 hover:bg-background/80 text-xs"
                                  onClick={() => addReaction(msg.id, emoji)}
                                >
                                  {emoji}
                                </Button>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                      
                      {/* Reactions Display */}
                      {msg.reactions && msg.reactions.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1 ml-1">
                          {Array.from(new Set(msg.reactions)).map((reaction, index) => {
                            const count = msg.reactions!.filter(r => r === reaction).length;
                            return (
                              <div
                                key={index}
                                className="flex items-center space-x-1 bg-primary/10 border border-primary/20 rounded-full px-2 py-1 text-xs"
                              >
                                <span>{reaction}</span>
                                {count > 1 && <span className="text-primary font-medium">{count}</span>}
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="flex justify-start group animate-fade-in">
                  <div className="max-w-xs lg:max-w-md relative order-1">
                    <div className="flex items-center space-x-2 mb-3">
                      <BondhuAvatar 
                        size="sm" 
                        isTyping={true}
                        mood="thinking"
                        showAnimation={true}
                      />
                      <span className="text-xs text-muted-foreground font-medium">Bondhu is thinking...</span>
                    </div>
                    <div className="bg-muted mr-4 border border-border/50 rounded-[1.25rem] rounded-bl-md shadow-md shadow-muted-foreground/5 px-4 py-3">
                      <div className="flex items-center space-x-2">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce" />
                          <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                          <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                        </div>
                        <span className="text-xs text-muted-foreground/70 animate-pulse">crafting a thoughtful response</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Quick Messages */}
            <div className="px-6 py-4 border-t bg-gradient-to-r from-primary/2 to-primary/5">
              <p className="text-xs font-medium text-muted-foreground mb-3">Quick responses:</p>
              <div className="flex flex-wrap gap-2">
                {quickMessages.map((quick, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    className="h-8 text-xs hover:bg-primary/10 hover:border-primary/30 transition-colors px-3 py-1"
                    onClick={() => handleQuickMessage(quick.text)}
                  >
                    <span className="mr-1">{quick.emoji}</span>
                    {quick.text}
                  </Button>
                ))}
              </div>
            </div>

            {/* Input Area */}
            <div className="p-6 border-t bg-gradient-to-r from-primary/3 to-primary/6 rounded-b-xl">
              <div className="flex space-x-3">
                <div className="flex-1 relative">
                  <Input
                    ref={inputRef}
                    placeholder="Share your thoughts with Bondhu..."
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    className="pr-12 h-14 bg-card border-border focus:border-primary focus:ring-2 focus:ring-primary/20 rounded-xl text-base"
                    disabled={isLoading}
                  />
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center space-x-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-10 w-10 p-0 hover:bg-primary/10"
                    >
                      <Mic className="h-5 w-5 text-muted-foreground hover:text-primary" />
                    </Button>
                  </div>
                </div>
                <Button 
                  onClick={handleSendMessage} 
                  disabled={!newMessage.trim() || isLoading}
                  className="h-14 w-14 p-0 bg-gradient-to-br from-primary to-primary/90 hover:from-primary/90 hover:to-primary/80 shadow-lg transition-all duration-200"
                >
                  {isLoading ? (
                    <div className="animate-spin h-6 w-6 border-2 border-white border-t-transparent rounded-full" />
                  ) : (
                    <Send className="h-6 w-6" />
                  )}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
