// Legal Calculations and Utility Functions

/**
 * Calculate case strength score based on multiple factors
 * @param {Object} factors - Case strength factors
 * @returns {Object} Calculated score and breakdown
 */
export const calculateCaseStrength = (factors) => {
  if (!factors || typeof factors !== 'object') {
    return { score: 0, breakdown: {}, confidence: 'low' };
  }

  const weights = {
    precedent_support: 0.25,      // 25% - Legal precedent strength
    factual_strength: 0.20,       // 20% - Strength of factual basis
    legal_authority: 0.20,        // 20% - Statutory/constitutional support
    jurisdictional_factors: 0.15, // 15% - Court and jurisdiction advantages
    opposing_arguments: 0.10,     // 10% - Strength of counter-arguments (inverse)
    evidence_quality: 0.10        // 10% - Quality and admissibility of evidence
  };

  let weightedScore = 0;
  let totalWeight = 0;
  const breakdown = {};

  // Calculate weighted score for each factor
  Object.entries(weights).forEach(([factor, weight]) => {
    const factorScore = factors[factor];
    if (typeof factorScore === 'number' && factorScore >= 0 && factorScore <= 10) {
      // For opposing arguments, invert the score (stronger opposition = lower case strength)
      const adjustedScore = factor === 'opposing_arguments' ? (10 - factorScore) : factorScore;

      weightedScore += adjustedScore * weight;
      totalWeight += weight;
      breakdown[factor] = {
        score: factorScore,
        adjustedScore,
        weight,
        contribution: adjustedScore * weight
      };
    }
  });

  // Normalize score to 0-10 scale
  const finalScore = totalWeight > 0 ? (weightedScore / totalWeight) : 0;

  // Determine confidence level
  let confidence = 'low';
  const factorCount = Object.keys(breakdown).length;

  if (factorCount >= 5 && finalScore >= 7) {
    confidence = 'high';
  } else if (factorCount >= 3 && finalScore >= 5) {
    confidence = 'medium';
  }

  return {
    score: Math.round(finalScore * 100) / 100, // Round to 2 decimal places
    breakdown,
    confidence,
    recommendation: getStrengthRecommendation(finalScore)
  };
};

/**
 * Get case strength recommendation based on score
 * @param {number} score - Case strength score (0-10)
 * @returns {string} Recommendation text
 */
const getStrengthRecommendation = (score) => {
  if (score >= 8) {
    return 'Strong case - Proceed with confidence. Consider settlement demands.';
  } else if (score >= 6) {
    return 'Moderate case - Strengthen weak areas before proceeding.';
  } else if (score >= 4) {
    return 'Weak case - Significant risks. Consider alternative strategies.';
  } else {
    return 'Very weak case - High risk of adverse outcome. Reconsider viability.';
  }
};

/**
 * Calculate litigation cost estimates
 * @param {Object} caseParams - Case parameters
 * @returns {Object} Cost breakdown and estimates
 */
export const calculateLitigationCosts = (caseParams) => {
  const {
    caseType = 'general',
    complexity = 'medium',
    jurisdiction = 'state',
    estimatedDuration = 12, // months
    hourlyRate = 500,
    disputeValue = 0
  } = caseParams;

  // Base hour estimates by case type and complexity
  const baseHours = {
    simple: { general: 50, contract: 40, employment: 60, personal_injury: 80 },
    medium: { general: 150, contract: 120, employment: 180, personal_injury: 200 },
    complex: { general: 400, contract: 300, employment: 500, personal_injury: 600 }
  };

  const estimatedHours = baseHours[complexity]?.[caseType] || baseHours[complexity].general;

  // Cost multipliers
  const jurisdictionMultiplier = jurisdiction === 'federal' ? 1.3 : 1.0;
  const durationMultiplier = Math.max(0.8, estimatedDuration / 12);

  // Calculate costs
  const attorneyFees = estimatedHours * hourlyRate * jurisdictionMultiplier * durationMultiplier;

  const costs = {
    attorney_fees: attorneyFees,
    court_fees: jurisdiction === 'federal' ? 1200 : 800,
    discovery_costs: estimatedHours * 50, // Estimated discovery costs
    expert_witnesses: complexity === 'complex' ? 15000 : complexity === 'medium' ? 7500 : 2500,
    depositions: Math.min(estimatedHours / 20, 15) * 1500,
    administrative: attorneyFees * 0.1 // 10% administrative overhead
  };

  const totalCosts = Object.values(costs).reduce((sum, cost) => sum + cost, 0);

  // Contingency analysis
  const contingencyFee = disputeValue > 0 ? disputeValue * 0.33 : 0; // 33% contingency
  const riskAdjustedValue = disputeValue * 0.7; // Assume 70% collection rate

  return {
    breakdown: costs,
    total_estimated_cost: Math.round(totalCosts),
    contingency_fee: Math.round(contingencyFee),
    net_expected_value: Math.round(riskAdjustedValue - totalCosts),
    cost_benefit_ratio: disputeValue > 0 ? riskAdjustedValue / totalCosts : 0,
    recommendation: getCostRecommendation(totalCosts, disputeValue)
  };
};

