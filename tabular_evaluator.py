"""
19th Hole Investment Club - Tabular Share Evaluator
Creates a comprehensive chart showing all evaluation parameters in table format
"""

import pandas as pd
import streamlit as st
import plotly.express as px
from investment_parameters import (
    get_sector_specific_weights, calculate_parameter_score,
    generate_investment_recommendation
)

def create_evaluation_table(stock_data):
    """
    Create a comprehensive evaluation table showing all parameters
    """
    company_name = stock_data.get('name', 'Unknown Company')
    ticker = stock_data.get('ticker', 'N/A')
    sector = stock_data.get('sector', 'Technology')
    parameters = stock_data.get('parameters', {})
    data_confidence = stock_data.get('data_confidence', {})
    
    # Get sector-specific weightings (importance scores)
    weightings = get_sector_specific_weights(sector)
    
    # Calculate parameter scores (performance 1-10)
    param_scores = {}
    for param, value in parameters.items():
        if pd.isna(value) or value is None:
            param_scores[param] = 5.0  # Neutral for missing data
        else:
            param_scores[param] = calculate_parameter_score(param, value, sector)
    
    # Create the evaluation table
    evaluation_data = []
    total_weighted_score = 0
    total_max_possible = 0
    
    for param in weightings.keys():
        if param in parameters:
            value = parameters[param]
            importance = weightings[param]
            performance = param_scores[param]
            weighted_score = performance * importance
            max_possible = 10 * importance
            
            total_weighted_score += weighted_score
            total_max_possible += max_possible
            
            # Format value for display
            if pd.isna(value) or value is None:
                value_display = "N/A"
            elif param in ['P/E Ratio', 'P/B Ratio', 'Debt/Equity', 'Current Ratio']:
                value_display = f"{value:.2f}"
            elif param in ['Revenue Growth', 'Return on Equity', 'EPS Growth', 'Free Cash Flow Yield', 'Dividend Yield', 'Operating Margin']:
                value_display = f"{value:.1f}%"
            else:
                value_display = f"{value:.2f}"
            
            evaluation_data.append({
                'Parameter': param,
                'Value': value_display,
                'Importance (d)': importance,
                'Performance (e)': f"{performance:.1f}",
                'Weighted Score (e×d)': f"{weighted_score:.1f}",
                'Max Possible': f"{max_possible:.1f}",
                'Data Confidence': data_confidence.get(param, 'Unknown')
            })
    
    # Calculate 19H score as percentage
    nineteen_h_score = (total_weighted_score / total_max_possible) * 100 if total_max_possible > 0 else 0
    
    return pd.DataFrame(evaluation_data), nineteen_h_score, total_weighted_score, total_max_possible

