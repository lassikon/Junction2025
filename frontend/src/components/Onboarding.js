import React, { useState } from "react";
import "../styles/Onboarding.css";

const EDUCATION_PATHS = {
  vocational: {
    label: "Vocational Training",
    description: "Practical skills and quick entry to workforce",
  },
  university: {
    label: "University",
    description: "Higher education and specialized knowledge",
  },
  high_school: {
    label: "High School",
    description: "General education, exploring options",
  },
  working: { label: "Already Working", description: "Started career early" },
};

const RISK_ATTITUDES = {
  risk_averse: {
    label: "Risk Averse",
    description: "I prefer safe and stable choices",
    icon: "🛡️",
  },
  balanced: {
    label: "Balanced",
    description: "I take calculated risks",
    icon: "⚖️",
  },
  risk_seeking: {
    label: "Risk Seeking",
    description: "I embrace high-risk, high-reward",
    icon: "🚀",
  },
};

const CITIES = [
  "Helsinki",
  "Espoo",
  "Tampere",
  "Vantaa",
  "Oulu",
  "Turku",
  "Jyväskylä",
  "Lahti",
  "Kuopio",
  "Pori",
];

const ASPIRATION_OPTIONS = [
  { key: "own_car", label: "Own a Car", icon: "🚗" },
  { key: "travel", label: "Travel the World", icon: "✈️" },
  { key: "own_pet", label: "Have a Pet", icon: "🐕" },
  { key: "own_home", label: "Own a Home", icon: "🏠" },
  { key: "early_retirement", label: "Early Retirement", icon: "🏖️" },
  { key: "start_business", label: "Start a Business", icon: "💼" },
  { key: "financial_freedom", label: "Financial Freedom", icon: "💰" },
  { key: "help_family", label: "Help Family", icon: "👨‍👩‍👧‍👦" },
];