/**
 * Get cost-benefit recommendation
 * @param {number} totalCosts - Total estimated costs
 * @param {number} disputeValue - Value in dispute
 * @returns {string} Cost recommendation
 */
const getCostRecommendation = (totalCosts, disputeValue) => {
  if (disputeValue === 0) {
    return 'Non-monetary case - Consider alternative dispute resolution.';
  }

  const ratio = disputeValue / totalCosts;

  if (ratio >= 3) {
    return 'Favorable cost-benefit ratio - Litigation economically viable.';
  } else if (ratio >= 1.5) {
    return 'Moderate cost-benefit ratio - Proceed with caution.';
  } else {
    return 'Poor cost-benefit ratio - Consider settlement or alternative strategies.';
  }
};

/**
 * Calculate damages based on different legal theories
 * @param {Object} damageParams - Damage calculation parameters
 * @returns {Object} Damage calculations
 */
export const calculateDamages = (damageParams) => {
  const {
    damageType = 'compensatory',
    economicLoss = 0,
    lostProfits = 0,
    medicalExpenses = 0,
    painAndSuffering = 0,
    punitiveMultiplier = 1.0,
    interestRate = 0.05,
    timePeriod = 1 // years
  } = damageParams;

  const damages = {};

  // Compensatory damages
  damages.compensatory = {
    economic_loss: economicLoss,
    lost_profits: lostProfits,
    medical_expenses: medicalExpenses,
    total: economicLoss + lostProfits + medicalExpenses
  };

  // Non-economic damages
  damages.non_economic = {
    pain_and_suffering: painAndSuffering,
    emotional_distress: painAndSuffering * 0.5, // Estimated
    total: painAndSuffering + (painAndSuffering * 0.5)
  };

  // Total compensatory
  const totalCompensatory = damages.compensatory.total + damages.non_economic.total;

  // Punitive damages (if applicable)
  damages.punitive = totalCompensatory * punitiveMultiplier;

  // Interest calculations
  const compoundInterest = totalCompensatory * Math.pow(1 + interestRate, timePeriod) - totalCompensatory;
  damages.interest = compoundInterest;

  // Total damages
  damages.total = totalCompensatory + damages.punitive + damages.interest;

  return {
    breakdown: damages,
    total_damages: Math.round(damages.total),
    present_value: Math.round(damages.total / Math.pow(1 + interestRate, timePeriod)),
    recommendation: getDamageRecommendation(damages)
  };
};

/**
 * Get damage calculation recommendation
 * @param {Object} damages - Damage breakdown
 * @returns {string} Recommendation
 */
const getDamageRecommendation = (damages) => {
  const total = damages.total;
  const compensatory = damages.compensatory.total + damages.non_economic.total;
  const punitiveRatio = damages.punitive / compensatory;

  let recommendation = `Total damages: $${Math.round(total).toLocaleString()}. `;

  if (punitiveRatio > 3) {
    recommendation += 'High punitive damages may face constitutional challenges.';
  } else if (damages.non_economic.total > damages.compensatory.total) {
    recommendation += 'Non-economic damages significant - ensure strong documentation.';
  } else {
    recommendation += 'Damage calculation appears reasonable and supportable.';
  }

  return recommendation;
};

/**
 * Calculate settlement negotiation ranges
 * @param {Object} settlementParams - Settlement parameters
 * @returns {Object} Settlement analysis
 */