def display_company_header(stock_data, nineteen_h_score):
    """
    Display company header with key information
    """
    company_name = stock_data.get('name', 'Unknown Company')
    ticker = stock_data.get('ticker', 'N/A')
    sector = stock_data.get('sector', 'Technology')
    current_price = stock_data.get('current_price', 0)
    
    col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
    
    with col1:
        st.markdown(f"### {company_name} ({ticker})")
        st.markdown(f"**Sector:** {sector}")
    
    with col2:
        st.metric("Current Price", f"${current_price:.2f}" if current_price else "N/A")
    
    with col3:
        # 19H Score with color coding
        score_color = "#28a745" if nineteen_h_score >= 75 else "#6f9bd1" if nineteen_h_score >= 60 else "#ffc107" if nineteen_h_score >= 40 else "#dc3545"
        st.markdown(f"""
        <div style="text-align: center; padding: 10px; border-radius: 10px; background-color: {score_color}20;">
            <div style="font-size: 1.5rem; font-weight: bold; color: {score_color};">
                19H Score
            </div>
            <div style="font-size: 2rem; font-weight: bold; color: {score_color};">
                {nineteen_h_score:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Investment recommendation
        weightings = get_sector_specific_weights(sector)
        parameters = stock_data.get('parameters', {})
        param_scores = {}
        for param, value in parameters.items():
            if pd.isna(value) or value is None:
                param_scores[param] = 5.0
            else:
                param_scores[param] = calculate_parameter_score(param, value, sector)
        
        recommendation = generate_investment_recommendation(param_scores, weightings, sector)
        rec_class = "success" if "BUY" in recommendation else "warning" if "HOLD" in recommendation else "error"
        st.markdown(f"**Investment Recommendation:**")
        if "STRONG BUY" in recommendation:
            st.success(recommendation)
        elif "BUY" in recommendation:
            st.info(recommendation)
        elif "HOLD" in recommendation:
            st.warning(recommendation)
        else:
            st.error(recommendation)

def style_evaluation_table(df):
    """
    Apply styling to the evaluation table
    """
    def highlight_performance(val):
        """Color code performance scores"""
        try:
            score = float(val)
            if score >= 8:
                return 'background-color: #d4edda; color: #155724; font-weight: bold'
            elif score >= 6:
                return 'background-color: #d1ecf1; color: #0c5460; font-weight: bold'
            elif score >= 4:
                return 'background-color: #fff3cd; color: #856404; font-weight: bold'
            else:
                return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
        except:
            return ''
    
    def highlight_importance(val):
        """Color code importance scores"""
        try:
            score = int(val)
            if score >= 9:
                return 'background-color: #6f42c1; color: white; font-weight: bold'
            elif score >= 7:
                return 'background-color: #007bff; color: white; font-weight: bold'
            elif score >= 5:
                return 'background-color: #17a2b8; color: white; font-weight: bold'
            else:
                return 'background-color: #6c757d; color: white; font-weight: bold'
        except:
            return ''
    
    # Apply styling
    styled_df = df.style.applymap(highlight_performance, subset=['Performance (e)'])
    styled_df = styled_df.applymap(highlight_importance, subset=['Importance (d)'])
    
    return styled_df

def create_parameter_chart(df, sector):
    """
    Create a visual chart of parameter performance vs importance
    """
    # Prepare data for plotting
    chart_data = []
    for _, row in df.iterrows():
        chart_data.append({
            'Parameter': row['Parameter'],
            'Importance': int(row['Importance (d)']),
            'Performance': float(row['Performance (e)']),
            'Weighted_Score': float(row['Weighted Score (e×d)'])
        })
    
    chart_df = pd.DataFrame(chart_data)
    
    # Create scatter plot
    fig = px.scatter(
        chart_df,
        x='Importance',
        y='Performance',
        size='Weighted_Score',
        color='Performance',
        hover_name='Parameter',
        color_continuous_scale='RdYlGn',
        title=f"Parameter Analysis for {sector} Sector",
        labels={
            'Importance': 'Parameter Importance (Sector-Specific)',
            'Performance': 'Company Performance (1-10)',
            'Weighted_Score': 'Weighted Score'
        },
        range_x=[0, 11],
        range_y=[0, 11]
    )
    
    # Add quadrant lines
    fig.add_hline(y=5, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=5, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Add annotations for quadrants
    fig.add_annotation(x=8.5, y=8.5, text="High Impact<br>Strong Performance", showarrow=False, 
                      bgcolor="rgba(40, 167, 69, 0.1)", bordercolor="green")
    fig.add_annotation(x=2.5, y=8.5, text="Low Impact<br>Strong Performance", showarrow=False,
                      bgcolor="rgba(111, 155, 209, 0.1)", bordercolor="blue")
    fig.add_annotation(x=8.5, y=2.5, text="High Impact<br>Weak Performance", showarrow=False,
                      bgcolor="rgba(220, 53, 69, 0.1)", bordercolor="red")
    fig.add_annotation(x=2.5, y=2.5, text="Low Impact<br>Weak Performance", showarrow=False,
                      bgcolor="rgba(108, 117, 125, 0.1)", bordercolor="gray")
    
    fig.update_layout(height=600)
    
    return fig

def display_sector_insights(sector, df):
    """
    Display insights about sector-specific parameter importance
    """
    st.markdown("### Sector Analysis Insights")
    
    # Find highest and lowest importance parameters
    df_sorted = df.sort_values('Importance (d)', ascending=False)
    highest_importance = df_sorted.iloc[0]
    lowest_importance = df_sorted.iloc[-1]
    
    # Find best and worst performing parameters
    df_perf_sorted = df.sort_values('Performance (e)', ascending=False)
    best_performance = df_perf_sorted.iloc[0]
    worst_performance = df_perf_sorted.iloc[-1]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Parameter Importance")
        st.info(f"**Most Critical for {sector}:** {highest_importance['Parameter']} (Importance: {highest_importance['Importance (d)']})")
        st.info(f"**Least Critical for {sector}:** {lowest_importance['Parameter']} (Importance: {lowest_importance['Importance (d)']})")
    
    with col2:
        st.markdown("#### Company Performance")
        st.success(f"**Strongest Area:** {best_performance['Parameter']} (Score: {best_performance['Performance (e)']})")
        st.error(f"**Weakest Area:** {worst_performance['Parameter']} (Score: {worst_performance['Performance (e)']})")