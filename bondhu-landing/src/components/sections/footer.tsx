"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { Heart, Mail, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Separator } from "@/components/ui/separator"
import { Logo } from "@/components/logo"

export function Footer() {
  const productLinks = [
    { name: "Features", href: "#features" },
    { name: "Demo", href: "#demo" },
    { name: "Pricing", href: "#pricing" },
    { name: "Roadmap", href: "#roadmap" },
  ]

  const companyLinks = [
    { name: "About", href: "#about" },
    { name: "Careers", href: "#careers" },
    { name: "Contact", href: "#contact" },
    { name: "Press", href: "#press" },
  ]

  const resourceLinks = [
    { name: "Blog", href: "#blog" },
    { name: "Help Center", href: "#help" },
    { name: "Community", href: "#community" },
    { name: "Privacy Policy", href: "#privacy" },
  ]

  const socialLinks = [
    { name: "Twitter", href: "https://twitter.com" },
    { name: "Instagram", href: "https://instagram.com" },
    { name: "LinkedIn", href: "https://linkedin.com" },
    { name: "Discord", href: "https://discord.com" },
  ]

  return (
    <footer className="bg-secondary py-16">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-8">
          {/* Logo & Description */}
          <motion.div
            className="lg:col-span-2"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <div className="mb-4">
              <Logo width={120} height={40} />
            </div>
            <p className="text-muted-foreground mb-6 max-w-sm">
              Your AI companion for mental wellness. Designed for Gen Z, built with empathy, 
              powered by advanced AI technology.
            </p>
            
            {/* Newsletter Signup */}
            <div className="mb-6">
              <h4 className="font-semibold mb-3">Stay Updated</h4>
              <div className="flex space-x-2">
                <Input 
                  placeholder="Enter your email" 
                  className="flex-1"
                  type="email"
                />
                <Button size="sm">
                  <Mail className="h-4 w-4 mr-1" />
                  Subscribe
                </Button>
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                Get the latest updates on new features and mental health resources.
              </p>
            </div>
          </motion.div>

          {/* Product Links */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.1 }}
            viewport={{ once: true }}
          >
            <h4 className="font-semibold mb-4">Product</h4>
            <ul className="space-y-2">
              {productLinks.map((link) => (
                <li key={link.name}>
                  <Link 
                    href={link.href}
                    className="text-muted-foreground hover:text-foreground transition-colors text-sm"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </motion.div>

          {/* Company Links */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            viewport={{ once: true }}
          >
            <h4 className="font-semibold mb-4">Company</h4>
            <ul className="space-y-2">
              {companyLinks.map((link) => (
                <li key={link.name}>
                  <Link 
                    href={link.href}
                    className="text-muted-foreground hover:text-foreground transition-colors text-sm"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </motion.div>

          {/* Resources & Connect */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            viewport={{ once: true }}
          >
            <h4 className="font-semibold mb-4">Resources</h4>
            <ul className="space-y-2 mb-6">
              {resourceLinks.map((link) => (
                <li key={link.name}>
                  <Link 
                    href={link.href}
                    className="text-muted-foreground hover:text-foreground transition-colors text-sm"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>

            <h4 className="font-semibold mb-4">Connect</h4>
            <ul className="space-y-2">
              {socialLinks.map((link) => (
                <li key={link.name}>
                  <Link 
                    href={link.href}
                    className="text-muted-foreground hover:text-foreground transition-colors text-sm inline-flex items-center"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {link.name}
                    <ArrowRight className="h-3 w-3 ml-1" />
                  </Link>
                </li>
              ))}
            </ul>
          </motion.div>
        </div>

        <Separator className="my-8" />

        {/* Bottom Footer */}
        <motion.div
          className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          viewport={{ once: true }}
        >
          <div className="flex items-center space-x-4 text-sm text-muted-foreground">
            <span>© 2025 Bondhu. All rights reserved.</span>
            <span className="hidden md:inline">•</span>
            <span className="flex items-center">
              Made with <Heart className="h-4 w-4 mx-1 text-red-500" /> for Gen Z mental health
            </span>
          </div>

          <div className="flex items-center space-x-4 text-sm">
            <Link href="#terms" className="text-muted-foreground hover:text-foreground transition-colors">
              Terms
            </Link>
            <Link href="#privacy" className="text-muted-foreground hover:text-foreground transition-colors">
              Privacy
            </Link>
            <Link href="#cookies" className="text-muted-foreground hover:text-foreground transition-colors">
              Cookies
            </Link>
          </div>
        </motion.div>

        {/* Final CTA */}
        <motion.div
          className="mt-8 text-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          viewport={{ once: true }}
        >
          <div className="inline-flex items-center space-x-2 text-sm text-muted-foreground">
            <span>Ready to meet your digital বন্ধু?</span>
            <Button size="sm" variant="outline" asChild>
              <Link href="#demo">Start Chatting</Link>
            </Button>
          </div>
        </motion.div>
      </div>
    </footer>
  )
}
