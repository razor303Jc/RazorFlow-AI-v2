import React, { useState, useEffect } from 'react'
import { Bot, DollarSign, TrendingUp, Calendar, BarChart3, Users, Clock, 
         Code, Palette, Cloud, Zap, MessageSquare, Briefcase, Star, 
         CheckCircle, ArrowRight, Globe, Database, Cpu, Settings, Shield, Award } from 'lucide-react'
import './App.css'
import Dashboard from './components/Dashboard'
import Chat from './components/Chat'
import PerformanceMonitor from './components/PerformanceMonitor'

const API_BASE = 'http://localhost:8000'

function App() {
  const [activeSection, setActiveSection] = useState('portfolio')
  const [activeBot, setActiveBot] = useState('finance')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [portfolioStats, setPortfolioStats] = useState(null)
  const [isVisible, setIsVisible] = useState({})

  // Inject Bootstrap CSS and styles directly
  useEffect(() => {
    // Create and inject Bootstrap CSS
    const bootstrapLink = document.createElement('link')
    bootstrapLink.rel = 'stylesheet'
    bootstrapLink.href = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css'
    bootstrapLink.integrity = 'sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN'
    bootstrapLink.crossOrigin = 'anonymous'
    document.head.appendChild(bootstrapLink)

    // Create and inject Bootstrap Icons
    const iconsLink = document.createElement('link')
    iconsLink.rel = 'stylesheet'
    iconsLink.href = 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css'
    document.head.appendChild(iconsLink)

    // Create and inject Google Fonts
    const fontsLink = document.createElement('link')
    fontsLink.rel = 'stylesheet'
    fontsLink.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap'
    document.head.appendChild(fontsLink)

    // Inject custom CSS
    const style = document.createElement('style')
    style.textContent = `
      body {
        font-family: 'Inter', sans-serif !important;
        background: #0f1419 !important;
        color: #e2e8f0 !important;
        background-image: 
          radial-gradient(at 20% 50%, hsla(240, 50%, 20%, 0.3) 0px, transparent 50%),
          radial-gradient(at 80% 20%, hsla(260, 50%, 25%, 0.3) 0px, transparent 50%) !important;
      }
      
      .glass-card {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 1rem !important;
      }
      
      .btn-gradient {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        border: none !important;
        color: white !important;
      }
      
      .btn-gradient:hover {
        background: linear-gradient(135deg, #5a6fd8, #6b4190) !important;
        color: white !important;
        transform: translateY(-2px) !important;
      }
      
      .navbar-custom {
        background: rgba(15, 20, 25, 0.95) !important;
        backdrop-filter: blur(20px) !important;
      }
      
      .text-primary-gradient {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
      }
    `
    document.head.appendChild(style)

    // Load Bootstrap JS
    const script = document.createElement('script')
    script.src = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js'
    script.integrity = 'sha384-C6RzsynM9kWDrMNeT87bh95OGNyZPhcTNXj1NW7RuBCsyN/o0jlpcV8Qyq46cDfL'
    script.crossOrigin = 'anonymous'
    document.body.appendChild(script)
  }, [])

  useEffect(() => {
    if (activeSection === 'demos') {
      fetchBotData(activeBot)
    } else if (activeSection === 'portfolio') {
      fetchPortfolioStats()
    }
  }, [activeBot, activeSection])

  // Intersection Observer for animations
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsVisible(prev => ({ ...prev, [entry.target.id]: true }))
          }
        })
      },
      { threshold: 0.1 }
    )

    document.querySelectorAll('[id]').forEach((el) => {
      observer.observe(el)
    })

    return () => observer.disconnect()
  }, [])

  const fetchBotData = async (botType) => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE}/api/${botType}`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const result = await response.json()
      setData(result)
    } catch (error) {
      console.error('Error fetching data:', error)
      setError('Error loading data. Please try again.')
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  const fetchPortfolioStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/portfolio/stats`)
      if (response.ok) {
        const stats = await response.json()
        setPortfolioStats(stats)
      }
    } catch (error) {
      console.error('Error fetching portfolio stats:', error)
    }
  }

  const navigationItems = [
    { id: 'portfolio', name: 'Portfolio', icon: Briefcase },
    { id: 'demos', name: 'Live Demos', icon: Bot },
    { id: 'services', name: 'Services', icon: Settings },
    { id: 'pipeline', name: 'AI Pipeline', icon: Zap }
  ]

  const services = [
    {
      icon: MessageSquare,
      title: 'AI Chatbots & Assistants',
      description: 'Custom AI chatbots for customer service, sales, and support with enterprise-grade capabilities',
      features: ['24/7 Customer Support', 'Multi-language Support', 'Integration Ready', 'Custom Training'],
      color: 'primary',
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    },
    {
      icon: Calendar,
      title: 'Automated Booking System',
      description: 'Smart scheduling and appointment management with AI-powered optimization',
      features: ['Smart Scheduling', 'Calendar Integration', 'Automated Reminders', 'Payment Processing'],
      color: 'success',
      gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
    },
    {
      icon: Palette,
      title: 'Design & Development',
      description: 'Full-stack AI application design and development from concept to deployment',
      features: ['UI/UX Design', 'Frontend Development', 'Backend API', 'Database Design'],
      color: 'info',
      gradient: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)'
    },
    {
      icon: Cloud,
      title: 'Hosting & Deployment',
      description: 'Scalable cloud hosting and deployment solutions with enterprise reliability',
      features: ['Docker Containers', 'Cloud Deployment', 'CI/CD Pipeline', 'Monitoring & Logs'],
      color: 'warning',
      gradient: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)'
    },
    {
      icon: Database,
      title: 'AI System Integration',
      description: 'Seamless integration of AI into existing systems with minimal disruption',
      features: ['API Integration', 'Data Migration', 'System Architecture', 'Performance Optimization'],
      color: 'secondary',
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    },
    {
      icon: Cpu,
      title: 'AI Pipeline Automation',
      description: 'End-to-end AI workflow automation and management for scalable operations',
      features: ['Data Processing', 'Model Training', 'Deployment Pipeline', 'Monitoring & Analytics'],
      color: 'danger',
      gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
    }
  ]

  const bots = [
    { id: 'finance', name: 'Finance Bot', icon: DollarSign, color: 'success', description: 'Financial analysis and insights' },
    { id: 'sales', name: 'Sales Bot', icon: TrendingUp, color: 'primary', description: 'Sales optimization and leads' },
    { id: 'scheduler', name: 'Scheduler Bot', icon: Calendar, color: 'info', description: 'Smart scheduling assistant' }
  ]

  const defaultStats = [
    { label: 'AI Projects Completed', value: '150+', icon: CheckCircle, color: 'success' },
    { label: 'Active AI Systems', value: '45+', icon: Bot, color: 'primary' },
    { label: 'Client Satisfaction', value: '99%', icon: Star, color: 'warning' },
    { label: 'Uptime Guarantee', value: '99.9%', icon: Globe, color: 'info' }
  ]

  const statsToShow = portfolioStats ? [
    { label: 'AI Projects Completed', value: `${portfolioStats.projects_completed}+`, icon: CheckCircle, color: 'success' },
    { label: 'Active AI Systems', value: `${portfolioStats.active_systems}+`, icon: Bot, color: 'primary' },
    { label: 'Client Satisfaction', value: `${portfolioStats.client_satisfaction}%`, icon: Star, color: 'warning' },
    { label: 'Uptime Guarantee', value: `${portfolioStats.uptime_guarantee}%`, icon: Globe, color: 'info' }
  ] : defaultStats

  return (
    <div className="min-h-screen">
      {/* Bootstrap Navbar */}
      <nav className="navbar navbar-expand-lg navbar-dark navbar-custom fixed-top">
        <div className="container-xl">
          <a className="navbar-brand d-flex align-items-center" href="#portfolio">
            <Bot size={32} className="text-primary me-3" />
            <div>
              <h4 className="mb-0 gradient-text">RazorFlow AI</h4>
              <small className="text-muted">Professional AI Solutions</small>
            </div>
          </a>
          
          <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span className="navbar-toggler-icon"></span>
          </button>
          
          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="navbar-nav ms-auto me-4">
              {navigationItems.map((item) => {
                const Icon = item.icon
                return (
                  <li key={item.id} className="nav-item">
                    <button
                      onClick={() => setActiveSection(item.id)}
                      className={`nav-link btn btn-link d-flex align-items-center ${
                        activeSection === item.id ? 'active text-primary' : 'text-light'
                      }`}
                    >
                      <Icon size={16} className="me-2" />
                      {item.name}
                    </button>
                  </li>
                )
              })}
            </ul>
            
            <div className="d-flex align-items-center">
              <span className="badge bg-success me-2">v2.0.0</span>
              <span className="badge bg-primary pulse">Live</span>
            </div>
          </div>
        </div>
      </nav>

      <main>
        {/* Portfolio Section */}
        {activeSection === 'portfolio' && (
          <>
            {/* Hero Section */}
            <section className="hero-section" id="hero">
              <div className="container-xl">
                <div className="row align-items-center min-vh-100">
                  <div className="col-lg-6" data-aos="fade-right">
                    <div className="floating-element">
                      <h1 className="display-2 fw-bold mb-4">
                        Professional 
                        <span className="gradient-text d-block">AI Solutions</span>
                      </h1>
                      <p className="lead mb-5 text-light">
                        Specializing in AI chatbots, automated systems, and complete AI integration pipelines. 
                        From design to deployment, I deliver cutting-edge AI solutions that transform businesses.
                      </p>
                      <div className="d-flex flex-column flex-sm-row gap-3">
                        <button 
                          onClick={() => setActiveSection('demos')}
                          className="btn btn-gradient btn-lg px-4 py-3"
                        >
                          <MessageSquare size={20} className="me-2" />
                          View Live Demos
                          <ArrowRight size={20} className="ms-2" />
                        </button>
                        <button 
                          onClick={() => setActiveSection('services')}
                          className="btn btn-outline-light btn-lg px-4 py-3"
                        >
                          <Settings size={20} className="me-2" />
                          Explore Services
                        </button>
                      </div>
                    </div>
                  </div>
                  
                  <div className="col-lg-6" data-aos="fade-left" data-aos-delay="200">
                    <div className="text-center">
                      <div className="glass-card p-5 floating-element">
                        <Bot size={80} className="text-primary mb-4" />
                        <h3 className="h4 mb-3">AI-Powered Excellence</h3>
                        <p className="text-muted mb-4">
                          Transforming businesses with intelligent automation and AI integration
                        </p>
                        <div className="row g-3">
                          <div className="col-6">
                            <div className="text-center">
                              <Shield size={24} className="text-success mb-2" />
                              <small className="d-block text-muted">Enterprise Security</small>
                            </div>
                          </div>
                          <div className="col-6">
                            <div className="text-center">
                              <Award size={24} className="text-warning mb-2" />
                              <small className="d-block text-muted">Certified Expert</small>
                            </div>
                          </div>
                          <div className="col-6">
                            <div className="text-center">
                              <Zap size={24} className="text-info mb-2" />
                              <small className="d-block text-muted">Fast Deployment</small>
                            </div>
                          </div>
                          <div className="col-6">
                            <div className="text-center">
                              <Globe size={24} className="text-primary mb-2" />
                              <small className="d-block text-muted">Global Scale</small>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Stats Section */}
            <section className="py-5" id="stats" data-aos="fade-up">
              <div className="container-xl">
                <div className="row g-4">
                  {statsToShow.map((stat, index) => {
                    const Icon = stat.icon
                    return (
                      <div key={index} className="col-6 col-lg-3">
                        <div className={`glass-card stat-card text-center p-4 h-100 border-${stat.color}`}>
                          <Icon size={32} className={`text-${stat.color} mb-3`} />
                          <h2 className="display-6 fw-bold mb-2">{stat.value}</h2>
                          <p className="text-muted mb-0 small">{stat.label}</p>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            </section>

            {/* Performance Monitor */}
            <section className="py-5" id="performance" data-aos="fade-up">
              <div className="container-xl">
                <div className="text-center mb-5">
                  <h2 className="display-5 fw-bold mb-3">Live System Performance</h2>
                  <p className="lead text-muted">Real-time monitoring of our AI infrastructure</p>
                </div>
                <div className="glass-card p-4">
                  <PerformanceMonitor apiBase={API_BASE} />
                </div>
              </div>
            </section>

            {/* Technologies Section */}
            {portfolioStats && (
              <section className="py-5" id="technologies" data-aos="fade-up">
                <div className="container-xl">
                  <div className="text-center mb-5">
                    <h2 className="display-5 fw-bold mb-3">Technology Stack</h2>
                    <p className="lead text-muted">Cutting-edge technologies for modern AI solutions</p>
                  </div>
                  
                  <div className="row g-4">
                    <div className="col-md-6 col-lg-4">
                      <div className="glass-card p-4 h-100">
                        <h5 className="text-primary mb-3">
                          <Code size={24} className="me-2" />
                          Core Technologies
                        </h5>
                        <div className="d-flex flex-wrap gap-2">
                          {portfolioStats.technologies.slice(0, 8).map((tech, idx) => (
                            <span key={idx} className="tech-badge">{tech}</span>
                          ))}
                        </div>
                      </div>
                    </div>
                    
                    <div className="col-md-6 col-lg-4">
                      <div className="glass-card p-4 h-100">
                        <h5 className="text-success mb-3">
                          <Award size={24} className="me-2" />
                          Certifications
                        </h5>
                        <ul className="list-unstyled">
                          {portfolioStats.certifications.map((cert, idx) => (
                            <li key={idx} className="mb-2 small">
                              <CheckCircle size={16} className="text-success me-2" />
                              {cert}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                    
                    <div className="col-md-12 col-lg-4">
                      <div className="glass-card p-4 h-100">
                        <h5 className="text-info mb-3">
                          <BarChart3 size={24} className="me-2" />
                          Key Metrics
                        </h5>
                        <div className="row g-3">
                          <div className="col-6">
                            <div className="text-center">
                              <h4 className="text-warning mb-1">{portfolioStats.ai_models_deployed}</h4>
                              <small className="text-muted">AI Models</small>
                            </div>
                          </div>
                          <div className="col-6">
                            <div className="text-center">
                              <h4 className="text-info mb-1">{portfolioStats.languages_supported}</h4>
                              <small className="text-muted">Languages</small>
                            </div>
                          </div>
                          <div className="col-6">
                            <div className="text-center">
                              <h4 className="text-success mb-1">{portfolioStats.integrations_completed}</h4>
                              <small className="text-muted">Integrations</small>
                            </div>
                          </div>
                          <div className="col-6">
                            <div className="text-center">
                              <h4 className="text-primary mb-1">{portfolioStats.years_experience}</h4>
                              <small className="text-muted">Years Exp.</small>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>
            )}
          </>
        )}

        {/* Services Section */}
        {activeSection === 'services' && (
          <section className="py-5 mt-5" id="services">
            <div className="container-xl">
              <div className="text-center mb-5" data-aos="fade-up">
                <h2 className="display-4 fw-bold mb-4">AI Services Portfolio</h2>
                <p className="lead text-muted">Comprehensive AI solutions from concept to deployment</p>
              </div>

              <div className="row g-4">
                {services.map((service, index) => {
                  const Icon = service.icon
                  return (
                    <div key={index} className="col-md-6 col-lg-4" data-aos="fade-up" data-aos-delay={index * 100}>
                      <div className="service-card p-4 rounded-4 h-100">
                        <div 
                          className="d-inline-flex p-3 rounded-3 mb-4"
                          style={{ background: service.gradient }}
                        >
                          <Icon size={32} className="text-white" />
                        </div>
                        <h4 className="mb-3">{service.title}</h4>
                        <p className="text-muted mb-4">{service.description}</p>
                        <ul className="list-unstyled">
                          {service.features.map((feature, idx) => (
                            <li key={idx} className="mb-2 d-flex align-items-center">
                              <CheckCircle size={16} className={`text-${service.color} me-2`} />
                              <small>{feature}</small>
                            </li>
                          ))}
                        </ul>
                        <button className={`btn btn-outline-${service.color} w-100 mt-3`}>
                          Learn More
                          <ArrowRight size={16} className="ms-2" />
                        </button>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </section>
        )}

        {/* AI Pipeline Section */}
        {activeSection === 'pipeline' && (
          <section className="py-5 mt-5" id="pipeline">
            <div className="container-xl">
              <div className="text-center mb-5" data-aos="fade-up">
                <h2 className="display-4 fw-bold mb-4">AI Development Pipeline</h2>
                <p className="lead text-muted">Automated end-to-end AI development and deployment process</p>
              </div>

              <div className="row">
                <div className="col-lg-8 mx-auto">
                  {[
                    { step: '01', title: 'Analysis & Design', description: 'Requirements gathering, system architecture, and AI model selection', icon: BarChart3, color: 'primary' },
                    { step: '02', title: 'Development & Training', description: 'Custom AI model development, training, and optimization', icon: Code, color: 'success' },
                    { step: '03', title: 'Integration & Testing', description: 'System integration, comprehensive testing, and performance validation', icon: Settings, color: 'info' },
                    { step: '04', title: 'Deployment & Monitoring', description: 'Cloud deployment, monitoring setup, and ongoing maintenance', icon: Cloud, color: 'warning' },
                    { step: '05', title: 'Optimization & Scaling', description: 'Performance optimization, scaling, and continuous improvement', icon: TrendingUp, color: 'danger' }
                  ].map((phase, index) => {
                    const Icon = phase.icon
                    return (
                      <div key={index} className="timeline-item" data-aos="fade-right" data-aos-delay={index * 100}>
                        <div className="glass-card p-4 rounded-4">
                          <div className="d-flex align-items-start">
                            <div className={`badge bg-${phase.color} rounded-pill me-4 p-3`}>
                              <strong>{phase.step}</strong>
                            </div>
                            <div className="flex-grow-1">
                              <div className="d-flex align-items-center mb-3">
                                <Icon size={24} className={`text-${phase.color} me-3`} />
                                <h4 className="mb-0">{phase.title}</h4>
                              </div>
                              <p className="text-muted mb-0">{phase.description}</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Live Demos Section */}
        {activeSection === 'demos' && (
          <section className="py-5 mt-5" id="demos">
            <div className="container-xl">
              <div className="text-center mb-5" data-aos="fade-up">
                <h2 className="display-4 fw-bold mb-4">Live AI Demos</h2>
                <p className="lead text-muted">Interact with working AI assistants and see the technology in action</p>
              </div>

              {/* Bot Selection */}
              <div className="row g-4 mb-5">
                {bots.map((bot) => {
                  const Icon = bot.icon
                  return (
                    <div key={bot.id} className="col-md-4" data-aos="fade-up" data-aos-delay={bots.indexOf(bot) * 100}>
                      <button
                        onClick={() => setActiveBot(bot.id)}
                        className={`w-100 p-4 rounded-4 border-0 transition-all ${
                          activeBot === bot.id
                            ? `bg-${bot.color} text-white shadow-lg`
                            : 'glass-card text-light'
                        }`}
                      >
                        <Icon size={48} className="mb-3" />
                        <h5 className="mb-2">{bot.name}</h5>
                        <p className="mb-0 small opacity-75">{bot.description}</p>
                      </button>
                    </div>
                  )
                })}
              </div>

              {/* Demo Content */}
              {loading ? (
                <div className="text-center py-5" data-aos="fade-up">
                  <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Loading demo...</span>
                  </div>
                  <p className="mt-3 text-muted">Loading demo...</p>
                </div>
              ) : error ? (
                <div className="text-center py-5" data-aos="fade-up">
                  <div className="alert alert-danger" role="alert">
                    <h4 className="alert-heading">Demo Error</h4>
                    <p>{error}</p>
                    <button 
                      onClick={() => fetchBotData(activeBot)}
                      className="btn btn-outline-danger"
                    >
                      <ArrowRight size={16} className="me-2" />
                      Retry Demo
                    </button>
                  </div>
                </div>
              ) : data ? (
                <div className="row g-4" data-aos="fade-up">
                  <div className="col-lg-8">
                    <div className="glass-card p-4 rounded-4">
                      <Dashboard data={data} botType={activeBot} />
                    </div>
                  </div>
                  <div className="col-lg-4">
                    <div className="glass-card p-4 rounded-4 h-100">
                      <Chat botType={activeBot} apiBase={API_BASE} />
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-5" data-aos="fade-up">
                  <div className="glass-card p-5 rounded-4">
                    <Bot size={64} className="text-muted mb-4" />
                    <h5 className="text-muted">Select a bot above to see the live demo</h5>
                  </div>
                </div>
              )}
            </div>
          </section>
        )}

        {/* Call to Action Section */}
        <section className="py-5 my-5" id="cta" data-aos="fade-up">
          <div className="container-xl">
            <div className="glass-card p-5 rounded-4 text-center">
              <div className="row align-items-center">
                <div className="col-lg-8 mx-auto">
                  <h2 className="display-5 fw-bold mb-4">Ready to Transform Your Business with AI?</h2>
                  <p className="lead text-muted mb-5">
                    Let's discuss your AI project and create a custom solution that fits your needs perfectly
                  </p>
                  <div className="d-flex flex-column flex-sm-row gap-3 justify-content-center">
                    <button className="btn btn-gradient btn-lg px-5 py-3">
                      <MessageSquare size={20} className="me-2" />
                      Get Free Consultation
                    </button>
                    <button 
                      onClick={() => setActiveSection('portfolio')}
                      className="btn btn-outline-light btn-lg px-5 py-3"
                    >
                      <Briefcase size={20} className="me-2" />
                      View Portfolio
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="py-5 mt-5" style={{ background: 'rgba(15, 20, 25, 0.95)' }}>
        <div className="container-xl">
          <div className="row g-4">
            <div className="col-md-6 col-lg-4">
              <div className="d-flex align-items-center mb-4">
                <Bot size={32} className="text-primary me-3" />
                <h4 className="mb-0 gradient-text">RazorFlow AI</h4>
              </div>
              <p className="text-muted mb-4">
                Professional AI freelancer specializing in chatbots, automation, and AI system integration. 
                Transforming businesses with cutting-edge artificial intelligence solutions.
              </p>
              <div className="d-flex gap-3">
                <button className="btn btn-outline-light btn-sm">
                  <i className="bi bi-linkedin"></i>
                </button>
                <button className="btn btn-outline-light btn-sm">
                  <i className="bi bi-github"></i>
                </button>
                <button className="btn btn-outline-light btn-sm">
                  <i className="bi bi-twitter"></i>
                </button>
              </div>
            </div>
            
            <div className="col-md-6 col-lg-2">
              <h5 className="fw-bold mb-3">Services</h5>
              <ul className="list-unstyled">
                <li><button className="btn btn-link text-muted p-0 mb-2">AI Chatbots</button></li>
                <li><button className="btn btn-link text-muted p-0 mb-2">Automation</button></li>
                <li><button className="btn btn-link text-muted p-0 mb-2">Integration</button></li>
                <li><button className="btn btn-link text-muted p-0 mb-2">Deployment</button></li>
              </ul>
            </div>
            
            <div className="col-md-6 col-lg-3">
              <h5 className="fw-bold mb-3">Contact</h5>
              <ul className="list-unstyled text-muted">
                <li className="mb-2">
                  <i className="bi bi-envelope me-2"></i>
                  hello@razorflow-ai.com
                </li>
                <li className="mb-2">
                  <i className="bi bi-telephone me-2"></i>
                  +1 (555) 123-4567
                </li>
                <li className="mb-2">
                  <i className="bi bi-clock me-2"></i>
                  Available 24/7
                </li>
              </ul>
            </div>
            
            <div className="col-md-6 col-lg-3">
              <h5 className="fw-bold mb-3">Newsletter</h5>
              <p className="text-muted mb-3">Stay updated with the latest AI trends and solutions.</p>
              <div className="input-group">
                <input type="email" className="form-control" placeholder="Your email" />
                <button className="btn btn-primary" type="button">
                  <i className="bi bi-arrow-right"></i>
                </button>
              </div>
            </div>
          </div>
          
          <hr className="my-4 opacity-25" />
          
          <div className="text-center text-muted">
            <p className="mb-0">&copy; 2025 RazorFlow AI. Professional AI Solutions & Automation Services.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
