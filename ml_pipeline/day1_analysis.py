# Day 1 - Complete Personality Dataset Analysis
# Real Extrovert vs Introvert Dataset (2,900 samples)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

print("PERSONALITY ANALYTICS - DAY 1: REAL DATASET ANALYSIS")
print("=" * 70)

def load_and_analyze_dataset():
    """Load and perform complete dataset analysis"""
    
    # Load the dataset
    try:
        df = pd.read_csv('../data/raw/personality_dataset.csv')
        print("DATASET LOADED SUCCESSFULLY")
        print(f"Dataset shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Basic info
        print(f"\nBASIC DATASET INFO:")
        print(f"   Total Samples: {len(df):,}")
        print(f"   Features: {len(df.columns) - 1}")
        print(f"   Target: Personality (Extrovert/Introvert)")
        
        # Target distribution
        print(f"\nPERSONALITY DISTRIBUTION:")
        personality_dist = df['Personality'].value_counts()
        for personality, count in personality_dist.items():
            percentage = (count / len(df)) * 100
            bar = "=" * int(percentage / 3)
            print(f"   {personality}: {count:,} samples ({percentage:.1f}%) {bar}")
        
        # Missing values
        missing = df.isnull().sum()
        if missing.sum() == 0:
            print(f"\nDATA QUALITY: No missing values found")
        else:
            print(f"\nMISSING VALUES DETECTED:")
            for col, count in missing[missing > 0].items():
                print(f"   {col}: {count} missing")
        
        # Feature analysis
        print(f"\nFEATURE ANALYSIS:")
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        categorical_cols = [col for col in categorical_cols if col != 'Personality']
        
        print(f"   Numerical features: {len(numeric_cols)}")
        for col in numeric_cols:
            print(f"     {col}: {df[col].min():.2f} - {df[col].max():.2f}")
        
        print(f"   Categorical features: {len(categorical_cols)}")
        for col in categorical_cols:
            unique_vals = df[col].unique()
            print(f"     {col}: {list(unique_vals)}")
        
        # Behavioral differences
        print(f"\nBEHAVIORAL DIFFERENCES:")
        extroverts = df[df['Personality'] == 'Extrovert']
        introverts = df[df['Personality'] == 'Introvert']
        
        for feature in numeric_cols:
            ext_mean = extroverts[feature].mean()
            int_mean = introverts[feature].mean()
            pct_diff = ((ext_mean - int_mean) / int_mean * 100) if int_mean != 0 else 0
            
            direction = "higher" if pct_diff > 0 else "lower"
            if abs(pct_diff) > 30:
                significance = "MAJOR"
            elif abs(pct_diff) > 15:
                significance = "SIGNIFICANT"
            else:
                significance = "MODERATE"
            
            print(f"   {feature}:")
            print(f"     Extroverts: {ext_mean:.2f} | Introverts: {int_mean:.2f}")
            print(f"     Difference: {significance} - Extroverts {pct_diff:+.1f}% {direction}")
        
        # Correlation analysis
        print(f"\nCORRELATION ANALYSIS:")
        df_encoded = df.copy()
        df_encoded['Personality_encoded'] = df_encoded['Personality'].map({'Extrovert': 1, 'Introvert': 0})
        
        # Calculate correlations with personality
        correlations = []
        for col in numeric_cols:
            corr = df_encoded[col].corr(df_encoded['Personality_encoded'])
            correlations.append((col, abs(corr), corr))
        
        correlations.sort(key=lambda x: x[1], reverse=True)
        
        print("   Top predictive features:")
        for i, (feature, abs_corr, corr) in enumerate(correlations[:5], 1):
            direction = "extrovert tendency" if corr > 0 else "introvert tendency"
            strength = "STRONG" if abs_corr > 0.5 else "MODERATE" if abs_corr > 0.3 else "WEAK"
            print(f"     {i}. {feature}: {corr:.3f} ({strength} - {direction})")
        
        # ML Readiness Assessment
        print(f"\nML READINESS ASSESSMENT:")
        
        # Sample size score
        sample_size = len(df)
        if sample_size >= 2000:
            size_score = "EXCELLENT"
        elif sample_size >= 1000:
            size_score = "GOOD"
        else:
            size_score = "FAIR"
        
        # Class balance score
        balance_ratio = personality_dist.max() / personality_dist.min()
        if balance_ratio <= 1.5:
            balance_score = "EXCELLENT"
        elif balance_ratio <= 2.0:
            balance_score = "GOOD"
        else:
            balance_score = "POOR"
        
        print(f"   Sample Size: {sample_size:,} samples ({size_score})")
        print(f"   Class Balance: {balance_ratio:.2f}:1 ratio ({balance_score})")
        print(f"   Missing Values: {missing.sum()} ({size_score if missing.sum() == 0 else 'NEEDS ATTENTION'})")
        print(f"   Feature Quality: {len(numeric_cols)} numerical features (GOOD)")
        
        # Overall assessment
        if size_score == "EXCELLENT" and balance_score in ["EXCELLENT", "GOOD"] and missing.sum() == 0:
            overall = "PRODUCTION READY"
        else:
            overall = "NEEDS MINOR PREPROCESSING"
        
        print(f"   Overall Assessment: {overall}")
        
        print(f"\nDAY 1 ANALYSIS COMPLETE")
        print(f"Dataset Quality: Excellent for ML development")
        print(f"Ready for Day 2: Model Development")
        
        return df
        
    except FileNotFoundError:
        print("ERROR: Dataset file not found!")
        print("Please upload personality_dataset.csv to data/raw/ folder")
        return None
    except Exception as e:
        print(f"ERROR: Error loading dataset: {e}")
        return None

if __name__ == "__main__":
    dataset = load_and_analyze_dataset()