export const calculateSettlementRange = (settlementParams) => {
  const {
    damageEstimate = 0,
    caseStrength = 5, // 1-10 scale
    litigationCosts = 0,
    timeToTrial = 12, // months
    riskTolerance = 'medium' // low, medium, high
  } = settlementParams;

  // Risk adjustment factors
  const riskFactors = {
    low: 0.6,    // Conservative, prefer certainty
    medium: 0.7,  // Balanced approach
    high: 0.8     // Willing to take risks for higher recovery
  };

  const riskFactor = riskFactors[riskTolerance] || 0.7;
  const strengthMultiplier = caseStrength / 10;

  // Calculate settlement ranges
  const expectedValue = damageEstimate * strengthMultiplier * riskFactor;
  const minSettlement = expectedValue * 0.6 - (litigationCosts * 0.5);
  const maxSettlement = expectedValue * 1.2;
  const optimalSettlement = expectedValue - (litigationCosts * 0.3);

  // Time value adjustments
  const timeDiscountFactor = Math.max(0.8, 1 - (timeToTrial / 100));
  const timeAdjustedMin = minSettlement * timeDiscountFactor;
  const timeAdjustedOptimal = optimalSettlement * timeDiscountFactor;

  return {
    minimum_acceptable: Math.max(0, Math.round(timeAdjustedMin)),
    optimal_target: Math.round(timeAdjustedOptimal),
    maximum_reasonable: Math.round(maxSettlement),
    expected_value: Math.round(expectedValue),
    recommendation: getSettlementRecommendation(caseStrength, riskTolerance),
    factors: {
      case_strength: strengthMultiplier,
      risk_adjustment: riskFactor,
      time_discount: timeDiscountFactor
    }
  };
};

/**
 * Get settlement recommendation
 * @param {number} caseStrength - Case strength score
 * @param {string} riskTolerance - Risk tolerance level
 * @returns {string} Settlement recommendation
 */
const getSettlementRecommendation = (caseStrength, riskTolerance) => {
  if (caseStrength >= 8) {
    return 'Strong case - Can demand higher settlement amounts.';
  } else if (caseStrength >= 6) {
    return 'Moderate case - Settlement likely preferable to trial risk.';
  } else if (caseStrength <= 4) {
    return 'Weak case - Strongly consider any reasonable settlement offer.';
  }

  return 'Evaluate settlement opportunities based on risk tolerance and costs.';
};

/**
 * Statute of limitations calculator
 * @param {Object} limitationParams - SOL parameters
 * @returns {Object} SOL analysis
 */
export const calculateStatuteOfLimitations = (limitationParams) => {
  const {
    claimType = 'general',
    jurisdiction = 'general',
    discoveryDate = null,
    accrualDate = null,
    filingDate = null
  } = limitationParams;

  // Standard SOL periods (in years)
  const standardPeriods = {
    contract: { written: 6, oral: 3 },
    tort: { personal_injury: 2, property_damage: 3, professional_malpractice: 2 },
    employment: { discrimination: 1, wage_hour: 2 },
    fraud: { general: 3, securities: 3 },
    general: 3
  };

  const solPeriod = standardPeriods[claimType] || standardPeriods.general;
  const years = typeof solPeriod === 'object' ? solPeriod.written || solPeriod.general : solPeriod;

  // Calculate key dates
  const accrual = accrualDate ? new Date(accrualDate) : new Date();
  const discovery = discoveryDate ? new Date(discoveryDate) : accrual;
  const filing = filingDate ? new Date(filingDate) : new Date();

  // Calculate expiration dates
  const accrualExpiry = new Date(accrual);
  accrualExpiry.setFullYear(accrualExpiry.getFullYear() + years);

  const discoveryExpiry = new Date(discovery);
  discoveryExpiry.setFullYear(discoveryExpiry.getFullYear() + years);

  // Use later of the two dates (discovery rule)
  const finalExpiry = accrualExpiry > discoveryExpiry ? accrualExpiry : discoveryExpiry;

  // Calculate days remaining
  const today = new Date();
  const daysRemaining = Math.ceil((finalExpiry - today) / (1000 * 60 * 60 * 24));

  return {
    sol_period_years: years,
    accrual_date: accrual.toISOString().split('T')[0],
    discovery_date: discovery.toISOString().split('T')[0],
    expiration_date: finalExpiry.toISOString().split('T')[0],
    days_remaining: daysRemaining,
    is_expired: daysRemaining <= 0,
    is_critical: daysRemaining <= 30 && daysRemaining > 0,
    recommendation: getSOLRecommendation(daysRemaining)
  };
};

/**
 * Get SOL recommendation
 * @param {number} daysRemaining - Days until expiration
 * @returns {string} SOL recommendation
 */
const getSOLRecommendation = (daysRemaining) => {
  if (daysRemaining <= 0) {
    return 'CRITICAL: Statute of limitations has expired. Immediate legal action required.';
  } else if (daysRemaining <= 30) {
    return 'URGENT: Less than 30 days remaining. File immediately.';
  } else if (daysRemaining <= 90) {
    return 'WARNING: Less than 90 days remaining. Begin filing preparations.';
  } else {
    return 'Adequate time remaining, but monitor deadlines closely.';
  }
};

export default {
  calculateCaseStrength,
  calculateLitigationCosts,
  calculateDamages,
  calculateSettlementRange,
  calculateStatuteOfLimitations
};