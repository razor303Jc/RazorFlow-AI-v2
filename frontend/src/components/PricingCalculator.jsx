import React, { useState } from 'react';
import { Calculator, DollarSign, Clock, CheckCircle } from 'lucide-react';

const PricingCalculator = () => {
  const [selectedService, setSelectedService] = useState('chatbot');
  const [complexity, setComplexity] = useState('basic');
  const [timeline, setTimeline] = useState('standard');
  const [showQuote, setShowQuote] = useState(false);

  const services = {
    chatbot: {
      name: 'AI Chatbot',
      base: 500,
      complexity: { basic: 1, advanced: 2, enterprise: 4 },
      timeline: { rush: 1.5, standard: 1, extended: 0.8 }
    },
    automation: {
      name: 'Business Automation',
      base: 300,
      complexity: { basic: 1, advanced: 2.5, enterprise: 5 },
      timeline: { rush: 1.5, standard: 1, extended: 0.8 }
    },
    integration: {
      name: 'API Integration',
      base: 800,
      complexity: { basic: 1, advanced: 2, enterprise: 3 },
      timeline: { rush: 1.5, standard: 1, extended: 0.8 }
    },
    custom: {
      name: 'Custom AI Solution',
      base: 2000,
      complexity: { basic: 1, advanced: 2, enterprise: 4 },
      timeline: { rush: 1.5, standard: 1, extended: 0.8 }
    }
  };

  const calculatePrice = () => {
    const service = services[selectedService];
    const basePrice = service.base;
    const complexityMultiplier = service.complexity[complexity];
    const timelineMultiplier = service.timeline[timeline];
    
    return Math.round(basePrice * complexityMultiplier * timelineMultiplier);
  };

  const getDeliveryTime = () => {
    const baseDays = {
      chatbot: 3,
      automation: 2,
      integration: 5,
      custom: 14
    };
    
    const timelineMultiplier = {
      rush: 0.6,
      standard: 1,
      extended: 1.5
    };
    
    return Math.round(baseDays[selectedService] * timelineMultiplier[timeline]);
  };

  const handleGetQuote = () => {
    setShowQuote(true);
    // Here you would typically send the data to your backend
    const quoteData = {
      service: selectedService,
      complexity,
      timeline,
      price: calculatePrice(),
      deliveryTime: getDeliveryTime(),
      timestamp: new Date().toISOString()
    };
    
    // Send to your backend API
    fetch('/api/quote-requests', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(quoteData)
    });
  };

  return (
    <div className="pricing-calculator">
      <div className="calculator-header">
        <Calculator size={32} />
        <h3>Get Your Project Quote</h3>
        <p>Calculate the cost for your AI solution in 30 seconds</p>
      </div>

      <div className="calculator-form">
        <div className="form-group">
          <label>What type of AI solution do you need?</label>
          <select 
            value={selectedService} 
            onChange={(e) => setSelectedService(e.target.value)}
            className="form-select"
          >
            <option value="chatbot">AI Chatbot for Customer Support</option>
            <option value="automation">Business Process Automation</option>
            <option value="integration">API & System Integration</option>
            <option value="custom">Custom AI Development</option>
          </select>
        </div>

        <div className="form-group">
          <label>Project Complexity</label>
          <div className="radio-group">
            <label className="radio-option">
              <input 
                type="radio" 
                value="basic" 
                checked={complexity === 'basic'}
                onChange={(e) => setComplexity(e.target.value)}
              />
              <span>Basic - Simple setup with standard features</span>
            </label>
            <label className="radio-option">
              <input 
                type="radio" 
                value="advanced" 
                checked={complexity === 'advanced'}
                onChange={(e) => setComplexity(e.target.value)}
              />
              <span>Advanced - Custom features and integrations</span>
            </label>
            <label className="radio-option">
              <input 
                type="radio" 
                value="enterprise" 
                checked={complexity === 'enterprise'}
                onChange={(e) => setComplexity(e.target.value)}
              />
              <span>Enterprise - Complex, multi-system solution</span>
            </label>
          </div>
        </div>

        <div className="form-group">
          <label>Timeline Preference</label>
          <div className="radio-group">
            <label className="radio-option">
              <input 
                type="radio" 
                value="rush" 
                checked={timeline === 'rush'}
                onChange={(e) => setTimeline(e.target.value)}
              />
              <span>Rush Delivery (+50% cost)</span>
            </label>
            <label className="radio-option">
              <input 
                type="radio" 
                value="standard" 
                checked={timeline === 'standard'}
                onChange={(e) => setTimeline(e.target.value)}
              />
              <span>Standard Timeline</span>
            </label>
            <label className="radio-option">
              <input 
                type="radio" 
                value="extended" 
                checked={timeline === 'extended'}
                onChange={(e) => setTimeline(e.target.value)}
              />
              <span>Extended Timeline (-20% discount)</span>
            </label>
          </div>
        </div>
      </div>

      <div className="quote-preview">
        <div className="quote-item">
          <DollarSign size={20} />
          <span>Estimated Cost: <strong>${calculatePrice().toLocaleString()}</strong></span>
        </div>
        <div className="quote-item">
          <Clock size={20} />
          <span>Delivery Time: <strong>{getDeliveryTime()} days</strong></span>
        </div>
        <div className="quote-item">
          <CheckCircle size={20} />
          <span>30-day warranty included</span>
        </div>
      </div>

      {!showQuote ? (
        <button 
          className="btn btn-primary btn-lg"
          onClick={handleGetQuote}
        >
          Get Detailed Quote & Timeline
        </button>
      ) : (
        <div className="quote-success">
          <CheckCircle size={48} className="success-icon" />
          <h4>Quote Generated Successfully!</h4>
          <p>We'll send you a detailed proposal within 2 hours.</p>
          <div className="contact-options">
            <button className="btn btn-success">Schedule Call</button>
            <button className="btn btn-outline">Download PDF Quote</button>
          </div>
        </div>
      )}

      <div className="calculator-footer">
        <p>💡 <strong>Free consultation included</strong> with every quote</p>
        <p>🚀 <strong>Projects starting this week</strong> get 15% early bird discount</p>
      </div>

      <style jsx>{`
        .pricing-calculator {
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.2);
          border-radius: 1rem;
          padding: 2rem;
          margin: 2rem 0;
          max-width: 600px;
        }

        .calculator-header {
          text-align: center;
          margin-bottom: 2rem;
        }

        .calculator-header h3 {
          margin: 0.5rem 0;
          color: #ffffff;
        }

        .form-group {
          margin-bottom: 1.5rem;
        }

        .form-group label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 600;
          color: #ffffff;
        }

        .form-select {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid rgba(255, 255, 255, 0.3);
          border-radius: 0.5rem;
          background: rgba(255, 255, 255, 0.1);
          color: #ffffff;
          font-size: 1rem;
        }

        .radio-group {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .radio-option {
          display: flex;
          align-items: center;
          padding: 0.75rem;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 0.5rem;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .radio-option:hover {
          background: rgba(255, 255, 255, 0.1);
          border-color: rgba(255, 255, 255, 0.3);
        }

        .radio-option input {
          margin-right: 0.75rem;
        }

        .quote-preview {
          background: rgba(0, 0, 0, 0.2);
          border-radius: 0.5rem;
          padding: 1.5rem;
          margin: 1.5rem 0;
        }

        .quote-item {
          display: flex;
          align-items: center;
          margin-bottom: 0.75rem;
          color: #ffffff;
        }

        .quote-item svg {
          margin-right: 0.75rem;
          color: #4facfe;
        }

        .btn-lg {
          width: 100%;
          padding: 1rem 2rem;
          font-size: 1.1rem;
          font-weight: 600;
        }

        .quote-success {
          text-align: center;
          padding: 2rem;
          background: rgba(0, 255, 0, 0.1);
          border-radius: 0.5rem;
          margin: 1rem 0;
        }

        .success-icon {
          color: #00ff88;
          margin-bottom: 1rem;
        }

        .contact-options {
          display: flex;
          gap: 1rem;
          justify-content: center;
          margin-top: 1rem;
        }

        .calculator-footer {
          text-align: center;
          margin-top: 2rem;
          padding-top: 1rem;
          border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .calculator-footer p {
          margin: 0.5rem 0;
          color: #ffffff;
          font-size: 0.9rem;
        }

        @media (max-width: 768px) {
          .contact-options {
            flex-direction: column;
          }
        }
      `}</style>
    </div>
  );
};

export default PricingCalculator;
