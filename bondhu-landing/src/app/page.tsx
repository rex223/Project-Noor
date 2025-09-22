import { Navigation } from "@/components/sections/navigation"
import { HeroSection } from "@/components/sections/hero-section"
import { ProblemSection } from "@/components/sections/problem-section"
import { SolutionSection } from "@/components/sections/solution-section"
import { InteractiveDemo } from "@/components/sections/interactive-demo"
import { FeaturesSection } from "@/components/sections/features-section"
import { SocialProof } from "@/components/sections/social-proof"
import { PricingSection } from "@/components/sections/pricing-section"
import { Footer } from "@/components/sections/footer"
import { FloatingCTA } from "@/components/floating-cta"

export default function Home() {
  return (
    <div className="min-h-screen">
      <Navigation />
      <main>
        <HeroSection />
        <ProblemSection />
        <SolutionSection />
        <InteractiveDemo />
        <FeaturesSection />
        <SocialProof />
        <PricingSection />
      </main>
      <Footer />
      <FloatingCTA />
    </div>
  )
}
