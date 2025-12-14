from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, 
    TableStyle, PageBreak, ListFlowable, ListItem
)
from reportlab.lib import colors
import os


def create_final_report(output_path: str = "results/final_report.pdf"):
    """Generate the final report PDF."""
    
    # Create document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=HexColor('#2C3E50')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=8,
        textColor=HexColor('#34495E')
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubheading',
        parent=styles['Heading3'],
        fontSize=12,
        spaceBefore=10,
        spaceAfter=5,
        textColor=HexColor('#7F8C8D')
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceBefore=5,
        spaceAfter=5,
        leading=14
    )
    
    # Build content
    story = []
    
    # Title
    story.append(Paragraph(
        "Dynamic Price Analysis of Aritzia E-commerce Products",
        title_style
    ))
    story.append(Spacer(1, 10))
    
    # Team Members Section
    story.append(Paragraph("1. Project Name and Team Members", heading_style))
    story.append(Paragraph(
        "<b>Project Name:</b> Dynamic Price Analysis of Aritzia E-commerce Products",
        body_style
    ))
    story.append(Paragraph(
        "<b>Team Members:</b>",
        body_style
    ))
    
    # Team table
    team_data = [
        ["Name", "USC Email", "USC ID"],
        ["[Mengxue Li]", "[mengxue@usc.edu]", "[6724826910]"],
    ]
    team_table = Table(team_data, colWidths=[2.5*inch, 2.5*inch, 1.5*inch])
    team_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#3498DB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(team_table)
    story.append(Spacer(1, 10))
    
    # Short Description
    story.append(Paragraph("2. Short Description", heading_style))
    story.append(Paragraph(
        "This project analyzes temporal price changes in Aritzia's online product catalog to uncover "
        "discount patterns, cross-category price behaviors, and potential pricing cycles. Fashion "
        "e-commerce platforms frequently employ dynamic pricing mechanisms that remain unclear to "
        "consumers. Our goal is to provide data-driven insights into Aritzia's pricing behavior and "
        "empower consumers with better purchasing strategies.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Research Questions:</b>",
        body_style
    ))
    story.append(Paragraph(
        "• Which product categories show the most frequent and significant discounts?<br/>"
        "• How do product prices change over time?<br/>"
        "• Are there identifiable patterns that can help consumers determine the best time to buy?",
        body_style
    ))
    story.append(Spacer(1, 5))
    
    # Data Section
    story.append(Paragraph("3. Data", heading_style))
    story.append(Paragraph("<b>Data Source:</b>", subheading_style))
    story.append(Paragraph(
        "Data was intended to be collected from the official Aritzia e-commerce website "
        "(https://www.aritzia.com) using Python's requests and BeautifulSoup libraries. However, "
        "due to website access restrictions, simulated data mimicking real Aritzia product data "
        "patterns was generated for this analysis.",
        body_style
    ))
    story.append(Paragraph("<b>Data Samples:</b>", subheading_style))
    
    # Data statistics table
    data_stats = [
        ["Metric", "Value"],
        ["Total Unique Products", "236"],
        ["Total Observations", "2,360 (236 products × 10 days)"],
        ["Collection Period", "December 1-10, 2025"],
        ["Categories Covered", "5 (Outerwear, Dresses, Tops, Pants, Accessories)"],
        ["Average Price", "$148.63"],
        ["Products on Sale", "50.3%"],
    ]
    data_table = Table(data_stats, colWidths=[2.5*inch, 4*inch])
    data_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#27AE60')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(data_table)
    story.append(Spacer(1, 10))
    
    # Data Cleaning, Analysis & Visualization
    story.append(Paragraph("4. Data Cleaning, Analysis & Visualization", heading_style))
    
    story.append(Paragraph("<b>Data Cleaning Process:</b>", subheading_style))
    story.append(Paragraph(
        "The raw data underwent several cleaning steps: (1) Removal of duplicate entries based on SKU, "
        "(2) Validation and standardization of price formats (rounding to 2 decimal places), "
        "(3) Recalculation of discount percentages for accuracy, (4) Addition of derived features "
        "including price tier (budget/mid-range/premium/luxury), discount tier (none/small/medium/large), "
        "and savings amount calculations.",
        body_style
    ))
    
    story.append(Paragraph("<b>Analysis Methods:</b>", subheading_style))
    story.append(Paragraph(
        "Three main analyses were conducted: (1) Category Discount Pattern Analysis examined which "
        "categories show the most frequent and significant discounts using aggregation and statistical "
        "measures. (2) Price Trend Analysis used time-series methods including linear regression to "
        "identify daily price change patterns. (3) Consumer Pattern Analysis identified actionable "
        "insights through correlation analysis and product-level tracking.",
        body_style
    ))
    
    story.append(Paragraph("<b>Key Findings:</b>", subheading_style))
    story.append(Paragraph(
        "<b>Finding 1 - Category Discounts:</b> Dresses had the highest discount frequency (61.1% of products "
        "on sale), while Tops showed the highest average discount rate (14.4%). Outerwear provided the "
        "largest absolute savings ($35.77 on average).",
        body_style
    ))
    story.append(Paragraph(
        "<b>Finding 2 - Price Trends:</b> A statistically significant decreasing trend in discount "
        "percentages was observed (slope: -0.145% per day, p-value: 0.001), suggesting discounts "
        "decreased over the collection period. Thursday showed the best average discounts.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Finding 3 - Consumer Patterns:</b> 67 products maintained consistent discounts throughout "
        "the period. No strong correlation was found between original price and discount percentage "
        "(r=0.021), indicating discounts are not primarily driven by price point.",
        body_style
    ))
    
    story.append(Paragraph("<b>Visualizations Created:</b>", subheading_style))
    story.append(Paragraph(
        "Seven visualizations were generated: (1) Daily price trajectory line charts showing price "
        "and discount trends over time, (2) Category discount comparison bar charts, (3) Box plots "
        "of price and discount distributions by category, (4) Heatmap showing category-level discount "
        "patterns across days, (5) Scatter plot of original price vs. discount rate, (6) Correlation "
        "matrix heatmap, and (7) Discount tier distribution charts.",
        body_style
    ))
    
    # Add a page break before section 5
    story.append(PageBreak())
    
    # Changes from Original Proposal
    story.append(Paragraph("5. Changes from Original Proposal", heading_style))
    story.append(Paragraph(
        "<b>Challenge Encountered:</b> The original proposal planned to collect data directly from "
        "Aritzia's website using Python's requests and BeautifulSoup libraries through publicly "
        "available JSON endpoints. However, the website implemented access restrictions that prevented "
        "direct data collection.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Solution Implemented:</b> To maintain the project's analytical rigor while working within "
        "constraints, realistic simulated data was generated that mimics actual e-commerce pricing "
        "patterns. The simulation includes: realistic price ranges for each category, dynamic price "
        "changes between days (15% daily change probability), appropriate discount distributions "
        "(10-50% discounts with weighted probabilities), and consistent product tracking across the "
        "10-day collection period.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Impact on Analysis:</b> While using simulated data, the analytical methods and "
        "visualization techniques remain exactly as proposed. The code infrastructure is designed "
        "to seamlessly handle real data when access becomes available.",
        body_style
    ))
    story.append(Spacer(1, 10))
    
    # Future Work
    story.append(Paragraph("6. Future Work", heading_style))
    story.append(Paragraph(
        "Given more time and resources, several improvements could be made:",
        body_style
    ))
    story.append(Paragraph(
        "<b>1. Real Data Collection:</b> Implement alternative data collection methods such as using "
        "Selenium for dynamic page rendering, or exploring official API partnerships with Aritzia.",
        body_style
    ))
    story.append(Paragraph(
        "<b>2. Extended Collection Period:</b> Collect data over 30-60 days to capture weekly and "
        "monthly patterns, including seasonal sales events (Black Friday, end-of-season sales).",
        body_style
    ))
    story.append(Paragraph(
        "<b>3. Predictive Modeling:</b> Develop machine learning models to predict future price "
        "changes and optimal purchase timing using historical patterns.",
        body_style
    ))
    story.append(Paragraph(
        "<b>4. Competitive Analysis:</b> Expand the analysis to compare Aritzia's pricing strategies "
        "with similar fashion retailers (Zara, H&M, Reformation) to provide broader market context.",
        body_style
    ))
    story.append(Paragraph(
        "<b>5. Consumer Alert System:</b> Build a notification system that alerts consumers when "
        "products reach their lowest historical prices or when new discounts are applied.",
        body_style
    ))
    
    # Build PDF
    doc.build(story)
    print(f"Final report saved to: {output_path}")


if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
    create_final_report("results/final_report.pdf")
