"""
Reserve Calculator Service for Insurance Claims
Implements actuarial methods for reserve calculation and trend analysis
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import json
from loguru import logger

from app.core.database import get_claims_data, ReserveCalculation, TrendAnalysis, SessionLocal


class ReserveCalculatorService:
    """Service for calculating insurance reserves using actuarial methods"""
    
    def __init__(self):
        self.confidence_level = 0.95
        self.development_period = 12  # months
        self.tail_factor = 1.05
        
    def calculate_chain_ladder_reserves(self, df: pd.DataFrame) -> Dict:
        """
        Calculate reserves using Chain Ladder method
        
        Args:
            df: Claims data DataFrame
            
        Returns:
            Reserve calculation results
        """
        try:
            logger.info("Calculating reserves using Chain Ladder method")
            
            # Create development triangle
            triangle = self._create_development_triangle(df)
            
            # Calculate development factors
            dev_factors = self._calculate_development_factors(triangle)
            
            # Project ultimate claims
            ultimate_claims = self._project_ultimate_claims(triangle, dev_factors)
            
            # Calculate reserves
            reserves = ultimate_claims - triangle.iloc[:, -1]
            total_reserves = reserves.sum()
            
            # Calculate confidence intervals
            confidence_intervals = self._calculate_confidence_intervals(
                triangle, dev_factors, ultimate_claims
            )
            
            result = {
                'method': 'Chain Ladder',
                'total_reserves': float(total_reserves),
                'development_factors': {str(k): float(v) for k, v in dev_factors.to_dict().items()},
                'ultimate_claims': {str(k): float(v) for k, v in ultimate_claims.to_dict().items()},
                'reserves_by_accident_year': {str(k): float(v) for k, v in reserves.to_dict().items()},
                'confidence_intervals': {k: float(v) for k, v in confidence_intervals.items()},
                'calculation_date': datetime.utcnow().isoformat()
            }
            
            # Save to database
            self._save_reserve_calculation(result)
            
            logger.info(f"Chain Ladder reserves calculated: ${total_reserves:,.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error in Chain Ladder calculation: {e}")
            raise
    
    def calculate_bornhuetter_ferguson_reserves(self, df: pd.DataFrame, 
                                             expected_loss_ratio: float = 0.75) -> Dict:
        """
        Calculate reserves using Bornhuetter-Ferguson method
        
        Args:
            df: Claims data DataFrame
            expected_loss_ratio: Expected loss ratio for the portfolio
            
        Returns:
            Reserve calculation results
        """
        try:
            logger.info("Calculating reserves using Bornhuetter-Ferguson method")
            
            # Get earned premiums (simulated based on charges)
            earned_premiums = df['charges'].sum() * 1.2  # Assume 20% loading
            
            # Calculate expected ultimate claims
            expected_ultimate = earned_premiums * expected_loss_ratio
            
            # Create development triangle
            triangle = self._create_development_triangle(df)
            
            # Calculate development factors
            dev_factors = self._calculate_development_factors(triangle)
            
            # Calculate reported claims by accident year
            reported_claims = triangle.iloc[:, -1]
            
            # Calculate reserves using BF formula
            reserves = {}
            for i, (accident_year, reported) in enumerate(reported_claims.items()):
                # Get development factor for this accident year
                if i < len(dev_factors):
                    dev_factor = dev_factors.iloc[i] if i < len(dev_factors) else 1.0
                else:
                    dev_factor = 1.0
                
                # Calculate expected ultimate for this accident year
                expected_ultimate_year = expected_ultimate * (reported / reported_claims.sum())
                
                # BF Reserve = Expected Ultimate * (1 - 1/Dev Factor)
                bf_reserve = expected_ultimate_year * (1 - 1/dev_factor)
                reserves[accident_year] = max(0, bf_reserve)
            
            total_reserves = sum(reserves.values())
            
            result = {
                'method': 'Bornhuetter-Ferguson',
                'total_reserves': float(total_reserves),
                'expected_loss_ratio': float(expected_loss_ratio),
                'earned_premiums': float(earned_premiums),
                'expected_ultimate_claims': float(expected_ultimate),
                'reserves_by_accident_year': {str(k): float(v) for k, v in reserves.items()},
                'calculation_date': datetime.utcnow().isoformat()
            }
            
            # Save to database
            self._save_reserve_calculation(result)
            
            logger.info(f"Bornhuetter-Ferguson reserves calculated: ${total_reserves:,.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error in Bornhuetter-Ferguson calculation: {e}")
            raise
    
    def calculate_frequency_severity_reserves(self, df: pd.DataFrame) -> Dict:
        """
        Calculate reserves using Frequency-Severity method
        
        Args:
            df: Claims data DataFrame
            
        Returns:
            Reserve calculation results
        """
        try:
            logger.info("Calculating reserves using Frequency-Severity method")
            
            # Separate claims and non-claims
            claims_data = df[df['insuranceclaim'] == 1]
            
            # Calculate frequency (claims per exposure)
            total_exposure = len(df)
            claim_frequency = len(claims_data) / total_exposure
            
            # Calculate severity (average claim amount)
            if len(claims_data) > 0:
                claim_severity = claims_data['charges'].mean()
            else:
                claim_severity = 0
            
            # Calculate expected claims
            expected_claims = claim_frequency * claim_severity * total_exposure
            
            # Calculate variance components
            frequency_variance = claim_frequency * (1 - claim_frequency) * total_exposure
            severity_variance = claims_data['charges'].var() if len(claims_data) > 1 else 0
            
            # Calculate total variance
            total_variance = (frequency_variance * claim_severity**2 + 
                            severity_variance * claim_frequency * total_exposure)
            
            # Calculate confidence intervals
            std_dev = np.sqrt(total_variance)
            z_score = stats.norm.ppf((1 + self.confidence_level) / 2)
            confidence_interval = z_score * std_dev
            
            # Calculate reserves
            total_reserves = expected_claims + confidence_interval
            
            result = {
                'method': 'Frequency-Severity',
                'total_reserves': float(total_reserves),
                'claim_frequency': float(claim_frequency),
                'claim_severity': float(claim_severity),
                'expected_claims': float(expected_claims),
                'total_variance': float(total_variance),
                'confidence_interval': float(confidence_interval),
                'calculation_date': datetime.utcnow().isoformat()
            }
            
            # Save to database
            self._save_reserve_calculation(result)
            
            logger.info(f"Frequency-Severity reserves calculated: ${total_reserves:,.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error in Frequency-Severity calculation: {e}")
            raise
    
    def perform_trend_analysis(self, df: pd.DataFrame) -> Dict:
        """
        Perform trend analysis on claims data
        
        Args:
            df: Claims data DataFrame
            
        Returns:
            Trend analysis results
        """
        try:
            logger.info("Performing trend analysis")
            
            # Create time series data (simulate based on age as proxy for time)
            df_sorted = df.sort_values('age')
            
            # Analyze different metrics
            trends = {}
            
            # Claims frequency trend
            age_groups = pd.cut(df_sorted['age'], bins=5, labels=False)
            frequency_by_age = df_sorted.groupby(age_groups)['insuranceclaim'].mean()
            trends['claims_frequency'] = self._analyze_trend(frequency_by_age.values, 'Claims Frequency')
            
            # Average charges trend
            charges_by_age = df_sorted.groupby(age_groups)['charges'].mean()
            trends['average_charges'] = self._analyze_trend(charges_by_age.values, 'Average Charges')
            
            # BMI trend
            bmi_by_age = df_sorted.groupby(age_groups)['bmi'].mean()
            trends['average_bmi'] = self._analyze_trend(bmi_by_age.values, 'Average BMI')
            
            # Smoker rate trend
            smoker_by_age = df_sorted.groupby(age_groups)['smoker'].mean()
            trends['smoker_rate'] = self._analyze_trend(smoker_by_age.values, 'Smoker Rate')
            
            # Save trend analysis to database
            for metric, trend_data in trends.items():
                self._save_trend_analysis(metric, trend_data)
            
            logger.info("Trend analysis completed")
            return trends
            
        except Exception as e:
            logger.error(f"Error in trend analysis: {e}")
            raise
    
    def _create_development_triangle(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create development triangle from claims data"""
        # Simulate development triangle using age as accident year proxy
        # In real implementation, this would use actual accident and development periods
        
        # Create accident years based on age groups
        df['accident_year'] = pd.cut(df['age'], bins=5, labels=['2019', '2020', '2021', '2022', '2023'])
        
        # Create development periods (simulate 12 months of development)
        development_periods = list(range(1, 13))
        
        # Create triangle structure
        triangle_data = {}
        for year in df['accident_year'].cat.categories:
            year_data = df[df['accident_year'] == year]
            if len(year_data) > 0:
                # Simulate cumulative claims development
                base_claims = year_data['charges'].sum()
                cumulative_claims = []
                
                for period in development_periods:
                    # Simulate development pattern
                    development_factor = min(1.0, period / 12 * 0.8 + 0.2)
                    cumulative_claim = base_claims * development_factor
                    cumulative_claims.append(cumulative_claim)
                
                triangle_data[year] = cumulative_claims
        
        triangle = pd.DataFrame(triangle_data, index=development_periods)
        return triangle
    
    def _calculate_development_factors(self, triangle: pd.DataFrame) -> pd.Series:
        """Calculate development factors from triangle"""
        dev_factors = []
        
        for i in range(len(triangle.columns) - 1):
            current_period = triangle.iloc[:, i]
            next_period = triangle.iloc[:, i + 1]
            
            # Calculate development factor
            factor = next_period.sum() / current_period.sum() if current_period.sum() > 0 else 1.0
            dev_factors.append(factor)
        
        return pd.Series(dev_factors, index=triangle.columns[:-1])
    
    def _project_ultimate_claims(self, triangle: pd.DataFrame, dev_factors: pd.Series) -> pd.Series:
        """Project ultimate claims using development factors"""
        ultimate_claims = {}
        
        for i, (accident_year, current_claims) in enumerate(triangle.iloc[:, -1].items()):
            if i < len(dev_factors):
                # Use calculated development factor
                dev_factor = dev_factors.iloc[i]
            else:
                # Use tail factor for older years
                dev_factor = self.tail_factor
            
            ultimate_claims[accident_year] = current_claims * dev_factor
        
        return pd.Series(ultimate_claims)
    
    def _calculate_confidence_intervals(self, triangle: pd.DataFrame, 
                                      dev_factors: pd.Series, 
                                      ultimate_claims: pd.Series) -> Dict:
        """Calculate confidence intervals for reserve estimates"""
        # Simplified confidence interval calculation
        # In practice, this would use more sophisticated methods like Mack's method
        
        total_ultimate = ultimate_claims.sum()
        total_reported = triangle.iloc[:, -1].sum()
        total_reserves = total_ultimate - total_reported
        
        # Estimate standard error (simplified)
        std_error = total_reserves * 0.1  # 10% of reserves as rough estimate
        
        z_score = stats.norm.ppf((1 + self.confidence_level) / 2)
        margin_of_error = z_score * std_error
        
        return {
            'lower_bound': total_reserves - margin_of_error,
            'upper_bound': total_reserves + margin_of_error,
            'standard_error': std_error,
            'confidence_level': self.confidence_level
        }
    
    def _analyze_trend(self, values: np.ndarray, metric_name: str) -> Dict:
        """Analyze trend in a time series"""
        if len(values) < 2:
            return {
                'metric': metric_name,
                'trend_direction': 'insufficient_data',
                'trend_strength': 0.0,
                'p_value': 1.0,
                'confidence_interval': [0, 0]
            }
        
        # Fit linear regression
        x = np.arange(len(values)).reshape(-1, 1)
        y = values
        
        model = LinearRegression()
        model.fit(x, y)
        
        # Calculate trend strength (R-squared)
        trend_strength = model.score(x, y)
        
        # Calculate p-value
        slope = model.coef_[0]
        residuals = y - model.predict(x)
        mse = np.mean(residuals**2)
        se_slope = np.sqrt(mse / np.sum((x - np.mean(x))**2))
        t_stat = slope / se_slope if se_slope > 0 else 0
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), len(values) - 2))
        
        # Determine trend direction
        if p_value < 0.05:
            trend_direction = 'increasing' if slope > 0 else 'decreasing'
        else:
            trend_direction = 'stable'
        
        # Calculate confidence interval
        confidence_interval = [
            slope - 1.96 * se_slope,
            slope + 1.96 * se_slope
        ]
        
        return {
            'metric': metric_name,
            'trend_direction': trend_direction,
            'trend_strength': trend_strength,
            'p_value': p_value,
            'slope': slope,
            'confidence_interval': confidence_interval
        }
    
    def _save_reserve_calculation(self, result: Dict):
        """Save reserve calculation to database"""
        try:
            db = SessionLocal()
            reserve_calc = ReserveCalculation(
                method=result['method'],
                total_reserves=result['total_reserves'],
                confidence_level=self.confidence_level,
                parameters=json.dumps(result)
            )
            db.add(reserve_calc)
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Error saving reserve calculation: {e}")
    
    def _save_trend_analysis(self, metric: str, trend_data: Dict):
        """Save trend analysis to database"""
        try:
            db = SessionLocal()
            trend_analysis = TrendAnalysis(
                metric=metric,
                trend_direction=trend_data['trend_direction'],
                trend_strength=trend_data['trend_strength'],
                p_value=trend_data['p_value'],
                confidence_interval=json.dumps(trend_data['confidence_interval'])
            )
            db.add(trend_analysis)
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Error saving trend analysis: {e}")
    
    def get_reserve_summary(self) -> Dict:
        """Get summary of all reserve calculations"""
        try:
            db = SessionLocal()
            recent_calculations = db.query(ReserveCalculation).order_by(
                ReserveCalculation.calculation_date.desc()
            ).limit(10).all()
            
            summary = {
                'total_calculations': len(recent_calculations),
                'latest_calculation': recent_calculations[0].calculation_date.isoformat() if recent_calculations else None,
                'methods_used': list(set([calc.method for calc in recent_calculations])),
                'total_reserves_by_method': {}
            }
            
            for calc in recent_calculations:
                if calc.method not in summary['total_reserves_by_method']:
                    summary['total_reserves_by_method'][calc.method] = []
                summary['total_reserves_by_method'][calc.method].append(calc.total_reserves)
            
            db.close()
            return summary
            
        except Exception as e:
            logger.error(f"Error getting reserve summary: {e}")
            return {}
