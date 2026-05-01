from fastapi import APIRouter, Depends
import httpx
from typing import List, Dict
from config import settings

router = APIRouter()

# Mock news for demonstration if API fails or key is missing
MOCK_NEWS = {
    "BCA": [
        {"title": "MNCs hiring Freshers for MERN Stack roles in Bangalore", "source": "TechCrunch", "link": "https://techcrunch.com", "snippet": "Demand for Full Stack developers is at an all-time high with salary packages up to 8 LPA."},
        {"title": "Top Skills for BCA Graduates in 2026: DevOps and Cloud", "source": "Business Insider", "link": "https://businessinsider.com", "snippet": "Learning Docker and Kubernetes can significantly boost your employability in the current market."},
    ],
    "BBA": [
        {"title": "MBA vs Experience: What top recruiters want for Marketing", "source": "Economic Times", "link": "https://economictimes.com", "snippet": "Companies are looking for digital marketing certifications and analytical skills for trainee roles."},
        {"title": "HR Tech is transforming hiring processes in India", "source": "Forbes", "link": "https://forbes.com", "snippet": "Understanding HR Analytics is now a prerequisite for many management trainee positions."},
    ],
    "B.Com": [
        {"title": "Big 4 Accounting firms announce record hiring for 2026", "source": "Bloomberg", "link": "https://bloomberg.com", "snippet": "PwC, EY, and Deloitte are looking for B.Com graduates with GST and advanced Excel skills."},
        {"title": "Future of FinTech: Careers in Digital Banking", "source": "LiveMint", "link": "https://livemint.com", "snippet": "Accounting graduates with knowledge of blockchain and digital ledgers are in high demand."},
    ]
}

@router.get("/news")
async def get_career_news(course: str = "Any"):
    # Normalize course
    course = "BCA" if "BCA" in course.upper() else "BBA" if "BBA" in course.upper() else "B.Com" if "COM" in course.upper() else "BCA"
    
    # In a real app, you would use NewsAPI.org here
    # query = f"{course} career opportunities India"
    # response = httpx.get(f"https://newsapi.org/v2/everything?q={query}&apiKey={settings.NEWS_KEY}")
    # return response.json()['articles']

    return MOCK_NEWS.get(course, MOCK_NEWS["BCA"])
