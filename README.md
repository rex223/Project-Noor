# Bondhu - AI Mental Health Companion Landing Page

A modern, responsive landing page built with Next.js 15, TypeScript, and shadcn/ui for Bondhu, an AI mental health companion designed for Gen Z.

## 🌟 Features

- **Modern Design**: Clean, responsive design with dark/light theme support
- **Interactive Elements**: Animated chat demo, floating CTA, and smooth scrolling
- **Accessibility**: WCAG 2.1 AA compliant with proper ARIA labels and keyboard navigation
- **Performance**: Optimized for Core Web Vitals with Next.js Image optimization
- **Animations**: Subtle Framer Motion animations for enhanced user experience
- **Bengali Support**: Includes Bengali script "বন্ধু" (friend) throughout the design

## 🚀 Tech Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Font**: Inter from Google Fonts
- **Theme**: next-themes for dark/light mode

## 📱 Sections

1. **Navigation** - Sticky header with theme toggle and mobile menu
2. **Hero Section** - Animated background with Bengali elements and CTAs
3. **Problem Section** - Statistics and pain points about Gen Z mental health
4. **Solution Section** - How Bondhu works in 3 steps
5. **Interactive Demo** - Live chat interface preview
6. **Features Section** - 6 key features with benefits
7. **Social Proof** - Testimonials and usage statistics
8. **Pricing Section** - Free beta and upcoming premium tiers
9. **Footer** - Links, newsletter signup, and social media

## 🛠️ Setup Instructions

### Prerequisites

- Node.js 18+ and npm
- Git

### Installation

1. **Clone and navigate to the project**:
   ```bash
   cd bondhu-landing
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Run the development server**:
   ```bash
   npm run dev
   ```

4. **Open your browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

### Build for Production

```bash
npm run build
npm start
```

## 📁 Project Structure

```
bondhu-landing/
├── src/
│   ├── app/
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── ui/                  # shadcn/ui components
│   │   ├── sections/            # Landing page sections
│   │   │   ├── navigation.tsx
│   │   │   ├── hero-section.tsx
│   │   │   ├── problem-section.tsx
│   │   │   ├── solution-section.tsx
│   │   │   ├── interactive-demo.tsx
│   │   │   ├── features-section.tsx
│   │   │   ├── social-proof.tsx
│   │   │   ├── pricing-section.tsx
│   │   │   └── footer.tsx
│   │   ├── floating-cta.tsx
│   │   ├── theme-provider.tsx
│   │   └── theme-toggle.tsx
│   └── lib/
│       └── utils.ts
├── components.json
├── tailwind.config.ts
└── README.md
```

## 🎨 Design System

### Colors
- **Light Mode**: Clean whites with blue primary (#3b82f6)
- **Dark Mode**: Dark grays with lighter blue primary (#60a5fa)
- **Secondary**: Subtle grays for backgrounds and muted text

### Typography
- **Font**: Inter for excellent readability
- **Headings**: Bold, tracking-tight for impact
- **Body**: Comfortable line height and spacing

### Components
- Consistent border radius (0.625rem)
- Subtle shadows and hover effects
- Smooth transitions (300ms duration)
- Accessible color contrast ratios

## 🔧 Customization

### Theme Colors
Edit the CSS variables in `src/app/globals.css` to customize colors:

```css
:root {
  --primary: your-color;
  --secondary: your-color;
  /* ... */
}
```

### Content
Update the content in each section component:
- Hero messaging in `hero-section.tsx`
- Features in `features-section.tsx`
- Testimonials in `social-proof.tsx`
- Pricing in `pricing-section.tsx`

### Animations
Modify Framer Motion animations in each component or disable them by removing the motion components.

## 📱 Responsive Design

- **Mobile**: Single column, touch-friendly buttons, simplified navigation
- **Tablet**: Two-column layouts, condensed sections
- **Desktop**: Full multi-column layouts, hover states, optimal typography

## ♿ Accessibility

- Semantic HTML structure
- ARIA labels for interactive elements
- Keyboard navigation support
- High contrast color schemes
- Screen reader friendly
- Focus indicators

## 🚀 Performance

- Next.js Image optimization
- Tree-shaking for unused code
- CSS optimization with Tailwind
- Lazy loading for animations
- Minimal JavaScript bundle

## 🔗 Key Features

### Interactive Elements
- **Theme Toggle**: Smooth light/dark mode switching
- **Chat Demo**: Animated typing indicators and message flow
- **Floating CTA**: Appears on scroll with pulse animation
- **Hover Effects**: Scale and glow on cards and buttons

### Bengali Integration
- Bengali script "বন্ধু" (friend) featured prominently
- Cultural sensitivity in design choices
- Localized for Indian Gen Z audience

### Mental Health Focus
- Empathetic copy and messaging
- Statistics from Indian mental health research
- Gen Z-focused pain points and solutions
- Community and support emphasis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is created for Bondhu AI Mental Health Companion. All rights reserved.

## 🙏 Acknowledgments

- **shadcn/ui** for beautiful, accessible components
- **Framer Motion** for smooth animations
- **Lucide** for consistent iconography
- **Next.js** team for the excellent framework
- **Tailwind CSS** for utility-first styling

---

**Made with ❤️ for Gen Z mental health**

For questions or support, please contact the Bondhu team.