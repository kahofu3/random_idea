#!/usr/bin/env python3
"""
School Social Media Content Scheduler
Helps manage and schedule social media content across platforms
"""

import json
import csv
import datetime
from datetime import timedelta
import os
import random
from typing import Dict, List, Optional

class SocialMediaScheduler:
    def __init__(self, school_name: str = "Your School"):
        self.school_name = school_name
        self.content_calendar = []
        self.templates = self.load_templates()
        
    def load_templates(self) -> Dict:
        """Load content templates for different post types"""
        return {
            "achievement": [
                "🌟 Congratulations to {student_name} for {achievement}! We're so proud of your hard work! #{school_name}Pride",
                "Amazing news! Our {team_group} just {achievement}! 🎉 #StudentSuccess #{school_name}",
                "👏 Shoutout to {student_name} who {achievement}! This is what excellence looks like! #ProudSchool"
            ],
            "event": [
                "📅 Mark your calendars! {event_name} is happening on {date} at {time}. Don't miss it! RSVP: {link}",
                "Join us for {event_name} on {date}! {description} See you there! 📍 {location}",
                "🎉 SAVE THE DATE: {event_name} - {date}. All are welcome! Details: {link}"
            ],
            "tip": [
                "📚 Study Tip: {tip_content} What's your favorite study method? #StudyTips #Education",
                "💡 Did you know? {fact_content} Learn more about our {program} at {link}",
                "✏️ Quick tip for success: {tip_content} #EducationMatters #{school_name}"
            ],
            "announcement": [
                "📢 Important: {announcement_content} For more info, visit {link} or call {phone}",
                "🔔 Attention {audience}: {announcement_content} Questions? Contact us at {email}",
                "Update: {announcement_content} Thank you for your patience and understanding."
            ]
        }
    
    def generate_monthly_calendar(self, month: int, year: int) -> List[Dict]:
        """Generate a month's worth of social media content"""
        calendar = []
        start_date = datetime.date(year, month, 1)
        
        # Calculate number of days in month
        if month == 12:
            days_in_month = 31
        else:
            days_in_month = (datetime.date(year, month + 1, 1) - start_date).days
        
        for day in range(1, days_in_month + 1):
            current_date = datetime.date(year, month, day)
            day_of_week = current_date.weekday()  # 0 = Monday, 6 = Sunday
            
            # Skip weekends for regular posts (unless special event)
            if day_of_week in [5, 6]:  # Saturday, Sunday
                continue
                
            # Assign content based on day of week
            if day_of_week == 0:  # Monday
                post_type = "motivation"
                content = self.create_motivation_post(current_date)
            elif day_of_week == 1:  # Tuesday
                post_type = "teacher_spotlight"
                content = self.create_teacher_spotlight(current_date)
            elif day_of_week == 2:  # Wednesday
                post_type = "tip"
                content = self.create_tip_post(current_date)
            elif day_of_week == 3:  # Thursday
                post_type = "throwback"
                content = self.create_throwback_post(current_date)
            elif day_of_week == 4:  # Friday
                post_type = "student_feature"
                content = self.create_student_feature(current_date)
            
            calendar.append({
                "date": current_date.isoformat(),
                "day_of_week": current_date.strftime("%A"),
                "post_type": post_type,
                "platforms": ["facebook", "twitter"],
                "content": content,
                "status": "scheduled"
            })
        
        return calendar
    
    def create_motivation_post(self, date: datetime.date) -> Dict:
        """Create Monday motivation content"""
        quotes = [
            "Education is the passport to the future, for tomorrow belongs to those who prepare for it today.",
            "The beautiful thing about learning is that no one can take it away from you.",
            "Success is the sum of small efforts repeated day in and day out.",
            "Your education is a dress rehearsal for a life that is yours to lead."
        ]
        
        return {
            "facebook": f"💪 Monday Motivation!\n\n\"{random.choice(quotes)}\"\n\nHave a great week, {self.school_name} family! What are your goals this week?\n\n#MondayMotivation #{self.school_name}Pride #Education",
            "twitter": f"Monday Motivation: \"{random.choice(quotes)[:100]}...\" 💪\n\n#MondayMotivation #Education #{self.school_name}",
            "image_suggestion": "Inspirational quote graphic with school colors"
        }
    
    def create_teacher_spotlight(self, date: datetime.date) -> Dict:
        """Create teacher spotlight content"""
        return {
            "facebook": f"🍎 Teacher Tuesday Spotlight!\n\nThis week we're featuring [Teacher Name], who teaches [Subject]. [He/She] has been inspiring students at {self.school_name} for [X] years!\n\nStudent quote: \"[Teacher impact quote]\"\n\nThank you for all you do! 👏\n\n#TeacherAppreciation #TeacherTuesday #{self.school_name}",
            "twitter": f"Teacher Tuesday! Celebrating [Teacher Name] who makes [Subject] come alive for our students! 🍎 Thank you for your dedication! #TeacherTuesday #{self.school_name}",
            "image_suggestion": "Teacher photo with quote overlay"
        }
    
    def create_tip_post(self, date: datetime.date) -> Dict:
        """Create educational tip content"""
        tips = [
            "Break study sessions into 25-minute chunks with 5-minute breaks to improve retention!",
            "Color-coding your notes can improve memory recall by up to 30%!",
            "Teaching someone else what you've learned is one of the best ways to retain information!",
            "Getting 8 hours of sleep before a test is more beneficial than an all-night study session!"
        ]
        
        tip = random.choice(tips)
        return {
            "facebook": f"📚 Wisdom Wednesday - Study Tip!\n\n{tip}\n\nWhat study techniques work best for you? Share your tips below! 👇\n\n#StudyTips #WisdomWednesday #{self.school_name} #Education",
            "twitter": f"Study Tip Wednesday: {tip} 📚 What's your go-to study method? #StudyTips #Education #{self.school_name}",
            "image_suggestion": "Study tip infographic"
        }
    
    def create_throwback_post(self, date: datetime.date) -> Dict:
        """Create throwback Thursday content"""
        return {
            "facebook": f"📸 #ThrowbackThursday!\n\nLooking back at [Event/Achievement from past]. [Brief description of memory and its significance].\n\nWhat's your favorite {self.school_name} memory? Share in the comments!\n\n#TBT #{self.school_name}Memories #SchoolPride",
            "twitter": f"#TBT to [past event/achievement]! 📸 Those were the days! What's your favorite {self.school_name} memory? #ThrowbackThursday",
            "image_suggestion": "Historical photo from school archives"
        }
    
    def create_student_feature(self, date: datetime.date) -> Dict:
        """Create student feature content"""
        return {
            "facebook": f"🌟 Feature Friday - Student Spotlight!\n\nMeet [Student Name], a [Grade] student who [achievement/involvement]. [He/She] is involved in [activities] and plans to [future goals].\n\nAdvice to other students: \"[Student quote]\"\n\nKeep shining! ✨\n\n#StudentSpotlight #FeatureFriday #{self.school_name}Excellence",
            "twitter": f"Feature Friday! 🌟 Celebrating [Student Name] who [achievement]. \"[Short quote]\" #StudentSuccess #{self.school_name}",
            "image_suggestion": "Student photo in action or portrait"
        }
    
    def schedule_special_event(self, date: str, event_name: str, event_details: Dict) -> Dict:
        """Schedule a special event post"""
        post = {
            "date": date,
            "post_type": "special_event",
            "event_name": event_name,
            "platforms": event_details.get("platforms", ["facebook", "twitter", "youtube"]),
            "content": {
                "facebook": event_details.get("facebook_content", ""),
                "twitter": event_details.get("twitter_content", ""),
                "youtube": event_details.get("youtube_description", "")
            },
            "media": event_details.get("media", []),
            "status": "scheduled"
        }
        self.content_calendar.append(post)
        return post
    
    def export_calendar_csv(self, filename: str = "content_calendar.csv"):
        """Export content calendar to CSV file"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['date', 'day_of_week', 'post_type', 'platforms', 
                         'facebook_content', 'twitter_content', 'status']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for post in self.content_calendar:
                row = {
                    'date': post['date'],
                    'day_of_week': post.get('day_of_week', ''),
                    'post_type': post['post_type'],
                    'platforms': ', '.join(post['platforms']),
                    'facebook_content': post['content'].get('facebook', ''),
                    'twitter_content': post['content'].get('twitter', ''),
                    'status': post['status']
                }
                writer.writerow(row)
    
    def generate_content_report(self) -> Dict:
        """Generate analytics report for scheduled content"""
        report = {
            "total_posts": len(self.content_calendar),
            "posts_by_type": {},
            "posts_by_platform": {},
            "posts_by_status": {}
        }
        
        for post in self.content_calendar:
            # Count by type
            post_type = post['post_type']
            report['posts_by_type'][post_type] = report['posts_by_type'].get(post_type, 0) + 1
            
            # Count by platform
            for platform in post['platforms']:
                report['posts_by_platform'][platform] = report['posts_by_platform'].get(platform, 0) + 1
            
            # Count by status
            status = post['status']
            report['posts_by_status'][status] = report['posts_by_status'].get(status, 0) + 1
        
        return report
    
    def get_upcoming_posts(self, days: int = 7) -> List[Dict]:
        """Get posts scheduled for the next X days"""
        today = datetime.date.today()
        upcoming = []
        
        for post in self.content_calendar:
            post_date = datetime.date.fromisoformat(post['date'])
            if today <= post_date <= today + timedelta(days=days):
                upcoming.append(post)
        
        return sorted(upcoming, key=lambda x: x['date'])
    
    def create_hashtag_bank(self) -> Dict:
        """Create a bank of hashtags for different occasions"""
        return {
            "general": [f"#{self.school_name}", f"#{self.school_name}Pride", "#Education", "#SchoolLife"],
            "academic": ["#AcademicExcellence", "#StudentSuccess", "#Learning", "#STEM", "#Arts"],
            "sports": ["#SchoolSports", "#GoTeam", "#Athletics", "#Champions"],
            "events": ["#SchoolEvents", "#Community", "#SaveTheDate", "#JoinUs"],
            "seasonal": {
                "fall": ["#BackToSchool", "#FallSemester", "#Autumn"],
                "winter": ["#WinterBreak", "#HolidaySeason", "#NewYear"],
                "spring": ["#SpringSemester", "#Graduation", "#Testing"],
                "summer": ["#SummerSchool", "#SummerCamp", "#Enrollment"]
            }
        }


def main():
    """Example usage of the Social Media Scheduler"""
    # Initialize scheduler
    scheduler = SocialMediaScheduler("Lincoln High School")
    
    # Generate content for current month
    today = datetime.date.today()
    monthly_content = scheduler.generate_monthly_calendar(today.month, today.year)
    scheduler.content_calendar.extend(monthly_content)
    
    # Add a special event
    scheduler.schedule_special_event(
        date="2025-02-14",
        event_name="Valentine's Day Dance",
        event_details={
            "platforms": ["facebook", "twitter"],
            "facebook_content": "💕 Join us for our Valentine's Day Dance! Friday, Feb 14, 7-10 PM in the gym. Tickets $5 at the door. All students welcome! #ValentinesDay",
            "twitter_content": "Valentine's Dance this Friday! 💕 7-10 PM, $5 tickets. See you there! #SchoolDance",
            "media": ["valentine_dance_poster.jpg"]
        }
    )
    
    # Export calendar
    scheduler.export_calendar_csv("school_content_calendar.csv")
    
    # Generate report
    report = scheduler.generate_content_report()
    print(f"Content Calendar Report:")
    print(f"Total Posts Scheduled: {report['total_posts']}")
    print(f"Posts by Type: {report['posts_by_type']}")
    print(f"Posts by Platform: {report['posts_by_platform']}")
    
    # Show upcoming posts
    print("\nUpcoming Posts (Next 7 Days):")
    upcoming = scheduler.get_upcoming_posts(7)
    for post in upcoming[:3]:  # Show first 3
        print(f"- {post['date']}: {post['post_type']} on {', '.join(post['platforms'])}")


if __name__ == "__main__":
    main()