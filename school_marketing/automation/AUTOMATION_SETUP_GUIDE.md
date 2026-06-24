# Social Media Automation Setup Guide

## Overview
This guide will help you set up and use the automation tools for managing your school's social media presence.

## Tools Included

### 1. Social Media Scheduler (`social_media_scheduler.py`)
Automatically generates and manages your content calendar with:
- Daily themed posts (Monday Motivation, Teacher Tuesday, etc.)
- Special event scheduling
- Content templates for various post types
- CSV export for easy viewing

### 2. Analytics Dashboard (`analytics_dashboard.py`)
Tracks and reports on your social media performance:
- Weekly performance reports
- Growth tracking across platforms
- Engagement insights
- Performance alerts

## Installation

### Prerequisites
- Python 3.7 or higher
- Basic command line knowledge

### Step 1: Install Python
If you don't have Python installed:
- Windows: Download from [python.org](https://python.org)
- Mac: Use Homebrew: `brew install python3`
- Linux: `sudo apt-get install python3`

### Step 2: Install Required Libraries
```bash
pip install -r requirements.txt
```

## Using the Social Media Scheduler

### Basic Usage
1. Navigate to the automation folder:
   ```bash
   cd school_marketing/automation
   ```

2. Run the scheduler:
   ```bash
   python social_media_scheduler.py
   ```

3. This will generate:
   - A month of content ideas
   - A CSV file with your content calendar
   - Post templates for each platform

### Customizing Your School Name
Edit the script and change:
```python
scheduler = SocialMediaScheduler("Your School Name Here")
```

### Adding Special Events
```python
scheduler.schedule_special_event(
    date="2025-03-15",
    event_name="Spring Open House",
    event_details={
        "platforms": ["facebook", "twitter"],
        "facebook_content": "Join us for Spring Open House!...",
        "twitter_content": "Spring Open House March 15!..."
    }
)
```

### Exporting Your Calendar
The script automatically creates `school_content_calendar.csv` which you can:
- Open in Excel or Google Sheets
- Share with your team
- Use with scheduling tools

## Using the Analytics Dashboard

### Generating Reports
1. Run the analytics dashboard:
   ```bash
   python analytics_dashboard.py
   ```

2. This creates:
   - Weekly performance report (markdown file)
   - CSV export of metrics
   - Performance alerts

### Understanding the Reports
- **Growth Metrics**: Shows follower changes
- **Engagement Rates**: Measures audience interaction
- **Platform Comparison**: Identifies best performers
- **Recommendations**: Actionable next steps

## Scheduling Tools Integration

### Option 1: Hootsuite (Paid)
1. Export your CSV calendar
2. Import into Hootsuite's bulk scheduler
3. Add images and final edits
4. Schedule all posts at once

### Option 2: Buffer (Free/Paid)
1. Use Buffer's CSV import feature
2. Upload your content calendar
3. Set posting times
4. Review and publish

### Option 3: Facebook Creator Studio (Free)
1. For Facebook and Instagram only
2. Manually copy content from calendar
3. Schedule directly in platform
4. Access built-in analytics

### Option 4: Later (Visual scheduler)
1. Best for Instagram-heavy strategies
2. Drag and drop interface
3. Visual content calendar
4. Link in bio tool included

## Best Practices

### Content Creation Workflow
1. **Monday**: Generate weekly content calendar
2. **Tuesday**: Create/gather visual assets
3. **Wednesday**: Write and refine copy
4. **Thursday**: Schedule posts for next week
5. **Friday**: Review analytics and adjust

### Image Requirements by Platform
- **Facebook**: 1200 x 630 pixels
- **Twitter/X**: 1024 x 512 pixels
- **Instagram**: 1080 x 1080 pixels (square)
- **YouTube thumbnail**: 1280 x 720 pixels

### Hashtag Guidelines
- Research trending education hashtags weekly
- Create school-specific hashtags
- Use 2-3 hashtags on Twitter
- Use 10-15 hashtags on Instagram
- Use 3-5 hashtags on Facebook

## Automation Tips

### Using Cron (Mac/Linux) for Scheduled Reports
Add to crontab for weekly reports:
```bash
0 9 * * 1 cd /path/to/automation && python analytics_dashboard.py
```

### Using Task Scheduler (Windows)
1. Open Task Scheduler
2. Create Basic Task
3. Set to run weekly
4. Action: Start program
5. Program: `python`
6. Arguments: `C:\path\to\analytics_dashboard.py`

## Troubleshooting

### Common Issues

**Issue**: "Module not found" error
**Solution**: Install requirements: `pip install -r requirements.txt`

**Issue**: CSV file not opening correctly
**Solution**: Ensure Excel/Sheets is set to UTF-8 encoding

**Issue**: Dates showing incorrectly
**Solution**: Check system date format settings

## Advanced Customization

### Adding New Post Types
Edit `social_media_scheduler.py`:
```python
def create_custom_post(self, date):
    return {
        "facebook": "Your custom Facebook content",
        "twitter": "Your custom Twitter content",
        "image_suggestion": "Description of visual"
    }
```

### Modifying Analytics Metrics
Edit `analytics_dashboard.py` to track custom metrics:
```python
# Add to platform data
"custom_metric": random.randint(0, 100)
```

## API Integration (Advanced)

### Facebook Graph API
For automated posting (requires approval):
1. Create Facebook App
2. Get Page Access Token
3. Use requests library to post

### Twitter API v2
For automated tweets:
1. Apply for developer account
2. Create app and get keys
3. Use tweepy library

### YouTube Data API
For video analytics:
1. Enable YouTube API in Google Console
2. Get API key
3. Use google-api-python-client

## Support Resources

### Documentation
- [Facebook for Developers](https://developers.facebook.com)
- [Twitter Developer Platform](https://developer.twitter.com)
- [YouTube API](https://developers.google.com/youtube)

### Scheduling Tool Tutorials
- [Hootsuite Academy](https://education.hootsuite.com)
- [Buffer Resources](https://buffer.com/resources)
- [Later Blog](https://later.com/blog)

### Community Support
- Join education marketing groups on Facebook
- Follow #EdTech on Twitter
- Subscribe to school marketing blogs

## Next Steps

1. **Week 1**: Set up tools and generate first calendar
2. **Week 2**: Start scheduling posts, track metrics
3. **Week 3**: Analyze results, refine strategy
4. **Month 1**: Full implementation and optimization

Remember: Consistency is key! Even automated tools need human oversight for best results.