const Onboarding = ({ onComplete, isLoading = false }) => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    player_name: "",
    age: 25,
    city: "Helsinki",
    education_path: "",
    risk_attitude: "",
    monthly_income: 2000,
    monthly_expenses: 1000,
    starting_savings: 0,
    starting_debt: 0,
    aspirations: {},
  });

  const totalSteps = 7;

  const handleNext = () => {
    if (step < totalSteps) {
      setStep(step + 1);
    } else {
      handleSubmit();
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const handleSubmit = async () => {
    try {
      // Convert aspirations object to boolean values
      const aspirationsData = {};
      Object.keys(formData.aspirations).forEach((key) => {
        aspirationsData[key] = true;
      });

      const payload = {
        ...formData,
        aspirations: aspirationsData,
      };

      await onComplete(payload);
    } catch (error) {
      console.error("Error submitting onboarding:", error);
      // Error handling is now done in App.js via TanStack Query
    }
  };

  const toggleAspiration = (key) => {
    setFormData((prev) => {
      const newAspirations = { ...prev.aspirations };
      if (newAspirations[key]) {
        delete newAspirations[key];
      } else {
        newAspirations[key] = true;
      }
      return { ...prev, aspirations: newAspirations };
    });
  };

  const isStepValid = () => {
    switch (step) {
      case 1:
        return formData.player_name.trim().length > 0;
      case 2:
        return formData.age >= 15 && formData.age <= 35;
      case 3:
        return formData.city !== "";
      case 4:
        return formData.education_path !== "";
      case 5:
        return formData.risk_attitude !== "";
      case 6:
        return formData.monthly_income > 0 && formData.monthly_expenses >= 0;
      case 7:
        return true; // Optional step
      default:
        return false;
    }
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <div className="step-content">
            <h2>👋 Welcome to LifeSim!</h2>
            <p className="step-description">
              Embark on a journey to financial independence. Let's start by
              learning about you.
            </p>

            <div className="form-group">
              <label htmlFor="player_name">What's your name?</label>
              <input
                id="player_name"
                type="text"
                maxLength="100"
                value={formData.player_name}
                onChange={(e) =>
                  setFormData({ ...formData, player_name: e.target.value })
                }
                className="input-field"
                placeholder="Enter your name"
              />
            </div>
          </div>
        );

      case 2:
        return (
          <div className="step-content">
            <h2>🎂 How old are you?</h2>
            <p className="step-description">
              Your age helps us tailor the experience to your life stage.
            </p>

            <div className="form-group">
              <label htmlFor="age">Age</label>
              <input
                id="age"
                type="number"
                min="15"
                max="35"
                value={formData.age}
                onChange={(e) =>
                  setFormData({ ...formData, age: parseInt(e.target.value) })
                }
                className="input-field"
              />
              <small className="input-hint">
                Age must be between 15 and 35
              </small>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="step-content">
            <h2>📍 Where do you live?</h2>
            <p className="step-description">
              Your location affects living costs and opportunities.
            </p>

            <div className="form-group">
              <label htmlFor="city">Select your city:</label>
              <select
                id="city"
                value={formData.city}
                onChange={(e) =>
                  setFormData({ ...formData, city: e.target.value })
                }
                className="select-field"
              >
                {CITIES.map((city) => (
                  <option key={city} value={city}>
                    {city}
                  </option>
                ))}
              </select>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="step-content">
            <h2>🎓 Education Path</h2>
            <p className="step-description">
              What's your current educational status?
            </p>

            <div className="option-grid">
              {Object.entries(EDUCATION_PATHS).map(([key, value]) => (
                <button
                  key={key}
                  className={`option-card ${
                    formData.education_path === key ? "selected" : ""
                  }`}
                  onClick={() =>
                    setFormData({ ...formData, education_path: key })
                  }
                >
                  <h3>{value.label}</h3>
                  <p>{value.description}</p>
                </button>
              ))}
            </div>
          </div>
        );

      case 5:
        return (
          <div className="step-content">
            <h2>💭 Risk Attitude</h2>
            <p className="step-description">
              How do you approach financial decisions?
            </p>

            <div className="option-grid">
              {Object.entries(RISK_ATTITUDES).map(([key, value]) => (
                <button
                  key={key}
                  className={`option-card ${
                    formData.risk_attitude === key ? "selected" : ""
                  }`}
                  onClick={() =>
                    setFormData({ ...formData, risk_attitude: key })
                  }
                >
                  <div className="option-icon">{value.icon}</div>
                  <h3>{value.label}</h3>
                  <p>{value.description}</p>
                </button>
              ))}
            </div>
          </div>
        );

      case 6:
        return (
          <div className="step-content">
            <h2>💼 Monthly Finances</h2>
            <p className="step-description">
              Tell us about your monthly income and expenses.
            </p>

            <div className="form-group">
              <label htmlFor="monthly_income">Monthly Income (€)</label>
              <input
                id="monthly_income"
                type="number"
                min="0"
                step="100"
                value={formData.monthly_income}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    monthly_income: parseFloat(e.target.value) || 0,
                  })
                }
                className="input-field"
              />
              <small className="input-hint">
                Your total monthly income after taxes
              </small>
            </div>

            <div className="form-group">
              <label htmlFor="monthly_expenses">Monthly Expenses (€)</label>
              <input
                id="monthly_expenses"
                type="number"
                min="0"
                step="100"
                value={formData.monthly_expenses}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    monthly_expenses: parseFloat(e.target.value) || 0,
                  })
                }
                className="input-field"
              />
              <small className="input-hint">
                Your total monthly expenses (rent, food, utilities, etc.)
              </small>
            </div>
          </div>
        );

      case 7:
        return (
          <div className="step-content">
            <h2>💰 Financial Starting Point</h2>
            <p className="step-description">
              Let's set up your initial financial situation.
            </p>

            <div className="form-group">
              <label htmlFor="savings">Starting Savings (€)</label>
              <input
                id="savings"
                type="number"
                min="0"
                step="100"
                value={formData.starting_savings}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    starting_savings: parseFloat(e.target.value) || 0,
                  })
                }
                className="input-field"
              />
            </div>

            <div className="form-group">
              <label htmlFor="debt">Starting Debt (€)</label>
              <input
                id="debt"
                type="number"
                min="0"
                step="100"
                value={formData.starting_debt}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    starting_debt: parseFloat(e.target.value) || 0,
                  })
                }
                className="input-field"
              />
            </div>

            <div className="form-group">
              <label>Your Aspirations (select all that apply)</label>
              <div className="aspirations-grid">
                {ASPIRATION_OPTIONS.map((option) => (
                  <button
                    key={option.key}
                    className={`aspiration-chip ${
                      formData.aspirations[option.key] ? "selected" : ""
                    }`}
                    onClick={() => toggleAspiration(option.key)}
                  >
                    <span className="aspiration-icon">{option.icon}</span>
                    <span>{option.label}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="onboarding-container">
      <div className="onboarding-card">
        {/* Progress Bar */}
        <div className="progress-bar">
          <div className="progress-steps">
            {[...Array(totalSteps)].map((_, index) => (
              <div
                key={index}
                className={`progress-step ${
                  index + 1 <= step ? "active" : ""
                } ${index + 1 < step ? "completed" : ""}`}
              >
                {index + 1}
              </div>
            ))}
          </div>
          <div
            className="progress-fill"
            style={{ width: `${(step / totalSteps) * 100}%` }}
          />
        </div>

        {/* Step Content */}
        {renderStep()}

        {/* Navigation Buttons */}
        <div className="button-group">
          <button
            onClick={handleBack}
            disabled={step === 1 || isLoading}
            className="btn btn-secondary"
          >
            Back
          </button>
          <button
            onClick={handleNext}
            disabled={!isStepValid() || isLoading}
            className="btn btn-primary"
          >
            {isLoading
              ? "Creating..."
              : step === totalSteps
              ? "Start Journey"
              : "Next"}
          </button>
        </div>

        {/* Step Indicator */}
        <div className="step-indicator">
          Step {step} of {totalSteps}
        </div>
      </div>
    </div>
  );
};

export default Onboarding;
