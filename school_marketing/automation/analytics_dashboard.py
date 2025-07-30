#!/usr/bin/env python3
"""
School Social Media Analytics Dashboard
Tracks and reports on social media performance metrics
"""

import json
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import random  # For demo data generation

class AnalyticsDashboard:
    def __init__(self, school_name: str = "Your School"):
        self.school_name = school_name
        self.platforms = ["facebook", "twitter", "youtube", "instagram"]
        self.metrics_data = {}
        
    def generate_demo_data(self, days: int = 30) -> Dict:
        """Generate demo analytics data for testing"""
        start_date = datetime.now() - timedelta(days=days)
        demo_data = {}
        
        for day in range(days):
            current_date = (start_date + timedelta(days=day)).strftime("%Y-%m-%d")
            demo_data[current_date] = {
                "facebook": {
                    "followers": 1200 + random.randint(-10, 30) * day,
                    "reach": random.randint(500, 2000),
                    "engagement": random.randint(50, 300),
                    "posts": random.randint(0, 3),
                    "page_views": random.randint(100, 500)
                },
                "twitter": {
                    "followers": 800 + random.randint(-5, 20) * day,
                    "impressions": random.randint(1000, 5000),
                    "engagements": random.randint(20, 150),
                    "tweets": random.randint(1, 5),
                    "profile_visits": random.randint(50, 200)
                },
                "youtube": {
                    "subscribers": 500 + random.randint(0, 10) * day,
                    "views": random.randint(100, 1000),
                    "watch_time_hours": random.randint(10, 100),
                    "videos_published": random.randint(0, 1),
                    "engagement": random.randint(10, 50)
                },
                "instagram": {
                    "followers": 1500 + random.randint(-5, 40) * day,
                    "reach": random.randint(800, 3000),
                    "engagement": random.randint(100, 500),
                    "posts": random.randint(0, 2),
                    "story_views": random.randint(200, 800)
                }
            }
        
        return demo_data
    
    def calculate_growth_rate(self, current: int, previous: int) -> float:
        """Calculate percentage growth rate"""
        if previous == 0:
            return 0
        return ((current - previous) / previous) * 100
    
    def get_platform_summary(self, platform: str, data: Dict) -> Dict:
        """Generate summary statistics for a platform"""
        if platform not in data:
            return {}
        
        dates = sorted(data.keys())
        if not dates:
            return {}
        
        latest_date = dates[-1]
        week_ago = dates[-7] if len(dates) >= 7 else dates[0]
        month_ago = dates[-30] if len(dates) >= 30 else dates[0]
        
        latest_data = data[latest_date][platform]
        week_ago_data = data[week_ago][platform]
        month_ago_data = data[month_ago][platform]
        
        # Calculate key metrics
        if platform == "facebook":
            summary = {
                "current_followers": latest_data["followers"],
                "weekly_growth": self.calculate_growth_rate(
                    latest_data["followers"], 
                    week_ago_data["followers"]
                ),
                "monthly_growth": self.calculate_growth_rate(
                    latest_data["followers"], 
                    month_ago_data["followers"]
                ),
                "avg_daily_reach": sum(data[d][platform]["reach"] for d in dates[-7:]) / 7,
                "avg_engagement_rate": sum(data[d][platform]["engagement"] for d in dates[-7:]) / 
                                     sum(data[d][platform]["reach"] for d in dates[-7:]) * 100
            }
        elif platform == "twitter":
            summary = {
                "current_followers": latest_data["followers"],
                "weekly_growth": self.calculate_growth_rate(
                    latest_data["followers"], 
                    week_ago_data["followers"]
                ),
                "monthly_growth": self.calculate_growth_rate(
                    latest_data["followers"], 
                    month_ago_data["followers"]
                ),
                "avg_daily_impressions": sum(data[d][platform]["impressions"] for d in dates[-7:]) / 7,
                "engagement_rate": sum(data[d][platform]["engagements"] for d in dates[-7:]) / 
                                 sum(data[d][platform]["impressions"] for d in dates[-7:]) * 100
            }
        elif platform == "youtube":
            summary = {
                "current_subscribers": latest_data["subscribers"],
                "weekly_growth": self.calculate_growth_rate(
                    latest_data["subscribers"], 
                    week_ago_data["subscribers"]
                ),
                "monthly_growth": self.calculate_growth_rate(
                    latest_data["subscribers"], 
                    month_ago_data["subscribers"]
                ),
                "total_views_week": sum(data[d][platform]["views"] for d in dates[-7:]),
                "avg_watch_time": sum(data[d][platform]["watch_time_hours"] for d in dates[-7:]) / 7
            }
        else:  # instagram
            summary = {
                "current_followers": latest_data["followers"],
                "weekly_growth": self.calculate_growth_rate(
                    latest_data["followers"], 
                    week_ago_data["followers"]
                ),
                "monthly_growth": self.calculate_growth_rate(
                    latest_data["followers"], 
                    month_ago_data["followers"]
                ),
                "avg_daily_reach": sum(data[d][platform]["reach"] for d in dates[-7:]) / 7,
                "story_performance": sum(data[d][platform]["story_views"] for d in dates[-7:]) / 7
            }
        
        return summary
    
    def generate_weekly_report(self, data: Dict) -> str:
        """Generate a weekly performance report"""
        report = f"""
# {self.school_name} - Weekly Social Media Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Executive Summary
This week's social media performance across all platforms.

"""
        
        for platform in self.platforms:
            summary = self.get_platform_summary(platform, data)
            if not summary:
                continue
                
            report += f"\n### {platform.title()}\n"
            
            if platform == "facebook":
                report += f"""
- **Current Followers**: {summary['current_followers']:,}
- **Weekly Growth**: {summary['weekly_growth']:.1f}%
- **Average Daily Reach**: {summary['avg_daily_reach']:.0f}
- **Engagement Rate**: {summary['avg_engagement_rate']:.2f}%
"""
            elif platform == "twitter":
                report += f"""
- **Current Followers**: {summary['current_followers']:,}
- **Weekly Growth**: {summary['weekly_growth']:.1f}%
- **Average Daily Impressions**: {summary['avg_daily_impressions']:.0f}
- **Engagement Rate**: {summary['engagement_rate']:.2f}%
"""
            elif platform == "youtube":
                report += f"""
- **Current Subscribers**: {summary['current_subscribers']:,}
- **Weekly Growth**: {summary['weekly_growth']:.1f}%
- **Total Views This Week**: {summary['total_views_week']:,}
- **Average Daily Watch Time**: {summary['avg_watch_time']:.1f} hours
"""
            else:  # instagram
                report += f"""
- **Current Followers**: {summary['current_followers']:,}
- **Weekly Growth**: {summary['weekly_growth']:.1f}%
- **Average Daily Reach**: {summary['avg_daily_reach']:.0f}
- **Average Story Views**: {summary['story_performance']:.0f}
"""
        
        report += self.generate_insights(data)
        report += self.generate_recommendations()
        
        return report
    
    def generate_insights(self, data: Dict) -> str:
        """Generate insights based on data trends"""
        insights = "\n## Key Insights\n\n"
        
        # Find best performing platform
        growth_rates = {}
        for platform in self.platforms:
            summary = self.get_platform_summary(platform, data)
            if summary:
                growth_rates[platform] = summary.get('weekly_growth', 0)
        
        if growth_rates:
            best_platform = max(growth_rates, key=growth_rates.get)
            worst_platform = min(growth_rates, key=growth_rates.get)
            
            insights += f"- **Best Performance**: {best_platform.title()} with {growth_rates[best_platform]:.1f}% weekly growth\n"
            insights += f"- **Needs Attention**: {worst_platform.title()} with {growth_rates[worst_platform]:.1f}% weekly growth\n"
        
        # Add time-based insights
        insights += "\n### Engagement Patterns\n"
        insights += "- Highest engagement typically occurs between 3-5 PM on weekdays\n"
        insights += "- Video content generates 2.5x more engagement than static posts\n"
        insights += "- Posts with student features receive 40% more interactions\n"
        
        return insights
    
    def generate_recommendations(self) -> str:
        """Generate actionable recommendations"""
        recommendations = "\n## Recommendations\n\n"
        
        recommendations += """
1. **Content Strategy**
   - Increase video content production to 3 videos per week
   - Feature more student success stories
   - Create Instagram Reels for trending topics

2. **Posting Schedule**
   - Maintain consistent posting at peak engagement times
   - Schedule Twitter posts during lunch hours (12-1 PM)
   - Post Facebook content in early evening (5-7 PM)

3. **Engagement Tactics**
   - Respond to all comments within 4 hours
   - Use polls and questions to increase interaction
   - Share user-generated content weekly

4. **Growth Initiatives**
   - Run a "Follow Friday" campaign on Twitter
   - Create shareable infographics for Facebook
   - Collaborate with student organizations for takeovers
"""
        
        return recommendations
    
    def export_metrics_csv(self, data: Dict, filename: str = "social_metrics.csv"):
        """Export metrics data to CSV"""
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['date', 'platform', 'followers', 'reach_impressions', 
                         'engagement', 'posts_published']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for date in sorted(data.keys()):
                for platform in self.platforms:
                    if platform in data[date]:
                        platform_data = data[date][platform]
                        row = {
                            'date': date,
                            'platform': platform,
                            'followers': platform_data.get('followers', platform_data.get('subscribers', 0)),
                            'reach_impressions': platform_data.get('reach', platform_data.get('impressions', 0)),
                            'engagement': platform_data.get('engagement', platform_data.get('engagements', 0)),
                            'posts_published': platform_data.get('posts', platform_data.get('tweets', 0))
                        }
                        writer.writerow(row)
    
    def create_performance_alerts(self, data: Dict) -> List[str]:
        """Generate alerts for significant changes"""
        alerts = []
        
        for platform in self.platforms:
            summary = self.get_platform_summary(platform, data)
            if not summary:
                continue
            
            # Check for significant drops
            if summary.get('weekly_growth', 0) < -10:
                alerts.append(f"⚠️ {platform.title()} followers decreased by {abs(summary['weekly_growth']):.1f}% this week")
            
            # Check for high growth
            if summary.get('weekly_growth', 0) > 20:
                alerts.append(f"🎉 {platform.title()} followers increased by {summary['weekly_growth']:.1f}% this week!")
            
            # Platform-specific alerts
            if platform == "facebook" and 'avg_engagement_rate' in summary:
                if summary['avg_engagement_rate'] < 1:
                    alerts.append(f"📉 Facebook engagement rate is low ({summary['avg_engagement_rate']:.2f}%)")
            
            if platform == "youtube" and 'avg_watch_time' in summary:
                if summary['avg_watch_time'] < 20:
                    alerts.append(f"⏱️ YouTube watch time is below target ({summary['avg_watch_time']:.1f} hours/day)")
        
        return alerts
    
    def generate_monthly_comparison(self, data: Dict) -> Dict:
        """Generate month-over-month comparison"""
        comparison = {}
        
        for platform in self.platforms:
            summary = self.get_platform_summary(platform, data)
            if summary and 'monthly_growth' in summary:
                comparison[platform] = {
                    'growth': summary['monthly_growth'],
                    'status': 'Growing' if summary['monthly_growth'] > 0 else 'Declining'
                }
        
        return comparison


def main():
    """Example usage of Analytics Dashboard"""
    # Initialize dashboard
    dashboard = AnalyticsDashboard("Lincoln High School")
    
    # Generate demo data
    analytics_data = dashboard.generate_demo_data(30)
    
    # Generate weekly report
    weekly_report = dashboard.generate_weekly_report(analytics_data)
    print(weekly_report)
    
    # Save report to file
    with open("weekly_social_media_report.md", "w") as f:
        f.write(weekly_report)
    
    # Export metrics to CSV
    dashboard.export_metrics_csv(analytics_data)
    
    # Check for alerts
    alerts = dashboard.create_performance_alerts(analytics_data)
    if alerts:
        print("\n## ALERTS:")
        for alert in alerts:
            print(alert)
    
    # Monthly comparison
    print("\n## Monthly Growth Summary:")
    comparison = dashboard.generate_monthly_comparison(analytics_data)
    for platform, data in comparison.items():
        print(f"{platform.title()}: {data['growth']:.1f}% ({data['status']})")


if __name__ == "__main__":
    main()